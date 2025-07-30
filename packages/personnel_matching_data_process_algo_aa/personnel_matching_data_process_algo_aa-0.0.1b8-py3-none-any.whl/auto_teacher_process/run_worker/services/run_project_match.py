import pandas as pd

from auto_teacher_process.db.services.db_insert_project_match import ProjectInsertDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.llm.services.llm_project_match import ProjectMatchLLMProcessor
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.mq.consumer import start_consumer
from auto_teacher_process.run_worker.run_base import BaseRunProcessor
from auto_teacher_process.utils.match_utils import get_teacher_past_schools
from auto_teacher_process.utils.paper_utils import project_parse


class ProjectMatchRunProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_teacher_data_processing_pipeline"  # 流水线名称
        self.task_type = "project_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "teacher_id"  # 数据主键字段
        self.set_file_paths()
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)

        self.db = ProjectInsertDBProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)
        self.llm = ProjectMatchLLMProcessor(logger=self.logger)

    async def process_row(self, row: pd.Series):
        # 以教师为单位进行处理
        teacher_id = row.teacher_id
        # 检查是否已经处理过该教师
        if teacher_id in self.processed_ids:
            return None  # 跳过已处理的教师

        derived_teacher_name = row.derived_teacher_name
        omit_description = row.omit_description
        project_experience = row.project_experience
        research_area = row.research_area
        school_name = row.school_name
        college_name = row.college_name
        project = project_parse(project_experience)

        # 教师过往经历学校查询：input: teacher_id; output: school_names
        past_schools_cn_list = get_teacher_past_schools(db=self.db, teacher_id=teacher_id, school_name=school_name)

        # TODO: ES 获取教师相关的项目，待完善
        teacher_projects = await self.es.async_es_to_df_by_teacher_name_and_supporting_unit_idx_project(
            derived_teacher_name, past_schools_cn_list
        )

        if teacher_projects is None:
            return None  # 如果没有相关论文，跳过

        batch_relation_list = []
        for _, data in teacher_projects.iterrows():
            if data["project_name"] is None or pd.isna(data["project_name"]):
                continue

            project_id, project_name, project_domain = data["project_id"], data["project_name"], data["project_domain"]

            data = {
                "mode": "high",
                "project_name": project_name,
                "project_domain": project_domain,
                "college": college_name,
                "description": omit_description,
                "project": project,
                "research": research_area,
            }

            llm_out = await self.llm.run(data)

            if llm_out:
                row = {
                    "teacher_id": teacher_id,
                    "project_id": project_id,
                    "high_true": 1,
                    "is_valid": 1,
                }
                batch_relation_list.append(row)
                continue
            # 如果没有匹配成功，仍然需要记录下来
            row = {
                "teacher_id": teacher_id,
                "project_id": project_id,
                "high_true": -1,
                "is_valid": 0,
            }
            batch_relation_list.append(row)

        return batch_relation_list

    async def run(self):
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        df = self.db.get_project_teacher_data_from_db(
            id_start=self.task_args["id_start"], id_end=self.task_args["id_end"]
        )
        self.logger.info(f"【{self.task_type}】: 数据读取完成", extra={"event": "db_read_end"})

        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        output_data = await self.process(df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})

        # ES需要手动关闭
        await self.es.close_es_engine()

        # 数据入库
        self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={"event": "db_insert_start"})
        db_input_data = {"file": output_data}
        self.db.run(db_input_data)
        self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={"event": "db_insert_end"})


@start_consumer(
    listen_queues=["queue.teacher_added_pipeline.run_info.project_match"],
    send_queues=[],
)
async def main(message) -> dict:
    args = message[0]
    processor = ProjectMatchRunProcessor(args)
    await processor.run()

    return args

from auto_teacher_process.db.db_base import BaseDBProcessor


class DedupInsertDBProcessor(BaseDBProcessor):
    """教师去重数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)

    def process(self, input_data: dict) -> None:
        """主处理流程"""
        # 获取输入参数
        province = input_data.get("province", "")
        file_dir = input_data.get("file_dir", "")
        if province == "" or file_dir == "":
            raise ValueError("请提供正确的省份和文件目录")

        merged_df = self._get_all_folders(file_dir, province)

        # 检查合并后数据是否为空
        if merged_df.empty:
            self.logger.debug("合并后数据为空，无需更新")
            return

        # 过滤需要更新的数据
        update_df = merged_df[merged_df["is_repeat"] == 1]
        self.logger.debug(f"需要更新的记录数: {len(update_df)}")

        # 构建SQL模板
        update_sql = """
            UPDATE derived_teacher_data
            SET
                related_teacher_id = :related_teacher_id,
                is_repeat = :is_repeat,
                status = :status,
                is_valid = :is_valid
            WHERE teacher_id = :teacher_id;
        """

        # 执行批量更新
        self.update_db(
            df=update_df,
            update_sql=update_sql,
            batch_size=1000,  # 根据实际情况调整批次大小
        )

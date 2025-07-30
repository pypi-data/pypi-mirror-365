import json
import time

from auto_teacher_process.config import Config
from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class TitleLLMProcessor(BaseLLMProcessor):
    prompt = """
## 任务描述
根据教师简介判断主人公教师当前是否具有'{title}'头衔。如果有，请返回True；否则，返回False。

## 注意事项
1. 不论'{title}'是该教师的主要身份还是次要身份，长期身份或短期身份，只要是主人公当前的头衔，即返回True。
2. 仅关注主人公教师的头衔，忽略简介中所有与主人公无关的信息。
3. 只关注当前头衔，忽略曾经的头衔。
4. 主人公可能同时拥有多个头衔，不需要进行比较。
5. 头衔范围不仅限于以下列表：{titles}。某些头衔可能有变体，例如，“讲座教授”、“客座教授”、“兼职教授”应视为“教授”的变体；同样，“特聘教授”和“名誉教授”等也应视为“教授”的变体。
6. 请根据上下文灵活判断头衔变体。若简介中出现未列出的头衔变体，但符合头衔的上下文含义，请视为该头衔的变体。
7. 头衔可能存在于对主人公教师的称呼中。

## 教师简介
{profile}
"""

    def __init__(
        self,
        logger=None,
        model_name: str = "qwen2.5-instruct-6-54-55",
        system: str = "llm_processor",
        stage: str = "unkonw_task_name",
    ):
        """
        职称提取处理器
        """
        super().__init__(model_name=model_name, system=system, stage=stage, logger=logger)
        # 加载职称配置
        self.titles = Config.LLM_CONFIG.TITLES.TITLES
        self.title_scores = Config.LLM_CONFIG.TITLES.TITLE_SCORES

    def build_prompt(self, input_data: dict) -> str:
        """
        构建提示词模板
        输入:
            input_data (dict): 包含profile键的输入数据
        输出:
            str: 完整的提示词
        """
        if "description" not in input_data:
            raise ValueError("input_data must contain 'description' key")

        return self.prompt.format(title=input_data["title"], titles=self.titles, profile=input_data["description"])

    def select_titles(self, title_list):
        # 职称评分字典

        if title_list is None:
            return 0, []
        scored_titles = []
        max_score = 10

        for title in title_list:
            score = 10
            for score_value, title_group in self.title_scores.items():
                score_value = int(score_value)  # 转换成整数
                if title in title_group:
                    score = score_value
                    break
            scored_titles.append((title, score))
            if score > max_score:
                max_score = score
        highest_titles = [title for title, score in scored_titles if score == max_score]

        return highest_titles

    async def process(self, input_data: dict) -> tuple:
        """
        处理LLM响应内容
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (处理结果, 是否成功)
        """
        extracted_titles = []

        for title_group in self.titles:
            for title in title_group:
                prompt = self.build_prompt({**input_data, "title": title})
                self.logger.debug(f"生成的提示词: {prompt[:200]}...")

                response = await self.get_llm_response(prompt, temperature=0)
                self.logger.debug(f"当前title:{title},LLM响应: {response[:200]}...")

                response = response if response is not None else ""
                if "True" in response:
                    self.logger.debug("处理结果:True")
                    extracted_titles.append(title)
                    self.logger.debug(f"成功提取职称: {title}")
                    break  # 只保留最高优先级的一个职称

        return extracted_titles, bool(extracted_titles)

    async def run(self, input_data: dict) -> tuple:
        """
        执行完整的处理流程
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (最终结果, 处理状态)
        """
        try:
            self.logger.info(
                f"启动llm处理流程{self.__class__.__name__}，输入参数:{input_data}", extra={"event": "start"}
            )
            start_time = time.time()
            if input_data.get("description"):
                result, is_valid = await self.process(input_data=input_data)
            else:
                raise ValueError("description is empty")

            if is_valid == 1:
                normalized_title = self.select_titles(result)
            else:
                normalized_title = []
            teacher_title = json.dumps(result, ensure_ascii=False)
            normalized_title = json.dumps(normalized_title, ensure_ascii=False)

            self.logger.debug(f"result: {(teacher_title, normalized_title, is_valid)}")

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            self.logger.info("处理完成", extra={"event": "end", "duration_ms": duration_ms})
            return teacher_title, normalized_title, is_valid
        except Exception as e:
            self.logger.error(f"处理过程出错: {e}", exc_info=True)
            return None, None, False

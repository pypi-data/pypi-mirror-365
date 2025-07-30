from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class PatentMatchLLMProcessor(BaseLLMProcessor):
    prompt_high = """
    ## 任务介绍
    对"专利信息"与"教师信息"在学科领域、研究方向等方面进行全面的分析，判断该专利是否属于该教师，如果属于回答"True"，不属于回答"False"。
    ## 专利信息
        "专利名称": {patent_name}
        "专利摘要": {abstract}
        "技术领域": {field}
    ## 教师信息
        "所属学院": {college}
        "教师简介": {description}
        "研究方向": {research}
        "相关项目": {project}

    ## 注意事项
    1. 只需要回答"True"或"False"，不要返回其他内容。 

    答案："""
    prompt_less = """
    ## 任务介绍
    从教师的所属学院判断该专利是否属于该教师，如果属于回答"True"，不属于回答"False"。
    ## 专利信息
        "专利名称": {patent_name}
        "专利摘要": {abstract}
    ## 教师信息
        "所属学院": {college}

    ## 注意事项
    1. 只需要回答"True"或"False"，不要返回其他内容。

    答案："""

    def __init__(self, model_name="qwen2.5-instruct-6-54-55", logger=None, system="llm_processor", stage="unkonw_task_name"):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        prompt_type = input_data.get("mode", "high")
        if prompt_type not in ["high", "less"]:
            raise ValueError("prompt_type must be one of 'high', 'less'")

        if prompt_type == "high":
            return self.prompt_high.format(
                patent_name=input_data["patent_name"],
                abstract=input_data["abstract"],
                field=input_data["field"],
                college=input_data["college"],
                description=input_data["description"],
                project=input_data["project"],
                research=input_data["research"],
            )
        if prompt_type == "less":
            return self.prompt_less.format(
                patent_name=input_data["patent_name"], abstract=input_data["abstract"], college=input_data["college"]
            )

    async def process(self, input_data: dict) -> str:
        """
        处理LLM响应内容
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (处理结果, 是否成功)
        """

        try:
            prompt = self.build_prompt(input_data)
            self.logger.debug(f"生成的提示词: {prompt[:200]}...")

            response = await self.get_llm_response(prompt, temperature=0.3)
            self.logger.debug(f"LLM响应: {response[:200]}...")
            return response
        except Exception as e:
            self.logger.error(f"处理流程失败: {e!s}", exc_info=True)
            raise e

    async def run(self, input_data: dict) -> bool:
        try:
            tip = 0
            while True:
                try:
                    output = await self.process(input_data=input_data)
                except Exception as e:  # 捕获所有异常
                    self.logger.error(f"请求失败，出现异常：{e}. 返回空字符串。", exc_info=True)
                    raise e
                if "True" in output:
                    return True
                if "False" in output:
                    return False
                tip += 1
                if tip > 3:
                    return False
        except Exception as e:
            self.logger.error(f"处理失败: {e!s}", exc_info=True)
            raise e

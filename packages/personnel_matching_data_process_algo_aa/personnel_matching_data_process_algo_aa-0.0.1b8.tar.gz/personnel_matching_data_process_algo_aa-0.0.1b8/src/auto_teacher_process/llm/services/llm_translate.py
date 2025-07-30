import re

from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class TranslateLLMProcessor(BaseLLMProcessor):
    prompt = """
你的任务是将给定的英文文本翻译成中文。请仔细阅读以下英文文本，并按照要求进行翻译。
英文文本:
<english_text>
{TEXT}
</english_text>
在翻译时，请遵循以下指南:
1. 确保翻译准确、通顺，符合中文表达习惯。
2. 只输出翻译后的文本，不包含其他任何内容。
请在<translation>标签内写下你的翻译结果。
输出: """

    def __init__(
        self, model_name="doubao-1-5-pro-32k-250115", logger=None, system="llm_processor", stage="unkonw_task_name"
    ):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        """
        构建提示词模板
        输入:
            input_data (dict): 包含TEXT键的输入数据
        输出:
            str: 完整的提示词
        """
        if "description" not in input_data:
            raise ValueError("input_data must contain 'description' key")

        return self.prompt.format(TEXT=input_data["description"])

    async def process(self, *args, **kwargs) -> tuple:
        """
        执行完整的处理流程
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (最终结果, 处理状态)
        """
        self.TEXT = kwargs["input_data"].get("description", "")
        if self.TEXT is None:
            raise ValueError("description is None")

        prompt = self.build_prompt(kwargs["input_data"])
        self.logger.debug(f"生成的提示词: {prompt[:200]}...")

        try:
            response = await self.get_llm_response(prompt)
        except Exception as e:
            self.logger.debug(f"请求失败，出现异常：{e}. 响应为空。")
            return "", 0

        self.logger.debug(f"LLM响应: {response[:200]}...")

        match = re.search(r"<translation[^>]*>(.*?)</translation>", response, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            response = (content, 1)
        else:
            response = ("", 0)

        description = response[0]
        is_stop = response[1]
        if is_stop == 0:
            result = self.TEXT
            is_valid = 0
        else:
            result = description
            is_valid = 1
        return result, is_valid

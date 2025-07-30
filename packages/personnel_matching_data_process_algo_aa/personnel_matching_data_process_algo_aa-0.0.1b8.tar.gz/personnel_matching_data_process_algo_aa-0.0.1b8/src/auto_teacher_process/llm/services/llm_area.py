import re

from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class AreaLLMProcessor(BaseLLMProcessor):
    prompt = """
你的任务是从提供的教师简介中提取并归纳该教师的研究方向/领域。提取的研究方向/领域应基于简介原文，但可以进行适当的归纳总结。
这是教师简介：
<description>
{description}
</description>

在提取研究方向/领域时，请遵循以下规则：
1.优先从简介中明确标注的“研究方向”或“研究领域”部分提取信息。
2.不能从教师的论文、专利、项目相关描述中提取研究方向/领域。
3.如果简介中没有明确标注，可以从职位、教学课程、学术贡献等相关内容中归纳研究方向。
4.提取的内容应保持与简介原文的一致性，不能进行主观推测或编造。
5.提取到的研究方向以字符串形式返回，方向间用“;”分隔。
6.如果无法明确提取到研究方向/领域，返回空数组。


在<回答>标签内写下最终提取的研究方向/领域字符串。
<回答>
"研究方向1";"研究方向2";"研究方向3"
</回答>

请按照此格式返回结果，不要添加其他额外内容。
"""

    def __init__(self, model_name="qwen2.5-instruct-6-54-55", logger=None, system="llm_processor", stage="unkonw_task_name"):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        """
        构建提示词模板
        输入:
            input_data (dict): 包含description键的输入数据
        输出:
            str: 完整的提示词
        """
        if "description" not in input_data:
            raise ValueError("input_data must contain 'description' key")

        return self.prompt.format(description=input_data["description"])

    async def process(self, *args, **kwargs) -> tuple:
        """
        执行完整的处理流程
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (最终结果, 处理状态)
        """
        self.logger.debug("开始提取研究领域")
        prompt = self.build_prompt(kwargs["input_data"])
        self.logger.debug(f"生成的提示词: {prompt[:200]}...")

        response = await self.get_llm_response(prompt, temperature=0.3)

        # 提取判断结果
        judgment_match = re.search(r"<回答>(.*?)</回答>", response, re.DOTALL)
        judgment = judgment_match.group(1).strip() if judgment_match else "无判断结果"

        # 如果提取到内容，则按';'分隔并存入列表
        if judgment != "无判断结果":
            # 去除双引号并按';'分隔
            research_areas = [item.strip('"') for item in judgment.split(";")]
            # 过滤掉空字符串
            research_areas = [area for area in research_areas if area]
            is_valid = 0 if len(research_areas) == 0 else 1
        else:
            research_areas = []
            is_valid = 0

        self.logger.debug(f"处理完成，结果: {research_areas}，有效: {is_valid}")
        return research_areas, is_valid

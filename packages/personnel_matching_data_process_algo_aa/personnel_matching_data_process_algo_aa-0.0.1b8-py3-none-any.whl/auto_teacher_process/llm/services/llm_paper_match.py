import re

from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class PaperMatchLLMProcessor(BaseLLMProcessor):
    prompt = """
你的任务是对论文信息与教师信息在学科领域、研究方向等方面进行全面严谨的分析，判断该论文是否属于该教师。

请仔细阅读以下论文信息：
<论文题目>
{title}
</论文题目>
<论文领域>
{area}
</论文领域>
<论文关键字>
{keywords}
</论文关键字>
<论文扩展关键字>
{keywords_plus}
</论文扩展关键字>

接下来，请阅读以下教师信息：
<教师简介>
{description}
</教师简介>
<研究方向>
{research}
</研究方向>
<相关项目>
{project}
</相关项目>

在判断论文是否属于该教师时，请考虑以下标准和方法：
1. 学科领域匹配度：论文的学科领域与教师的研究方向和相关项目所涉及的学科领域是否一致或高度相关。
2. 关键字关联度：论文的关键字和扩展关键字是否与教师的研究方向、相关项目中的关键概念或术语相匹配。
3. 研究内容契合度：结合教师简介、研究方向和相关项目，判断论文的研究内容是否与教师的研究兴趣和工作重点相符。

请按照以下步骤进行分析和判断：
1. 仔细研读论文信息和教师信息。
2. 逐一对比上述判断标准。
3. 综合考虑各方面因素，形成初步判断。
4. 再次检查，确保没有遗漏重要细节。

在<思考>标签中详细分析论文和教师信息的匹配情况。然后在<回答>标签中给出你的最终判断，使用“True”或“False”。最后，在<解释>标签中详细解释你的判断理由。

<思考>
[在此详细分析论文和教师信息的匹配情况]
</思考>
<回答>
[在此给出“True”或“False”的判断]
</回答>
"""

    def __init__(self, model_name="qwen2.5-instruct-6-54-55", logger=None, system="llm_processor", stage="unkonw_task_name"):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        """
        构建提示词模板
        输入:
            input_data (dict): 包含profile键的输入数据
        输出:
            str: 完整的提示词
        """
        required_fields = ["title", "area", "keywords", "keywords_plus", "description", "project", "research_area"]

        if set(required_fields).issubset(input_data):
            return self.prompt.format(
                title=input_data["title"],
                area=input_data["area"],
                keywords=input_data["keywords"],
                keywords_plus=input_data["keywords_plus"],
                description=input_data["description"],
                project=input_data["project"],
                research=input_data["research_area"],
            )
        missing = set(required_fields) - input_data.keys()
        raise ValueError(f"Missing required fields: {missing}")

    async def process(self, input_data: dict) -> tuple:
        """
        处理LLM响应内容
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (处理结果, 是否成功)
        """
        prompt = self.build_prompt({**input_data})
        self.logger.debug(f"生成的提示词: {prompt[:200]}...")

        response = await self.get_llm_response(prompt, temperature=0.3)
        self.logger.debug(f"LLM响应: {response[:200]}...")

        judgment_match = re.search(r"<回答>(.*?)</回答>", response, re.DOTALL)
        judgment = judgment_match.group(1).strip().lower() if judgment_match else "false"
        if "true" in judgment:
            return True
        return False

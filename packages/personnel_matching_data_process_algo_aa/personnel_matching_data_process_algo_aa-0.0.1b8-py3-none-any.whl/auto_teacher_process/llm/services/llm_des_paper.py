import ast
import re
import time

from openai import AsyncOpenAI
from openai._types import NOT_GIVEN, NotGiven
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed

from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class DesPaperLLMProcessor(BaseLLMProcessor):
    prompt = """
你的任务是从提供的教师简介内容中提取该教师论文的题目。
以下是教师简介内容：
<教师简介>
{description}
</教师简介>
在提取论文题目时，请遵循以下要求：
1. 论文题目必须是来自教师简介原文中的内容。
2. 只提取具体的论文题目，不提取期刊会议名称、项目名称、专利名称、书籍著作名称以及其他无关信息。
3. 多个论文题目以Python列表的形式返回。
4. 不要对简介中的论文题目进行改写和翻译。
5. 不要提取期刊会议的缩写名称，注意甄别期刊缩写名称如：Opt. Expres、Opt. Lett等
6. 不要提取教师的主讲课程
7. 不要提取教师的参与开发项目课题信息
8. 不要将论文内容当作论文题目
9. 不要提取教师获奖相关信息、专题研究、开发技术
10.不要提取教师研究方向

请在<回答>标签内写下你的结果。
<回答>
[具体实现时会输出提取的论文题目列表]
</回答>
"""

    def __init__(self, model_name="qwen2.5-instruct-6-54-55", logger=None, system="llm_processor", stage="unkonw_task_name"):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        if "description" not in input_data:
            raise ValueError("input_data must contain 'description' key")

        return self.prompt.format(description=input_data["description"])

    def initialize_llm_client(self, model_name=["qwen2.5-instruct", "doubao-1-5-pro-32k-250115"]) -> None:
        """
        初始化LLM客户端
        输入:
            model_name (str): 模型名称
        输出: 无 (初始化实例变量 model_name 和 client)
        """
        for name in model_name:
            if name not in self.config:
                raise ValueError(f"未找到模型配置: {model_name}")

        conf_qwen = self.config[model_name[0]]
        conf_doubao = self.config[model_name[1]]
        self.model_name = {"qwen": model_name[0], "doubao": model_name[1]}
        self.client = {
            "qwen": AsyncOpenAI(api_key=conf_qwen["api_key"], base_url=conf_qwen["base_url"]),
            "doubao": AsyncOpenAI(api_key=conf_doubao["api_key"], base_url=conf_doubao["base_url"]),
        }
        self.logger.debug(f"LLM客户端初始化完成，模型: {model_name}")

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_exception(lambda e: True))
    async def get_llm_response(
        self,
        prompt: str,
        model_type: str,
        temperature: float | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        带重试机制的LLM请求
        输入:
            prompt (str): 提示词
            temperature (float): 生成温度
        输出:
            str: LLM的响应文本
        """
        if self.client is None:
            self.logger.warning("LLM client没有初始化，使用默认配置初始化")
            self.initialize_llm_client()

        messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]

        try:
            self.logger.info(f"异步发送LLM请求: {prompt[:100]}...", extra={"event": "running"})
            start_time = time.time()
            completion = await self.client[model_type].chat.completions.create(
                model=self.model_name[model_type],
                messages=messages,
                temperature=temperature,
            )
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            self.logger.info(
                f"LLM响应: {completion.choices[-1].message.content[:100]}...",
                extra={"event": "running", "duration_ms": duration_ms},
            )
            return completion.choices[-1].message.content
        except Exception as e:
            self.logger.error(f"LLM请求失败: {e!s}", exc_info=True)
            raise e

    async def process(self, *args, **kwargs) -> tuple:
        """
        教师简介论文提取处理过程
        """

        def parse_papers(output_text):
            match = re.search(r"<回答>\s*(\[.*?\])\s*</回答>", output_text, re.DOTALL)
            if match:
                try:
                    return 1, ast.literal_eval(match.group(1))  # 安全地解析为 Python 列表
                except Exception as e:
                    return 0, f"解析错误: {e}"
            return 0, "未找到 <回答> 区块"

        prompt = self.build_prompt(kwargs["input_data"])

        if len(prompt) <= 10000:
            try:
                response = await self.get_llm_response(prompt, model_type="qwen")
            except Exception as e:
                self.logger.debug(f"LLM请求出错{e}")
                return None, False
        else:
            try:
                response = await self.get_llm_response(prompt, model_type="doubao")
            except Exception as e:
                self.logger.debug(f"LLM请求出错{e}")
                return None, False

        is_valid, papers = parse_papers(response)

        return papers, is_valid

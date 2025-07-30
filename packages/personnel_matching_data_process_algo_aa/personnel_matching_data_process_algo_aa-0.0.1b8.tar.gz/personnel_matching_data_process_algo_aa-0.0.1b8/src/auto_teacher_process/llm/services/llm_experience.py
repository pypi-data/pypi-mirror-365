import ast
import json
import re
import time

from openai import AsyncOpenAI
from openai._types import NOT_GIVEN, NotGiven
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed

from auto_teacher_process.config import Config
from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class ExperienceLLMProcessor(BaseLLMProcessor):
    prompt_work = """
    你的任务是从提供的教师简介内容中提取该教师的工作经历（不限语言），并以标准 JSON 格式返回结构化结果。注意区分职称和职务的区别！
    以下是教师简介内容：
    <教师简介>
    {description}
    </教师简介>
    请严格按照以下规则与格式输出结果：
    ### 输出格式（必须为合法 JSON）
    ```json
    {
      "work": [
        {
          "start_date": "YYYY-MM or null",必须是简介中提到的对应时间,不能凭空捏造
          "end_date": "YYYY-MM or null",必须是简介中提到的对应时间,不能凭空捏造
          "organization": "工作单位名称，若缺失为 null",
          "city": "根据工作单位推测出所在城市",
          "role_title": "职称，只能提取通用的职称，如：教授、副教授、讲师、助理研究员、研究员 等,必须是简介中出现的职称,不能凭空捏造,注意：教师不是职称"
          "position":"职务，只能提取通用的行政管理类职务，如：校长、院长、副院长、主任、访问学者、理事等，必须是简介中出现的职务,不能凭空捏造，注意：研究员不是职务"
        }
      ]
    }
    ### 缺失值处理
    - 时间格式统一为：YYYY-MM（如 '2010-09'），若原文未明确月份，使用 'YYYY'
    - 若某个字段缺失，用 null 表示
    - 若只有一个年份（如“2008”），视为毕业/离职时间，起始时间设为 null
    - 若有“present”或“至今”等表述，结束时间为 '至今'
    ### 提取规则
    1. **内容来源**：
    - 仅保留原文中明确可分辨的经历,不得添加或推断原文未提及的信息。
    - 不能将多条经历融合成一条进行输出
    - 如果原文是“进修学习”或“访问”，那么 `position` 应该填写具体的进修身份（如访问学者），而 `role_title` 在这种情况下应为 `null`。
    2. **信息拆分**：
    - 合并同一段落中连续的教育/工作经历描述
    - 拆分不同段落或明确分隔的经历描述
    3. **优先级规则**：
    - 优先提取时间明确的经历
    - 若时间范围重叠，保留最新的记录
    - 请不要输出任何字段全为 null 的经历项,这些视为无效信息。
    请以标准 JSON 格式输出结果。

    """

    prompt_edu = """
    你的任务是从提供的教师简介内容中提取该教师的教育经历（不限语言），并以标准 JSON 格式返回结构化结果。
    以下是教师简介内容：
    <教师简介>
    {description}
    </教师简介>
    请严格遵循以下规则与格式：

    ### 输出格式（必须为合法 JSON）
    ```json
    {
      "education": [
        {
          "start_date": "YYYY-MM or null",必须是简介中明确提到的对应时间,不能凭空捏造
          "end_date": "YYYY-MM or null",必须是简介中明确提到的对应时间,不能凭空捏造
          "organization": "单位名称，若缺失为 null",
          "city": "根据单位名称推测出所在城市",
          "department": "专业或院系，接受该教育经历的专业或院系，如 `计算机技术`, `环境学`等，若未提及则为 `null`",
          "degree": "学位，只能提取标准、规范的学位名称，不能提取专业名称，如 学士、硕士、博士等，若缺失为 null"
        }
      ]
    }
    1. **缺失值处理**：
    - 时间格式统一为：YYYY-MM（如 '2010-09'），若原文未明确月份，使用 'YYYY'
    - 若只有一个年份（如“2008”），视为毕业/离职时间，起始时间设为 null
    - 若有“present”或“至今”等表述，结束时间为 '至今'

    2. **内容来源**：
    - 仅保留原文中明确可分辨的经历,不得添加或推断原文未提及的信息，
    - 不能将论文中出现的学校直接认定为教育经历学校
    - 不能将多条经历融合成一条进行输出

    3. **信息拆分**：
    - 合并同一段落中连续的教育/工作经历描述
    - 拆分不同段落或明确分隔的经历描述

    4. **优先级规则**：
    - 优先提取时间明确的经历
    - 若时间范围重叠，保留最新的记录
    - 请不要输出任何字段全为 null 的经历项,这些视为无效信息。

    请以标准 JSON 格式输出结果。

    """

    def __init__(
        self,
        model_name=["qwen2.5-instruct-6-54-55", "doubao-1-5-pro-32k-250115"],
        logger=None,
        system="llm_processor",
        stage="unkonw_task_name",
    ):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        prompt_type = input_data.get("prompt_type", "")
        if prompt_type not in ["work", "edu"]:
            raise ValueError("prompt_type must be one of 'work', 'edu'")

        if "description" not in input_data:
            raise ValueError("input_data must contain 'description' key")
        description = input_data.get("description", "")

        if description is None:
            raise ValueError("description cannot be None")

        def safe_prompt(prompt_template):
            return prompt_template.replace("{", "{{").replace("}", "}}").replace("{{description}}", "{description}")

        if prompt_type == "work":
            return safe_prompt(self.prompt_work).format(description=description)
        if prompt_type == "edu":
            return safe_prompt(self.prompt_edu).format(description=description)

    def initialize_llm_client(self, model_name=["qwen2.5-instruct", "doubao-1-5-pro-32k-250115"]) -> None:
        """
        初始化LLM客户端
        输入:
            model_name (str): 模型名称
        输出: 无 (初始化实例变量 model_name 和 client)
        """
        for name in model_name:
            self.logger.info(f"正在初始化模型 {name}：{Config.LLM.is_in_model_list(name)}")
            if not Config.LLM.is_in_model_list(name):
                raise ValueError(f"未找到模型配置: {model_name}")

        conf_qwen = Config.LLM.get_llm_config(model_name[0])
        conf_doubao = Config.LLM.get_llm_config(model_name[1])
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

    def parse_description_json(self, output_text):
        """
        从 LLM 输出中提取 JSON 格式结构化数据，返回 Python 对象（不转字符串）
        """

        def extract_json_block(text):
            """
            提取 JSON 主体，清除 markdown 包裹。
            """
            cleaned = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if match:
                return match.group(0)
            raise ValueError("未找到 JSON 主体")

        try:
            json_text = extract_json_block(output_text)

            # 优先尝试 json.loads
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError:
                # 宽容处理单引号 JSON
                data = ast.literal_eval(json_text)

            if not isinstance(data, dict):
                return 0, {"education": [], "work": []}

            # 直接返回 Python 对象（列表）供后续处理或 json.dumps
            return 1, {"education": data.get("education", []), "work": data.get("work", [])}

        except Exception:
            return 0, {"education": [], "work": []}

    async def process(self, *args, **kwargs) -> tuple:
        """
        教师简介论文提取处理过程
        """
        input_data: dict = kwargs.get("input_data", {})
        description = input_data.get("description")
        if description is None:
            raise Exception("缺少参数: description")

        prompt_work = self.build_prompt({"prompt_type": "work", "description": description})
        prompt_edu = self.build_prompt({"prompt_type": "edu", "description": description})

        if len(description) <= 10000:
            model_type = "doubao"
        else:
            model_type = "doubao"

        self.logger.debug(f"使用模型 {model_type} 处理教师简介")
        try:
            response_work = await self.get_llm_response(prompt_work, model_type)
            response_edu = await self.get_llm_response(prompt_edu, model_type)
        except Exception as e:
            self.logger.debug(f"LLM请求出错{e}")
            return None, None, 0

        # 分别解析
        work_valid, work_data = self.parse_description_json(response_work)
        edu_valid, edu_data = self.parse_description_json(response_edu)

        self.logger.debug(f"work_data: {work_valid, work_data}")
        self.logger.debug(f"edu_data: {edu_valid, edu_data}")
        # 合并结果
        is_valid = 1 if edu_valid or work_valid else 0
        if is_valid:
            work_data = json.dumps(work_data.get("work", []), ensure_ascii=False)
            edu_data = json.dumps(edu_data.get("education", []), ensure_ascii=False)
        else:
            work_data = []
            edu_data = []
        return work_data, edu_data, is_valid

    # async def run(self, input_data: dict) -> tuple:
    #     """
    #     执行完整的处理流程
    #     输入:
    #         input_data (dict): 输入数据,字典格式，以支持多个输入
    #     输出:
    #         tuple: (最终结果, 处理状态)
    #     """
    #     return await self.process(input_data=input_data)

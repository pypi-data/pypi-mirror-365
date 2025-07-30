import json
import re
import string
import time

from auto_teacher_process.config import Config
from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class FamousLLMProcessor(BaseLLMProcessor):
    prompt = """
## 任务描述
根据提供的教师简介信息，判断主人公教师是否明确获得、主持了或拥有以下任何一种情况：
- {title} 奖项
- {title} 项目
- {title} 头衔
如果是，请返回True；否则返回False。

## 注意事项
1. {title}在简介上下文中的级别仅限于国家级、教育部、中组部、某省级、某自治区级或某市级，满足一种即可。不包括其他机构级别，例如：区、学会、协会、高校等。唯一例外是青年人才托举工程，可以包括中国科协、省市科协。

## 教师简介
{description}
"""

    def __init__(
        self,
        logger=None,
        model_name: str = "qwen2.5-instruct-6-54-55",
        system: str = "llm_processor",
        stage: str = "unkonw_task_name",
    ):
        """
        著名人才处理器初始化
        实例变量:
        - title_list: 从配置文件加载的标题列表
        - title_dict: 从配置文件加载的标题字典
        - process: 从配置文件加载的处理列表
        - re_list: 从配置文件加载的正则列表
        - title_scores: 从配置文件加载的标题评分
        """
        super().__init__(model_name=model_name, system=system, stage=stage, logger=logger)
        self.title_list = Config.LLM_CONFIG.FAMOUS_TITLES.TITLE_LIST
        self.title_dict = Config.LLM_CONFIG.FAMOUS_TITLES.TITLE_DICT
        self._process = Config.LLM_CONFIG.FAMOUS_TITLES.PROCESS
        self.re_list = Config.LLM_CONFIG.FAMOUS_TITLES.RE_LIST
        self.title_scores = Config.LLM_CONFIG.FAMOUS_TITLES.TITLE_SCORES

    def build_prompt(self, input_data: dict[str, str]) -> str:
        """
        构建提示词
        输入:
            input_data (dict): 包含'description'键的输入数据字典
        输出:
            str: 完整的提示词
        """
        if "description" not in input_data or "title" not in input_data:
            raise ValueError("缺少必要参数: description or title")

        description = input_data["description"]
        title = input_data["title"]

        return self.prompt.format(title=title, description=description)

    def normalize_title(self, survey_titles: list[str]) -> list[str]:
        """
        规范化职称名称
        输入:
            survey_titles (list): 需要规范化的职称列表
        输出:
            list: 规范化后的职称列表
        """
        title_out_keywords = ["国家级", "国家", "教育部", "中组部"]
        # print(survey_titles)
        normalized_titles = []
        levels = ["国家", "省", "市"]
        for title in survey_titles:
            ##字典规范化
            sf = False
            for standard_title, variants in self.title_dict.items():
                if title in variants:
                    normalized_titles.append(standard_title)
                    sf = True
                    break
            if sf:
                continue

            if any(keyword in title for keyword in title_out_keywords):
                for keyword in title_out_keywords:
                    title = title.replace(keyword, "国家")
            # 青年人才托举工程
            if "人才托举工程" in title:
                if not any(level in title for level in levels):
                    normalized_titles.append("青年人才托举工程")
                else:
                    if "国家" in title:
                        normalized_titles.append("国家青年人才托举工程")
                    elif "省" in title:
                        normalized_titles.append("省青年人才托举工程")
                    elif "市" in title:
                        normalized_titles.append("市青年人才托举工程")
            # 优秀青年
            elif "优" in title and "青" in title:
                if not any(level in title for level in levels):
                    if "海外" in title:
                        normalized_titles.append("海外优秀青年基金")
                    else:
                        normalized_titles.append("优秀青年基金")
                else:
                    if "国家" in title:
                        if "海外" in title:
                            normalized_titles.append("国家海外优秀青年基金")
                        else:
                            normalized_titles.append("国家优秀青年基金")
                    elif "省" in title:
                        if "海外" in title:
                            normalized_titles.append("省海外优秀青年基金")
                        else:
                            normalized_titles.append("省优秀青年基金")
                    elif "市" in title:
                        if "海外" in title:
                            normalized_titles.append("市海外优秀青年基金")
                        else:
                            normalized_titles.append("市优秀青年基金")
            # 万人计划
            elif "万人计划" in title:
                if not any(level in title for level in levels):
                    if "青年" in title:
                        normalized_titles.append("万人计划-青年")
                    else:
                        normalized_titles.append("万人计划")
                else:
                    if "国家" in title:
                        if "青年" in title:
                            normalized_titles.append("国家万人计划-青年")
                        else:
                            normalized_titles.append("国家万人计划")
                    elif "省" in title:
                        if "青年" in title:
                            normalized_titles.append("省万人计划-青年")
                        else:
                            normalized_titles.append("省万人计划")
                    elif "市" in title:
                        if "青年" in title:
                            normalized_titles.append("市万人计划-青年")
                        else:
                            normalized_titles.append("市万人计划")

            # 高层次人才
            elif "高层次" in title:
                if not any(level in title for level in levels):
                    if "青年" in title:
                        normalized_titles.append("高层次人才-青年")
                    else:
                        normalized_titles.append("高层次人才")
                else:
                    if "国家" in title:
                        if "青年" in title:
                            normalized_titles.append("国家高层次人才-青年")
                        else:
                            normalized_titles.append("国家高层次人才")
                    elif "省" in title:
                        if "青年" in title:
                            normalized_titles.append("省高层次人才-青年")
                        else:
                            normalized_titles.append("省高层次人才")
                    elif "市" in title:
                        if "青年" in title:
                            normalized_titles.append("市高层次人才-青年")
                        else:
                            normalized_titles.append("市高层次人才")
            # 杰出青年基金
            elif "杰" in title and "青" in title:
                if "国家" in title:
                    normalized_titles.append("国家杰出青年基金")
                elif "省" in title:
                    normalized_titles.append("省杰出青年基金")
                elif "市" in title:
                    normalized_titles.append("市杰出青年基金")
                else:
                    normalized_titles.append("杰出青年基金")

        normalized_titles = list(set(normalized_titles))
        return normalized_titles

    def is_excluded(self, prefix: str, title: str) -> bool:
        """
        判断职称是否在排除列表中
        输入:
            prefix (str): 职称前缀
            title (str): 职称名称
        输出:
            bool: 是否排除
        """
        exclude_keywords = ["大学", "学院", "协会", "学会", "高校"]
        if "区" in prefix and "自治区" not in prefix:
            return True
        if "人才托举工程" in title:
            return False
        if "中科院" in prefix or "中国科学院" in prefix:
            return False
        return any(keyword in prefix for keyword in exclude_keywords)

    def adjust_title_with_context(self, title: str, prefix: str, suffix: str) -> str:
        """
        根据上下文调整职称名称
        输入:
            title (str): 原始职称名称
            prefix (str): 前缀内容
            suffix (str): 后缀内容
        输出:
            str: 调整后的职称名称
        """
        title_out_keywords = ["国家级", "国家", "教育部", "中组部"]
        province_and_city = ["省", "市"]
        province = ["省"]
        city = ["市"]

        if title in self._process or (("高层次" in title or "万人计划" in title) and "青年" in title):
            if any(keyword in prefix for keyword in title_out_keywords) or any(
                keyword in suffix for keyword in title_out_keywords
            ):
                for keyword in title_out_keywords:
                    if keyword in prefix or keyword in suffix:
                        return f"国家-{title}"

            if any(keyword in prefix for keyword in province_and_city) or any(
                keyword in suffix for keyword in province_and_city
            ):
                for keyword in province:
                    if keyword in prefix and "市" not in prefix:
                        return f"{keyword}-{title}"
                    if keyword in suffix and "市" not in suffix:
                        return f"{keyword}-{title}"

                for keyword in city:
                    if keyword in prefix:
                        return f"{keyword}-{title}"
                    if keyword in suffix:
                        return f"{keyword}-{title}"

        if title not in self._process and "长江" in title and "青年" in title:
            return "教育部青年长江学者"

        return title

    def extract_titles_from_description(self, description: str) -> list[tuple[str, int]]:
        """
        从描述中提取所有可能的职称及其位置
        输入:
            description (str): 教师简介
        输出:
            list: 包含(职称, 起始位置)元组的列表
        """
        filtered_titles_with_positions = []

        for titles in self.title_list:
            for title in titles:
                matches = re.finditer(re.escape(title), description)
                for match in matches:
                    filtered_titles_with_positions.append((title, match.start()))

        return filtered_titles_with_positions

    def remove_punctuation(self, text: str) -> str:
        """
        移除文本中的标点符号
        输入:
            text (str): 需要去除标点的文本
        输出:
            str: 处理后的文本
        """
        punctuation = string.punctuation + '“”‘’？【】（）《》—"·'
        text = re.sub(rf"[{punctuation}]+", "", text)
        if re.search("[a-zA-Z]", text):
            text = text.lower()
        return text

    def get_context_around_title(
        self, description: str, title_index: int, title_length: int, length: int = 12
    ) -> tuple[str, str]:
        """
        获取职称周围的上下文
        输入:
            description (str): 教师简介
            title_index (int): 职称起始位置
            title_length (int): 职称长度
            length (int): 上下文长度
        输出:
            tuple: (前缀, 后缀)
        """
        text_before_title = description[:title_index]
        text_after_title = description[title_index + title_length :]

        punctuation_positions_before = [
            text_before_title.rfind(punc)
            for punc in ["，", "。", "、", "：", "；", "？", "！", "-", ".", ",", " ", "\n", "\t", "及", "和", "与"]
        ]
        last_punctuation_index_before = max(punctuation_positions_before)

        prefix = (
            text_before_title[last_punctuation_index_before + 1 :]
            if last_punctuation_index_before != -1
            else text_before_title
        )
        prefix = prefix[-length:] if len(prefix) >= length else prefix

        punctuation_positions_after = [
            text_after_title.find(punc)
            for punc in ["，", "。", "、", "：", "；", "？", "！", "-", ".", ",", " ", "\n", "\t", "及", "和", "与"]
            if text_after_title.find(punc) != -1
        ]
        first_punctuation_index_after = min(punctuation_positions_after) if punctuation_positions_after else -1

        suffix = (
            text_after_title[:first_punctuation_index_after]
            if first_punctuation_index_after != -1
            else text_after_title
        )
        suffix = suffix[:length] if len(suffix) >= length else suffix

        return prefix, suffix

    def check_high_level_non_youth(self, title: str) -> bool:
        """
        检查是否为非青年类高级职称
        输入:
            title (str): 职称名称
        输出:
            bool: 是否为非青年类高级职称
        """
        return any(pattern in title for pattern in ["高层次.*青年", "万人计划[^青年]*$", "长江[^青年]*$"])

    async def process(self, *args, **kwargs) -> tuple[tuple[list[str], list[str]], bool]:
        """
        主要处理流程
        输入:
            input_data (dict): 包含'description'键的输入数据
        输出:
            tuple: (匹配的职称列表, 是否成功)
        """
        self.logger.debug("开始处理著名事件")
        input_data: dict[str, str] = kwargs["input_data"]
        description = self.remove_punctuation(input_data["description"])
        # 提取所有可能的职称
        filtered_titles_with_positions = self.extract_titles_from_description(description)
        # 处理每个职称
        titles_to_check = []
        for title, position in filtered_titles_with_positions:
            prefix, suffix = self.get_context_around_title(description, position, len(title))

            if self.is_excluded(prefix, title):
                continue

            if self.check_high_level_non_youth(title) and ("青年" in prefix or "青年" in suffix):
                title = f"青年-{title}"

            adjusted_title = self.adjust_title_with_context(title, prefix, suffix)
            titles_to_check.append(adjusted_title)

        for title in titles_to_check:
            if "-" in title:
                title_without_dash = title.replace("-", "")
                if title_without_dash in titles_to_check and title_without_dash != title:
                    titles_to_check.remove(title)
        titles_to_check = list(set(titles_to_check))

        # LLM验证
        validated_titles = []
        for title in titles_to_check:
            prompt = self.build_prompt({"title": title, "description": description})
            if await self.get_llm_response(prompt=prompt, temperature=0):
                validated_titles.append(title)
        validated_titles = list(set(validated_titles))

        # 规范化处理
        normalized_titles = self.normalize_title(validated_titles)

        self.logger.debug(f"处理完成，检测到{len(normalized_titles)}个著名人才职称:{normalized_titles}")
        return validated_titles, normalized_titles, True

    def remove_sub_from_list(self, input_string):
        for substring in self.re_list:
            input_string = input_string.replace(substring, "")
        return input_string

    def sort_titles(self, input_list):
        score_map = {}
        for score, titles in self.title_scores.items():
            for title in titles:
                score_map[title] = score

        # 对输入列表进行排序，按分数降序，相同分数保持原顺序
        sorted_list = sorted(input_list, key=lambda x: score_map.get(x, 0))
        return sorted_list

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
            if input_data["description"]:
                teacher_famous, normalized_famous, _ = await self.process(input_data=input_data)
                if len(teacher_famous) == 0:
                    famous_valid = 0
                else:
                    famous_valid = 1
            else:
                raise Exception("description is empty")

            normalized_famous = self.sort_titles(normalized_famous)
            teacher_famous = json.dumps(teacher_famous, ensure_ascii=False)
            normalized_famous = json.dumps(normalized_famous, ensure_ascii=False)
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            self.logger.info("处理完成", extra={"event": "end", "duration_ms": duration_ms})
            return teacher_famous, normalized_famous, famous_valid
        except Exception as e:
            self.logger.error(f"处理出错:{e}", exc_info=True)
            raise e

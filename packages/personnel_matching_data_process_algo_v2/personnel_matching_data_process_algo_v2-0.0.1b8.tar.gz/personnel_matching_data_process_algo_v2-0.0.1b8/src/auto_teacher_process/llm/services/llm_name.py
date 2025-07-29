import re

from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class NameLLMProcessor(BaseLLMProcessor):
    prompt = """
你的任务是从提供的文本中提取出一个干净的姓名。干净的姓名指不包含多余的修饰、符号等，仅为姓名本身，且必须来自提供的文本原文，不能进行改写。
请仔细阅读以下文本：
<文本>
{TEXT}
</文本>
注意事项：
1.在提取姓名时，请确保只提取出姓名部分，去除任何非姓名的内容，并且姓名来自提供的文本原文。
2.存在中文姓名和其他语言的姓名混合时，只提取出中文名称。
3.不需要翻译(如拼音翻译为汉字，英语翻译为中文)，只需要原文。
4.如果文本中没有姓名，请返回"false"。
请在<name>标签内写下提取出的干净姓名。
输出: """

    # 海外教师姓名提取的提示词
    prompt_intl = """
你的任务是从提供的文本中提取出一个干净的姓名。干净的姓名指不包含多余的修饰、符号等，仅为姓名本身，且必须来自提供的文本原文，不能进行改写。
请仔细阅读以下文本：
<文本>
{TEXT}
</文本>
注意事项：
1.在提取姓名时，请确保只提取出姓名部分，去除任何非姓名的内容，并且姓名来自提供的文本原文。
2.存在英文姓名(包括拼音)和其他语言的姓名混合时，只提取出英文名称。
3.不需要翻译(如拼音翻译为汉字，英语翻译为中文)，只需要原文。
4.如果文本中没有姓名，请返回"false"。
请在<name>标签内写下提取出的干净姓名。
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
        if "teacher_name" not in input_data:
            raise ValueError("input_data must contain 'teacher_name' key")

        return self.prompt.format(TEXT=input_data["teacher_name"])

    async def process(self, *args, **kwargs) -> tuple:
        """
        执行完整的处理流程
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (最终结果, 处理状态)
        """
        self.logger.debug("开始提取姓名")
        prompt = self.build_prompt(kwargs["input_data"])
        self.logger.debug(f"输入数据: {kwargs['input_data']}")
        self.logger.debug(f"生成的提示词: {prompt[:200]}...")

        try:
            response = await self.get_llm_response(prompt)
        except Exception as e:
            self.logger.debug(f"LLM调用错误: {e}")
            return "", 0
        self.logger.debug(f"LLM响应: {response[:200]}...")

        match = re.search(r"<name>(.*?)</name>", response)
        if match:
            content = match.group(1)
            self.logger.debug(f"找到标签:{match}")
            response = (content, True)
        else:
            self.logger.warning("未找到 <> 标签")
            response = ("false", False)
        self.logger.debug(f"处理完成，结果:{response}")

        name = response[0]
        is_stop = response[1]
        if "false" in name or is_stop == 0:
            result = ""
            is_valid = 0
        else:
            result = name
            is_valid = 1
        self.logger.debug(f"验证完成，结果: {result}，有效: {is_valid}")

        return result, is_valid

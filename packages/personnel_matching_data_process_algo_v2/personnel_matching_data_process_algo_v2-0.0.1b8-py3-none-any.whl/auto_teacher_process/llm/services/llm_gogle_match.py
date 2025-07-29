import re

from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class NameSeparationLLMProcessor(BaseLLMProcessor):
    prompt = """
你的任务是从输入文本中提取出<英文姓名或拼音>和<中文姓名>，若其中一个不存在则值为null。
以下是输入文本：
<text>
{TEXT}
</text>
英文姓名或拼音：包括英文字母和中文的拼音；
中文姓名：由中文字符组成。。
请在<提取结果>标签内输出提取的英文姓名和中文姓名，格式如下：
<英文姓名或拼音>英文姓名或拼音内容，若不存在则为null</英文姓名或拼音>
<中文姓名>中文姓名内容，若不存在则为null</中文姓名>
<提取结果>
<英文姓名或拼音>英文姓名或拼音内容，若不存在则为null</英文姓名或拼音>
<中文姓名>中文姓名内容，若不存在则为null</中文姓名>
</提取结果>
"""

    def __init__(self, model_name="qwen2.5-instruct-6-54-55", logger=None, system="llm_processor", stage="unkonw_task_name"):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        if "en_name" not in input_data:
            raise ValueError("input_data must contain 'en_name' key")

        return self.prompt.format(TEXT=input_data["en_name"])

    async def process(self, *args, **kwargs) -> tuple:
        """
        email提取处理过程
        """

        self.logger.info("开始提取姓名")
        prompt = self.build_prompt(kwargs["input_data"])
        self.logger.debug(f"生成的提示词: {prompt[:200]}...")

        response = await self.get_llm_response(prompt, temperature=0.3)
        self.logger.debug(f"LLM响应: {response[:200]}...")

        try:
            result_block_match = re.search(r"<提取结果>(.*?)</提取结果>", response, re.DOTALL)
            if not result_block_match:
                return {"english_name": None, "chinese_name": None}, 0

            result_block = result_block_match.group(1)

            # 提取英文姓名
            english_match = re.search(r"<英文姓名或拼音>(.*?)</英文姓名或拼音>", result_block)
            english_name = english_match.group(1).strip() if english_match else None
            if english_name == "null":
                english_name = None

            # 提取中文姓名
            chinese_match = re.search(r"<中文姓名>(.*?)</中文姓名>", result_block)
            chinese_name = chinese_match.group(1).strip() if chinese_match else None
            if chinese_name == "null":
                chinese_name = None
            return {"english_name": english_name, "chinese_name": chinese_name}, 1
        except Exception as e:
            self.logger.error(f"处理流程失败: {e!s}")
            return {"english_name": None, "chinese_name": None}, 0

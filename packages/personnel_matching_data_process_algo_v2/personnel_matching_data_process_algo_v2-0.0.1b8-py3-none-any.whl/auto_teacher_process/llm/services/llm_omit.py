import pandas as pd

from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class OmitLLMProcessor(BaseLLMProcessor):
    omit_filter_prompt = """
## 任务描述
以下是从网页上爬取到的教师简介信息。文本中可能包含导航栏、侧边栏、表格、广告等无关内容。请过滤掉这些无关内容，保留干净的文本：
1. 过滤掉导航栏、侧边栏、页脚、表格说明、广告、页面描述等无关信息。
2. 只需要输出过滤后的内容，不需要任何额外信息。

请根据上述要求提取以下文本中的有效教师简介内容：
{name}
{ori_description}
"""

    omit_description_prompt_new = """
## 任务描述
你需要从提供的信息文本中，提取并总结出一个紧凑且正式的个人官方简介。各个信息之间用逗号分割，一定不能出现"是一位"三个字。请确保所有信息均来自于提供的信息文本，不能包含任何信息文本之外的内容，如果无法提取出准确完整的个人介绍，请返回"False"。

## 任务要求
1. 各个信息之间用逗号分割，一定不能出现"是一位"三个字，最好以“姓名，职称，......”的格式开头。
2. 必须确保个人介绍中的内容完全来自于信息文本，不得包含任何虚构信息或信息文本以外的内容。
3. 如果无法提取出准确完整的个人介绍，请返回"False"。
4. 输出的个人介绍必须是中文的。
5. 字数在200字以内。

## 信息文本
姓名: {name}，
{ori_description}

输出: """

    english_omit_description_prompt = """
## 任务描述
你需要从提供的信息文本中，为"{name}"提取并总结出一个紧凑且正式的个人官方简介。各个信息之间用逗号分割，一定不能出现"是一位"三个字。请确保所有信息均来自于提供的信息文本，不能包含任何信息文本之外的内容，如果无法提取出准确完整的个人介绍，请返回"False"。

## 注意事项
1. 各个信息之间用逗号分割，一定不能出现"是一位"三个字，最好以“姓名，职称，......”的格式开头。
2. 必须确保个人介绍中的内容完全来自于信息文本，不得包含任何虚构信息或信息文本以外的内容。
3. 输出的个人介绍必须是中文的。
4. 字数在200字以内。

## 信息文本
姓名: {name}.
信息: {ori_description}

输出: """

    replace_name_prompt = """
## 任务描述
请将以下个人介绍中的主人公的姓名替换为"{name}"，只需替换姓名，不能进行其他任何的修改。只输出替换后的个人介绍，不要输出思考过程和任何其他的内容。

## 输出要求
1. 只输出替换后的个人介绍，不要输出思考过程和任何其他的内容。

## 个人介绍
{ori_description}

输出: """

    def __init__(self, model_name="qwen2.5-instruct-6-54-55", logger=None, system="llm_processor", stage="unkonw_task_name"):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        prompt_type = input_data.get("prompt_type", "")
        if prompt_type not in ["omit_filter", "omit_description", "english_omit_description", "replace_name"]:
            raise ValueError(
                "prompt_type must be one of 'omit_filter', 'omit_description', 'english_omit_description', 'replace_name'"
            )

        name = input_data.get("name", "")
        ori_description = input_data.get("ori_description", "")
        if name is None or ori_description is None:
            raise ValueError("name and ori_description cannot be None")

        if prompt_type == "omit_filter":
            return self.omit_filter_prompt.format(name=name, ori_description=ori_description)
        if prompt_type == "omit_description":
            return self.omit_description_prompt_new.format(name=name, ori_description=ori_description)
        if prompt_type == "english_omit_description":
            return self.english_omit_description_prompt.format(name=name, ori_description=ori_description)
        if prompt_type == "replace_name":
            return self.replace_name_prompt.format(name=name, ori_description=ori_description)

    async def process(self, *args, **kwargs):
        kwargs = kwargs["input_data"]
        mode = kwargs["mode"]
        self.logger.debug(f"开始处理教师简介, mode: {mode}")
        if mode not in ["cn", "en"]:
            raise ValueError("mode must be one of 'cn', 'en'")

        name = kwargs["teacher_name"]
        ori_description = kwargs["description"]
        if name is None or ori_description is None:
            raise ValueError("name and ori_description cannot be None")

        if pd.isna(ori_description) or len(ori_description.replace("\n", "").replace(" ", "").replace("?", "")) < 20:
            return "", 0
        raw_prompt = self.build_prompt(
            {"prompt_type": "omit_filter", "name": name, "ori_description": ori_description}
        )

        result = await self.get_llm_response(raw_prompt, temperature=0.3)
        clean_omit = result if result is not None else ""

        if len(clean_omit.replace("\n", "").replace(" ", "").replace("?", "")) < 20:
            return clean_omit, 0

        prompt_type = "omit_description" if mode == "cn" else "english_omit_description"
        prompt = self.build_prompt({"prompt_type": prompt_type, "name": name, "ori_description": clean_omit})

        tip = 0
        omit_description = ""
        while "我是" in omit_description[:10] or omit_description == "":
            tip += 1
            if tip > 3:
                break
            try:
                result = await self.get_llm_response(prompt, temperature=0.3)
            except Exception as e:  # 捕获所有异常
                self.logger.error(f"请求失败，出现异常：{e}. 返回空字符串。", exc_info=True)
                raise e
            omit_description = result if result is not None else ""

        if omit_description == "" or "False" in omit_description or omit_description is None:
            return "", 0

        if len(omit_description) < 20:
            return omit_description, 0
        if mode == "cn":
            self.logger.debug(f"omit_description: {omit_description}")
            return omit_description, 1

        # 英文额外处理
        prompt = self.build_prompt({"prompt_type": "replace_name", "name": name, "ori_description": omit_description})

        result = await self.get_llm_response(prompt, temperature=0.3)

        omit_description = result if result is not None else ""

        if name not in omit_description or len(omit_description) < 20:
            return omit_description, 0
        self.logger.debug(f"omit_description: {omit_description}")
        return omit_description, 1

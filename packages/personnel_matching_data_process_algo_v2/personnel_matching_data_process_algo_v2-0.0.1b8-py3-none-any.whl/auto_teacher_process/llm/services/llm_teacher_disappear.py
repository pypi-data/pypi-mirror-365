import json

from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class TeacherDisappearLLMProcessor(BaseLLMProcessor):
    homepage_match_prompt = """
### 任务描述
你将获得一位教师的信息（包括姓名、简介）以及一个教师主页的markdown内容（该主页由html转换而来）。请判断该主页是否属于该教师本人。

### 输入
1. 教师姓名: {name}
2. 教师简介: {profile}
3. 教师主页markdown内容:
{homepage_markdown}

### 判断标准
- 如果主页内容中有明确证据（如姓名、研究方向、教育背景、工作单位、学术成果等）与教师简介高度匹配，且无明显矛盾，请判断为“True”。
- 如果主页内容与教师简介明显不符，或有矛盾信息（如姓名不同、单位不同等），请判断为“False”。
- 如果主页内容信息极少，无法判断，请返回“False”。

### 输出要求
请仅输出“True”、“False”，不要输出任何解释或多余内容。
"""

    work_experience_prompt = """
你将获得一位教师的百度百科信息，内容以markdown格式给出。请你从中提取出所有与“工作经历”相关的内容，整理为一个有序的列表，每一项为一个字典，包含以下字段：
- 时间（如“2010年9月-2015年7月”，如无具体时间可填“未知”）
- 单位（如“中山大学”）
- 职位（如“讲师”、“教授”等）

以下是百度百科markdown信息：
<baike_markdown>
{baike_markdown}
</baike_markdown>

请严格按照以下要求输出：
1. 只提取与工作经历相关的信息，忽略教育经历、获奖、社会兼职等内容。
2. 输出格式为JSON数组，每个元素为一个字典，字段为“{{时间}}”、“{{单位}}”、“{{职位}}”，如：
[
  {{"时间": "2010年9月-2015年7月", "单位": "中山大学", "职位": "讲师"}},
  {{"时间": "2015年8月-至今", "单位": "中山大学", "职位": "教授"}}
]
3. 如果时间信息缺失，请将“{{时间}}”字段填为“未知”。
4. 按照时间顺序从早到晚排列。
5. 只输出JSON数组，不要输出任何解释或多余内容。
"""

    is_same_teacher_prompt = """
你的任务是判断给出的两份教师个人简介文本是否描述的是同一个人。请仔细阅读以下两份简介文本，并按照指示进行判断。
第一份教师个人简介：
<teacher_profile1>
{des1}
</teacher_profile1>
第二份教师个人简介：
<teacher_profile2>
{des2}
</teacher_profile2>
在判断时，请从研究方向、研究领域、教学方向、所属学院、毕业学校、研究成果、教育经历、工作经历、教育背景、专业领域等关键信息进行对比分析。
如果两份简介描述的是同一个人，请回答“True”；如果描述的是不同的人，请回答“False”。
注意事项：
1. 只需要回答"True"或"False"。不需要返回其他任何的内容。
输出:
    """

    def build_prompt(self, input_data: dict) -> str:
        """
        根据type字段返回对应的prompt
        输入:
            input_data (dict):
                - type: 功能类型（'homepage_match', 'work_experience', 'is_same_teacher'）
                - 主页归属: 必须包含'name', 'profile', 'homepage_markdown'
                - 提取工作经历: 必须包含'name', 'profile', 'homepage_markdowns'（list）
                - 判断是否同一人: 必须包含'des1', 'des2'
        输出:
            str: 完整的prompt
        """
        type_ = input_data.get("type")
        if type_ == "homepage_match":
            return self.homepage_match_prompt.format(
                name=input_data["name"],
                profile=input_data["profile"],
                homepage_markdown=input_data["homepage_markdown"],
            )
        if type_ == "work_experience":
            # 这里只返回工作经历prompt，实际流程在process里处理
            return self.work_experience_prompt
        if type_ == "is_same_teacher":
            return self.is_same_teacher_prompt.format(des1=input_data["des1"], des2=input_data["des2"])
        raise ValueError("input_data['type'] 不符合要求")

    async def process(self, input_data: dict) -> tuple:
        """
        处理流程：根据type构建prompt，调用LLM，解析结果。
        输入:
            input_data (dict):
                - type: 功能类型
                - 主页归属: 必须包含'name', 'profile', 'homepage_markdown'
                - 提取工作经历: 必须包含'name', 'profile', 'homepage_markdowns'（list）
                - 判断是否同一人: 必须包含'des1', 'des2'
        输出:
            tuple: (处理结果, 是否成功)
        """
        type_ = input_data.get("type")
        if type_ == "homepage_match" or type_ == "is_same_teacher":
            prompt = self.build_prompt(input_data)
            response = await self.get_llm_response(prompt)
            result = response.strip()
            if result in ["True", "False"]:
                return result, True
            return result, False
        if type_ == "work_experience":
            # 输入: name, profile, homepage_markdowns (list)
            name = input_data.get("name")
            profile = input_data.get("profile")
            homepage_markdowns = input_data.get("homepage_markdowns", [])
            if not (name and profile and isinstance(homepage_markdowns, list) and homepage_markdowns):
                return "缺少必要字段或homepage_markdowns为空", False
            # 依次判断归属
            for md in homepage_markdowns:
                match_prompt = self.homepage_match_prompt.format(name=name, profile=profile, homepage_markdown=md)
                match_resp = await self.get_llm_response(match_prompt)
                match_result = match_resp.strip()
                if match_result == "True":
                    # 归属该教师，提取工作经历
                    work_prompt = self.work_experience_prompt.format(baike_markdown=md)
                    work_resp = await self.get_llm_response(work_prompt)
                    work_result = work_resp.strip()
                    try:
                        json_result = json.loads(work_result)
                        if isinstance(json_result, list):
                            return json_result, True
                        return work_result, False
                    except Exception:
                        return work_result, False
            # 没有找到归属主页
            return "未找到归属该教师的主页", False
        raise ValueError("type不支持")

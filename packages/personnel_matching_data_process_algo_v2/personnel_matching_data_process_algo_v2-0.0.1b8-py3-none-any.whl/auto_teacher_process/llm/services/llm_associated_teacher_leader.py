import pandas as pd

from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class TeacherLeaderAssociatedProcessor(BaseLLMProcessor):
    prompt = """
你的任务是判断两份教师简介是否描述同一人。仔细阅读以下两份简介，对比研究方向、领域、教学方向、所属学院、毕业学校、研究成果、教育/工作经历、专业背景、职位信息、获奖情况等关键点，并遵循：
1. 若两份简介的关键信息完全匹配且无冲突，返回 "True"；
2. 若关键信息存在矛盾（如不同学院/学位/研究方向）或核心信息缺失导致无法验证，返回 "False"；
3. 即使部分非关键信息相似，只要核心信息不确定，仍返回 "False"；
4. 严格避免空回答，所有情况必须只输出 "True" 或 "False"。
5. 不需要解释原因，只需要返回一个布尔值（"True" 或 "False"）
第一份简介：
<teacher_profile1>
{des1}
</teacher_profile1>

第二份简介：
<teacher_profile2>
{des2}
</teacher_profile2>

回答（仅包含True/False，不允许出现其他回答）："""

    def build_prompt(self, input_data: dict) -> str:
        if "leader_description" not in input_data or "teacher_description" not in input_data:
            raise ValueError("des1 and des2 are required")

        return self.prompt.format(des1=input_data["leader_description"], des2=input_data["teacher_description"])

    async def process(self, *args, **kwargs):
        self.logger.debug("开始关联领导和教师")
        df: pd.DataFrame = kwargs["input_data"].get("df")
        rows = df.to_dict("records")

        result = []
        for row_dict in rows:
            try:
                self.logger.debug(f"正在判断关联：{row_dict}")

                # 判断长度，超长截断：
                if len(row_dict["leader_description"]) >= 10000:
                    row_dict["leader_description"] = row_dict["leader_description"][:10000]
                if len(row_dict["teacher_description"]) >= 10000:
                    row_dict["teacher_description"] = row_dict["teacher_description"][:10000]

                prompt = self.build_prompt(row_dict)
                response = await self.get_llm_response(prompt)
                if response not in ["True", "False"]:
                    self.logger.error(f"{row_dict['name']}: LLM返回结果错误: {response}")
                    continue
                result.append(
                    {
                        "name": row_dict["name"],
                        "school_name": row_dict["school_name"],
                        "leader_id": row_dict["leader_id"],
                        "teacher_id": row_dict["teacher_id"],
                        "is_same": response,
                    }
                )
            except Exception as e:
                self.logger.error(f"LLM调用错误: {e}")
            self.logger.debug(f"LLM响应: {response[:200]}...")

        return result

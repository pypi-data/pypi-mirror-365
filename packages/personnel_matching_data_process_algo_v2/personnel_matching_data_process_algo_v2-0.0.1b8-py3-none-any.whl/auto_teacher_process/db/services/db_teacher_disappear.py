import pandas as pd

from auto_teacher_process.db.db_base import BaseDBProcessor


class TeacherDisappearDBProcessor(BaseDBProcessor):
    def __init__(self, logger=None, system="teacher_disappear", stage="unkonw_task_name"):
        super().__init__(logger=logger, system=system, stage=stage)

    def get_teacher_info_by_id(self, teacher_id: int) -> dict:
        """
        根据teacher_id查derived_teacher_data表的derived_teacher_name、school_name、raw_data_id和description，
        再根据raw_data_id查raw_teacher_data表的link，返回{'derived_teacher_name':'xxx','school_name':'xxx','description':'xxx','link':'xxx'}
        """
        # 查询derived_teacher_data表
        query1 = f"""
            SELECT derived_teacher_name, school_name, raw_data_id, description
            FROM derived_teacher_data
            WHERE teacher_id = {teacher_id}
        """
        df1 = self.get_db(query1)
        if df1.empty:
            return {}
        derived_teacher_name = df1.iloc[0]["derived_teacher_name"]
        school_name = df1.iloc[0]["school_name"]
        raw_data_id = df1.iloc[0]["raw_data_id"]
        description = df1.iloc[0]["description"]

        # 查询raw_teacher_data表
        query2 = f"""
            SELECT link
            FROM raw_teacher_data
            WHERE raw_data_id = {raw_data_id}
        """
        df2 = self.get_db(query2)
        link = df2.iloc[0]["link"] if not df2.empty else None

        return {
            "derived_teacher_name": derived_teacher_name,
            "school_name": school_name,
            "description": description,
            "link": link,
        }

    def get_description_by_name_and_school(self, derived_teacher_name: str, school_name: str) -> list:
        """
        根据derived_teacher_name和school_name查derived_teacher_data表的所有description，
        返回一个list，每个元素为{'derived_teacher_name':..., 'school_name':..., 'description':...}
        """
        query = f"""
            SELECT description
            FROM derived_teacher_data
            WHERE derived_teacher_name = '{derived_teacher_name}' AND school_name = '{school_name}'
        """
        df = self.get_db(query)
        result = []
        if not df.empty:
            for desc in df["description"]:
                result.append(
                    {"derived_teacher_name": derived_teacher_name, "school_name": school_name, "description": desc}
                )
        return result

    def set_teacher_invalid_by_id(self, teacher_id: int) -> None:
        """
        根据teacher_id将derived_teacher_data表的is_valid字段设为0
        """
        query = """
            UPDATE derived_teacher_data
            SET is_valid = 0
            WHERE teacher_id = :teacher_id
        """
        self.update_db(df=pd.DataFrame({"teacher_id": [teacher_id]}), update_sql=query, batch_size=1000)

    def process(self, input_data):
        """
        主处理流程，根据input_data['type']决定调用哪个查询方法。
        type: 'by_teacher_id'、'by_name_and_school' 或 'set_invalid_by_teacher_id'
        其他参数：
          - by_teacher_id: 需要 teacher_id
          - by_name_and_school: 需要 derived_teacher_name, school_name
          - set_invalid_by_teacher_id: 需要 teacher_id
        返回查询结果
        """
        query_type = input_data.get("type")
        if query_type == "by_teacher_id":
            teacher_id = input_data.get("teacher_id")
            if teacher_id is None:
                raise ValueError("缺少teacher_id参数")
            result = self.get_teacher_info_by_id(teacher_id)
            return result
        if query_type == "by_name_and_school":
            derived_teacher_name = input_data.get("derived_teacher_name")
            school_name = input_data.get("school_name")
            if not derived_teacher_name or not school_name:
                raise ValueError("缺少derived_teacher_name或school_name参数")
            result = self.get_description_by_name_and_school(derived_teacher_name, school_name)
            return result
        if query_type == "set_invalid_by_teacher_id":
            teacher_id = input_data.get("teacher_id")
            if teacher_id is None:
                raise ValueError("缺少teacher_id参数")
            self.set_teacher_invalid_by_id(teacher_id)
            return {"status": "success"}
        raise ValueError(f"不支持的type类型: {query_type}")

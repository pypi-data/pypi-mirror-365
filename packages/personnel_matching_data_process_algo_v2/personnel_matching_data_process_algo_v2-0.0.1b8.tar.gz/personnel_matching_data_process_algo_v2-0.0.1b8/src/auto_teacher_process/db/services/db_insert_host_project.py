import json
import uuid

import pandas as pd
from tqdm import tqdm

from auto_teacher_process.db.db_base import BaseDBProcessor


class HostProjectInsertDBProcessor(BaseDBProcessor):
    """主持项目数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)

    def process(self, input_data):
        """主处理流程"""
        # 获取输入参数
        province = input_data.get("province", "")
        query_sql = input_data.get("query_sql", "")

        if not province or not query_sql:
            raise ValueError("缺少必要参数")

        filter_df_list = []  # 如果没有传空list []
        raw_project_df_list = []
        relation_df_list = []

        projects_df = self.get_db(query_sql)
        self.logger.debug(f"projects_df of len: {len(projects_df)}")

        for index, p_info in tqdm(projects_df.iterrows(), total=len(projects_df), desc="project processing row:"):
            teacher_id = p_info["teacher_id"]
            project_str = p_info["project_experience"]
            p_is_valid = p_info["is_valid"]
            if p_is_valid == 0:
                filter_row = {
                    "teacher_id": teacher_id,
                    "filtered_project_experience": json.dumps([], ensure_ascii=False),
                    "is_valid": 0,
                    "status": 3,
                }
                filter_df_list.append(filter_row)
            else:
                try:
                    projects = json.loads(project_str)
                except Exception as e:
                    self.logger.debug(f"json解析出错:{e}")
                    continue

                host_projects = projects["主持的项目"]  # list
                if len(host_projects) == 0:
                    filter_row = {
                        "teacher_id": teacher_id,
                        "filtered_project_experience": json.dumps([], ensure_ascii=False),
                        "is_valid": 0,
                        "status": 3,
                    }
                    filter_df_list.append(filter_row)
                else:
                    # filter 主持的项目
                    filter_row = {
                        "teacher_id": teacher_id,
                        "filtered_project_experience": json.dumps(host_projects, ensure_ascii=False),
                        "is_valid": 1,
                        "status": 3,
                    }
                    filter_df_list.append(filter_row)

                    # raw_project project_id(uuid) -> project_relation
                    filtered_projects = [p for p in host_projects if len(p) < 150]
                    for p in filtered_projects:
                        project_id = uuid.uuid4()
                        raw_project_row = {
                            "project_id": project_id,
                            "project_name": p,
                            "data_source": "derived_project_experience_filtered",
                            "teacher_id": teacher_id,
                        }
                        raw_project_df_list.append(raw_project_row)
                        # project_relation
                        project_relation_row = {
                            "teacher_id": teacher_id,
                            "project_id": project_id,
                            "is_from_match": 0,
                            "is_valid": 1,
                        }
                        relation_df_list.append(project_relation_row)

        filter_df = pd.DataFrame(filter_df_list)
        raw_project_df = pd.DataFrame(raw_project_df_list)
        relation_df = pd.DataFrame(relation_df_list)

        # 插入数据
        self.logger.debug("inserting data...")
        self.insert_db(
            df=filter_df,
            table_name="derived_project_experience_filtered",
            batch_size=1000,
            progress_file="insert_filtered_progress.txt",
        )
        self.logger.debug("第一次插入数据完成")
        self.insert_db(
            df=raw_project_df,
            table_name="raw_teacher_project",
            batch_size=1000,
            progress_file="insert_raw_project_progress.txt",
        )
        self.logger.debug("第二次插入数据完成")
        self.insert_db(
            df=relation_df,
            table_name="product_teacher_project_relation",
            batch_size=1000,
            progress_file="insert_project_relation_progress.txt",
        )
        self.logger.debug("第三次插入数据完成")

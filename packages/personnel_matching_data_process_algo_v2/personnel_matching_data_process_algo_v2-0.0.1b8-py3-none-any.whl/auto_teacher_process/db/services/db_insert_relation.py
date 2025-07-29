import json

import pandas as pd
from tqdm import tqdm

from auto_teacher_process.db.db_base import BaseDBProcessor


class RelationInsertDBProcessor(BaseDBProcessor):
    """教师关系数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)

    def _get_teacher_project_level(self, file_dir, province, merge_relation_df):
        """获取教师项目等级信息"""
        teacher_project_level = {}
        for index, row in tqdm(merge_relation_df.iterrows(), total=len(merge_relation_df)):
            teacher_id = row["teacher_id"]
            project_level = row["project_level"]
            if project_level is None or pd.isna(project_level):
                continue
            if teacher_id not in teacher_project_level:
                teacher_project_level[teacher_id] = set()
            teacher_project_level[teacher_id].add(project_level)
        save_list = []
        for teacher_id, project_level_set in teacher_project_level.items():
            row = {"teacher_id": teacher_id, "project_level": json.dumps(list(project_level_set), ensure_ascii=False)}
            save_list.append(row)
        teacher_project_level_df = pd.DataFrame(save_list)
        teacher_project_level_df.to_csv(f"{file_dir}/{province}_teacher_project_level.csv", index=False)
        self.logger.debug("教师项目等级信息已保存")

    def process(self, input_data: dict) -> None:
        """主处理流程"""
        # 获取输入参数
        province = input_data.get("province", "")
        file_dir = input_data.get("file_dir", "")
        relation_type = input_data.get("type", "")

        if not all([province, file_dir, relation_type]):
            raise ValueError("参数校验失败")

        self.logger.debug(f"开始处理{relation_type}关系数据，省份: {province}")

        merged_df = self._get_all_folders(file_dir, province)

        if merged_df.empty:
            self.logger.debug("合并后数据为空")
            return

        if relation_type == "paper":
            merged_df = merged_df.drop(columns=["orcid"])

        ids = f"{relation_type}_id"
        if relation_type == "cn_paper":
            ids = "paper_id"

        self.logger.debug(f"{province} 去重前 {relation_type}关系数量: {len(merged_df)}")
        df_unique = merged_df.drop_duplicates(subset=["teacher_id", ids])
        self.logger.debug(f"{province} 去重后 {relation_type}关系数量: {len(df_unique)}")

        unique_teacher_set = set(df_unique["teacher_id"])
        self.logger.debug(f"{province} 共有 {len(unique_teacher_set)} 位教师，匹配有{relation_type}。")
        unique_paper_set = set(df_unique[ids])
        self.logger.debug(f"{province} 共有 {len(unique_paper_set)} 个{relation_type}，匹配有教师。")

        if relation_type == "project":
            df_unique["is_from_match"] = 1
            self._get_teacher_project_level(file_dir, province, df_unique)
            df_unique = df_unique.drop(columns=["id", "project_level"])

        table_name = f"product_teacher_{relation_type}_relation"

        # 执行批量插入
        self.insert_db(
            df=df_unique,
            table_name=table_name,
            batch_size=1000,  # 根据实际情况调整批次大小
        )

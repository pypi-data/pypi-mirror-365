import json
import uuid

import pandas as pd

from auto_teacher_process.db.db_base import BaseDBProcessor
from auto_teacher_process.db.services.db_insert_famous_projects import FamousProjectsInsertDBProcessor
from auto_teacher_process.db.services.db_insert_teacher_level import TeacherLevelDBProcessor


class UpdateInfosDBProcessor(BaseDBProcessor):
    """教师信息更新处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)
        famous_projects_processor = FamousProjectsInsertDBProcessor()
        teacher_level_processor = TeacherLevelDBProcessor()
        self.project_famous_check = famous_projects_processor._project_famous_check
        self.quchong = famous_projects_processor._quchong
        self.calculate_teacher_level = teacher_level_processor.calculate_teacher_level

    def _db_insert_host_project(self, projects_df):
        # TODO: 1.参与  2.长度100-120过滤
        # TODO: 4.project_filter 表 → raw_teacher_project    5.project_filter 表 → product_teacher_project_relation
        # famous_project_df, raw_teacher_project_df, project_relation_df
        filter_df_list = []  # 如果没有传空list []
        raw_project_df_list = []
        relation_df_list = []

        self.logger.debug(f"projects_df of len: {len(projects_df)}")

        for index, p_info in projects_df.iterrows():
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
                projects = json.loads(project_str)
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

        # TODO: 修改为更新数据
        # 1. derived_project_experience_filtered
        host_project_update_sql = """
                UPDATE derived_project_experience_filtered
                SET filtered_project_experience = :filtered_project_experience,
                    is_valid = :is_valid,
                    status = :status
                WHERE teacher_id = :teacher_id
            """
        self.update_db(
            df=filter_df, update_sql=host_project_update_sql, progress_file="update_host_project_progress.txt"
        )

        self.insert_db(
            df=raw_project_df,
            table_name="raw_teacher_project",
            batch_size=1000,
            progress_file="insert_raw_project_progress.txt",
        )

        self.logger.debug(f"relation_df:{len(relation_df)}\n{relation_df}")
        self.insert_db(
            df=relation_df,
            table_name="product_teacher_project_relation",
            batch_size=1000,
            progress_file="insert_project_relation_progress.txt",
        )

    def _db_insert_famous_project(self, projects_df):
        self.logger.debug("执行db_insert_famous_project")
        famous_df_list = []

        query_sql = f"""
        SELECT 
            t.teacher_id, 
            rp.project_level
        FROM 
            derived_teacher_data t
        LEFT JOIN 
            product_teacher_project_relation r 
            ON t.teacher_id = r.teacher_id
        LEFT JOIN 
            raw_teacher_project rp 
            ON r.project_id = rp.project_id
        WHERE 
            r.is_from_match = 1 AND t.teacher_id IN ({",".join([f"'{i}'" for i in projects_df["teacher_id"].to_list()])});
        """

        projects_with_levels_df = self.get_db(query_sql)

        projects_with_levels_df = projects_with_levels_df.dropna(subset=["project_level"])
        projects_with_levels_df.set_index("teacher_id", inplace=True)
        for index, p_info in projects_df.iterrows():
            teacher_id = p_info["teacher_id"]
            project_str = p_info["project_experience"]
            p_is_valid = p_info["is_valid"]
            if p_is_valid == 0:
                host_projects = []
                join_projects = []
            else:
                projects = json.loads(project_str)
                try:
                    host_projects = projects["主持的项目"]  # list
                except:
                    self.logger.debug(projects)
                    host_projects = []
                try:
                    join_projects = projects["参与的项目"]
                except:
                    self.logger.debug(projects)
                    join_projects = []

            if teacher_id in projects_with_levels_df.index:
                teacher_projects_with_level = projects_with_levels_df.loc[teacher_id]

                if not teacher_projects_with_level.empty:
                    if isinstance(teacher_projects_with_level, pd.Series):
                        # 如果是 Series, 直接使用它的 'project_level' 列并获取唯一值
                        non_null_project_levels = teacher_projects_with_level.unique().tolist()
                    elif isinstance(teacher_projects_with_level, pd.DataFrame):
                        # 如果是 DataFrame, 选择 'project_level' 列并获取唯一值
                        non_null_project_levels = teacher_projects_with_level["project_level"].unique().tolist()
                    host_projects.extend(non_null_project_levels)

            famous_host_projects = self.project_famous_check(host_projects)
            famous_host_projects = self.quchong(famous_host_projects)

            famous_join_projects = self.project_famous_check(join_projects)
            famous_join_projects = self.quchong(famous_join_projects)
            if len(famous_host_projects) == 0 and len(famous_join_projects) == 0:
                is_valid = 0
            else:
                is_valid = 1
            famous_row = {
                "teacher_id": teacher_id,
                "host_projects": json.dumps(famous_host_projects, ensure_ascii=False),
                "join_projects": json.dumps(famous_join_projects, ensure_ascii=False),
                "is_valid": is_valid,
                "status": 3,
            }
            famous_df_list.append(famous_row)

        famous_df = pd.DataFrame(famous_df_list)

        self.logger.debug(f"更新数量：{len(famous_df)}")
        # 1. derived_famous_projects
        famous_project_update_sql = """
                UPDATE derived_famous_projects
                SET host_projects = :host_projects,
                    join_projects = :join_projects,
                    is_valid = :is_valid,
                    status = :status
                WHERE teacher_id = :teacher_id
            """
        self.update_db(
            df=famous_df, update_sql=famous_project_update_sql, progress_file="update_famous_project_progress.txt"
        )

    def _get_old_famous_titles(self, teacher_ids):
        """
        获取旧的著名头衔数据
        """
        self.logger.debug("执行_get_old_famous_titles")
        teacher_ids_str = ",".join([f"'{i}'" for i in teacher_ids])
        query_sql = f"""
        SELECT teacher_id, normalized_titles
        FROM derived_famous_titles
        WHERE teacher_id IN ({teacher_ids_str})
        """
        return self.get_db(query_sql)

    def _merge_old_famous_titles(self, famous_df, old_famous_df):
        """
        将新的著名头衔和旧的著名头衔合并去重
        """
        merged_df = famous_df.merge(
            old_famous_df[["teacher_id", "normalized_titles"]], on="teacher_id", how="left", suffixes=("", "_old")
        )

        # 合并并去重
        def merge_titles(new_titles_str, old_titles_str):
            try:
                new = json.loads(new_titles_str) if new_titles_str else []
            except:
                new = []
            try:
                old = json.loads(old_titles_str) if old_titles_str else []
            except:
                old = []
            return json.dumps(list(set(new + old)), ensure_ascii=False)

        merged_df["normalized_titles"] = merged_df.apply(
            lambda row: merge_titles(row["normalized_titles"], row["normalized_titles_old"]), axis=1
        )

        # 删除旧列
        merged_df.drop(columns=["normalized_titles_old"], inplace=True)
        return merged_df

    def process(self, input_data: dict) -> None:
        """主处理流程"""
        # 获取输入参数
        province = input_data.get("province", "")
        file_dir = input_data.get("file_dir", "")
        if province == "" or file_dir == "":
            raise ValueError("请提供正确的省份和文件目录")

        merged_df = self._get_all_folders(file_dir, province)

        if merged_df.empty:
            self.logger.debug("合并后数据为空")
            return

        merged_df = merged_df.where(pd.notnull(merged_df), None)
        # 筛选出 is_valid 为 1 的数据
        self.logger.debug(f"总的数据量: {len(merged_df)}")
        teacher_level_df = merged_df[["teacher_id"]].copy()

        # 将merged_df处理成四种数据库表需要的格式
        omit_df = merged_df[["teacher_id", "omit_description", "omit_valid"]].copy()
        omit_df.rename(columns={"omit_valid": "is_valid"}, inplace=True)
        omit_df = omit_df[omit_df["is_valid"] == 1]

        omit_update_sql = """
                UPDATE derived_omit_description
                SET omit_description = :omit_description,
                    is_valid = :is_valid
                WHERE teacher_id = :teacher_id
            """

        area_df = merged_df[["teacher_id", "research_area", "area_valid"]].copy()
        area_df.rename(columns={"area_valid": "is_valid"}, inplace=True)
        area_df = area_df[area_df["is_valid"] == 1]
        area_df = area_df[area_df["research_area"] != "[]"]

        area_update_sql = """
                    UPDATE derived_research_area
                    SET research_area = :research_area,
                        is_valid = :is_valid
                    WHERE teacher_id = :teacher_id
                """

        email_df = merged_df[["teacher_id", "email", "email_valid"]].copy()
        email_df.rename(columns={"email_valid": "is_valid"}, inplace=True)
        email_df = email_df[email_df["is_valid"] == 1]

        email_update_sql = """
                        UPDATE derived_email
                        SET email = :email,
                            is_valid = :is_valid
                        WHERE teacher_id = :teacher_id
                    """

        title_df = merged_df[["teacher_id", "title", "normalized_title", "title_valid"]].copy()
        title_df.rename(columns={"title_valid": "is_valid"}, inplace=True)
        title_df = title_df[title_df["is_valid"] == 1]

        title_update_sql = """
                            UPDATE derived_title
                            SET title = :title,
                                normalized_title = :normalized_title,
                                is_valid = :is_valid
                            WHERE teacher_id = :teacher_id
                        """

        famous_df = merged_df[["teacher_id", "famous_titles", "normalized_famous_titles", "famous_valid"]].copy()
        famous_df.rename(
            columns={"famous_valid": "is_valid", "normalized_famous_titles": "normalized_titles"}, inplace=True
        )
        famous_df = famous_df[famous_df["is_valid"] == 1]
        # TODO: 将旧的帽子查出来，跟现有提取出的帽子合并去重
        teacher_ids = famous_df["teacher_id"].tolist()
        old_famous_df = self._get_old_famous_titles(teacher_ids)
        # 将 famous_df 的 normalized_titles列 和 old_famous_df 的 normalized_titles列 转化为列表合并去重之后，赋值给 famous_df 的 normalized_titles 列
        new_famous_df = self._merge_old_famous_titles(famous_df, old_famous_df).copy()

        famous_update_sql = """
                            UPDATE derived_famous_titles
                            SET famous_titles = :famous_titles,
                                normalized_titles = :normalized_titles,
                                is_valid = :is_valid
                            WHERE teacher_id = :teacher_id
                        """

        position_df = merged_df[["teacher_id", "position", "position_valid"]].copy()
        position_df.rename(columns={"position_valid": "is_valid"}, inplace=True)
        # 筛选出is_valid值为1的数据
        # TODO: 职务比较特殊，仅保留该教师当前的职务
        # position_df = position_df[position_df['is_valid'] == 1]

        position_update_sql = """
                                UPDATE derived_position
                                SET position = :position,
                                    is_valid = :is_valid
                                WHERE teacher_id = :teacher_id
                            """

        project_df = merged_df[["teacher_id", "project_experience", "project_valid"]].copy()
        project_df.rename(columns={"project_valid": "is_valid"}, inplace=True)

        project_update_sql = """
                                UPDATE derived_project_experience
                                SET project_experience = :project_experience,
                                    is_valid = :is_valid
                                WHERE teacher_id = :teacher_id
                            """

        self.logger.debug("---------------开始更新omit_description表数据---------------")
        self.update_db(df=omit_df, update_sql=omit_update_sql, progress_file="update_omit_progress.txt")
        self.logger.debug("～～～～～～～～～完成更新omit_description表数据～～～～～～～～～")

        self.logger.debug("---------------开始更新research_area表数据---------------")
        self.update_db(df=area_df, update_sql=area_update_sql, progress_file="update_area_progress.txt")
        self.logger.debug("～～～～～～～～～完成更新research_area表数据～～～～～～～～～")

        self.logger.debug("---------------开始更新email表数据---------------")
        self.update_db(df=email_df, update_sql=email_update_sql, progress_file="update_email_progress.txt")
        self.logger.debug("～～～～～～～～～完成更新email表数据～～～～～～～～～")

        self.logger.debug("---------------开始更新title表数据---------------")
        self.update_db(df=title_df, update_sql=title_update_sql, progress_file="update_title_progress.txt")
        self.logger.debug("～～～～～～～～～完成更新title表数据～～～～～～～～～")

        self.logger.debug("---------------开始更新famous_titles表数据---------------")
        self.update_db(df=new_famous_df, update_sql=famous_update_sql, progress_file="update_famous_progress.txt")
        self.logger.debug("～～～～～～～～～完成更新famous_titles表数据～～～～～～～～～")

        self.logger.debug("---------------开始更新position表数据---------------")
        self.update_db(df=position_df, update_sql=position_update_sql, progress_file="update_position_progress.txt")
        self.logger.debug("～～～～～～～～～完成更新position表数据～～～～～～～～～")

        self.logger.debug("---------------开始更新project_experience表数据---------------")
        self.update_db(df=project_df, update_sql=project_update_sql, progress_file="update_project_progress.txt")
        self.logger.debug("～～～～～～～～～完成更新project_experience表数据～～～～～～～～～")

        # 删除数据
        delete_sql = """DELETE FROM raw_teacher_project """
        self.logger.debug("---------------开始删除raw_teacher_project表数据---------------")
        self.delete_db(df=project_df, delete_sql=delete_sql, progress_file="delete_project_progress.txt")
        self.logger.debug("～～～～～～～～～完成删除raw_teacher_project表数据～～～～～～～～～")

        self.logger.debug("---------------开始插入host_project数据---------------")
        self._db_insert_host_project(project_df)
        self.logger.debug("～～～～～～～～～完成插入host_project数据～～～～～～～～～")

        self.logger.debug("---------------开始插入famous_project数据---------------")
        self._db_insert_famous_project(project_df)
        self.logger.debug("～～～～～～～～～完成插入famous_project数据～～～～～～～～～")

        self.logger.debug("---------------开始更新teacher_level数据---------------")
        # 创建teacher_level_df
        teacher_level_df = merged_df[["teacher_id"]].copy()
        teacher_level_update_sql = """
            UPDATE derived_teacher_level
            SET
                famous_titles_level = :famous_titles_level,
                project_level = :project_level,
                position_level = :position_level,
                job_title_level = :job_title_level,
                school_level = :school_level
            WHERE teacher_id = :teacher_id;
        """
        # 获取需要更新的数据
        teacher_ids = teacher_level_df["teacher_id"].tolist()
        teacher_ids_str = ",".join([f"'{i}'" for i in teacher_ids])
        query_sql = f"""
        SELECT t.teacher_id, t.school_name, pos.position, tit.title, ftit.normalized_titles, fp.host_projects, fp.join_projects
        FROM derived_teacher_data t
        LEFT JOIN derived_position pos ON t.teacher_id = pos.teacher_id
        LEFT JOIN derived_title tit ON t.teacher_id = tit.teacher_id
        LEFT JOIN derived_famous_titles ftit ON t.teacher_id = ftit.teacher_id
        LEFT JOIN derived_famous_projects fp ON t.teacher_id = fp.teacher_id
        WHERE t.is_valid = 1 AND t.teacher_id IN ({teacher_ids_str});
        """
        self.logger.debug("---------------开始获取需要更新的teacher_level数据---------------")
        teacher_info_df = self.get_db(query_sql)
        level_df = self.calculate_teacher_level(teacher_info_df)
        self.logger.debug(f"level_df:{len(level_df)}\n{level_df}")
        self.update_db(
            df=level_df, update_sql=teacher_level_update_sql, progress_file="update_teacher_level_progress.txt"
        )
        self.logger.debug("～～～～～～～～～完成更新teacher_level数据～～～～～～～～～")

        self.logger.debug("############# 所有数据更新成功！！！")
        self.logger.debug("done")

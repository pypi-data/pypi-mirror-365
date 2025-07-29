import json

import pandas as pd

from auto_teacher_process.config import Config
from auto_teacher_process.db.db_base import BaseDBProcessor
from auto_teacher_process.utils.project_utils import _project_famous_check, _quchong, calculate_teacher_level


class ProjectInsertDBProcessor(BaseDBProcessor):
    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)
        self.province_code_dict = Config.DB_CONFIG.TEACHER_LEVEL.PORVINCE_CODE_DICT
        self.famous_projects_level_scores = Config.DB_CONFIG.TEACHER_LEVEL.FAMOUS_PROJECTS_LEVEL_SCORES
        self.famous_titles_level_scores = Config.DB_CONFIG.TEACHER_LEVEL.FAMOUS_TITLES_LEVEL_SCORES
        self.titles_level_scores = Config.DB_CONFIG.TEACHER_LEVEL.TITLES_LEVEL_SCORES

    def get_project_teacher_data_from_db(self, id_start, id_end):
        query = f"""
                SELECT t.teacher_id, t.derived_teacher_name, t.college_name, t.description, des.omit_description, proj.project_experience, area.research_area, em.email, t.school_name
                FROM derived_teacher_data t
                LEFT JOIN derived_omit_description des ON t.teacher_id = des.teacher_id
                LEFT JOIN derived_project_experience proj ON t.teacher_id = proj.teacher_id
                LEFT JOIN derived_research_area area ON t.teacher_id = area.teacher_id
                LEFT JOIN derived_email em ON t.teacher_id = em.teacher_id
                WHERE t.is_valid=1 AND (t.raw_data_id>={id_start} AND t.raw_data_id<={id_end});
                """
        return self.get_db(query)

    def db_insert_famous_projects(self, id_start, id_end) -> None:
        # 构建查询语句
        teacher_query = f"""
                    SELECT p.teacher_id, p.project_experience, p.is_valid
                    FROM derived_teacher_data t
                    LEFT JOIN derived_project_experience p ON t.teacher_id = p.teacher_id
                    WHERE t.is_valid=1 AND (t.raw_data_id>={id_start} AND t.raw_data_id<={id_end});
                """

        relation_query = f"""
                    SELECT t.teacher_id, rp.project_level
                    FROM derived_teacher_data t
                    LEFT JOIN product_teacher_project_relation r ON t.teacher_id = r.teacher_id
                    LEFT JOIN raw_teacher_project rp ON r.project_id = rp.project_id
                    WHERE t.is_valid=1 AND (t.raw_data_id>={id_start} AND t.raw_data_id<={id_end}) AND r.is_from_match = 1;
                """

        # 查询数据
        projects_df = self.get_db(teacher_query)
        projects_with_levels_df = self.get_db(relation_query)

        # 处理数据
        famous_df_list = []
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
                try:
                    projects = json.loads(project_str)
                except Exception as e:
                    self.logger.debug(f"解析project出错:{e}")
                    continue
                self.logger.debug(projects)
                try:
                    host_projects = projects["主持的项目"]  # list
                except Exception as e:
                    self.logger.debug(f"{projects}出错:{e}")
                    host_projects = []
                try:
                    join_projects = projects["参与的项目"]
                except:
                    self.logger.debug(f"{projects}出错:{e}")
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

            famous_host_projects = _project_famous_check(host_projects)
            famous_host_projects = _quchong(famous_host_projects)

            famous_join_projects = _project_famous_check(join_projects)
            famous_join_projects = _quchong(famous_join_projects)
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

        # 插入数据
        famous_df = pd.DataFrame(famous_df_list)

        self.insert_db(
            df=famous_df,
            table_name="derived_famous_projects",
            batch_size=1000,
            progress_file="insert_famous_projects_progress.txt",
        )

    def get_school_level(self) -> dict:
        """获取学校信息"""
        self.logger.debug("获取学校信息")
        query = """
            SELECT school_name, school_level
            FROM product_school_info
            ORDER BY id ASC;
        """
        school_df = self.get_db(query)
        level_map = {0: 40, 1: 100, 2: 90, 3: 80, 4: 70, 5: 60}
        return {row["school_name"]: level_map.get(row["school_level"], 40) for _, row in school_df.iterrows()}

    def db_insert_teacher_level(self, id_start, id_end) -> None:
        query_sql = f"""
                SELECT t.teacher_id, t.school_name, pos.position, tit.title, ftit.normalized_titles, fp.host_projects, fp.join_projects
                FROM derived_teacher_data t
                LEFT JOIN derived_position pos ON t.teacher_id = pos.teacher_id
                LEFT JOIN derived_title tit ON t.teacher_id = tit.teacher_id
                LEFT JOIN derived_famous_titles ftit ON t.teacher_id = ftit.teacher_id
                LEFT JOIN derived_famous_projects fp ON t.teacher_id = fp.teacher_id
                WHERE (t.raw_data_id>={id_start} AND t.raw_data_id<={id_end}) AND t.is_valid = 1;
                """

        # 获取教师数据
        teacher_df = self.get_db(query_sql)

        school_level_dict = self.get_school_level()

        # 计算教师等级
        level_df = calculate_teacher_level(teacher_df, school_level_dict)

        # 插入数据库
        self.insert_db(df=level_df, table_name="derived_teacher_level", batch_size=1000)
        self.logger.debug("教师等级数据插入成功")

    def process(self, input_data):
        """主处理流程"""

        merged_df = self.get_df(input_data["file"])

        if merged_df.empty:
            self.logger.debug("没有需要处理的数据")
            return

        merged_df = merged_df[merged_df["is_valid"] == 1]
        df_unique = merged_df.drop_duplicates(subset=["teacher_id", "project_id"])
        df_unique["is_from_match"] = 1

        # 更新数据
        self.logger.debug("开始插入数据库...")
        self.insert_db(
            df=df_unique,
            table_name="product_teacher_project_relation",
            batch_size=1000,
            progress_file="project_match_relation_insert_progress.txt",
        )

        self.db_insert_famous_projects(id_start=input_data["id_start"], id_end=input_data["id_end"])
        self.db_insert_teacher_level(id_start=input_data["id_start"], id_end=input_data["id_end"])

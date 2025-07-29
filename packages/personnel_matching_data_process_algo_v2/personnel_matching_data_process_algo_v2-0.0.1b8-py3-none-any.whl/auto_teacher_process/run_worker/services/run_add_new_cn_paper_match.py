import pandas as pd

from auto_teacher_process.db.services.db_insert_cn_paper_match import CNPaperMatchInsertDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.llm.services.llm_cn_paper_match import CNPaperMatchLLMProcessor
from auto_teacher_process.run_worker.run_base import BaseRunProcessor
from auto_teacher_process.utils.cn_paper_utils import parse_unit_names
from auto_teacher_process.utils.paper_utils import find_best_match, project_parse
from auto_teacher_process.utils.text_utils import contains_chinese


class NewCnPaperMatchProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_cn_paper_data_processing_pipeline"  # 流水线名称
        self.task_type = "new_add_cn_paper_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "paper_id"  # 数据主键字段
        self.school_en_cn_dict = None
        self.school_cn_en_dict = None
        self.school_en_list = None
        self.db = CNPaperMatchInsertDBProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)
        self.llm = CNPaperMatchLLMProcessor(logger=self.logger)

        self.school_cn_en_dict, self.school_en_cn_dict, self.school_cn_list, self.school_en_list = (
            self.get_school_name_dict()
        )

    def get_school_name_dict(self):
        school_df = self.db.get_all_school_info()
        school_names = school_df["school_name"]
        school_names_en = school_df["school_name_en"]
        return (
            dict(zip(school_names, school_names_en, strict=False)),
            dict(zip(school_names_en, school_names, strict=False)),
            list(school_names),
            list(school_names_en),
        )

    async def process_row(self, paper_info: pd.Series) -> dict | None:
        batch_relation_list = []
        paper_id = paper_info["id"]
        # 检查是否已经处理过该论文
        if paper_id in self.processed_ids:
            return None  # 跳过已处理的论文

        paper_info = paper_info.to_dict()

        if paper_info["author_list"] is None or pd.isna(paper_info["author_list"]):
            return None
        if paper_info["addresses"] is None or pd.isna(paper_info["addresses"]):
            return None

        unit_names = parse_unit_names(paper_info["author_list"], paper_info["institution"])

        for affiliation, author_names_list in unit_names.items():
            if contains_chinese(affiliation):
                affiliation = find_best_match(affiliation, self.school_cn_list)
                if affiliation is None:
                    continue
            else:
                affiliation = find_best_match(affiliation, self.school_en_list)
                affiliation = self.school_en_cn_dict[affiliation]
                if affiliation is None:
                    continue

            for author_name in author_names_list:
                teacher_df = await self.es.async_es_to_df_by_teacher_and_school_name_idx_teacher_data(
                    author_name, affiliation
                )
                if teacher_df is None:
                    continue
                for _, teacher in teacher_df.iterrows():
                    college, description, research = (
                        teacher["college_name"],
                        teacher["omit_description"],
                        teacher["research_area"],
                    )
                    teacher_id = teacher["teacher_id"]
                    email = teacher["email"]
                    project_str = teacher["project_experience"]
                    project = project_parse(project_str)
                    try:
                        author_order = author_names_list.index(author_name) + 1
                    except:
                        author_order = -1
                    # 邮箱判断
                    if not pd.isna(email) and not pd.isna(paper_info["email"]):
                        llm_out = True if email in paper_info["email"] else False
                        if llm_out:
                            new_row = {
                                "teacher_id": teacher_id,
                                "paper_id": paper_id,
                                "author_order": author_order,
                                "high_true": 3,  # 通过邮箱进行挂载
                                "is_valid": 1,
                            }
                            batch_relation_list.append(new_row)
                            break
                    if college in affiliation:
                        new_row = {
                            "teacher_id": teacher_id,
                            "paper_id": paper_id,
                            "author_order": author_order,
                            "high_true": 2,  # 通过学院in包含进行挂载
                            "is_valid": 1,
                        }
                        batch_relation_list.append(new_row)
                        break

                    prompt_args = {
                        "mode": "high",
                        "title": paper_info["title"],
                        "keywords": paper_info["keywords"],
                        "zhuanji": paper_info["zhuanji"],
                        "zhuanti": paper_info["zhuanti"],
                        "college": college,
                        "description": description,
                        "project": project,
                        "research": research,
                    }

                    llm_out = await self.llm.run(prompt_args)
                    if llm_out:
                        new_row = {
                            "teacher_id": teacher_id,
                            "paper_id": paper_id,
                            "author_order": author_order,
                            "high_true": 1,
                            "is_valid": 1,
                        }
                        batch_relation_list.append(new_row)
                        break

        return batch_relation_list

    async def run(self):
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        cn_paper_df = self.db.get_cn_paper_by_id_range(self.task_args["id_start"], self.task_args["id_end"])
        self.logger.info(f"【{self.task_type}】: 数据读取完成", extra={"event": "db_read_end"})

        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        output_data = await self.process(cn_paper_df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})

        # ES需要手动关闭
        await self.es.close_es_engine()

        # 数据入库
        self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={"event": "db_insert_start"})
        db_input_data = {"file": output_data}
        self.db.run(db_input_data)
        self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={"event": "db_insert_end"})

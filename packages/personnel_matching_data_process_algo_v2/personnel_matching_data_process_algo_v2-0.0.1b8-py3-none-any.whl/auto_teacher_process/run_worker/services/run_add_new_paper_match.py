import sys

sys.path.append("/home/personnel-matching-data-process-algo")

import pandas as pd

from auto_teacher_process.db.services.db_insert_paper_match import PaperInsertDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.llm.services.llm_paper_match import PaperMatchLLMProcessor
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.mq.consumer import start_consumer
from auto_teacher_process.run_worker.run_base import BaseRunProcessor
from auto_teacher_process.utils.match_utils import select_teacher_by_past_schools
from auto_teacher_process.utils.paper_utils import (
    extract_and_match_institutions,
    get_reprint_author,
    normalize_name,
    project_parse,
)


class NewPaperMatchRunProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_wos_paper_data_processing_pipeline"  # 流水线名称
        self.task_type = "new_add_paper_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "paper_id"  # 数据主键字段
        self.set_file_paths()
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)
        self.db = PaperInsertDBProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)
        self.llm = PaperMatchLLMProcessor(logger=self.logger)

        self.school_cn_en_dict, self.school_en_cn_dict = self.db.get_school_name_dict()

    async def process_row(self, row: pd.Series) -> list | dict | None:
        paper_id = row["id"]
        # 检查是否已经处理过该论文
        if paper_id in self.processed_ids:
            return None  # 跳过已处理的论文

        if row["author_list"] is None or pd.isna(row["author_list"]):
            return None
        if row["addresses"] is None or pd.isna(row["addresses"]):
            return None
        if row["affiliations"] is None or pd.isna(row["affiliations"]):
            return None

        abb_full_school_name_dict, abb_author_list_dict = extract_and_match_institutions(
            row["addresses"], row["affiliations"]
        )

        full_author_list = row["author_list"].split("; ")
        try:
            # 获取通信作者全名
            reprint_author = get_reprint_author(full_author_list, row["reprint_addresses"])
        except:
            reprint_author = set()

        batch_relation_list = []

        for abb_school_name, author_list in abb_author_list_dict.items():
            full_school_name = abb_full_school_name_dict.get(abb_school_name, None)

            if full_school_name is None:
                continue

            # 遍历教师列表
            for author_name in author_list:
                author_name_std = normalize_name(author_name)
                school_name_cn = self.school_en_cn_dict.get(full_school_name, None)
                if school_name_cn is None:
                    continue
                # 找出所有姓名变体匹配的教师
                teacher_df = await self.es.async_es_to_df_by_teacher_idx_teacher_data(author_name_std.lower())
                if teacher_df is None:
                    continue

                matched_teacher_df = await select_teacher_by_past_schools(
                    db=self.db, teacher_df=teacher_df, school_names_cn=school_name_cn
                )
                if matched_teacher_df is None:
                    continue

                for _, teacher in matched_teacher_df.iterrows():
                    teacher_id = teacher["teacher_id"]
                    teacher_email = teacher["email"]
                    college, omit_description, research_area = (
                        teacher["college_name"],
                        teacher["omit_description"],
                        teacher["research_area"],
                    )
                    # 获得作者位序
                    try:
                        author_order = full_author_list.index(author_name) + 1
                    except:
                        author_order = 0
                    # 邮箱判断
                    if not pd.isna(teacher_email) and not pd.isna(row["email_addresses"]):
                        paper_email_list = row["email_addresses"].split("; ")
                        llm_out = True if teacher_email in paper_email_list else False
                        if llm_out:
                            new_row = {
                                "teacher_id": teacher_id,
                                "paper_id": paper_id,
                                "author_order": author_order,
                                "is_corresponding_author": 1 if author_name in reprint_author else 0,
                                "high_true": 3,
                                "orcid": "",
                                "is_valid": 1,
                            }
                            batch_relation_list.append(new_row)
                            continue

                        project_str = teacher["project_experience"]
                        project = project_parse(project_str)

                        prompt_args = {
                            "title": row["title"],
                            "area": row["research_area"],
                            "keywords": row["keywords"],
                            "keywords_plus": row["keywords_plus"],
                            "description": omit_description,
                            "project": project,
                            "research_area": research_area,
                        }
                        llm_out = await self.llm.run(prompt_args)
                        if llm_out:
                            new_row = {
                                "teacher_id": teacher_id,
                                "paper_id": paper_id,
                                "author_order": author_order,
                                "is_corresponding_author": 1 if author_name in reprint_author else 0,
                                "high_true": 1,
                                "orcid": "",
                                "is_valid": 1,
                            }
                            batch_relation_list.append(new_row)
                            continue
                        # 仅姓名变体匹配，模型判断未通过
                        new_row = {
                            "teacher_id": teacher_id,
                            "paper_id": paper_id,
                            "author_order": author_order,
                            "is_corresponding_author": 1 if author_name in reprint_author else 0,
                            "high_true": -1,
                            "orcid": "",
                            "is_valid": 0,
                        }
                        batch_relation_list.append(new_row)

        return batch_relation_list

    async def run(self):
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})

        await self.db.set_up_async_db_engine()

        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        df = self.db.get_paper_by_id_range(self.task_args["id_start"], self.task_args["id_end"])
        self.logger.info(f"【{self.task_type}】: 数据读取完成", extra={"event": "db_read_end"})

        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        output_data = await self.process(df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})

        # 数据入库
        self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={"event": "db_insert_start"})
        db_input_data = {"file": output_data}
        self.db.run(db_input_data)
        self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={"event": "db_insert_end"})

        # ES需要手动关闭
        await self.es.close_es_engine()
        await self.db.close_async_db_engine()


@start_consumer(
    listen_queues=["queue.new_wos_paper_added_pipeline.crawl_paper.paper_match"],
    send_queues=[],
)
async def main(message) -> dict:
    args = message[0]
    processor = NewPaperMatchRunProcessor(args)
    await processor.run()

    return args

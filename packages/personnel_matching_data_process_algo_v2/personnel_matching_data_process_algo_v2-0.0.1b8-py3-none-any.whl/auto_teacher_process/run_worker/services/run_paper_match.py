import sys

sys.path.append("/home/personnel-matching-data-process-algo")

import pandas as pd

from auto_teacher_process.db.services.db_insert_paper_match import PaperInsertDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.llm.services.llm_paper_match import PaperMatchLLMProcessor
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.mq.consumer import start_consumer
from auto_teacher_process.run_worker.run_base import BaseRunProcessor
from auto_teacher_process.utils.match_utils import get_teacher_past_schools
from auto_teacher_process.utils.name_utils import get_name_variants
from auto_teacher_process.utils.paper_utils import judge_affiliation_match, project_parse


class PaperMatchRunProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_teacher_data_processing_pipeline"  # 流水线名称
        self.task_type = "paper_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "teacher_id"  # 数据主键字段
        self.set_file_paths()
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)

        self.db = PaperInsertDBProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)
        self.llm = PaperMatchLLMProcessor(logger=self.logger)

        self.school_cn_en_dict = self.db.get_school_name_dict()

    async def process_row(self, row: pd.Series) -> list | dict | None:
        teacher_id = row.teacher_id
        # 检查是否已经处理过该教师
        if teacher_id in self.processed_ids:
            return None  # 跳过已处理的教师

        derived_teacher_name = row.derived_teacher_name
        # college_name = row.college_name
        omit_description = row.omit_description
        project_experience = row.project_experience
        research_area = row.research_area
        teacher_email = row.email
        school_name = row.school_name
        project = project_parse(project_experience)

        teacher_name_variants = list(get_name_variants(derived_teacher_name))

        # 教师过往经历学校查询：input: teacher_id; output: school_names
        past_schools_cn_list = await get_teacher_past_schools(
            db=self.db, teacher_id=teacher_id, school_name=school_name
        )
        past_schools_en_list = [self.school_cn_en_dict.get(school, school).lower() for school in past_schools_cn_list]

        # TODO: ES 获取教师相关的论文
        teacher_papers = await self.es.async_es_to_df_by_author_and_affiliation_idx_paper(
            author=teacher_name_variants, affiliation=past_schools_en_list
        )

        if teacher_papers is None:
            return None  # 如果没有相关论文，跳过

        batch_relation_list = []

        for _, data in teacher_papers.iterrows():
            data["reprint_addresses"] = (
                data["reprint_addresses"]
                if data["reprint_addresses"] is not None and isinstance(data["reprint_addresses"], str)
                else ""
            )

            if data["author_list"] is None or pd.isna(data["author_list"]):
                continue
            if data["addresses"] is None or pd.isna(data["addresses"]):
                continue

            # TODO：判断该教师在论文中的机构是否匹配，若匹配则进行论文挂载，get_reprint_author，author_order
            is_school_match, author_order, is_corresponding_author = judge_affiliation_match(
                data, past_schools_en_list, teacher_name_variants
            )

            if is_school_match:
                # 邮箱判断
                if not pd.isna(teacher_email) and not pd.isna(data["email_addresses"]):
                    paper_email_list = data["email_addresses"].split("; ")
                    llm_out = True if teacher_email in paper_email_list else False
                    if llm_out:
                        new_row = {
                            "teacher_id": teacher_id,
                            "paper_id": data["id"],
                            "author_order": author_order,
                            "is_corresponding_author": is_corresponding_author,
                            "high_true": 3,
                            "orcid": "",
                            "is_valid": 1,
                        }
                        batch_relation_list.append(new_row)
                        continue

                prompt_args = {
                    "title": data["title"],
                    "area": data["research_area"],
                    "keywords": data["keywords"],
                    "keywords_plus": data["keywords_plus"],
                    "description": omit_description,
                    "project": project,
                    "research_area": research_area,
                }
                llm_out = await self.llm.run(prompt_args)

                if llm_out:
                    new_row = {
                        "teacher_id": teacher_id,
                        "paper_id": data["id"],
                        "author_order": author_order,
                        "is_corresponding_author": is_corresponding_author,
                        "high_true": 1,
                        "orcid": "",
                        "is_valid": 1,
                    }
                    batch_relation_list.append(new_row)
                    continue
                # 仅姓名变体匹配，模型判断未通过
                new_row = {
                    "teacher_id": teacher_id,
                    "paper_id": data["id"],
                    "author_order": author_order,
                    "is_corresponding_author": is_corresponding_author,
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
        df = self.db.get_paper_teacher_data_from_db(
            id_start=self.task_args["id_start"], id_end=self.task_args["id_end"]
        )
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
    listen_queues=["queue.teacher_added_pipeline.run_info.paper_match"],
    send_queues=["queue.teacher_added_pipeline.paper_match.patent_match"],
)
async def main(message) -> dict:
    args = message[0]
    processor = PaperMatchRunProcessor(args)
    await processor.run()

    return args

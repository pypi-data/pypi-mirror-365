import sys

sys.path.append("/home/personnel-matching-data-process-algo")

import pandas as pd

from auto_teacher_process.db.services.db_google_match import GoogleMatchDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.llm.services.llm_gogle_match import NameSeparationLLMProcessor
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.mq.consumer import start_consumer
from auto_teacher_process.run_worker.run_base import BaseRunProcessor
from auto_teacher_process.utils.name_utils import get_name_variants
from auto_teacher_process.utils.text_utils import contains_chinese


class GooglePageMatchProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_teacher_data_processing_pipeline"  # 流水线名称
        self.task_type = "google_paper_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "teacher_id"  # 数据主键字段
        self.set_file_paths()
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)
        self.llm = NameSeparationLLMProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)
        self.db = GoogleMatchDBProcessor(logger=self.logger)
        self.school_en_cn_dict = self.get_school_name_dict()

    def get_school_name_dict(self) -> dict[str, str]:
        school_df = self.db.get_all_intl_school_info()
        school_names = school_df["school_name"]
        school_names_en = school_df["school_name_en"]
        return dict(zip(school_names_en, school_names, strict=False))

    async def process_row(self, row: pd.Series) -> list | dict | None:
        if row.teacher_id in self.processed_ids:
            return None
        row_dict = row.to_dict()
        google_id = row_dict["google_id"]
        teacher_id = row_dict["teacher_id"]
        inter_papers_len = row_dict["inter_papers_len"]
        if inter_papers_len == 0:
            return None
        df_google_paper = await self.db.fetch_google_paper_async(google_id)
        df_teacher = await self.db.fetch_teacher_data_async(teacher_id)
        en_name = df_teacher["en_name"]

        if contains_chinese(en_name):
            try:
                llm_result, is_valid = await self.llm.run({"en_name": en_name})
                row_dict["english_name"] = llm_result["english_name"]
                row_dict["chinese_name"] = llm_result["chinese_name"]
                en_name = llm_result["english_name"] or ""
            except Exception as e:
                self.logger.warning(f"LLM调用失败: {en_name} -> {e}")
                row_dict["english_name"] = None
                row_dict["chinese_name"] = None
        else:
            row_dict["english_name"] = en_name
            row_dict["chinese_name"] = None

        name_variants = list(get_name_variants(en_name))
        batch_relation_list = []

        for _, paper in df_google_paper.iterrows():
            paper_title = paper["title"]
            if not isinstance(paper_title, str) or paper_title.strip() == "" or paper_title == "...":
                continue
            papers_df = await self.es.async_es_to_df_by_title_idx_paper(title=paper_title)
            if papers_df is None:
                continue

            for _, paper_info in papers_df.iterrows():
                paper_id = paper_info["id"]
                if pd.isna(paper_info["author_list"]):
                    continue
                author_list = paper_info["author_list"].split("; ")
                title = paper["title"]
                for i, author in enumerate(author_list):
                    if author.lower() in name_variants:
                        batch_relation_list.append(
                            {
                                "paper_id": paper_id,
                                "teacher_id": teacher_id,
                                "teacher_name": en_name,
                                "author_name": author,
                                "author_order": i + 1,
                                "title": title,
                            }
                        )
                        break

        return batch_relation_list

    async def run(self) -> None:
        await self.db.set_up_async_db_engine()
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        df = self.db.get_google_teacher_relation_from_db(
            id_start=self.task_args["id_start"], id_end=self.task_args["id_end"]
        )
        self.logger.info(f"【{self.task_type}】: 数据读取完成", extra={"event": "db_read_end"})

        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        # output_data = await self.process(df)
        await self.process(df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})

        # # ES需要手动关闭
        await self.es.close_es_engine()
        await self.db.close_async_db_engine()
        # # 数据入库
        # self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={'event': 'db_insert_start'})
        # db_input_data = {
        #     'file': output_data
        # }
        # self.db.run(db_input_data)
        # self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={'event': 'db_insert_end'})


@start_consumer(
    listen_queues=["queue.teacher_added_pipeline.crawl.run_name"],
    send_queues=["queue.teacher_added_pipeline.run_name.run_info"],
)
async def main(message) -> dict:
    processor = GooglePageMatchProcessor(message[0])
    await processor.run()

    return {
        "task_id": "T123",
        "task_args": {
            "id_start": 1,
            "id_end": 10,
        },
    }

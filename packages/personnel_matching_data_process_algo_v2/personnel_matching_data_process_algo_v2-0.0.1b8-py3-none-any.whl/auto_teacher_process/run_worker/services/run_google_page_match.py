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
from auto_teacher_process.utils.text_utils import contains_chinese, normalize_title


class GooglePageMatchRunProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_teacher_data_processing_pipeline"  # 流水线名称
        self.task_type = "google_page_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "u_id"  # 数据主键字段
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
        if row.u_id in self.processed_ids:
            return None
        row_dict = row.to_dict()
        en_name = row_dict["author_list"]
        school_name_en = row_dict["school_name"]
        google_id = row_dict["u_id"]

        if pd.isna(en_name) or pd.isna(school_name_en):
            return None

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

        teacher_name_variants = list(get_name_variants(en_name))

        df_teacher = await self.es.async_es_to_df_by_teacher_and_school_name_idx_teacher_data(
            teacher=teacher_name_variants, school_name=self.school_en_cn_dict[school_name_en]
        )

        if df_teacher is None:
            return None

        save_list = []

        df_google_paper = await self.db.fetch_google_paper_async(google_id)
        google_papers = df_google_paper["title"].tolist()
        google_papers = set(normalize_title(s) for s in google_papers if isinstance(s, str))

        for _, teacher_row in df_teacher.iterrows():
            teacher_id = teacher_row["teacher_id"]
            teacher_name = teacher_row["derived_teacher_name"]
            # 查询教师数据库论文
            df_teacher_paper = await self.db.fetch_papers_by_teacher_id_async(teacher_id)
            df_teacher_paper_filtered = df_teacher_paper[
                (df_teacher_paper["high_true"].isin([3, 4])) & df_teacher_paper["title"].notna()
            ]

            teacher_papers_db = set(
                normalize_title(s) for s in df_teacher_paper_filtered["title"].tolist() if isinstance(s, str)
            )

            # Step 6: 求交集
            inter_paper = list(google_papers & teacher_papers_db)

            new_row = {
                "google_id": google_id,
                "teacher_id": teacher_id,
                "teacher_name": teacher_name,
                "len_google_papers": len(google_papers),
                "len_db_papers": len(teacher_papers_db),
                "len_inter_papers": len(inter_paper),
            }

            save_list.append(new_row)

        return save_list

    async def run(self) -> None:
        await self.db.set_up_async_db_engine()
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        df = self.db.get_google_teacher_data_from_db(
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

        # # ES需要手动关闭
        await self.es.close_es_engine()
        await self.db.close_async_db_engine()


@start_consumer(
    listen_queues=["queue.teacher_added_pipeline.crawl.run_name"],
    send_queues=["queue.teacher_added_pipeline.run_name.run_info"],
)
async def main(message) -> dict:
    processor = GooglePageMatchRunProcessor(message[0])
    await processor.run()

    return {
        "task_id": "T123",
        "task_args": {
            "id_start": 1,
            "id_end": 10,
        },
    }

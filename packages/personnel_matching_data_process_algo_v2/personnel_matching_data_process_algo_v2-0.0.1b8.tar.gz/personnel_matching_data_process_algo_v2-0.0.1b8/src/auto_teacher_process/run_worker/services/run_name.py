import sys

sys.path.append("/home/personnel-matching-data-process-algo")

import pandas as pd

from auto_teacher_process.db.services.db_insert_name import NameInsertDBProcessor
from auto_teacher_process.llm.services.llm_name import NameLLMProcessor
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.mq.consumer import start_consumer
from auto_teacher_process.run_worker.run_base import BaseRunProcessor
from auto_teacher_process.utils.text_utils import PROVINCE_CODE_DICT, contains_chinese, judge_en


class RunNameProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_teacher_data_processing_pipeline"  # 流水线名称
        self.task_type = "name_extract"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "raw_data_id"  # 数据主键字段
        self.set_file_paths()
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)
        self.llm = NameLLMProcessor()
        self.llm.logger = self.logger
        self.db = NameInsertDBProcessor()
        self.db.logger = self.logger

    async def process_row(self, row: pd.Series) -> dict | None:
        if row.id in self.processed_ids:
            return None

        teacher_name = row.teacher_name
        description = str(row.description).replace("?", "")
        is_en = judge_en(description)
        province_code = PROVINCE_CODE_DICT.get(row.province, -1)

        # LLM 处理姓名提取
        extract_name, is_valid = await self.llm.run({"teacher_name": teacher_name})
        extract_name = extract_name.strip()

        if is_valid and contains_chinese(extract_name):
            extract_name = extract_name.replace(" ", "")

        return {
            "raw_data_id": row.id,
            "raw_teacher_name": teacher_name,
            "derived_teacher_name": extract_name,
            "province": row.province,
            "school_name": row.school_name,
            "college_name": row.college_name,
            "description": description,
            "status": 0,
            "is_valid": is_valid,
            "is_en": is_en,
            "province_code": province_code,
        }

    async def run(self) -> None:
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        df = self.db.get_raw_teacher_data_from_db(self.task_args["id_start"], self.task_args["id_end"])
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


@start_consumer(
    listen_queues=["queue.teacher_added_pipeline.crawl.run_name"],
    send_queues=["queue.teacher_added_pipeline.run_name.run_info"],
)
async def main(message) -> dict:
    args = message[0]
    processor = RunNameProcessor(args)
    await processor.run()

    return args

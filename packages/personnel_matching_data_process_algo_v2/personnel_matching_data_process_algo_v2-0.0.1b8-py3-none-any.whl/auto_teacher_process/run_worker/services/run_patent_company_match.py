import pandas as pd

from auto_teacher_process.db.services.db_insert_patent_match import PatentInsertDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.llm.services.llm_patent_match import PatentMatchLLMProcessor
from auto_teacher_process.run_worker.run_base import BaseRunProcessor


class NewPatentMatchProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_patent_data_processing_pipeline"  # 流水线名称
        self.task_type = "new_company_patent_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "patent_id"  # 数据主键字段
        self.db = PatentInsertDBProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)
        self.llm = PatentMatchLLMProcessor(logger=self.logger)

    async def process_row(self, patent_info: pd.Series):
        batch_relation_list = []
        patent_id = patent_info["id"]
        # 缓存中已存在的数据不再处理
        if patent_id in self.processed_ids:
            return None  # 跳过已处理的专利
        patent_info = patent_info.to_dict()

        applicant = patent_info["applicant"]

        return batch_relation_list

    async def run(self):
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})

        patent_df = self.db.get_raw_teacher_patent_from_db(self.task_args["id_start"], self.task_args["id_end"])
        self.logger.info(f"【{self.task_type}】: 数据读取完成", extra={"event": "db_read_end"})

        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        output_data = await self.process(patent_df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})

        # ES需要手动关闭
        await self.es.close_es_engine()

        # 数据入库
        self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={"event": "db_insert_start"})
        db_input_data = {"file": output_data}
        self.db.run(db_input_data)
        self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={"event": "db_insert_end"})

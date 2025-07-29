import pandas as pd

import auto_teacher_process.db.services.db_associated_teacher_leader as db_associated_teacher_leader
import auto_teacher_process.llm.services.llm_associated_teacher_leader as llm_associated_teacher_leader
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.run_worker.run_base import BaseRunProcessor


class RunTeacherLeaderAssociatedProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_teacher_data_processing_pipeline"  # 流水线名称
        self.task_type = "name_extract"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "raw_data_id"  # 数据主键字段
        self.set_file_paths()
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)
        self.db = db_associated_teacher_leader.TeacherLeaderAssociatedProcessor(logger=self.logger)
        self.llm = llm_associated_teacher_leader.TeacherLeaderAssociatedProcessor(logger=self.logger)

    async def process_row(self, row):
        result = await self.llm.run({"df": pd.DataFrame([row])})
        return result

    async def run(self) -> None:
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        df = self.db.get_teacher_leader_group(self.task_args["school_name"])
        self.logger.info(f"【{self.task_type}】: 数据读取完成，共{len(df)}行", extra={"event": "db_read_end"})

        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        output_data = await self.process(df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})

        # 数据入库
        # 保存为csv测试
        self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={"event": "db_insert_start"})
        # output_data.to_csv('auto_teacher_process/run_worker/test_result.csv')
        self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={"event": "db_insert_end"})

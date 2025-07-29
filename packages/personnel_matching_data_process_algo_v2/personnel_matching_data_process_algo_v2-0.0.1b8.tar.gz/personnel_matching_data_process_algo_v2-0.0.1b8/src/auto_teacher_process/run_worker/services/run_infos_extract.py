import asyncio
import sys

sys.path.append("/home/personnel-matching-data-process-algo")

import pandas as pd

from auto_teacher_process.db.services.db_insert_infos import InfoInsertDBProcessor
from auto_teacher_process.llm.services.llm_area import AreaLLMProcessor
from auto_teacher_process.llm.services.llm_des_paper import DesPaperLLMProcessor
from auto_teacher_process.llm.services.llm_email import EmailLLMProcessor
from auto_teacher_process.llm.services.llm_experience import ExperienceLLMProcessor
from auto_teacher_process.llm.services.llm_famous import FamousLLMProcessor
from auto_teacher_process.llm.services.llm_omit import OmitLLMProcessor
from auto_teacher_process.llm.services.llm_position import PositionLLMProcessor
from auto_teacher_process.llm.services.llm_project import ProjectLLMProcessor
from auto_teacher_process.llm.services.llm_title import TitleLLMProcessor
from auto_teacher_process.llm.services.llm_translate import TranslateLLMProcessor
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.mq.consumer import start_consumer
from auto_teacher_process.run_worker.run_base import BaseRunProcessor


class TeacherInfoProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_teacher_data_processing_pipeline"  # 流水线名称
        self.task_type = "infos_extract"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "teacher_id"  # 数据主键字段
        self.need_en = 0  # 是否需要英文翻译，1表示需要，0表示不需要
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)
        self.set_file_paths()

        self.translate_llm = TranslateLLMProcessor(logger=self.logger)
        self.omit_llm = OmitLLMProcessor(logger=self.logger)
        self.area_llm = AreaLLMProcessor(logger=self.logger)
        self.project_llm = ProjectLLMProcessor(logger=self.logger)
        self.email_llm = EmailLLMProcessor(logger=self.logger)
        self.title_llm = TitleLLMProcessor(logger=self.logger)
        self.famous_llm = FamousLLMProcessor(logger=self.logger)
        self.position_llm = PositionLLMProcessor(logger=self.logger)
        self.experience_llm = ExperienceLLMProcessor(logger=self.logger)
        self.paper_llm = DesPaperLLMProcessor(logger=self.logger)
        self.db = InfoInsertDBProcessor(logger=self.logger)

    async def process_row(self, row: pd.Series) -> dict | None:
        teacher_id = row.teacher_id
        teacher_name = row.derived_teacher_name
        ori_description = row.description
        if pd.isna(ori_description):
            ori_description = "无"
        is_en = row.is_en

        # 检查是否已经处理过该教师
        if teacher_id in self.processed_ids:
            return None  # 跳过已处理的教师
        data = {
            "teacher_id": teacher_id,
            "teacher_name": teacher_name,
            "description": ori_description,
            "is_en": is_en,
            "mode": "en" if is_en == 1 else "cn",
        }

        if is_en == 1 and self.need_en == 1:
            ori_description_cn, trans_valid = await self.translate_llm.run(data)
            if trans_valid == 1:
                ori_description = ori_description_cn
                data["description"] = ori_description  # 更新为翻译后的内容
        # 并发其他 LLM 请求

        results = await asyncio.gather(
            self.omit_llm.run(data),
            self.area_llm.run(data),
            self.project_llm.run(data),
            self.email_llm.run(data),
            self.title_llm.run(data),
            self.famous_llm.run(data),
            self.position_llm.run(data),
            self.experience_llm.run(data),
            self.paper_llm.run(data),
        )

        (
            (extracted_omit, omit_valid),
            (extracted_area, area_valid),
            (extracted_project, project_valid),
            (extracted_email, email_valid),
            (extracted_title, normalized_title, title_valid),
            (extracted_famous, normalized_famous, famous_valid),
            (extracted_position, position_valid),
            (work_data, edu_data, experience_valid),
            (papers, paper_valid),
        ) = results

        new_row = {
            "teacher_id": teacher_id,
            "is_en": is_en,
            "ori_description": ori_description if is_en == 1 else "",
            "omit_description": extracted_omit,
            "omit_valid": omit_valid,
            "research_area": extracted_area,
            "area_valid": area_valid,
            "email": extracted_email,
            "email_valid": email_valid,
            "project_experience": extracted_project,
            "project_valid": project_valid,
            "title": extracted_title,
            "normalized_title": normalized_title,
            "title_valid": title_valid,
            "famous_titles": extracted_famous,
            "normalized_famous_titles": normalized_famous,
            "famous_valid": famous_valid,
            "position": extracted_position,
            "position_valid": position_valid,
            "education": work_data,
            "work": edu_data,
            "experience_valid": experience_valid,
            "paper_list": papers,
            "paper_valid": paper_valid,
        }

        return new_row

    async def run(self) -> None:
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        df = self.db.get_derived_teacher_data_from_db(self.task_args["id_start"], self.task_args["id_end"])
        self.logger.info(f"【{self.task_type}】: 数据读取完成", extra={"event": "db_read_end"})

        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        await self.process(df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})

        # 数据入库
        self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={"event": "db_insert_start"})
        # db_input_data = {
        #     'file': output_data
        # }
        # self.db.run(db_input_data)
        self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={"event": "db_insert_end"})


@start_consumer(
    listen_queues=["queue.teacher_added_pipeline.run_name.run_info"],
    send_queues=[
        "queue.teacher_added_pipeline.run_info.des_paper_match",
        "queue.teacher_added_pipeline.run_info.paper_match",
        "queue.teacher_added_pipeline.run_info.cn_paper_match",
        "queue.teacher_added_pipeline.run_info.project_match",
    ],
)
async def main(message) -> dict:
    args = message[0]
    processor = TeacherInfoProcessor(args)
    await processor.run()

    return args

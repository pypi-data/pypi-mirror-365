import pandas as pd

from auto_teacher_process.db.services.db_insert_des_paper import DesPaperInsertDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.mq.consumer import start_consumer
from auto_teacher_process.run_worker.run_base import BaseRunProcessor
from auto_teacher_process.utils.name_utils import get_name_variants


class DesPaperMatchRunProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_teacher_data_processing_pipeline"  # 流水线名称
        self.task_type = "des_paper_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "teacher_id"  # 数据主键字段
        self.set_file_paths()
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)

        self.db = DesPaperInsertDBProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)

    async def process_row(self, row: pd.Series) -> list | dict | None:
        teacher_id = row.teacher_id
        teacher_name = row.derived_teacher_name
        # 检查是否已经处理过该教师
        if teacher_id in self.processed_ids:
            return None  # 跳过已处理的教师
        try:
            papers = eval(row.papers)  # 替换为 ast.literal_eval(row.papers) 更安全
        except Exception:
            # print(f"论文字段解析失败：{teacher_id}, 错误: {e}")
            return None

        name_variants = get_name_variants(teacher_name)

        paper_titles = []
        for title in papers:
            if not isinstance(title, str) or title.strip() == "" or title == "...":
                # print(f"无效的论文标题: {paper_title}")
                continue
            paper_titles.append(title.strip().lower())
        if not paper_titles:
            return None

        papers_df = await self.es.async_es_to_df_by_title_idx_paper(title=paper_titles)
        if papers_df is None:
            return None

        batch_relation_list = []
        for _, paper_info in papers_df.iterrows():
            paper_id = paper_info["id"]
            if pd.isna(paper_info["author_list"]):
                continue
            author_list = paper_info["author_list"].split("; ")
            title = paper_info["title"]
            for i, author in enumerate(author_list):
                if author.lower() in name_variants:
                    batch_relation_list.append(
                        {
                            "paper_id": paper_id,
                            "teacher_id": teacher_id,
                            "teacher_name": teacher_name,
                            "author_name": author,
                            "author_order": i + 1,
                            "title": title,
                        }
                    )
                    break

        return batch_relation_list

    async def run(self):
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        df = self.db.get_teacher_des_paper_data(id_start=self.task_args["id_start"], id_end=self.task_args["id_end"])
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
    listen_queues=["queue.teacher_added_pipeline.run_info.des_paper_match"],
    send_queues=["queue.teacher_added_pipeline.des_paper_match.patent_match"],
)
async def main(message) -> dict:
    args = message[0]
    processor = DesPaperMatchRunProcessor(args)
    await processor.run()

    return args

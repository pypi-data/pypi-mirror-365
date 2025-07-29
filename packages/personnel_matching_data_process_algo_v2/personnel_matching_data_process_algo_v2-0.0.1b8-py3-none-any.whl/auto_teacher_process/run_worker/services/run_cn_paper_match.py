import pandas as pd

from auto_teacher_process.db.services.db_insert_cn_paper_match import CNPaperMatchInsertDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.llm.services.llm_cn_paper_match import CNPaperMatchLLMProcessor
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.mq.consumer import start_consumer
from auto_teacher_process.run_worker.run_base import BaseRunProcessor
from auto_teacher_process.utils.cn_paper_utils import (
    judge_cn_paper_affiliation_match,
)
from auto_teacher_process.utils.match_utils import get_teacher_past_schools
from auto_teacher_process.utils.name_utils import get_name_variants
from auto_teacher_process.utils.paper_utils import project_parse


class CNPaperMatchRunProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_teacher_data_processing_pipeline"  # 流水线名称
        self.task_type = "cn_paper_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "teacher_id"  # 数据主键字段
        self.set_file_paths()
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)

        self.db = CNPaperMatchInsertDBProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)
        self.llm = CNPaperMatchLLMProcessor(logger=self.logger)

        self.school_cn_en_dict = self.db.get_school_name_dict()

    def check_paper_author_overlap(self, teacher_id, full_name_list) -> bool:
        paper_author_df = self.db.get_teacher_paper_author_list(teacher_id=teacher_id)

        if paper_author_df.empty:
            return False  # 如果没有论文作者信息，直接返回 False

        # 将 paper_author_df的author_list列转换为列表
        paper_author_str_list = paper_author_df["author_list"].tolist()
        for author_str in paper_author_str_list:
            if author_str is None or pd.isna(author_str):
                continue
            paper_author = author_str.split("; ")
            # 每篇论文的作者列表
            match_count = 0
            for author in full_name_list:  # 张三，李四，王五
                pinyin_set = get_name_variants(author)
                for en_auth in paper_author:  # Wang, Yongkang; Li, Qiankun; Qu, Lunjun; Huang, Jiayue; Zhu, Ying;
                    en_auth = en_auth.lower()
                    if en_auth in pinyin_set:
                        match_count += 1
                        # 如果匹配到两个以上的作者，则认为是匹配成功
                        if match_count > 2:
                            return True
                        break
        return False

    async def process_row(self, row: pd.Series):
        # 以教师为单位进行处理
        teacher_id = row.teacher_id
        # 检查是否已经处理过该教师
        if teacher_id in self.processed_ids:
            return None  # 跳过已处理的教师

        derived_teacher_name = row.derived_teacher_name
        omit_description = row.omit_description
        project_experience = row.project_experience
        research_area = row.research_area
        school_name = row.school_name
        college_name = row.college_name
        project = project_parse(project_experience)

        # 教师过往经历学校查询：input: teacher_id; output: school_names
        past_schools_cn_list = await get_teacher_past_schools(db=self.db, teacher_id=teacher_id, school_name=school_name)
        past_schools_en_list = [self.school_cn_en_dict.get(school, school).lower() for school in past_schools_cn_list]
        past_schools_all = past_schools_cn_list + past_schools_en_list

        teacher_name_variants = get_name_variants(derived_teacher_name)

        # TODO: ES 获取教师相关的中文论文
        teacher_cn_papers = await self.es.async_es_to_df_by_full_author_list_and_affiliation_idx_cn_paper(
            teacher_name_variants,
            past_schools_all
        )

        if teacher_cn_papers is None:
            return None  # 如果没有相关论文，跳过

        batch_relation_list = []

        for _, data in teacher_cn_papers.iterrows():
            paper_id = data["id"]
            full_authors = data["full_author_list"]
            addresses = data["addresses"]
            title = data["title"]
            keywords = data["keywords"]
            zhuanji = data["zhuanji"]
            zhuanti = data["zhuanti"]
            paper_email = data["email"]

            if pd.isna(full_authors) or pd.isna(addresses):
                continue  # 跳过没有作者的专利

            full_authors_list = full_authors.split("; ")

            # TODO：判断该教师在论文中的机构是否匹配，若匹配则进行论文挂载，get_reprint_author，author_order
            is_school_match, author_order = judge_cn_paper_affiliation_match(
                full_authors_list, addresses, school_name, teacher_name_variants
            )

            if is_school_match:
                # 检查专利作者和教师论文作者的交集是否大于2
                llm_out = self.check_paper_author_overlap(teacher_id, full_authors_list)

                if llm_out:
                    new_row = {
                        "teacher_id": teacher_id,
                        "paper_id": paper_id,
                        "author_order": author_order,
                        "high_true": 2,
                        "is_valid": 1,
                    }
                    batch_relation_list.append(new_row)
                    continue

                data = {
                    "mode": "high",
                    "title": title,
                    "keywords": keywords,
                    "zhuanji": zhuanji,
                    "zhuanti": zhuanti,
                    "college": college_name,
                    "description": omit_description,
                    "project": project,
                    "research": research_area,
                }

                llm_out = await self.llm.run(data)

                if llm_out:
                    new_row = {
                        "teacher_id": teacher_id,
                        "paper_id": paper_id,
                        "author_order": author_order,
                        "high_true": 1,
                        "is_valid": 1,
                    }
                    batch_relation_list.append(new_row)
                    continue
                # 如果没有匹配成功，仍然需要记录下来
                new_row = {
                    "teacher_id": teacher_id,
                    "paper_id": paper_id,
                    "author_order": author_order,
                    "high_true": -1,
                    "is_valid": 0,
                }
                batch_relation_list.append(new_row)

        return batch_relation_list

    async def run(self):
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        df = self.db.get_cn_paper_teacher_data_from_db(
            id_start=self.task_args["id_start"], id_end=self.task_args["id_end"]
        )
        self.logger.info(f"【{self.task_type}】: 数据读取完成", extra={"event": "db_read_end"})

        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        output_data = await self.process(df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})

        # ES需要手动关闭
        await self.es.close_es_engine()

        # 数据入库
        self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={"event": "db_insert_start"})
        db_input_data = {"file": output_data}
        self.db.run(db_input_data)
        self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={"event": "db_insert_end"})


@start_consumer(
    listen_queues=["queue.teacher_added_pipeline.run_info.cn_paper_match"],
    send_queues=[],
)
async def main(message) -> dict:
    args = message[0]
    processor = CNPaperMatchRunProcessor(args)
    await processor.run()

    return args

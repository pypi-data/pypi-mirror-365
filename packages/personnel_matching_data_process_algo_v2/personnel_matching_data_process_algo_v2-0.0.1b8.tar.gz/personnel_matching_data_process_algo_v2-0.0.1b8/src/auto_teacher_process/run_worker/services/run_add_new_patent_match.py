import pandas as pd

from auto_teacher_process.db.services.db_insert_patent_match import PatentInsertDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.llm.services.llm_patent_match import PatentMatchLLMProcessor
from auto_teacher_process.run_worker.run_base import BaseRunProcessor
from auto_teacher_process.utils.match_utils import select_teacher_by_past_schools
from auto_teacher_process.utils.name_utils import chinese_name_to_pinyin
from auto_teacher_process.utils.paper_utils import project_parse
from auto_teacher_process.utils.patent_utils import extract_matched_schools_from_applicant


class NewPatentMatchProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_patent_data_processing_pipeline"  # 流水线名称
        self.task_type = "new_add_patent_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "patent_id"  # 数据主键字段
        self.db = PatentInsertDBProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)
        self.llm = PatentMatchLLMProcessor(logger=self.logger)
        self.school_cn_list = self.get_school_cn_name_list()

    def get_school_cn_name_list(self):
        school_df = self.db.get_all_school_info()
        school_names = school_df["school_name"]
        return list(school_names)

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
                pinyin_set = chinese_name_to_pinyin(author)
                for en_auth in paper_author:  # Wang, Yongkang; Li, Qiankun; Qu, Lunjun; Huang, Jiayue; Zhu, Ying;
                    en_auth = en_auth.lower()
                    if en_auth in pinyin_set:
                        match_count += 1
                        # 如果匹配到两个以上的作者，则认为是匹配成功
                        if match_count > 2:
                            return True
                        break
        return False

    async def process_row(self, patent_info: pd.Series):
        batch_relation_list = []
        patent_id = patent_info["id"]
        # 缓存中已存在的数据不再处理
        if patent_id in self.processed_ids:
            return None  # 跳过已处理的专利
        patent_info = patent_info.to_dict()

        full_name_list = patent_info["inventor"].split(";")
        full_name_list = [name.strip() for name in full_name_list]

        patent_name, abstract = patent_info["invention_name"], patent_info["patent_abstract"]
        patent_field = patent_info["Technology_neighborhood"]

        school_list = extract_matched_schools_from_applicant(patent_info["applicant"], self.school_cn_list)

        if school_list is None:
            return None

        teacher_df = await self.es.async_es_to_df_by_teacher_idx_teacher_data(full_name_list)

        if teacher_df is None:
            return None

        matched_teacher_df = await select_teacher_by_past_schools(
            db=self.db, teacher_df=teacher_df, school_names_cn=school_list
        )
        for _, teacher in matched_teacher_df.iterrows():
            if teacher["school_name"] not in patent_info["applicant"]:
                continue
            derived_teacher_name = teacher["derived_teacher_name"]
            college_name, omit_description, research_area = (
                teacher["college_name"],
                teacher["omit_description"],
                teacher["research_area"],
            )
            teacher_id = teacher["teacher_id"]
            project_str = teacher["project_experience"]
            project = project_parse(project_str)

            # 检查专利作者和教师论文作者的交集是否大于2
            llm_out = self.check_paper_author_overlap(teacher_id, full_name_list)

            if llm_out:
                row = {
                    "teacher_id": teacher_id,
                    "patent_id": patent_id,
                    "author_order": full_name_list.index(derived_teacher_name) + 1,
                    "high_true": 2,
                    "is_valid": 1,
                }
                batch_relation_list.append(row)
                continue

            data = {
                "mode": "high",
                "patent_name": patent_name,
                "abstract": abstract,
                "field": patent_field,
                "college": college_name,
                "description": omit_description,
                "project": project,
                "research": research_area,
            }

            llm_out = await self.llm.run(data)

            if llm_out:
                row = {
                    "teacher_id": teacher_id,
                    "patent_id": patent_id,
                    "author_order": full_name_list.index(derived_teacher_name) + 1,
                    "high_true": 1,
                    "is_valid": 1,
                }
                batch_relation_list.append(row)
                continue
            # 如果没有匹配成功，仍然需要记录下来
            row = {
                "teacher_id": teacher_id,
                "patent_id": patent_id,
                "author_order": full_name_list.index(derived_teacher_name) + 1,
                "high_true": -1,
                "is_valid": 0,
            }
            batch_relation_list.append(row)

        return batch_relation_list

    async def run(self):
        await self.db.set_up_async_db_engine()
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
        await self.db.close_async_db_engine()
        # 数据入库
        self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={"event": "db_insert_start"})
        db_input_data = {"file": output_data}
        self.db.run(db_input_data)
        self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={"event": "db_insert_end"})

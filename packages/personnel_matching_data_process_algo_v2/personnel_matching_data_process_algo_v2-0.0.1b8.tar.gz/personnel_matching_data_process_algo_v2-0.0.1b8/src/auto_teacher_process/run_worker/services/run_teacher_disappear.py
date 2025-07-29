import sys

sys.path.append("/home/personnel-matching-data-process-algo")

import pandas as pd

from auto_teacher_process.db.services.db_teacher_disappear import TeacherDisappearDBProcessor
from auto_teacher_process.llm.services.llm_teacher_disappear import TeacherDisappearLLMProcessor
from auto_teacher_process.logger import setup_logger
from auto_teacher_process.run_worker.run_base import BaseRunProcessor


# 百度百科信息获取函数（占位）
def get_baike_info(teacher_name: str) -> list:
    """
    输入教师姓名，返回该教师的百度百科markdown页面列表（占位实现）。
    """
    # TODO: 实现百度百科信息抓取
    return []


class RunTeacherDisappearProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "teacher_disappear_pipeline"
        self.task_type = "teacher_disappear"
        self.task_status = "start"
        self.data_primary_key_field = "teacher_id"
        self.set_file_paths()
        self.logger = setup_logger(system=self.pipeline, stage=self.task_type)
        self.db = TeacherDisappearDBProcessor(logger=self.logger)
        self.llm = TeacherDisappearLLMProcessor(logger=self.logger)

    async def process_row(self, row: pd.Series) -> dict | None:
        teacher_id = row.teacher_id if "teacher_id" in row else row["teacher_id"]
        if teacher_id in self.processed_ids:
            return None
        # 1. 获取简介信息和link
        info = self.db.run({"type": "by_teacher_id", "teacher_id": teacher_id})
        self.logger.debug(f"info: {info}")
        if not info:
            raise ValueError(f"未找到teacher_id={teacher_id}的教师信息")
        name = info["derived_teacher_name"]
        school = info["school_name"]
        description = info["description"]
        link = info["link"]
        # 2. 判断link有效性（简单判断）
        is_link_valid = link and link.startswith("http")
        is_teacher_homepage = False
        if is_link_valid:
            # 3. 用LLM判断该link是否为该教师主页
            homepage_markdown = ""  # TODO: 这里应有网页内容抓取，暂留空
            llm_input = {
                "type": "homepage_match",
                "name": name,
                "profile": description,
                "homepage_markdown": homepage_markdown,
            }
            result, success = await self.llm.run(llm_input)
            self.logger.debug(f"result: {result}, success: {success}")
            is_teacher_homepage = result == "True" and success
        else:
            # 如果link无效，则不进行后续处理
            raise ValueError(f"link={link}无效")
        # 4. 如果不是该教师主页，获取百度百科信息
        baike_work_exps = []
        if not is_teacher_homepage:
            baike_markdowns = get_baike_info(name)
            if baike_markdowns:
                # 用LLM判断哪个百科页面属于该教师并提取工作经历
                llm_input = {
                    "type": "work_experience",
                    "name": name,
                    "profile": description,
                    "homepage_markdowns": baike_markdowns,
                }
                work_exp, success = await self.llm.run(llm_input)
                self.logger.debug(f"work_exp: {work_exp}, success: {success}")
                if success and isinstance(work_exp, list) and work_exp:
                    baike_work_exps = work_exp
                else:
                    # 如果工作经历为空，则不进行后续处理
                    raise ValueError("工作经历为空")
            else:
                # 如果百度百科信息为空，则不进行后续处理
                raise ValueError("百度百科信息为空")
        else:
            # 如果是教师主页，则不进行处理
            raise ValueError(f"link={link}为教师主页")
        # 5. 判断最新工作单位是否变更
        latest_unit = None
        if baike_work_exps:
            latest_unit = baike_work_exps[-1].get("单位")
        unit_changed = latest_unit and latest_unit != school
        # 6. 如果变更，则用教师名和新单位检索数据库
        matched_teacher = None
        if unit_changed:
            # 将旧教师信息设为无效
            self.db.run({"type": "set_invalid_by_teacher_id", "teacher_id": teacher_id})
            # 用教师名和新单位检索数据库
            desc_list = self.db.run(
                {"type": "by_name_and_school", "derived_teacher_name": name, "school_name": latest_unit}
            )
            for desc_item in desc_list:
                db_desc = desc_item["description"]
                llm_input = {"type": "is_same_teacher", "des1": description, "des2": db_desc}
                is_same, success = await self.llm.run(llm_input)
                self.logger.debug(f"is_same: {is_same}, success: {success}")
                if is_same == "True" and success:
                    matched_teacher = desc_item
                    break
        else:
            # 如果未变更，则不进行后续处理
            raise ValueError("未变更")
        return {
            "teacher_id": teacher_id,
            "name": name,
            "origin_school": school,
            "origin_description": description,
            "origin_link": link,
            "is_teacher_homepage": is_teacher_homepage,
            "baike_work_exps": baike_work_exps,
            "latest_unit": latest_unit,
            "unit_changed": unit_changed,
            "matched_teacher": matched_teacher,
        }

    async def run(self) -> None:
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})
        # 假设输入为teacher_id列表
        teacher_ids = self.task_args.get("teacher_ids", [])
        df = pd.DataFrame({"teacher_id": teacher_ids})
        self.logger.info(f"【{self.task_type}】: 数据读取完成，共{len(df)}条", extra={"event": "db_read_end"})
        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        output_data = await self.process(df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})
        # 可选：结果入库或保存
        # self.db.save_disappear_result(output_data)


# 如需集成消息队列消费，可参考run_name.py的main函数装饰器

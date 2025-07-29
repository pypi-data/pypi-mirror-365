import pandas as pd
import pytest

import auto_teacher_process.run_worker.services.run_teacher_disappear as disappear_mod
from auto_teacher_process.run_worker.services.run_teacher_disappear import RunTeacherDisappearProcessor

pytestmark = pytest.mark.asyncio


class DummyDB:
    def run(self, input_data):
        if input_data["type"] == "by_teacher_id":
            return {
                "derived_teacher_name": "张三",
                "school_name": "清华大学",
                "description": "张三，男，清华大学教授。",
                "link": "http://example.com/zhangsan",
            }
        if input_data["type"] == "by_name_and_school":
            return [
                {"derived_teacher_name": "张三", "school_name": "北京大学", "description": "张三，男，北京大学教授。"}
            ]
        return {}


class DummyLLM:
    async def run(self, input_data):
        if input_data["type"] == "homepage_match":
            return "False", True
        if input_data["type"] == "work_experience":
            return [
                {"时间": "2010-2015", "单位": "清华大学", "职位": "讲师"},
                {"时间": "2015-2024", "单位": "北京大学", "职位": "教授"},
            ], True
        if input_data["type"] == "is_same_teacher":
            return "True", True
        return "", False


class DummyArgs:
    def __init__(self):
        self.task_id = 1
        self.task_args = {"teacher_ids": [123]}
        self.save_dir = "./tmp/"


@pytest.fixture
def processor(monkeypatch):
    args = DummyArgs()
    proc = RunTeacherDisappearProcessor(args)
    proc.db = DummyDB()
    proc.llm = DummyLLM()
    # mock get_baike_info 返回非空markdown列表
    monkeypatch.setattr(disappear_mod, "get_baike_info", lambda name: ["dummy_markdown"])
    return proc


async def test_process_row_main_flow(processor):
    row = pd.Series({"teacher_id": 123})
    result = await processor.process_row(row)
    processor.logger.info(f"result: {result}")
    assert result["teacher_id"] == 123
    assert result["name"] == "张三"
    assert result["origin_school"] == "清华大学"
    assert result["origin_description"] == "张三，男，清华大学教授。"
    assert result["origin_link"] == "http://example.com/zhangsan"
    assert result["is_teacher_homepage"] is False
    assert isinstance(result["baike_work_exps"], list)
    assert result["latest_unit"] == "北京大学"
    assert result["unit_changed"]
    assert result["matched_teacher"] is not None

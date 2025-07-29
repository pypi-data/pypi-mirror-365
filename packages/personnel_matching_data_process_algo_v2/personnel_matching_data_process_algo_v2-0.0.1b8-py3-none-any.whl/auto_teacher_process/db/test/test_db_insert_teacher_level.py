import pandas as pd
import pytest

from auto_teacher_process.db.services.db_insert_teacher_level import TeacherLevelDBProcessor


# 测试参数缺失场景
def test_run_missing_parameters(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(TeacherLevelDBProcessor, "_setup_db_engine")
    processor = TeacherLevelDBProcessor()

    # 调用run方法 - 缺少province
    with pytest.raises(ValueError):
        processor.run({"file_dir": "/test/dir"})

    # 调用run方法 - 缺少file_dir
    with pytest.raises(ValueError):
        processor.run({"province": "test_province"})


# 测试数据库更新场景
def test_update_db_call(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(TeacherLevelDBProcessor, "_setup_db_engine")
    processor = TeacherLevelDBProcessor()

    # 模拟insert_db方法
    mock_insert_db = mocker.patch.object(processor, "insert_db")
    mock_get_db = mocker.patch.object(processor, "get_db")

    mock_get_db.return_value = pd.read_csv("auto_teacher_process/db/test/teacher_level_test_data.csv")

    mock_fetch_school_info_by_province = mocker.patch.object(processor, "fetch_school_info_by_province")
    mock_fetch_school_info_by_province.return_value = {"东莞理工学院": 40}

    # 调用process方法
    processor.process({"province": "test_province", "query_sql": "test_query_sql"})

    # 验证insert_db被调用
    mock_insert_db.assert_called_once()

    # 验证调用参数
    args, kwargs = mock_insert_db.call_args
    assert kwargs["table_name"] == "derived_teacher_level"
    assert len(kwargs["df"]) == 50
    assert "teacher_id" in kwargs["df"].columns
    assert "project_level" in kwargs["df"].columns

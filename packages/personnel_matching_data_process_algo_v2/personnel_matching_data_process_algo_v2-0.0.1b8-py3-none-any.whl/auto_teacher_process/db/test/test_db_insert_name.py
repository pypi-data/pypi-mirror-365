from unittest.mock import patch

import pandas as pd
import pytest

from auto_teacher_process.db.services.db_insert_name import NameInsertDBProcessor


# 测试参数缺失场景
def test_run_missing_parameters(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(NameInsertDBProcessor, "_setup_db_engine")  # 避免实际数据库连接
    processor = NameInsertDBProcessor()

    # 调用run方法 - 缺少province
    with pytest.raises(ValueError):
        processor.run({"file_dir": "/test/dir"})

    # 调用run方法 - 缺少file_dir
    with pytest.raises(ValueError):
        processor.run({"province": "test_province"})


# 测试数据库更新场景
def test_update_db_call(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(NameInsertDBProcessor, "_setup_db_engine")  # 避免实际数据库连接
    processor = NameInsertDBProcessor()

    # 模拟_get_all_folders方法
    mocker.patch.object(
        processor,
        "_get_all_folders",
        return_value=pd.DataFrame(
            {
                "teacher_id": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
                "is_en": [1, 1, 0, 1, 1, 0, 1, 0, 0, 1],
                "omit_description": ["", "家庭原因", "健康问题", "", "其他任务", "", "未说明", "保密", "", "时间冲突"],
                "omit_valid": [0, 1, 1, 0, 1, 0, 0, 0, 0, 1],
                "research_area": [
                    "人工智能",
                    "量子计算",
                    "生物信息学",
                    "纳米材料",
                    "环境工程",
                    "金融数学",
                    "认知心理学",
                    "农业经济",
                    "海洋生物学",
                    "网络安全",
                ],
                "area_valid": [1, 1, 0, 1, 1, 0, 1, 0, 1, 1],
                "email": [
                    "john.doe@univ.edu",
                    "invalid_email",
                    "li_ming@research.cn",
                    "no-reply",
                    "sarah.smith@tech.edu",
                    "contact@",
                    "robert@eng-department.org",
                    "missing@.com",
                    "emily.wang@uni.edu",
                    "james@cs-center.net",
                ],
                "email_valid": [1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
                "project_experience": [
                    "国家自然科学基金重点项目",
                    "",
                    "企业合作研发项目",
                    "省部级科研项目",
                    "国际合作项目",
                    "",
                    "青年科学基金",
                    "横向课题",
                    "国家重点研发计划",
                    "校级教改项目",
                ],
                "project_valid": [1, 0, 1, 1, 1, 0, 1, 0, 1, 0],
                "title": [
                    "教授",
                    "副教授",
                    "讲师",
                    "研究员",
                    "高级工程师",
                    "助理教授",
                    "特聘教授",
                    "副研究员",
                    "教授级高工",
                    "讲师",
                ],
                "normalized_title": [
                    "Professor",
                    "Associate Professor",
                    "Lecturer",
                    "Research Professor",
                    "Senior Engineer",
                    "Assistant Professor",
                    "Chair Professor",
                    "Associate Research Fellow",
                    "Professor-level Senior Engineer",
                    "Lecturer",
                ],
                "title_valid": [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
                "famous_titles": [
                    "长江学者",
                    "",
                    "国家杰青",
                    "",
                    "IEEE Fellow",
                    "青年千人",
                    "",
                    "ACM Distinguished Member",
                    "国家级教学名师",
                    "",
                ],
                "normalized_famous_titles": [
                    "Changjiang Scholar",
                    "",
                    "National Outstanding Young Scientist",
                    "",
                    "IEEE Fellow",
                    "Young Thousand Talents",
                    "",
                    "ACM Distinguished Member",
                    "National Teaching Master",
                    "",
                ],
                "famous_valid": [1, 0, 1, 0, 1, 1, 0, 1, 1, 0],
                "position": [
                    "系主任",
                    "副院长",
                    "实验室主任",
                    "无",
                    "研究中心主任",
                    "教学委员会成员",
                    "院长",
                    "学科带头人",
                    "无",
                    "研究生导师",
                ],
                "position_valid": [1, 1, 0, 0, 1, 1, 1, 0, 0, 1],
                "description": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
                "raw_teacher_name": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            }
        ),
    )

    mock_insert_db = mocker.patch.object(processor, "insert_db")

    # 调用process方法
    processor.process({"province": "test_province", "file_dir": "/test/dir"})

    # 验证insert_db调用参数
    assert mock_insert_db.call_count == 1


# 测试空数据处理场景
@patch("os.listdir")
@patch("os.path.isdir")
def test_run_empty_data(mock_isdir, mock_listdir, mocker):
    # 设置模拟返回值
    mock_listdir.return_value = []
    mock_isdir.return_value = True

    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(NameInsertDBProcessor, "_setup_db_engine")  # 避免实际数据库连接
    processor = NameInsertDBProcessor()
    mocker.patch.object(processor, "update_db")

    # 调用run方法
    input_data = {"province": "test_province", "file_dir": "/test/dir"}
    processor.run(input_data)

    # 验证update_db未被调用
    processor.update_db.assert_not_called()

from auto_teacher_process.db.services.db_associated_teacher_leader import TeacherLeaderAssociatedProcessor


# 测试数据查询
def test_get_db():
    processor = TeacherLeaderAssociatedProcessor()
    school_name = "清华大学"
    print(processor.get_teacher_leader_group(school_name))

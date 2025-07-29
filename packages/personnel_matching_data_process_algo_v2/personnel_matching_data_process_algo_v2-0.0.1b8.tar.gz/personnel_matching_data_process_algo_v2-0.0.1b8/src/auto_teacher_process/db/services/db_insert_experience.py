from auto_teacher_process.db.db_base import BaseDBProcessor


class ExperienceInsertDBProcessor(BaseDBProcessor):
    """网页数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)

    def process(self, input_data):
        """主处理流程"""
        # 获取输入参数
        province = input_data.get("province", "")
        file_dir = input_data.get("file_dir", "")
        if province == "" or file_dir == "":
            self.logger.error("请提供正确的省份和文件目录")
            raise ValueError("请提供正确的省份和文件目录")

        merged_df = self._get_all_folders(file_dir, province)

        if merged_df.empty:
            self.logger.info("没有需要处理的数据")
            return

        self.logger.info(f"总的数量:{len(merged_df)}")
        merged_df = merged_df[merged_df["is_valid"] == 1]
        self.logger.info(f"有效数量:{len(merged_df)}")

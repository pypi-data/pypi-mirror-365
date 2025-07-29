from auto_teacher_process.db.db_base import BaseDBProcessor


class HTMLInsertDBProcessor(BaseDBProcessor):
    """网页数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)

    def process(self, input_data):
        """主处理流程"""
        # 获取输入参数
        province = input_data.get("province", "")
        file_dir = input_data.get("file_dir", "")
        if province == "" or file_dir == "":
            raise ValueError("请提供正确的省份和文件目录")

        merged_df = self._get_all_folders(file_dir, province)

        if merged_df.empty:
            self.logger.debug("没有需要处理的数据")
            return

        self.logger.debug(f"总的数量:{len(merged_df)}")
        merged_df = merged_df[merged_df["is_valid"] == 1]
        self.logger.debug(f"有效数量:{len(merged_df)}")

        des_df = merged_df[["teacher_id", "extracted_description", "is_en"]].copy()

        des_update_sql = """
            UPDATE derived_teacher_data
            SET description = :extracted_description,
                is_en = :is_en,
                is_update = 1
            WHERE teacher_id = :teacher_id
        """

        # 更新数据
        self.logger.debug("开始更新数据库...")
        self.update_db(
            df=des_df,
            update_sql=des_update_sql,
            progress_file="update_derived_teacher_data_progress.txt",
        )

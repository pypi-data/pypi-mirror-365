from auto_teacher_process.db.db_base import BaseDBProcessor


class NameInsertDBProcessor(BaseDBProcessor):
    """姓名数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)

    def get_raw_teacher_data_from_db(self, id_start, id_end):
        query = f"""
        SELECT * 
        FROM raw_teacher_data 
        WHERE id >= {id_start} and id <= {id_end} AND status=0;
        """
        return self.get_db(query)

    def process(self, input_data):
        """主处理流程"""

        merged_df = self.get_df(input_data["file"])

        if merged_df.empty:
            self.logger.debug("合并后数据为空")
            return

        derived_df = merged_df.drop(columns=["raw_teacher_name"])
        self.logger.debug("插入中文教师信息表")
        self.insert_db(
            df=derived_df, table_name="derived_teacher_data", batch_size=1000, progress_file="name_insert_progress.txt"
        )

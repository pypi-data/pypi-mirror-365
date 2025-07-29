from auto_teacher_process.db.db_base import BaseDBProcessor


class DesPaperInsertDBProcessor(BaseDBProcessor):
    """网页数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)

    def get_teacher_des_paper_data(self, id_start, id_end):
        """获取教师论文数据"""
        query = f"""
            SELECT *
            FROM derived_teacher_data t 
            JOIN derived_des_paper p ON t.teacher_id = p.teacher_id
            WHERE (t.raw_data_id >= {id_start} and t.raw_data_id <= {id_end}) AND t.is_valid = 1;
        """
        return self.get_db(query)

    def process(self, input_data):
        """主处理流程"""

        merged_df = self.get_df(input_data["file"])

        if merged_df.empty:
            self.logger.debug("合并后数据为空")
            return

        if merged_df.empty:
            self.logger.debug("没有需要处理的数据")
            return

        sql = """
                INSERT INTO product_teacher_paper_relation (teacher_id, paper_id, author_order, high_true)
                VALUES (:teacher_id, :paper_id, :author_order, :high_true)
                ON DUPLICATE KEY UPDATE
                    author_order = VALUES(author_order),
                    high_true = VALUES(high_true);
              """
        self.update_db(merged_df, sql)

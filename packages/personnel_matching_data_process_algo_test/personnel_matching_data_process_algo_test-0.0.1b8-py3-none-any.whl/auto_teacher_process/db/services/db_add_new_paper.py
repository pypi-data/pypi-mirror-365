from auto_teacher_process.db.db_base import BaseDBProcessor


class NewPaperInsertProcessor(BaseDBProcessor):
    """网页数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name"):
        super().__init__(system, stage)

    def get_raw_paper_data_from_db(self, id1, id2):
        query = f"""
        SELECT * FROM raw_paper_data 
        WHERE id >= {id1} and id <= {id2};
        """
        return self.get_db(query)

    def process(self, input_data):
        """主处理流程"""

        merged_df = self.get_df(input_data["file"])

        if merged_df.empty:
            self.logger.debug("没有需要处理的数据")
            return

        merged_df = merged_df[merged_df["is_valid"] == 1]
        merged_df = merged_df.drop(columns=["orcid"]).copy()
        df_unique = merged_df.drop_duplicates(subset=["teacher_id", "paper_id"])

        # 更新数据
        self.logger.debug("开始插入数据库...")
        self.insert_db(
            df=df_unique,
            table_name="product_teacher_paper_relation",
            batch_size=1000,
            progress_file="paper_match_relation_insert_progress.txt",
        )

from auto_teacher_process.db.db_base import BaseDBProcessor


class GoogleMatchDBProcessor(BaseDBProcessor):
    def get_teacher_data_from_db(self, id_start, id_end):
        query = f"""
        SELECT * FROM derived_intl_teacher_data WHERE id >= {id_start} and id <= {id_end};
        """
        return self.get_db(query)

    def get_google_teacher_data_from_db(self, id_start, id_end):
        query = f"""
        SELECT * FROM raw_intl_google_scholar_data WHERE id >= {id_start} and id <= {id_end};
        """
        return self.get_db(query)

    def get_google_teacher_relation_from_db(self, id_start, id_end):
        query = f"""
        SELECT * FROM product_teacher_google_page_relation WHERE id >= {id_start} and id <= {id_end};
        """
        return self.get_db(query)

    def get_school_name_from_db(self, id1, id2):
        query = f"""
        SELECT DISTINCT school_name FROM raw_intl_google_scholar_data WHERE school_name IS NOT NULL and id >= {id1} and id <= {id2};
        """
        df = self.get_db(query)
        return df["school_name"].dropna().tolist()

    def get_all_intl_school_info(self):
        query = """
        SELECT * FROM product_intl_school_info
        """
        return self.get_db(query)

    async def fetch_google_paper_async(self, u_id):
        query = """
            SELECT * FROM raw_intl_google_scholar_paper WHERE u_id = %s;
        """
        return await self.async_db_execute_query(query, u_id)

    async def fetch_teacher_data_async(self, teacher_id):
        query = """
            SELECT * FROM derived_intl_teacher_data WHERE teacher_id = %s;
        """
        return await self.async_db_execute_query(query, teacher_id)

    async def fetch_papers_by_teacher_id_async(self, teacher_id):
        query = """
            SELECT 
                dcp.id, pitpr.teacher_id, title, high_true
            FROM 
                raw_teacher_paper dcp
            RIGHT JOIN 
                product_intl_teacher_paper_relation pitpr
            ON 
                dcp.id = pitpr.paper_id
            WHERE 
                pitpr.teacher_id = %s
        """
        return await self.async_db_execute_query(query, teacher_id)

    async def fetch_google_page_async(self, teacher_names: list[str], school_name: str):
        placeholders = ",".join(["%s"] * len(teacher_names))
        query = f"""
            SELECT 
                *
            FROM 
                raw_intl_google_scholar_data 
            WHERE 
                author_list IN ({placeholders}) AND school_name = %s;        
        """
        params = teacher_names + [school_name]

        return await self.async_db_execute_query(query, params)

    def process(self, input_data: dict) -> None:
        """
        主处理流程 (抽象方法，子类必须实现)
        输入: 无
        输出: 无
        """
        merged_df = self.get_df(input_data["file"])

        if merged_df.empty:
            self.logger.debug("合并后数据为空")
            return

        derived_df = merged_df.copy()
        # position_df = merged_df[['teacher_id', 'position', 'position_valid']].copy()
        rename_mapping = {
            "teacher_name": "derived_teacher_name",
            "len_google_papers": "google_papers_len",
            "len_db_papers": "db_paper_len",
            "len_inter_papers": "inter_papers_len",
        }

        derived_df.rename(columns=rename_mapping, inplace=True)
        self.logger.debug("插入海外谷歌主页与教师关联表")
        self.insert_db(
            df=derived_df,
            table_name="product_teacher_google_page_relation",
            batch_size=1000,
            progress_file="product_teacher_google_page_relation_insert_progress.txt",
        )

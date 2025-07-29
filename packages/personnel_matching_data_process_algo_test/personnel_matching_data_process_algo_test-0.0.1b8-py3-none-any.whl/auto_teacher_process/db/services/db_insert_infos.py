import json
import uuid

import pandas as pd
from tqdm import tqdm

from auto_teacher_process.db.db_base import BaseDBProcessor
from auto_teacher_process.utils.text_utils import contains_chinese


class InfoInsertDBProcessor(BaseDBProcessor):
    """信息数据插入处理器"""

    def get_derived_teacher_data_from_db(self, id_start, id_end):
        query = f"""
        SELECT * FROM derived_teacher_data 
        WHERE (raw_data_id >= {id_start} and raw_data_id <= {id_end}) AND is_valid = 1;
        """
        return self.get_db(query)

    def get_school_data_from_db(self):
        query = """
        SELECT school_name, school_name_en FROM product_intl_school_info
        UNION
        SELECT school_name, school_name_en FROM product_school_info
        """
        return self.get_db(query)

    def find_standard_school_name(self, organization: str) -> str | None:
        if not organization or not organization.strip():
            return None
        # 判断是否是中文
        is_chinese = contains_chinese(organization)

        # 如果是英文，去空格 + 转小写
        if not is_chinese:
            org = organization.replace(" ", "").lower()

        school_df = self.get_school_data_from_db()

        # 标准化英文字段列
        school_df["school_name_en_clean"] = (
            school_df["school_name_en"].astype(str).str.replace(" ", "", regex=False).str.lower()
        )

        if is_chinese:
            # 只匹配中文字段
            exact_match = school_df[school_df["school_name"] == org]
            if not exact_match.empty:
                return exact_match.iloc[0]["school_name"]

            fuzzy_match = school_df[school_df["school_name"].str.contains(org, na=False)]
            if not fuzzy_match.empty:
                return fuzzy_match.iloc[0]["school_name"]
        else:
            # 只匹配英文清洗字段
            exact_match = school_df[school_df["school_name_en_clean"] == org]
            if not exact_match.empty:
                return exact_match.iloc[0]["school_name"]

            fuzzy_match = school_df[school_df["school_name_en_clean"].str.contains(org, na=False)]
            if not fuzzy_match.empty:
                return fuzzy_match.iloc[0]["school_name"]

        return None

    def db_insert_host_project(self, projects_df):
        filter_df_list = []  # 如果没有传空list []
        raw_project_df_list = []
        relation_df_list = []

        for index, p_info in tqdm(projects_df.iterrows(), total=len(projects_df), desc="project processing row:"):
            teacher_id = p_info["teacher_id"]
            project_str = p_info["project_experience"]
            p_is_valid = p_info["is_valid"]
            if p_is_valid == 0:
                filter_row = {
                    "teacher_id": teacher_id,
                    "filtered_project_experience": json.dumps([], ensure_ascii=False),
                    "is_valid": 0,
                    "status": 3,
                }
                filter_df_list.append(filter_row)
            else:
                try:
                    projects = json.loads(project_str)
                except Exception as e:
                    self.logger.debug(f"json解析出错:{e}")
                    continue

                host_projects = projects["主持的项目"]  # list
                if len(host_projects) == 0:
                    filter_row = {
                        "teacher_id": teacher_id,
                        "filtered_project_experience": json.dumps([], ensure_ascii=False),
                        "is_valid": 0,
                        "status": 3,
                    }
                    filter_df_list.append(filter_row)
                else:
                    # filter 主持的项目
                    filter_row = {
                        "teacher_id": teacher_id,
                        "filtered_project_experience": json.dumps(host_projects, ensure_ascii=False),
                        "is_valid": 1,
                        "status": 3,
                    }
                    filter_df_list.append(filter_row)

                    # raw_project project_id(uuid) -> project_relation
                    filtered_projects = [p for p in host_projects if len(p) < 150]
                    for p in filtered_projects:
                        project_id = uuid.uuid4()
                        raw_project_row = {
                            "project_id": project_id,
                            "project_name": p,
                            "data_source": "derived_project_experience_filtered",
                            "teacher_id": teacher_id,
                        }
                        raw_project_df_list.append(raw_project_row)
                        # project_relation
                        project_relation_row = {
                            "teacher_id": teacher_id,
                            "project_id": project_id,
                            "is_from_match": 0,
                            "is_valid": 1,
                        }
                        relation_df_list.append(project_relation_row)

        filter_df = pd.DataFrame(filter_df_list)
        raw_project_df = pd.DataFrame(raw_project_df_list)
        relation_df = pd.DataFrame(relation_df_list)

        # 插入数据
        self.logger.debug("inserting data...")
        self.insert_db(
            df=filter_df,
            table_name="derived_project_experience_filtered",
            batch_size=1000,
            progress_file="insert_filtered_progress.txt",
        )
        self.logger.debug("第一次插入数据完成")
        self.insert_db(
            df=raw_project_df,
            table_name="raw_teacher_project",
            batch_size=1000,
            progress_file="insert_raw_project_progress.txt",
        )
        self.logger.debug("第二次插入数据完成")
        self.insert_db(
            df=relation_df,
            table_name="product_teacher_project_relation",
            batch_size=1000,
            progress_file="insert_project_relation_progress.txt",
        )
        self.logger.debug("第三次插入数据完成")

    def db_insert_past_experience(self, experience_df, source=0):
        def parse_json_list(x):
            if isinstance(x, str):
                try:
                    return json.loads(x)
                except Exception:
                    return []
            elif isinstance(x, list):
                return x
            else:
                return []

        rows = []

        for _, row in experience_df.iterrows():
            teacher_id = row["teacher_id"]
            educations = parse_json_list(row.get("education", []))
            works = parse_json_list(row.get("work", []))

            # 教育经历
            for edu in educations:
                org = edu.get("organization")
                rows.append(
                    {
                        "teacher_id": teacher_id,
                        "type": 0,
                        "start_date": edu.get("start_date"),
                        "end_date": edu.get("end_date"),
                        "organization": org,
                        "normalized_organization": self.find_standard_school_name(org),
                        "department": edu.get("department"),
                        "degree": edu.get("degree"),
                        "role_title": None,
                        "position": None,
                        "city": edu.get("city"),
                        "region": None,
                        "country": None,
                        "source": source,
                        "is_valid": int(bool(org)),
                        "institution": edu.get("institution"),
                    }
                )

            # 工作经历
            for job in works:
                org = job.get("organization")
                rows.append(
                    {
                        "teacher_id": teacher_id,
                        "type": 1,
                        "start_date": job.get("start_date"),
                        "end_date": job.get("end_date"),
                        "organization": org,
                        "normalized_organization": self.find_standard_school_name(org),
                        "department": None,
                        "degree": None,
                        "role_title": job.get("role_title"),
                        "position": None,
                        "city": job.get("city"),
                        "region": None,
                        "country": None,
                        "source": source,
                        "is_valid": int(bool(org)),
                        "institution": job.get("institution"),
                    }
                )

        result = pd.DataFrame(rows)
        self.insert_db(df=result, table_name="derived_past_experience", single_operation=True)

    def process(self, input_data):
        """主处理流程"""

        merged_df = self.get_df(input_data["file"])

        if merged_df.empty:
            self.logger.debug("合并后数据为空")
            return

        # 将merged_df处理成四种数据库表需要的格式
        omit_df = merged_df[["teacher_id", "omit_description", "omit_valid"]].copy()
        omit_df.rename(columns={"omit_valid": "is_valid"}, inplace=True)

        area_df = merged_df[["teacher_id", "research_area", "area_valid"]].copy()
        area_df.rename(columns={"area_valid": "is_valid"}, inplace=True)

        email_df = merged_df[["teacher_id", "email", "email_valid"]].copy()
        email_df.rename(columns={"email_valid": "is_valid"}, inplace=True)

        project_df = merged_df[["teacher_id", "project_experience", "project_valid"]].copy()
        project_df.rename(columns={"project_valid": "is_valid"}, inplace=True)

        title_df = merged_df[["teacher_id", "title", "normalized_title", "title_valid"]].copy()
        title_df.rename(columns={"title_valid": "is_valid"}, inplace=True)

        famous_df = merged_df[["teacher_id", "famous_titles", "normalized_famous_titles", "famous_valid"]].copy()
        famous_df.rename(
            columns={"famous_valid": "is_valid", "normalized_famous_titles": "normalized_titles"}, inplace=True
        )

        position_df = merged_df[["teacher_id", "position", "position_valid"]].copy()
        position_df.rename(columns={"position_valid": "is_valid"}, inplace=True)

        paper_df = merged_df[["teacher_id", "paper_list", "paper_valid"]].copy()
        paper_df.rename(columns={"paper_valid": "is_valid"}, inplace=True)

        experience_df = merged_df[["teacher_id", "education", "work", "experience_valid"]].copy()
        experience_df.rename(columns={"experience_valid": "is_valid"}, inplace=True)

        # 插入数据
        self.logger.debug("开始插入数据...")
        self.insert_db(df=omit_df, table_name="derived_omit_description", single_operation=True)
        self.insert_db(df=area_df, table_name="derived_research_area", single_operation=True)
        self.insert_db(df=email_df, table_name="derived_email", single_operation=True)
        self.insert_db(df=project_df, table_name="derived_project_experience", single_operation=True)
        self.insert_db(df=title_df, table_name="derived_title", single_operation=True)
        self.insert_db(df=famous_df, table_name="derived_famous_titles", single_operation=True)
        self.insert_db(df=position_df, table_name="derived_position", single_operation=True)
        self.insert_db(df=paper_df, table_name="derived_paper", single_operation=True)

        self.logger.debug("数据插入完成！")

        # 更新数据
        df_update_en = merged_df[merged_df["is_en"] == 1]
        self.logger.debug(f"开始更新英文教师的 description 信息，需要更新的数据量：{len(df_update_en)}")

        update_query = """
            UPDATE derived_teacher_data
            SET
                description = :description
            WHERE teacher_id = :teacher_id;
        """

        for _, row in tqdm(df_update_en.iterrows(), total=len(df_update_en)):
            data = {"description": row["description"], "teacher_id": row["teacher_id"]}
            self.update_db(df=pd.DataFrame([data]), update_sql=update_query, single_operation=True)

        # 教师项目关系生成
        self.db_insert_host_project(project_df)
        # 教师经历数据插入
        self.db_insert_past_experience(experience_df)

import json

import pandas as pd
from tqdm import tqdm

from auto_teacher_process.db.db_base import BaseDBProcessor
from auto_teacher_process.utils.project_utils import _project_famous_check, _quchong


class FamousProjectsInsertDBProcessor(BaseDBProcessor):
    """国家级重要项目数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)

    def process(self, input_data: dict) -> None:
        """主处理流程"""
        # 获取输入参数
        id_start = input_data.get("id_start", "")
        id_end = input_data.get("id_end", "")

        # 构建查询语句
        teacher_query = f"""
            SELECT p.teacher_id, p.project_experience, p.is_valid
            FROM derived_teacher_data t
            LEFT JOIN derived_project_experience p ON t.teacher_id = p.teacher_id
            WHERE t.is_valid=1 AND (t.raw_data_id>={id_start} AND t.raw_data_id<={id_end});
        """

        relation_query = f"""
            SELECT t.teacher_id, rp.project_level
            FROM derived_teacher_data t
            LEFT JOIN product_teacher_project_relation r ON t.teacher_id = r.teacher_id
            LEFT JOIN raw_teacher_project rp ON r.project_id = rp.project_id
            WHERE t.is_valid=1 AND (t.raw_data_id>={id_start} AND t.raw_data_id<={id_end}) AND r.is_from_match = 1;
        """

        # 查询数据
        projects_df = self.get_db(teacher_query)

        projects_with_levels_df = self.get_db(relation_query)

        # 处理数据
        famous_df_list = []
        projects_with_levels_df = projects_with_levels_df.dropna(subset=["project_level"])
        projects_with_levels_df.set_index("teacher_id", inplace=True)

        for index, p_info in tqdm(projects_df.iterrows(), total=len(projects_df), desc="project processing row:"):
            teacher_id = p_info["teacher_id"]
            project_str = p_info["project_experience"]
            p_is_valid = p_info["is_valid"]
            if p_is_valid == 0:
                host_projects = []
                join_projects = []
            else:
                try:
                    projects = json.loads(project_str)
                except Exception as e:
                    self.logger.debug(f"解析project出错:{e}")
                    continue
                self.logger.debug(projects)
                try:
                    host_projects = projects["主持的项目"]  # list
                except Exception as e:
                    self.logger.debug(f"{projects}出错:{e}")
                    host_projects = []
                try:
                    join_projects = projects["参与的项目"]
                except:
                    self.logger.debug(f"{projects}出错:{e}")
                    join_projects = []

            if teacher_id in projects_with_levels_df.index:
                teacher_projects_with_level = projects_with_levels_df.loc[teacher_id]

                if not teacher_projects_with_level.empty:
                    if isinstance(teacher_projects_with_level, pd.Series):
                        # 如果是 Series, 直接使用它的 'project_level' 列并获取唯一值
                        non_null_project_levels = teacher_projects_with_level.unique().tolist()
                    elif isinstance(teacher_projects_with_level, pd.DataFrame):
                        # 如果是 DataFrame, 选择 'project_level' 列并获取唯一值
                        non_null_project_levels = teacher_projects_with_level["project_level"].unique().tolist()
                    host_projects.extend(non_null_project_levels)

            famous_host_projects = _project_famous_check(host_projects)
            famous_host_projects = _quchong(famous_host_projects)

            famous_join_projects = _project_famous_check(join_projects)
            famous_join_projects = _quchong(famous_join_projects)
            if len(famous_host_projects) == 0 and len(famous_join_projects) == 0:
                is_valid = 0
            else:
                is_valid = 1
            famous_row = {
                "teacher_id": teacher_id,
                "host_projects": json.dumps(famous_host_projects, ensure_ascii=False),
                "join_projects": json.dumps(famous_join_projects, ensure_ascii=False),
                "is_valid": is_valid,
                "status": 3,
            }
            famous_df_list.append(famous_row)

        # 插入数据
        famous_df = pd.DataFrame(famous_df_list)
        self.logger.debug(famous_df)

        self.insert_db(
            df=famous_df,
            table_name="derived_famous_projects",
            batch_size=1000,
            progress_file="insert_famous_projects_progress.txt",
        )

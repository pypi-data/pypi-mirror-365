import json

import pandas as pd
from tqdm import tqdm

from auto_teacher_process.config import Config
from auto_teacher_process.db.db_base import BaseDBProcessor


class TeacherLevelDBProcessor(BaseDBProcessor):
    """教师等级处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)
        self.province_code_dict = Config.DB_CONFIG.TEACHER_LEVEL.PORVINCE_CODE_DICT
        self.famous_projects_level_scores = Config.DB_CONFIG.TEACHER_LEVEL.FAMOUS_PROJECTS_LEVEL_SCORES
        self.famous_titles_level_scores = Config.DB_CONFIG.TEACHER_LEVEL.FAMOUS_TITLES_LEVEL_SCORES
        self.titles_level_scores = Config.DB_CONFIG.TEACHER_LEVEL.TITLES_LEVEL_SCORES

    def fetch_school_info_by_province(self) -> dict:
        """获取学校信息"""
        self.logger.debug("获取学校信息")
        query = """
            SELECT school_name, school_level
            FROM product_school_info
            ORDER BY id ASC;
        """
        school_df = self.get_db(query)
        level_map = {0: 40, 1: 100, 2: 90, 3: 80, 4: 70, 5: 60}
        return {row["school_name"]: level_map.get(row["school_level"], 40) for _, row in school_df.iterrows()}

    def calculate_famous_projects_level(self, projects: list) -> int:
        """计算项目等级评分"""
        if not projects:
            return 0

        max_score = 10  # 默认评分
        for project in projects:
            for score_str, title_group in self.famous_projects_level_scores.items():
                if project in title_group:
                    max_score = max(max_score, int(score_str))
                    break
        return max_score

    def calculate_famous_titles_level(self, famous_titles: list) -> int:
        """计算帽子等级评分"""
        if not famous_titles:
            return 0

        max_score = 40  # 默认评分
        for title in famous_titles:
            for score_str, title_group in self.famous_titles_level_scores.items():
                if title in title_group:
                    max_score = max(max_score, int(score_str))
                    break
        return max_score

    def calculate_position_level(self, position_list: list) -> int:
        """计算职位等级评分"""
        if not position_list:
            return 0

        # 定义职位等级映射，以分数为键，职位为值（字符串匹配）90
        def is_principal(position):
            if "校长" in position and "副" not in position:
                if "助理" not in position:
                    if "讲座教授" not in position:
                        return True
            return False

        # 匹配“副校长”，返回85分
        def is_vice_principal(position):
            if "副校长" in position:
                if "助理" not in position:
                    return True
            return False

        # 匹配“国家”或“中国”并且包含“主任”或“理事长”，排除“副”  80
        def is_national_lab_director(position):
            if ("国家" in position or "中国" in position) and ("主任" in position or "理事长" in position):
                if "副" not in position:  # 排除副职
                    return True
            return False

        # 匹配“带头人”或“首席科学家”，返回80分
        def is_leader_or_chief_scientist(position):
            if "带头人" in position or "首席科学家" in position:
                return True
            return False

        # 匹配“国家”或“中国”并且包含“主任”或“理事长”、“秘书长”、“组长”、“主席”，要求副职  70
        def is_national_lab_vice_director(position):
            if ("国家" in position or "中国" in position) and (
                "主任" in position
                or "理事长" in position
                or "秘书长" in position
                or "组长" in position
                or "主席" in position
            ):
                if "副" in position:  # 副职
                    return True
            return False

        # 匹配包含“省”或省名字，并且包含“主任”或“理事长”、“秘书长”、“组长”、“主席”，排除副职 70
        def is_provincial_position(position):
            if "省" in position and (
                "主任" in position
                or "理事长" in position
                or "秘书长" in position
                or "组长" in position
                or "主席" in position
            ):
                if "副" not in position:  # 排除副职
                    return True
            return False

        def is_director_or_chair(position):
            if "处长" in position or "院长" in position or "部长" in position or "党委书记" in position:
                if "助理" not in position:
                    return True
            return False

        # 取出所有匹配的职位等级
        levels = []

        # 遍历所有职位，匹配对应的规则
        for position in position_list:
            if is_principal(position):
                levels.append(90)
            if is_vice_principal(position):
                levels.append(85)
            if is_national_lab_director(position):
                levels.append(80)
            if is_leader_or_chief_scientist(position):
                levels.append(80)
            if is_national_lab_vice_director(position):
                levels.append(70)
            if is_provincial_position(position):
                levels.append(70)
            if is_director_or_chair(position):
                levels.append(70)
            if not any(
                [
                    is_principal(position),
                    is_vice_principal(position),
                    is_national_lab_director(position),
                    is_leader_or_chief_scientist(position),
                    is_national_lab_vice_director(position),
                    is_provincial_position(position),
                    is_director_or_chair(position),
                ]
            ):
                levels.append(60)
        # print(levels)
        # 如果找到匹配的职位等级，返回最高的
        if levels:
            highest_level = max(levels)
        # 如果没有匹配的职位，且职位列表不为空，返回 60 分
        else:
            highest_level = 0

        return highest_level

    def calculate_titles_level(self, titles: list) -> int:
        """计算职称等级评分"""
        if not titles:
            return 10

        max_score = 10  # 默认评分
        for title in titles:
            for score_str, title_group in self.titles_level_scores.items():
                if title in title_group:
                    max_score = max(max_score, int(score_str))
                    break
        return max_score

    def calculate_teacher_level(self, teacher_df: pd.DataFrame) -> pd.DataFrame:
        """计算教师等级信息"""
        self.logger.debug("开始计算教师等级信息")
        school_level_dict = self.fetch_school_info_by_province()

        levels = []
        for _, row in tqdm(teacher_df.iterrows(), total=len(teacher_df)):
            try:
                self.logger.debug(f"row:\n{row}")
                self.logger.debug(f"正在处理教师positions：{row['position']}")
                positions = json.loads(row["position"]) if row["position"] else None

                self.logger.debug("正在处理教师title")
                titles = json.loads(row["title"])

                self.logger.debug("正在处理教师normalized_titles")
                famous_titles = json.loads(row["normalized_titles"])

                self.logger.debug("正在处理教师host_projects")
                host_projects = json.loads(row["host_projects"])

                self.logger.debug("正在处理教师join_projects")
                join_projects = json.loads(row["join_projects"])

                level_row = {
                    "teacher_id": row["teacher_id"],
                    "famous_titles_level": self.calculate_famous_titles_level(famous_titles),
                    "project_level": self.calculate_famous_projects_level(host_projects),
                    "position_level": self.calculate_position_level(positions),
                    "job_title_level": self.calculate_titles_level(titles),
                    "school_level": school_level_dict.get(row["school_name"], 40),
                }
                levels.append(level_row)

            except Exception as e:
                self.logger.debug(f"处理教师数据失败: {row['teacher_id']} - {e}")
                continue

        return pd.DataFrame(levels)

    def process(self, input_data: dict) -> None:
        """主处理流程"""
        id_start = input_data.get("id_start", "")
        id_end = input_data.get("id_end", "")

        query_sql = f"""
        SELECT t.teacher_id, t.school_name, pos.position, tit.title, ftit.normalized_titles, fp.host_projects, fp.join_projects
        FROM derived_teacher_data t
        LEFT JOIN derived_position pos ON t.teacher_id = pos.teacher_id
        LEFT JOIN derived_title tit ON t.teacher_id = tit.teacher_id
        LEFT JOIN derived_famous_titles ftit ON t.teacher_id = ftit.teacher_id
        LEFT JOIN derived_famous_projects fp ON t.teacher_id = fp.teacher_id
        WHERE (t.raw_data_id>={id_start} AND t.raw_data_id<={id_end}) AND t.is_valid = 1;
        """

        # 获取教师数据
        self.logger.debug("获取教师数据")
        teacher_df = self.get_db(query_sql)

        if teacher_df.empty:
            self.logger.warning("未查询到教师数据")
            return

        # 计算教师等级
        level_df = self.calculate_teacher_level(teacher_df)
        if level_df.empty:
            self.logger.warning("未生成教师等级数据")
            return

        # 插入数据库
        self.insert_db(df=level_df, table_name="derived_teacher_level", batch_size=1000)
        self.logger.debug("教师等级数据插入成功")

import pandas as pd

from auto_teacher_process.db.services.db_insert_patent_match import PatentInsertDBProcessor
from auto_teacher_process.db.services.es_operator import ESOperator
from auto_teacher_process.llm.services.llm_patent_match import PatentMatchLLMProcessor
from auto_teacher_process.run_worker.run_base import BaseRunProcessor


class NewPatentMatchProcessor(BaseRunProcessor):
    def __init__(self, args):
        super().__init__(args)
        self.pipeline = "new_patent_data_processing_pipeline"  # 流水线名称
        self.task_type = "new_add_company_patent_match"  # 任务类型
        self.task_status = "start"  # 任务状态
        self.data_primary_key_field = "company_id"  # 数据主键字段
        self.db = PatentInsertDBProcessor(logger=self.logger)
        self.es = ESOperator(logger=self.logger)
        self.llm = PatentMatchLLMProcessor(logger=self.logger)

    async def process_row(self, company_info: pd.Series):
        batch_relation_list = []
        company_id = company_info["company_id"]
        # 缓存中已存在的数据不再处理
        if company_id in self.processed_ids:
            return None  # 跳过已处理的专利
        company_info = company_info.to_dict()

        company_name = company_info["company_name"]
        former_names = company_info["clean_former_name"]

        if not former_names or former_names.strip() == "-" or pd.isna(former_names):
            name_list = [company_name]
        else:
            # 拆分成列表，去除前后空格与空项
            former_list = [name.strip() for name in former_names.split(";") if name.strip()]
            name_list = [company_name] + former_list

        # Todo
        patent_df = await self.es.async_es_to_df_by_affiliation(name_list)

        if patent_df is None:
            return None

        for _, patent in patent_df.iterrows():
            row = {
                "company_id": company_id,
                "patent_id": patent[id],
            }
            batch_relation_list.append(row)

        return batch_relation_list

    async def run(self):
        self.logger.info(f"【{self.task_type}】: 任务开始", extra={"event": "task_start"})
        # 读取数据
        self.logger.info(f"【{self.task_type}】: 开始读取数据", extra={"event": "db_read_start"})

        patent_df = self.db.get_new_company_info_from_db(self.task_args["id_start"], self.task_args["id_end"])
        self.logger.info(f"【{self.task_type}】: 数据读取完成", extra={"event": "db_read_end"})

        # 数据处理
        self.logger.info(f"【{self.task_type}】: 开始处理数据", extra={"event": "process_start"})
        output_data = await self.process(patent_df)
        self.logger.info(f"【{self.task_type}】: 数据处理完成", extra={"event": "process_end"})

        # ES需要手动关闭
        await self.es.close_es_engine()

        # 数据入库
        self.logger.info(f"【{self.task_type}】: 开始插入数据", extra={"event": "db_insert_start"})
        db_input_data = {"file": output_data}
        self.db.run(db_input_data)
        self.logger.info(f"【{self.task_type}】: 插入数据完成", extra={"event": "db_insert_end"})

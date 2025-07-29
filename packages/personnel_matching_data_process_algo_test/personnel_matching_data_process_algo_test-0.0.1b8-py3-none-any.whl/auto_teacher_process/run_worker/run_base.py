import asyncio
import os
from abc import ABC, abstractmethod

import pandas as pd
from tqdm import tqdm

from auto_teacher_process.config import Config


class BaseRunProcessor(ABC):
    def __init__(self, args):
        """
        教师信息处理基类
        """
        self.logger = None
        self.batch_size = 10000
        self.save_interval = 1

        self.save_dir = Config.DATA_CACHE_PATH  # 配置文件读取保存目录
        self.task_id = args["task_id"]
        self.task_args = args["task_args"]

        self.data_primary_key_field = ""
        # 日志相关变量
        self.pipeline = ""
        self.task_type = ""
        self.task_status = ""
        # 文件路径相关变量
        self.cache_path = ""
        self.output_path = ""

        self.cache_data: list[dict] = []
        self.processed_ids: set = set()

    # 路径配置：基于任务名称/任务ID
    def set_file_paths(self) -> None:
        """
        设置文件路径
        输入: task_type (str), task_id (str)
        输出: 无 (更新实例变量 output_path 和 cache_path)
        """
        output_dir = os.path.join(self.save_dir, str(self.task_id), self.task_type)
        os.makedirs(output_dir, exist_ok=True)
        self.cache_path = os.path.join(output_dir, f"{self.task_type}_cache.parquet")
        self.output_path = os.path.join(output_dir, f"{self.task_type}_all.parquet")

    def load_cache(self) -> None:
        """加载历史缓存（避免重复处理）"""
        if os.path.exists(self.cache_path):
            self.logger.info(f"[缓存] 加载：{self.cache_path}")
            df = pd.read_parquet(self.cache_path)
            self.logger.info(f"{df.columns}")
            if self.data_primary_key_field not in df.columns:
                raise ValueError(f"缓存文件中未找到主键字段: '{self.data_primary_key_field}'，请确认字段名是否正确")

            self.processed_ids = set(df[self.data_primary_key_field].values)
            self.cache_data = df.to_dict(orient="records")
        else:
            self.logger.info("[缓存] 未找到，开始新处理")
            self.processed_ids = set()
            self.cache_data = []

    def save_cache(self) -> None:
        """保存缓存结果到Parquet"""
        pd.DataFrame(self.cache_data).to_parquet(self.cache_path, index=False)
        self.logger.info(f"[缓存] 保存：{self.cache_path}")

    async def process_batch(self, batch_rows: pd.DataFrame | list, max_concurrent=500):
        """
        通用异步批处理函数，支持 DataFrame 或 list 输入。
        参数:
            - batch_rows: pd.DataFrame 或 list[pd.Series or dict]
            - process_row: 单个处理函数 (async)
            - max_concurrent: 并发上限
        返回:
            list: 所有非空处理结果
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_with_semaphore(row):
            async with semaphore:
                return await self.process_row(row)

        if isinstance(batch_rows, pd.DataFrame):
            tasks = [asyncio.create_task(run_with_semaphore(row)) for _, row in batch_rows.iterrows()]
        elif isinstance(batch_rows, list):
            tasks = [asyncio.create_task(run_with_semaphore(row)) for row in batch_rows]
        else:
            raise TypeError("batch_rows must be a list or pd.DataFrame")

        results = await asyncio.gather(*tasks)

        # 如果每个任务返回 list，要 flatten；否则保持原样
        if results and isinstance(results[0], list):
            return [item for result in results if result for item in result]
        return [result for result in results if result]

    async def process(self, df: pd.DataFrame | list):
        """执行完整处理流程"""
        # 判断最终保存文件是否存在
        if os.path.exists(self.output_path):
            self.logger.info(f"[输出] {self.task_type}任务 {self.task_id} 已存在，跳过处理")
            return pd.read_parquet(self.output_path)
        self.load_cache()
        self.logger.info(f"[数据] {self.task_type}任务 {self.task_id}：共 {len(df)} 条")

        for i in tqdm(range(0, len(df), self.batch_size)):
            if isinstance(df, pd.DataFrame):
                batch = df.iloc[i : i + self.batch_size]
            elif isinstance(df, list):
                batch = df[i : i + self.batch_size]
            else:
                raise TypeError(f"Unsupported data type: {type(df)}")
            new_rows = await self.process_batch(batch)
            self.cache_data.extend(new_rows)

            if (i // self.batch_size + 1) % self.save_interval == 0 and len(self.cache_data) > 0:
                self.logger.info(f"[进度] {self.task_type}任务 {self.task_id} - 批次缓存")
                self.save_cache()

        # 最终保存结果
        df_final = pd.DataFrame(self.cache_data)

        df_final.to_parquet(self.output_path, index=False)
        self.logger.info(f"[完成] {self.task_type}任务 {self.task_id} 输出保存到 {self.output_path}")
        return df_final

    @abstractmethod
    async def run(self) -> None:
        pass

    @abstractmethod
    async def process_row(self, row: pd.Series) -> dict | None:
        """抽象方法：处理单个信息行"""

import random
from types import SimpleNamespace

import pytest

from auto_teacher_process.run_worker.services.run_associated_teacher_leader import RunTeacherLeaderAssociatedProcessor
from auto_teacher_process.run_worker.services.run_infos_extract import TeacherInfoProcessor

pytestmark = pytest.mark.asyncio


class DummyArgs:
    def __init__(self):
        self.save_dir = "/home/personnel-matching-data-process-algo/auto_teacher_process/tmp"
        self.sub = 1
        self.all = 1
        self.province = "北京市"
        self.query_sql = "SELECT * FROM fake_table"
        self.primary_key_field = "id"


# @pytest.fixture
# def processor():
#     args = DummyArgs()
#     processor = QwenTeacherNameProcessor(args)
#     return processor


# async def test_process_row_real_llm(processor):
#     row = pd.Series({
#         "id": 1,
#         "teacher_name": "Dr. 张伟 (Tsinghua University)",
#         "description": "张伟，男，博士，清华大学教授，研究人工智能。",
#         "province": "北京市",
#         "school_name": "清华大学",
#         "college_name": "计算机系"
#     })

#     result = await processor.process_row(row)

#     assert result is not None
#     print("处理结果：", result)


#     assert result["raw_data_id"] == 1
#     assert result["province_code"] == 11
#     assert isinstance(result["derived_teacher_name"], str)
#     assert result["derived_teacher_name"] != ""
#     assert result["is_valid"] in (0, 1)
#     assert result["is_en"] in (0, 1)
def get_real_args():
    return SimpleNamespace(
        save_dir="/home/personnel-matching-data-process-algo/auto_teacher_process/tmp/",  # ✅ 真实缓存路径
        id1=1,
        id2=10,
        task_id=1,
        task_type="NAME_PROCESS",
        query_sql="""
            SELECT teacher_id, derived_teacher_name, description, is_en
            FROM derived_teacher_data
            WHERE province = '广东省'
            LIMIT 5
        """,  # ✅ 真实 SQL 查询
        primary_key_field="teacher_id",
        need_en=1,
    )


async def test_full_real_pipeline():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--province', required=True, help='省份名')
    # parser.add_argument('--save_dir', default='./output', help='缓存输出目录')
    # parser.add_argument('--query_sql', required=True, help='用于获取原始数据的SQL')
    # parser.add_argument('--primary_key_field', default='raw_data_id')
    # parser.add_argument('--sub', default='default', help='子任务名')
    # parser.add_argument('--all', default='default', help='任务名')
    # parser.add_argument('--need_en', default='default', help='任务名')

    # args = parser.parse_args()
    # args.province = "广东省"
    # args.sub = 1
    # args.save_dir ="/home/personnel-matching-data-process-algo/auto_teacher_process/tmp/",  # ✅ 真实缓存路径
    # args.query_sql="""
    #         SELECT teacher_id, derived_teacher_name, description, is_en
    #         FROM derived_teacher_data
    #         WHERE province = '广东省'
    #         LIMIT 5
    #     """
    # args.primary_key_field="teacher_id",
    # args.need_en = 1
    message = get_real_args()
    processor = TeacherInfoProcessor(message)
    # insert_processor = NameInsertProcessor()
    # df = insert_processor.get_db(args.query_sql)
    await processor.run()
    # insert_processor.process({
    #             'province': args.province,
    #             'file_dir': os.path.join(args.save_dir, args.province)
    #         })
    print(f"✅ 全流程真实执行完成，请检查 {message.save_dir} 下的缓存/最终 Parquet 文件")


async def test_associated_teacher_leader():
    args = SimpleNamespace(task_id=random.randint(1, 100000000), task_args={"school_name": "广州大学"})
    processer = RunTeacherLeaderAssociatedProcessor(args)

    await processer.run()

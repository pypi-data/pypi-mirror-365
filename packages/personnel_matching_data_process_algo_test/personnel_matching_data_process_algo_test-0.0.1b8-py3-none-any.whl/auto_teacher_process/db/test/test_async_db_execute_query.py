import pytest
import pandas as pd
from auto_teacher_process.db.db_base import BaseDBProcessor


class TestAsyncDBProcessor(BaseDBProcessor):
    def process(self, input_data):
        pass


@pytest.mark.asyncio
async def test_fetch_paper_by_title():
    process = TestAsyncDBProcessor()
    query = """
    SELECT id, author_list, addresses, affiliations, title
    FROM raw_teacher_paper
    WHERE title = %s ;
    """
    title_params = ("Effective Long Afterglow Amplification Induced by Surface Coordination Interaction",)

    await process.set_up_async_db_engine()
    result = await process.async_db_execute_query(query, title_params)
    await process.close_async_db_engine()

    process.logger.info(result)
    print(result)
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert isinstance(result.iloc[0], pd.Series)


@pytest.mark.asyncio
async def test_fetch_teacher_name_by_id():
    process = TestAsyncDBProcessor()
    query = """
    SELECT derived_teacher_name
    FROM derived_intl_teacher_data
    WHERE teacher_id = %s ;
    """
    id_params = ("6c9caa3a-6e78-46a8-b404-809293b690f3",)

    await process.set_up_async_db_engine()
    result = await process.async_db_execute_query(query, id_params, "one")
    await process.close_async_db_engine()

    process.logger.info(result[0] if result else None)

    assert result == ("Fraser H. Brown",)


@pytest.mark.asyncio
async def test_uninitialized_db_engine_error():
    process = TestAsyncDBProcessor()
    query = "SELECT 1"

    # 验证未初始化数据库引擎时抛出ConnectionError
    with pytest.raises(ConnectionError) as exc_info:
        await process.async_db_execute_query(query)

    assert "请先初始化异步数据库引擎" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_fetch_type_error():
    process = TestAsyncDBProcessor()
    query = "SELECT 1"

    await process.set_up_async_db_engine()

    # 验证无效的fetch_type参数抛出ValueError
    with pytest.raises(ValueError) as exc_info:
        await process.async_db_execute_query(query, fetch_type="invalid")

    assert "无效的fetch_type: invalid" in str(exc_info.value)

    await process.close_async_db_engine()


@pytest.mark.asyncio
async def test_invalid_execute_type_error():
    process = TestAsyncDBProcessor()
    query = "SELECT 1"

    await process.set_up_async_db_engine()

    # 验证无效的fetch_type参数抛出ValueError
    with pytest.raises(ValueError) as exc_info:
        await process.async_db_execute_query(query, execute_type="invalid")

    assert "无效的execute_type: invalid" in str(exc_info.value)

    await process.close_async_db_engine()

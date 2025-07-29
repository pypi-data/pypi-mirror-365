import pytest

from auto_teacher_process.db.services.es_operator import ESOperator


@pytest.mark.asyncio
async def test_async_es_to_df_by_title_idx_paper():
    es = ESOperator()
    result = await es.async_es_to_df_by_title_idx_paper("deep learning")
    await es.close_es_engine()
    # DataFrame 断言
    assert result is not None
    assert not result.empty


@pytest.mark.asyncio
async def test_async_es_to_df_by_affiliation_idx_paper():
    es = ESOperator()
    result = await es.async_es_to_df_by_affiliation_idx_paper("Guangzhou University")
    await es.close_es_engine()
    # DataFrame 断言
    assert result is not None
    assert not result.empty

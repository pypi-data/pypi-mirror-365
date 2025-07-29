from unittest.mock import patch

import pandas as pd
import pytest

from auto_teacher_process.db.services.db_insert_relation import RelationInsertDBProcessor


# 测试参数缺失场景
def test_process_missing_parameters(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(RelationInsertDBProcessor, "_setup_db_engine")
    processor = RelationInsertDBProcessor()

    # 缺少province参数
    with pytest.raises(ValueError):
        processor.process({"file_dir": "/test/dir", "type": "paper"})

    # 缺少file_dir参数
    with pytest.raises(ValueError):
        processor.process({"province": "test_province", "type": "paper"})

    # 缺少type参数
    with pytest.raises(ValueError):
        processor.process({"province": "test_province", "file_dir": "/test/dir"})


# 测试paper关系数据处理
def test_process_paper_relation(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(RelationInsertDBProcessor, "_setup_db_engine")
    processor = RelationInsertDBProcessor()

    # 模拟_get_all_folders返回测试数据
    mock_df = pd.DataFrame(
        {"teacher_id": [101, 102, 103], "paper_id": [201, 202, 203], "orcid": ["orcid1", "orcid2", "orcid3"]}
    )
    mocker.patch.object(processor, "_get_all_folders", return_value=mock_df)

    # 模拟insert_db方法
    mock_insert_db = mocker.patch.object(processor, "insert_db")

    # 调用process方法
    processor.process({"province": "test_province", "file_dir": "/test/dir", "type": "paper"})

    # 验证处理结果
    assert mock_insert_db.call_count == 1
    call_args = mock_insert_db.call_args[1]
    assert call_args["table_name"] == "product_teacher_paper_relation"
    assert len(call_args["df"]) == 3
    assert "orcid" not in call_args["df"].columns  # 验证paper类型时orcid列被移除


# 测试cn_paper关系数据处理
def test_process_cn_paper_relation(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(RelationInsertDBProcessor, "_setup_db_engine")
    processor = RelationInsertDBProcessor()

    # 模拟_get_all_folders返回测试数据
    mock_df = pd.DataFrame({"teacher_id": [101, 102, 103], "paper_id": [201, 202, 203]})
    mocker.patch.object(processor, "_get_all_folders", return_value=mock_df)

    # 模拟insert_db方法
    mock_insert_db = mocker.patch.object(processor, "insert_db")

    # 调用process方法
    processor.process({"province": "test_province", "file_dir": "/test/dir", "type": "cn_paper"})

    # 验证处理结果
    assert mock_insert_db.call_count == 1
    call_args = mock_insert_db.call_args[1]
    assert call_args["table_name"] == "product_teacher_cn_paper_relation"
    assert "paper_id" in call_args["df"].columns  # 验证cn_paper类型时paper_id列存在


# 测试project关系数据处理
def test_process_project_relation(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(RelationInsertDBProcessor, "_setup_db_engine")
    processor = RelationInsertDBProcessor()

    # 模拟_get_all_folders返回测试数据
    mock_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "teacher_id": [101, 102, 103],
            "project_id": [301, 302, 303],
            "project_level": ["A", "B", "A"],
        }
    )
    mocker.patch.object(processor, "_get_all_folders", return_value=mock_df)

    # 模拟insert_db方法
    mock_insert_db = mocker.patch.object(processor, "insert_db")

    # 模拟to_csv方法
    mock_to_csv = mocker.patch.object(pd.DataFrame, "to_csv")

    # 调用process方法
    processor.process({"province": "test_province", "file_dir": "/test/dir", "type": "project"})

    # 验证处理结果
    assert mock_insert_db.call_count == 1
    call_args = mock_insert_db.call_args[1]
    assert call_args["table_name"] == "product_teacher_project_relation"
    assert "is_from_match" in call_args["df"].columns  # 验证project类型添加了新列
    assert "project_level" not in call_args["df"].columns  # 验证project_level列被移除

    # 验证教师项目等级文件保存
    assert mock_to_csv.call_count == 1
    assert "test_province_teacher_project_level.csv" in mock_to_csv.call_args[0][0]


# 测试空数据处理场景
def test_process_empty_data(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(RelationInsertDBProcessor, "_setup_db_engine")
    processor = RelationInsertDBProcessor()

    # 模拟_get_all_folders返回空DataFrame
    mocker.patch.object(processor, "_get_all_folders", return_value=pd.DataFrame())

    # 模拟insert_db方法
    mock_insert_db = mocker.patch.object(processor, "insert_db")

    # 调用process方法
    processor.process({"province": "test_province", "file_dir": "/test/dir", "type": "paper"})

    # 验证insert_db未被调用
    mock_insert_db.assert_not_called()


# 测试文件系统操作模拟
@patch("os.walk")
def test_file_processing(mock_walk, mocker):
    # 设置模拟返回值
    mock_walk.return_value = [
        ("/test/dir", [], ["file1.csv", "test_province_file2.csv"]),
        ("/test/dir/sub", [], ["test_province_file3.csv"]),
    ]

    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(RelationInsertDBProcessor, "_setup_db_engine")
    processor = RelationInsertDBProcessor()

    # 模拟pd.read_csv
    mock_read_csv = mocker.patch("pandas.read_csv")
    mock_read_csv.side_effect = [
        pd.DataFrame({"teacher_id": [101], "paper_id": [201], "orcid": [1]}),
        pd.DataFrame({"teacher_id": [102], "paper_id": [202], "orcid": [2]}),
    ]

    # 模拟insert_db
    mock_insert_db = mocker.patch.object(processor, "insert_db")

    # 调用process方法
    processor.process({"province": "test_province", "file_dir": "/test/dir", "type": "paper"})

    # 验证文件读取次数
    assert mock_read_csv.call_count == 2
    assert mock_insert_db.call_count == 1

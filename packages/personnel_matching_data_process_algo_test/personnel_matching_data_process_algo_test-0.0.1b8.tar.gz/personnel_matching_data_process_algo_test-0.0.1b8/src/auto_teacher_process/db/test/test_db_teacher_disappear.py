import pandas as pd
import pytest

from auto_teacher_process.db.services.db_teacher_disappear import TeacherDisappearDBProcessor


def test_process_by_teacher_id(mocker):
    # mock数据库初始化
    mocker.patch.object(TeacherDisappearDBProcessor, "_setup_db_engine")
    processor = TeacherDisappearDBProcessor()

    # mock get_db
    def fake_get_db(query):
        if "FROM derived_teacher_data" in query:
            return pd.DataFrame(
                [
                    {
                        "derived_teacher_name": "何奎",
                        "school_name": "东莞理工学院",
                        "raw_data_id": 18,
                        "description": "与热质传递机(这是其中一部分)",
                    }
                ]
            )
        if "FROM raw_teacher_data" in query:
            return pd.DataFrame([{"link": "http://test-link.com"}])
        return pd.DataFrame([])

    mocker.patch.object(processor, "get_db", side_effect=fake_get_db)
    input_data = {"type": "by_teacher_id", "teacher_id": "be14ced9-108c-433e-994c-5a4eabefacea"}
    result = processor.process(input_data)
    assert result["derived_teacher_name"] == "何奎"
    assert result["school_name"] == "东莞理工学院"
    assert result["description"].startswith("与热质传递机")
    assert result["link"] == "http://test-link.com"


def test_process_by_name_and_school(mocker):
    mocker.patch.object(TeacherDisappearDBProcessor, "_setup_db_engine")
    processor = TeacherDisappearDBProcessor()

    def fake_get_db(query):
        if "FROM derived_teacher_data" in query:
            return pd.DataFrame(
                [{"description": "与热质传递机(这是其中一部分)"}, {"description": "与热质传递机(另一部分)"}]
            )
        return pd.DataFrame([])

    mocker.patch.object(processor, "get_db", side_effect=fake_get_db)
    input_data = {"type": "by_name_and_school", "derived_teacher_name": "何奎", "school_name": "东莞理工学院"}
    result = processor.process(input_data)
    assert isinstance(result, list)
    assert len(result) == 2
    for item in result:
        assert item["derived_teacher_name"] == "何奎"
        assert item["school_name"] == "东莞理工学院"
        assert item["description"].startswith("与热质传递机")


def test_process_missing_teacher_id(mocker):
    mocker.patch.object(TeacherDisappearDBProcessor, "_setup_db_engine")
    processor = TeacherDisappearDBProcessor()
    # 缺少teacher_id
    input_data = {"type": "by_teacher_id"}
    with pytest.raises(ValueError) as excinfo:
        processor.process(input_data)
    assert "teacher_id" in str(excinfo.value)


def test_process_missing_name_or_school(mocker):
    mocker.patch.object(TeacherDisappearDBProcessor, "_setup_db_engine")
    processor = TeacherDisappearDBProcessor()
    # 缺少derived_teacher_name
    input_data1 = {"type": "by_name_and_school", "school_name": "东莞理工学院"}
    with pytest.raises(ValueError) as excinfo1:
        processor.process(input_data1)
    assert "derived_teacher_name" in str(excinfo1.value) or "school_name" in str(excinfo1.value)
    # 缺少school_name
    input_data2 = {"type": "by_name_and_school", "derived_teacher_name": "何奎"}
    with pytest.raises(ValueError) as excinfo2:
        processor.process(input_data2)
    assert "derived_teacher_name" in str(excinfo2.value) or "school_name" in str(excinfo2.value)


def test_process_invalid_type(mocker):
    mocker.patch.object(TeacherDisappearDBProcessor, "_setup_db_engine")
    processor = TeacherDisappearDBProcessor()
    input_data = {"type": "not_exist_type"}
    with pytest.raises(ValueError) as excinfo:
        processor.process(input_data)
    assert "type" in str(excinfo.value)


def test_set_teacher_invalid_by_id(mocker):
    mocker.patch.object(TeacherDisappearDBProcessor, "_setup_db_engine")
    processor = TeacherDisappearDBProcessor()
    mock_update_db = mocker.patch.object(processor, "update_db")
    teacher_id = 123
    processor.set_teacher_invalid_by_id(teacher_id)
    # 检查SQL和参数
    assert mock_update_db.called
    args, kwargs = mock_update_db.call_args
    assert "UPDATE derived_teacher_data" in kwargs["update_sql"]
    assert kwargs["df"]["teacher_id"].iloc[0] == teacher_id


def test_process_set_invalid_by_teacher_id(mocker):
    mocker.patch.object(TeacherDisappearDBProcessor, "_setup_db_engine")
    processor = TeacherDisappearDBProcessor()
    mock_set_invalid = mocker.patch.object(processor, "set_teacher_invalid_by_id")
    teacher_id = 456
    input_data = {"type": "set_invalid_by_teacher_id", "teacher_id": teacher_id}
    result = processor.process(input_data)
    mock_set_invalid.assert_called_once_with(teacher_id)
    assert result == {"status": "success"}

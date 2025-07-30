from unittest.mock import patch

import pandas as pd
import pytest

from auto_teacher_process.db.services.db_insert_html import HTMLInsertDBProcessor


# 测试参数缺失场景
def test_run_missing_parameters(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(HTMLInsertDBProcessor, "_setup_db_engine")  # 避免实际数据库连接
    processor = HTMLInsertDBProcessor()

    # 调用run方法 - 缺少province
    with pytest.raises(ValueError):
        processor.run({"file_dir": "/test/dir"})

    # 调用run方法 - 缺少file_dir
    with pytest.raises(ValueError):
        processor.run({"province": "test_province"})


# 测试文件处理场景
@patch("os.walk")
@patch("pandas.read_csv")
def test_run_file_processing(mock_read_csv, mock_walk, mocker):
    # 设置模拟返回值
    mock_walk.return_value = [
        ("/test/dir", ["sub1", "sub2", "sub3"], []),  # 第一级目录
        ("/test/dir/sub1", [], ["test_province_file.csv"]),  # 子目录及匹配文件
        ("/test/dir/sub2", [], ["not_csv_file.txt"]),  # 子目录及匹配文件
        ("/test/dir/sub3", [], ["test_province_file.csv"]),  # 子目录及匹配文件
    ]

    # 创建模拟DataFrame（文件名必须包含'test_province'）
    mock_df1 = pd.DataFrame(
        {
            "teacher_id": [1, 2],
            "is_repeat": [1, 0],
            "related_teacher_id": [10, None],
            "status": ["active", "inactive"],
            "is_valid": [1, 1],
            "is_en": [1, 0],
            "extracted_description": ["测试描述1", "测试描述2"],
        }
    )
    mock_df2 = pd.DataFrame(
        {
            "teacher_id": [3],
            "is_repeat": [1],
            "related_teacher_id": [20],
            "status": ["active"],
            "is_valid": [1],
            "is_en": [1],
            "extracted_description": ["测试描述3"],
        }
    )

    # 设置read_csv的模拟返回值（文件名需包含'test_province'）
    mock_read_csv.side_effect = [
        mock_df1,  # sub1/test_province_file.csv
        mock_df2,  # sub3/test_province_file.csv
    ]

    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(HTMLInsertDBProcessor, "_setup_db_engine")  # 避免实际数据库连接
    processor = HTMLInsertDBProcessor()
    mocker.patch.object(processor, "update_db")

    # 调用run方法
    input_data = {
        "province": "test_province",  # 确保与文件名匹配
        "file_dir": "/test/dir",
    }
    processor.run(input_data)

    # 验证文件读取次数（仅匹配包含'test_province'的文件）
    assert mock_read_csv.call_count == 2  # 修改为实际匹配的文件数

    # 验证update_db调用
    processor.update_db.assert_called_once()
    call_args = processor.update_db.call_args[1]


# 测试数据库更新场景
def test_update_db_call(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(HTMLInsertDBProcessor, "_setup_db_engine")  # 避免实际数据库连接
    processor = HTMLInsertDBProcessor()

    # 模拟_get_all_folders方法
    mocker.patch.object(
        processor,
        "_get_all_folders",
        return_value=pd.DataFrame(
            {
                "teacher_id": [1, 2],
                "is_repeat": [1, 1],
                "related_teacher_id": [10, 20],
                "status": ["active", "inactive"],
                "is_valid": [1, 1],
                "is_en": [1, 0],
                "extracted_description": ["测试描述1", "测试描述2"],
            }
        ),
    )

    # 模拟update_db方法
    mock_update_db = mocker.patch.object(processor, "update_db")

    # 调用process方法
    processor.process({"province": "test_province", "file_dir": "/test/dir"})

    # 验证update_db调用参数
    mock_update_db.assert_called_once()
    call_args = mock_update_db.call_args[1]
    assert call_args["update_sql"].strip().startswith("UPDATE derived_teacher_data")


# 测试空数据处理场景
@patch("os.listdir")
@patch("os.path.isdir")
def test_run_empty_data(mock_isdir, mock_listdir, mocker):
    # 设置模拟返回值
    mock_listdir.return_value = []
    mock_isdir.return_value = True

    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(HTMLInsertDBProcessor, "_setup_db_engine")  # 避免实际数据库连接
    processor = HTMLInsertDBProcessor()
    mocker.patch.object(processor, "update_db")

    # 调用run方法
    input_data = {"province": "test_province", "file_dir": "/test/dir"}
    processor.run(input_data)

    # 验证update_db未被调用
    processor.update_db.assert_not_called()

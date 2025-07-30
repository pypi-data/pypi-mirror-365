import json

import pandas as pd
import pytest

from auto_teacher_process.db.services.db_insert_famous_projects import FamousProjectsInsertDBProcessor


# 测试参数缺失场景
def test_run_missing_parameters(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(FamousProjectsInsertDBProcessor, "_setup_db_engine")  # 避免实际数据库连接
    processor = FamousProjectsInsertDBProcessor()

    # 调用run方法 - 缺少province
    with pytest.raises(ValueError):
        processor.run({"query_sql": "test_sql"})

    # 调用run方法 - 缺少query_sql
    with pytest.raises(ValueError):
        processor.run({"province": "test_province"})


# 测试数据库查询场景
def test_database_query(mocker):
    # 创建处理器实例并模拟数据库初始化
    mocker.patch.object(FamousProjectsInsertDBProcessor, "_setup_db_engine")  # 避免实际数据库连接

    # 模拟get_db返回值
    mock_get_db = mocker.patch.object(FamousProjectsInsertDBProcessor, "get_db")

    def get_db_retrun(query):
        if "SELECT p.teacher_id" in query:
            return pd.DataFrame(
                {
                    "teacher_id": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
                    "project_experience": [
                        # 教师1001：有主持和参与项目
                        json.dumps(
                            {
                                "主持的项目": ["Python教学系统开发国家重点项目"],
                                "参与的项目": ["AI课程设计", "教育大数据分析平台"],
                            },
                            ensure_ascii=False,
                        ),
                        # 教师1002：只有参与项目
                        json.dumps(
                            {"主持的项目": [], "参与的项目": ["在线考试系统", "智能课堂助手"]}, ensure_ascii=False
                        ),
                        # 教师1003：无项目经验 (空值)
                        json.dumps(
                            {"主持的项目": ["AI大模型首席科学家"], "参与的项目": ["智能课堂助手"]}, ensure_ascii=False
                        ),
                        # 教师1004：有主持和参与项目
                        json.dumps(
                            {"主持的项目": ["教育大数据分析平台子课题"], "参与的项目": ["Python教学系统开发"]},
                            ensure_ascii=False,
                        ),
                        # 教师1005：只有主持项目
                        json.dumps({"主持的项目": ["智能课堂助手"], "参与的项目": []}, ensure_ascii=False),
                        # 教师1006：多个主持项目
                        json.dumps(
                            {"主持的项目": ["AI课程设计", "在线考试系统"], "参与的项目": ["教育大数据分析平台子课题"]},
                            ensure_ascii=False,
                        ),
                        # 教师1007：无主持项目，多个参与项目
                        json.dumps(
                            {
                                "主持的项目": [],
                                "参与的项目": ["Python教学系统开发国家科技重大专项", "智能课堂助手", "AI课程设计"],
                            },
                            ensure_ascii=False,
                        ),
                        # 教师1008：空项目列表
                        json.dumps({"主持的项目": [], "参与的项目": []}, ensure_ascii=False),
                        # 教师1009：只有主持项目
                        json.dumps({"主持的项目": ["教育大数据分析平台"], "参与的项目": []}, ensure_ascii=False),
                        # 教师1010
                        json.dumps(
                            {"主持的项目": [], "参与的项目": ["教育大数据分析平台国家科技重大专项"]},
                            ensure_ascii=False,
                        ),
                    ],
                    "is_valid": [1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
                }
            )
        return pd.DataFrame(
            {
                "teacher_id": [1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011],
                "project_level": ["A", "B", "C", "A", "D", "A", "B", "C", "A", "B"],
            }
        )

    mock_get_db.side_effect = get_db_retrun

    # 模拟insert_db方法
    mock_insert_db = mocker.patch.object(FamousProjectsInsertDBProcessor, "insert_db")

    # 创建测试实例
    processor = FamousProjectsInsertDBProcessor()

    # 准备测试输入
    input_data = {"province": "test_province", "query_sql": "test_sql"}

    # 执行测试
    processor.run(input_data)

    # 验证get_db被调用两次（教师项目数据和挂载项目关系）
    assert mock_get_db.call_count == 2

    # 验证insert_db调用
    mock_insert_db.assert_called_once()
    call_args = mock_insert_db.call_args[1]
    assert len(call_args["df"]) == 10  # 验证数据量

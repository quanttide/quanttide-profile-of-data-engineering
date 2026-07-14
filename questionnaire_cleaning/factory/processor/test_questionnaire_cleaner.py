"""
QuestionnaireCleaner 单元测试

重点针对清洗器的核心转换方法：
- 异常值转换逻辑 (异常收入置空、工作负荷越界标记)
- 多选题拆分逻辑
- 逻辑矛盾校验标记 (如学生身份、退休年龄冲突等)
- 重复值标记与去重
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 添加处理器目录到路径
pipeline_dir = Path(__file__).resolve().parent
processor_dir = pipeline_dir.parent / "processor"
sys.path.insert(0, str(processor_dir))

from questionnaire_cleaner import QuestionnaireCleaner


@pytest.fixture
def cleaner():
    """初始化清洗器实例"""
    return QuestionnaireCleaner()


@pytest.fixture
def mock_raw_data():
    """构造一个包含各种异常噪声的模拟 DataFrame 样本"""
    return pd.DataFrame([
        # 正常数据
        {
            "提交答卷时间": "2023/10/1 12:00:00",
            "您的年龄": "28",
            "您的总工作年限": "5",
            "您目前的月收入": "8000",
            "您目前所在部门": "技术部",
            "您目前的整体满意度": "4",
            "您目前的工作负荷": "3",
            "您的性别": "男",
            "您的最高学历": "本科",
            "您目前的就业状态": "全职员工",
            "您在目前单位的工作年限": "3",
            "您目前所在的城市": "北京",
            "您目前享受的福利支持": "基本养老保险（五险一金等）⁪定期带薪年假",
            "其他说明": "无"
        },
        # 异常收入与越界工作负荷
        {
            "提交答卷时间": "2023/10/1 12:05:00",
            "您的年龄": "35",
            "您的总工作年限": "10",
            "您目前的月收入": "-500",  # 负数收入异常值
            "您目前所在部门": "财务部",
            "您目前的整体满意度": "3",
            "您目前的工作负荷": "99",  # 越界工作负荷
            "您的性别": "女",
            "您的最高学历": "硕士",
            "您目前的就业状态": "全职员工",
            "您在目前单位的工作年限": "5",
            "您目前所在的城市": "上海",
            "您目前享受的福利支持": "定期带薪年假",
            "其他说明": "测试"  # 测试数据标识
        },
        # 逻辑矛盾：学生身份有工作经验
        {
            "提交答卷时间": "2023/10/1 12:10:00",
            "您的年龄": "19",
            "您的总工作年限": "8",  # 19岁不可能工作8年
            "您目前的月收入": "3000",
            "您目前所在部门": "其他",
            "您目前的整体满意度": "3",
            "您目前的工作负荷": "3",
            "您的性别": "女",
            "您的最高学历": "大专及以下",
            "您目前的就业状态": "学生",  # 学生身份
            "您在目前单位的工作年限": "2",
            "您目前所在的城市": "深圳",
            "您目前享受的福利支持": "无",
            "其他说明": ""
        },
        # 重复记录（与第一条内容完全一致，仅提交时间或极细微处不同）
        {
            "提交答卷时间": "2023/10/1 12:00:00",
            "您的年龄": "28",
            "您的总工作年限": "5",
            "您目前的月收入": "8000",
            "您目前所在部门": "技术部",
            "您目前的整体满意度": "4",
            "您目前的工作负荷": "3",
            "您的性别": "男",
            "您的最高学历": "本科",
            "您目前的就业状态": "全职员工",
            "您在目前单位的工作年限": "3",
            "您目前所在的城市": "北京",
            "您目前享受的福利支持": "基本养老保险（五险一金等）⁪定期带薪年假",
            "其他说明": "无"
        }
    ])


class TestQuestionnaireCleaner:
    """问卷清洗器核心逻辑单元测试"""

    def test_column_rename_and_mapping(self, cleaner, mock_raw_data):
        """测试字段名是否正确映射为英文"""
        processed_df = cleaner.process(mock_raw_data)
        
        expected_cols = ["id", "submit_time", "age", "total_exp", "dept", "monthly_income"]
        for col in expected_cols:
            assert col in processed_df.columns

    def test_negative_income_handling(self, cleaner, mock_raw_data):
        """测试异常负数收入是否被转换为 Null (None/NaN)"""
        processed_df = cleaner.process(mock_raw_data)
        
        # 第二条记录的月收入为 -500，应当被置空
        converted_income = processed_df.loc[1, "monthly_income"]
        assert pd.isna(converted_income) or converted_income is None

    def test_workload_extreme_value_flag(self, cleaner, mock_raw_data):
        """测试工作负荷越界时，是否被打上了正确的标记"""
        processed_df = cleaner.process(mock_raw_data)
        
        # 第二条记录的工作负荷为 99，属于越界
        flag = processed_df.loc[1, "data_quality_flag"]
        assert "工作负荷越界" in flag or "异常值" in flag

    def test_student_logic_validation(self, cleaner, mock_raw_data):
        """测试学生状态与其工作经验冲突时的逻辑校验标记"""
        processed_df = cleaner.process(mock_raw_data)
        
        # 第三条记录：学生身份却有 8 年工作经验
        flag = processed_df.loc[2, "data_quality_flag"]
        assert "逻辑校验_学生" in flag or "学生" in flag

    def test_multi_select_split(self, cleaner, mock_raw_data):
        """测试多选题字段拆分"""
        processed_df = cleaner.process(mock_raw_data)
        
        # 第一条数据包含："基本养老保险（五险一金等）" 和 "定期带薪年假"
        assert processed_df.loc[0, "benefit_pension"] is True
        assert processed_df.loc[0, "benefit_annual_leave"] is True
        assert processed_df.loc[0, "benefit_health_ins"] is False

    def test_duplicate_marking(self, cleaner, mock_raw_data):
        """测试重复项被识别并打上 `is_duplicate` 和标记"""
        processed_df = cleaner.process(mock_raw_data)
        
        # 理论上第 1 条和第 4 条是完全重复的数据
        assert processed_df.loc[3, "is_duplicate"] is True
        assert "重复记录" in processed_df.loc[3, "data_quality_flag"]
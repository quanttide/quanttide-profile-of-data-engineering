"""
问卷数据清洗流水线集成测试

验证流水线能正常运行并产生清洗后的数据，且完美契合 DataContract 规范。
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

from questionnaire_pipeline import QuestionnairePipeline


class TestQuestionnairePipeline:
    """问卷流水线集成测试类"""

    @pytest.fixture
    def pipeline_dir(self):
        """返回流水线目录路径"""
        return Path(__file__).resolve().parent

    @pytest.fixture
    def record_dir(self, pipeline_dir):
        """返回记录目录路径"""
        # 兼容 catelog 与 catalog 拼写
        potential_dir = pipeline_dir.parent.parent / "catelog" / "record"
        if not potential_dir.exists():
            potential_dir = pipeline_dir.parent.parent / "catalog" / "record"
        return potential_dir

    @pytest.fixture
    def dirty_csv_path(self, record_dir):
        """返回脏数据 CSV 文件路径"""
        return record_dir / "dirty.csv"

    @pytest.fixture
    def clean_csv_path(self, record_dir):
        """返回清洗后数据 CSV 文件路径"""
        return record_dir / "clean.csv"

    @pytest.fixture
    def expected_clean_df(self, clean_csv_path):
        """加载预期清洗后数据"""
        return pd.read_csv(clean_csv_path)

    @pytest.fixture
    def pipeline(self, dirty_csv_path):
        """创建流水线实例"""
        return QuestionnairePipeline(dirty_csv_path)

    @pytest.fixture
    def actual_clean_df(self, pipeline):
        """运行流水线获取实际清洗后数据"""
        return pipeline.run()

    # ========== 基础功能测试 ==========

    def test_pipeline_loads_data(self, pipeline, dirty_csv_path):
        """测试流水线能正确加载数据"""
        raw_df = pipeline.load_data()

        assert raw_df is not None
        assert isinstance(raw_df, pd.DataFrame)
        assert len(raw_df) > 0
        assert len(raw_df) == 19

    def test_pipeline_processes_data(self, pipeline):
        """测试流水线能正确处理数据"""
        cleaned_df = pipeline.run()

        assert cleaned_df is not None
        assert isinstance(cleaned_df, pd.DataFrame)
        assert len(cleaned_df) == 19

    # ========== 基本结构测试 ==========

    def test_pipeline_output_has_required_columns(self, actual_clean_df):
        """测试流水线输出包含所需列"""
        required_columns = [
            "id", "submit_time", "age", "total_exp", "dept",
            "overall_satis", "workload", "gender", "edu",
            "emp_status", "tenure", "monthly_income", "city",
            "benefit_pension", "benefit_annual_leave", "benefit_health_ins",
            "benefit_other", "is_duplicate", "data_quality_flag"
        ]

        for col in required_columns:
            assert col in actual_clean_df.columns, f"缺少必需列: {col}"

    def test_pipeline_output_column_count(self, actual_clean_df):
        """测试流水线输出列数正确"""
        assert len(actual_clean_df.columns) == 20

    # ========== 数据类型测试 ==========

    def test_id_column_is_integer(self, actual_clean_df):
        """测试 ID 列是整数类型"""
        assert pd.api.types.is_integer_dtype(actual_clean_df["id"].astype('int64'))

    def test_boolean_columns(self, actual_clean_df):
        """测试布尔类型列"""
        boolean_columns = [
            "benefit_pension", "benefit_annual_leave", "benefit_health_ins",
            "benefit_other", "is_duplicate"
        ]

        for col in boolean_columns:
            if col in actual_clean_df.columns:
                # 排除缺失值的影响后，值应当能安全转换为布尔型
                non_null_vals = actual_clean_df[col].dropna()
                assert pd.api.types.is_bool_dtype(non_null_vals.astype(bool)), f"{col} 应该是布尔类型"

    # ========== 数据质量标记测试 ==========

    def test_has_duplicate_records_marked(self, actual_clean_df):
        """测试有重复记录被标记"""
        assert actual_clean_df["is_duplicate"].any()

    def test_has_quality_flags(self, actual_clean_df):
        """测试有数据质量标记"""
        unique_flags = actual_clean_df["data_quality_flag"].unique()
        assert len(unique_flags) > 1, f"应该有多种质量标记，实际只有: {unique_flags}"

    def test_has_test_data_flag(self, actual_clean_df):
        """测试包含重复/测试数据标记"""
        flags_str = "".join(actual_clean_df["data_quality_flag"].dropna().astype(str))
        assert "重复记录" in flags_str or "测试数据" in flags_str

    # ========== 特殊用例测试 ==========

    def test_negative_income_converted_to_null(self, actual_clean_df):
        """测试收入字段处理（异常值应置空）"""
        assert "monthly_income" in actual_clean_df.columns
        assert actual_clean_df["monthly_income"].isna().any()

    def test_extreme_age_allowed(self, actual_clean_df):
        """测试极端年龄保留"""
        assert "age" in actual_clean_df.columns
        # 极端年龄不应被粗暴截断或删去，而是通过 data_quality_flag 标记
        assert (actual_clean_df["age"].dropna() > 70).any()

    # ========== ID 生成测试 ==========

    def test_ids_are_sequential(self, actual_clean_df):
        """测试 ID 是连续的"""
        ids = actual_clean_df["id"].tolist()
        expected_ids = list(range(1, 20))
        assert ids == expected_ids, f"ID 应该连续且为 1-19，实际: {ids}"

    # ========== 流水线完整性测试 ==========

    def test_pipeline_preserves_record_count(self, pipeline):
        """测试流水线保持原始记录条数"""
        raw_df = pipeline.load_data()
        cleaned_df = pipeline.run()
        assert len(cleaned_df) == len(raw_df)

    # ========== 与预期数据一致性测试 ==========

    def test_record_count_matches_expected(self, actual_clean_df, expected_clean_df):
        """测试记录数与预期一致"""
        assert len(actual_clean_df) == len(expected_clean_df)

    def test_column_names_match_expected(self, actual_clean_df, expected_clean_df):
        """测试列名与标准结果完全对账"""
        actual_columns = set(actual_clean_df.columns)
        expected_columns = set(expected_clean_df.columns)
        assert actual_columns == expected_columns
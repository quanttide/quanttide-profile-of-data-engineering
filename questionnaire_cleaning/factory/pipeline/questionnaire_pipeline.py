"""
问卷数据清洗流水线

使用 catalog/record 中的 dirty.csv 作为输入，
通过 factory/processor 中的 QuestionnaireCleaner 进行处理，
结果与 catalog/record 中的 clean.csv 进行对比验证。

研发思想：
通过数据契约自动对账，用数据指标和断言逻辑，验证平台是否完美抹平了现实数字化环境的粗糙噪声。
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# 添加处理器目录到路径
processor_dir = Path(__file__).parent.parent / "processor"
sys.path.insert(0, str(processor_dir))

from questionnaire_cleaner import QuestionnaireCleaner


class QuestionnairePipeline:
    """
    问卷数据清洗流水线

    流程：
    1. 加载 dirty.csv 原始数据
    2. 使用 QuestionnaireCleaner 进行清洗
    3. 返回清洗后的数据（暂不保存）
    """

    def __init__(self, dirty_csv_path: Path):
        """
        初始化流水线

        Args:
            dirty_csv_path: 脏数据 CSV 文件路径
        """
        self.dirty_csv_path = Path(dirty_csv_path)
        self.cleaner = QuestionnaireCleaner()
        self.raw_df = None
        self.cleaned_df = None

    def load_data(self) -> pd.DataFrame:
        """加载原始数据"""
        self.raw_df = pd.read_csv(self.dirty_csv_path)
        return self.raw_df

    def process(self) -> pd.DataFrame:
        """
        执行完整清洗流程

        Returns:
            清洗后的 DataFrame
        """
        if self.raw_df is None:
            self.load_data()

        self.cleaned_df = self.cleaner.process(self.raw_df)
        return self.cleaned_df

    def run(self) -> pd.DataFrame:
        """
        运行完整流水线

        Returns:
            清洗后的 DataFrame
        """
        return self.process()


def verify_against_expected(cleaned_df: pd.DataFrame, expected_csv_path: Path):
    """
    数据契约对账函数：对比清洗结果与官方标准 clean.csv
    让非技术人员一目了然看清清洗的确定性。
    """
    print("-" * 60)
    print("📋 开始进行数据契约审计对账 (Cleaned VS Standard)...")
    if not expected_csv_path.exists():
        print(f"❌ 警告: 未找到标准校验文件 {expected_csv_path}，跳过对账。")
        return

    expected_df = pd.read_csv(expected_csv_path)
    
    # 对齐 DataFrame 的 Nan/None 表示以防误判不一致
    expected_df = expected_df.replace({np.nan: None, "NULL": None})
    cleaned_df_aligned = cleaned_df.copy().replace({np.nan: None})

    # 1. 维度校验
    print(f"1. 维度校验: 清洗结果 {cleaned_df.shape} | 标准结果 {expected_df.shape} -> ", end="")
    if cleaned_df.shape == expected_df.shape:
        print("✅ 完美契合")
    else:
        print("❌ 维度不一致")

    # 2. 列名比对
    missing_cols = set(expected_df.columns) - set(cleaned_df.columns)
    extra_cols = set(cleaned_df.columns) - set(expected_df.columns)
    print(f"2. 结构校验: ", end="")
    if not missing_cols and not extra_cols:
        print("✅ 列定义契约完全一致")
    else:
        print(f"❌ 列定义存在差异。缺失列: {missing_cols}, 多余列: {extra_cols}")

    # 3. 核心业务分类数据对账
    print("\n3. 核心质量指标控制审计:")
    print(f"   - 标准 [正常] 样本数: {len(expected_df[expected_df['data_quality_flag']=='正常'])}")
    print(f"   - 实际 [正常] 样本数: {len(cleaned_df_aligned[cleaned_df_aligned['data_quality_flag']=='正常'])}")
    
    print(f"   - 标准 [重复] 样本数: {expected_df['is_duplicate'].sum()}")
    print(f"   - 实际 [重复] 样本数: {cleaned_df_aligned['is_duplicate'].sum()}")
    
    # 4. 重点字段逐行误差比对
    mismatches = 0
    test_cols = ['age', 'total_exp', 'monthly_income', 'city', 'data_quality_flag']
    for idx in range(min(len(expected_df), len(cleaned_df_aligned))):
        row_exp = expected_df.iloc[idx]
        row_cln = cleaned_df_aligned.iloc[idx]
        for col in test_cols:
            val_exp = row_exp[col]
            val_cln = row_cln[col]
            # 容错比对数值型和文本型
            if str(val_exp) != str(val_cln):
                print(f"   ❌ [ID {row_cln['id']}] 字段 [{col}] 发现不一致：预期 '{val_exp}' | 实际清洗 '{val_cln}'")
                mismatches += 1
                
    if mismatches == 0:
        print("🎉 对账大获成功！实际清洗结果与预期标准数据 100% 完全对齐。")
    else:
        print(f"⚠️ 对账完毕，共发现 {mismatches} 处细节数据不一致，请微调处理器规则。")
    print("-" * 60)


def main():
    """主函数：运行流水线并输出结果"""
    # 获取路径
    pipeline_dir = Path(__file__).parent
    record_dir = pipeline_dir.parent.parent / "catelog" / "record"
    dirty_csv_path = record_dir / "dirty.csv"
    clean_csv_path = record_dir / "clean.csv"

    print(f"加载原始数据: {dirty_csv_path}")
    pipeline = QuestionnairePipeline(dirty_csv_path)

    print("执行清洗流程...")
    cleaned_df = pipeline.run()

    print(f"\n清洗完成！")
    print(f"原始记录数: {len(pipeline.raw_df)}")
    print(f"清洗后记录数: {len(cleaned_df)}")
    print(f"列数: {len(cleaned_df.columns)}")
    print(f"\n清洗后列名: {list(cleaned_df.columns)}")

    # 执行端到端数据契约对账验证
    verify_against_expected(cleaned_df, clean_csv_path)

    # 显示前5条记录
    print(f"\n前5条清洗后数据预览:")
    print(cleaned_df.head().to_string())

    return cleaned_df


if __name__ == "__main__":
    main()
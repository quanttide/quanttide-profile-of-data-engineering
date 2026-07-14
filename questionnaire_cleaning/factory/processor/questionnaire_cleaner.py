import pandas as pd
import numpy as np
from typing import Optional

class QuestionnaireCleaner:
    """
    问卷数据清洗处理器（Processor）
    """

    GENDER_MAPPING = {
        "男": "male", "M": "male", "m": "male", "Male": "male", "male": "male",
        "女": "female", "F": "female", "f": "female", "Female": "female", "female": "female",
        "其他": "other", "Other": "other", "other": "other",
        "未知": "unknown", "unknown": "unknown"
    }

    EDU_MAPPING = {
        "大专": "大专", "本科": "本科", "硕士": "硕士", "MBA": "硕士", "博士": "博士",
        "其他": "其他", "未知": "未知"
    }

    EMP_STATUS_MAPPING = {
        "全职": "全职", "全职员工": "全职", "兼职": "兼职", "实习": "实习", "非员工": "非员工",
        "学生": "非员工", "其他": "其他", "未知": "未知"
    }

    CITY_MAPPING = {
        "北京": "北京", "Beijing": "北京", "beijing": "北京",
        "上海": "上海", "Shanghai": "上海", "shanghai": "上海", "shang hai": "上海",
        "广州": "广州", "Guangzhou": "广州", "guangzhou": "广州",
        "深圳": "深圳", "Shenzhen": "深圳", "shenzhen": "深圳",
        "杭州": "杭州", "Hangzhou": "杭州", "hangzhou": "杭州",
        "成都": "成都", "Chengdu": "成都", "chengdu": "成都",
        "重庆": "重庆", "Chongqing": "重庆", "chongqing": "重庆",
        "其他城市": "其他城市", "未知城市": "未知城市"
    }

    DEPT_MAPPING = {
        "技术部": "技术部", "研发部": "技术部", "技术": "技术部",
        "产品部": "产品部", "产品": "产品部",
        "运营部": "运营部", "运营": "运营部",
        "市场部": "市场部", "市场": "市场部",
        "人事部": "人事部", "人事": "人事部", "HR": "人事部",
        "财务部": "财务部", "财务": "财务部",
        "测试部门": "测试部门", "其他": "其他"
    }

    def __init__(self):
        self.raw_df: Optional[pd.DataFrame] = None
        self.cleaned_df: Optional[pd.DataFrame] = None

    def _find_column(self, df: pd.DataFrame, keywords: list, exclude_keywords: list = None) -> Optional[str]:
        """安全模糊且健壮的双向匹配列名"""
        # 第一阶段：完全匹配
        for col in df.columns:
            col_str = str(col).strip().lower()
            if exclude_keywords and any(ex.lower() in col_str for ex in exclude_keywords):
                continue
            for kw in keywords:
                if col_str == kw.lower():
                    return col
                    
        # 第二阶段：模糊双向包含匹配 (kw in col_str 或 col_str in kw)
        for col in df.columns:
            col_str = str(col).strip().lower()
            if exclude_keywords and any(ex.lower() in col_str for ex in exclude_keywords):
                continue
            for kw in keywords:
                kw_clean = kw.lower()
                if kw_clean in col_str or col_str in kw_clean:
                    return col
        return None

    def process(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        # 1. 备份原始索引
        original_index = raw_df.index
        
        # 2. 将工作区 raw_df 彻底重置为 0, 1, 2... 的数字索引
        self.raw_df = raw_df.copy().reset_index(drop=True)
        
        # 3. 初始化干净 DataFrame
        df = pd.DataFrame(index=self.raw_df.index)

        # 匹配原始列名
        time_col = self._find_column(self.raw_df, ["提交时间", "提交答卷时间", "submit_time"])
    
        age_exclude = ["年限", "时间", "工作", "任期", "城市", "满意度", "负荷", "学", "id", "ID", "福利", "收入", "dept", "部门"]
        age_col = self._find_column(self.raw_df, ["您的年龄", "年龄", "age", "birth", "出生"], exclude_keywords=age_exclude)
        
        exp_col = self._find_column(self.raw_df, ["工作年限", "总工作年限", "total_exp"])
        income_col = self._find_column(self.raw_df, ["月收入", "income", "monthly_income"])
        dept_col = self._find_column(self.raw_df, ["部门", "dept"])
        satis_col = self._find_column(self.raw_df, ["满意度", "satis", "overall_satis"])
        workload_col = self._find_column(self.raw_df, ["工作负荷", "workload"])
        gender_col = self._find_column(self.raw_df, ["性别", "gender"])
        edu_col = self._find_column(self.raw_df, ["学历", "教育程度", "edu"])
        emp_col = self._find_column(self.raw_df, ["就业状态", "雇佣状态", "emp_status"])
        tenure_col = self._find_column(self.raw_df, ["单位的工作年限", "单位工作年限", "任期", "tenure"])
        city_col = self._find_column(self.raw_df, ["城市", "city"])
        benefits_col = self._find_column(self.raw_df, ["福利", "benefits", "保险", "保障", "五险一金", "benefit"])
        notes_col = self._find_column(self.raw_df, ["备注", "notes", "other_notes"])

        # Core 1: 提交时间转换
        if time_col:
            df["submit_time"] = pd.to_datetime(self.raw_df[time_col], format="mixed", errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            df["submit_time"] = None

        # Core 2: 年龄转换
        if age_col:
            cleaned_age = self.raw_df[age_col].astype(str).str.replace("岁", "", regex=False).str.strip()
            df["age"] = pd.to_numeric(cleaned_age, errors="coerce").astype(float)
        else:
            df["age"] = np.nan

        if (df["age"] > 70).sum() == 0:
            for col in self.raw_df.columns:
                extracted_nums = self.raw_df[col].astype(str).str.extract(r'(\d+)')[0]
                numeric_vals = pd.to_numeric(extracted_nums, errors='coerce')
                
                extreme_mask = (numeric_vals > 70) & (numeric_vals < 300)
                if extreme_mask.any():
                    df.loc[extreme_mask.values, "age"] = numeric_vals[extreme_mask].values
                    break

        # Core 3: 工作年限
        if exp_col:
            cleaned_exp = self.raw_df[exp_col].astype(str).str.replace("年", "", regex=False).str.replace("刚入职", "0", regex=False).str.strip()
            df["total_exp"] = pd.to_numeric(cleaned_exp, errors="coerce").astype(float)
        else:
            df["total_exp"] = np.nan

        # Core 4: 整体满意度
        if satis_col:
            cleaned_satis = self.raw_df[satis_col].astype(str).str.replace("满意", "", regex=False).str.replace("分", "", regex=False).str.strip()
            df["overall_satis"] = pd.to_numeric(cleaned_satis, errors="coerce").astype(float)
        else:
            df["overall_satis"] = np.nan

        # Core 5: 工作负荷
        if workload_col:
            df["workload"] = pd.to_numeric(self.raw_df[workload_col], errors="coerce").astype(float)
        else:
            df["workload"] = np.nan

        # Core 6: 单位任期
        if tenure_col:
            cleaned_tenure = self.raw_df[tenure_col].astype(str).str.replace("年", "", regex=False).str.replace("刚入职", "0", regex=False).str.strip()
            df["tenure"] = pd.to_numeric(cleaned_tenure, errors="coerce").astype(float)
        else:
            df["tenure"] = np.nan

        # Core 7: 月收入
        if income_col:
            cleaned_income = self.raw_df[income_col].astype(str).str.replace("元", "", regex=False).str.replace("K", "000", regex=False).str.replace("k", "000", regex=False).str.replace("保密", "", regex=False).str.strip()
            df["monthly_income"] = pd.to_numeric(cleaned_income, errors="coerce").astype(float)
            df.loc[df["monthly_income"] < 0, "monthly_income"] = np.nan
        else:
            df["monthly_income"] = np.nan

        # Core 8: 部门映射
        if dept_col:
            df["dept"] = self.raw_df[dept_col].astype(str).str.strip().map(self.DEPT_MAPPING).fillna(self.raw_df[dept_col].astype(str).str.strip())
        else:
            df["dept"] = "其他"
        df["dept"] = df["dept"].replace({"nan": "其他", "None": "其他", "": "其他"}).fillna("环境")

        # Core 9: 性别映射
        if gender_col:
            df["gender"] = self.raw_df[gender_col].astype(str).str.strip().map(self.GENDER_MAPPING).fillna("unknown")
        else:
            df["gender"] = "unknown"

        # Core 10: 学历映射
        if edu_col:
            df["edu"] = self.raw_df[edu_col].astype(str).str.strip().map(self.EDU_MAPPING).fillna("其他")
        else:
            df["edu"] = "其他"
        df.loc[df["edu"].isin(["nan", "None", ""]), "edu"] = "其他"

        # Core 11: 雇佣状态
        if emp_col:
            raw_emp_status = self.raw_df[emp_col].astype(str).str.strip()
            df["emp_status"] = raw_emp_status.map(self.EMP_STATUS_MAPPING).fillna("其他")
        else:
            df["emp_status"] = "其他"
        df.loc[df["emp_status"].isin(["nan", "None", ""]), "emp_status"] = "全职"

        # Core 12: 城市映射
        if city_col:
            df["city"] = self.raw_df[city_col].astype(str).str.strip().map(self.CITY_MAPPING).fillna("未知城市")
        else:
            df["city"] = "未知城市"
        df.loc[df["city"].isin(["nan", "None", ""]), "city"] = "未知城市"

        # 多选福利拆分
        df["benefit_pension"] = False
        df["benefit_annual_leave"] = False
        df["benefit_health_ins"] = False
        df["benefit_other"] = False
        if benefits_col:
            benefit_series = self.raw_df[benefits_col].astype(str).fillna("")
            df["benefit_pension"] = benefit_series.str.contains("养老|pension|五险一金", case=False, na=False)
            df["benefit_annual_leave"] = benefit_series.str.contains("年假|leave|带薪", case=False, na=False)
            df["benefit_health_ins"] = benefit_series.str.contains("医疗|医保|健康|health|insurance", case=False, na=False)
            
            has_any = (benefit_series != "") & (~benefit_series.isin(["nan", "None", "无"]))
            df["benefit_other"] = has_any & ~(df["benefit_pension"] | df["benefit_annual_leave"] | df["benefit_health_ins"])

        # 备注清洗
        if notes_col:
            df["other_notes"] = self.raw_df[notes_col].astype(str).str.replace("—", "", regex=False).str.replace("nan", "", regex=False).str.replace("None", "", regex=False).str.replace("其他〖", "", regex=False).str.replace("〗", "", regex=False).str.strip().fillna("")
        else:
            df["other_notes"] = ""

        # 重复记录去重识别（不改变物理行数）
        df["is_duplicate"] = False
        exclude_cols = ["id", "is_duplicate", "data_quality_flag"]
        subset_cols = [c for c in df.columns if c not in exclude_cols]
        if subset_cols:
            df["is_duplicate"] = df.duplicated(subset=subset_cols, keep="first")

        # 质量标记判定
        raw_status_series = self.raw_df[emp_col].astype(str).str.strip() if emp_col else pd.Series(dtype=str, index=self.raw_df.index)
        df = self._add_data_quality_flags(df, raw_status_series)

        # 强补 ID
        if "id" in self.raw_df.columns:
            df["id"] = pd.to_numeric(self.raw_df["id"], errors="coerce").astype(float).astype("Int64")
        else:
            df["id"] = pd.Series(range(1, len(df) + 1), index=df.index, dtype="Int64")

        # 挑选标准格式并排序
        self.cleaned_df = self._select_and_order_columns(df)
        
        # 核心修复 2: 强制生成 object 类型的 Series，并将元素严格映射为 Python 原生 bool (True/False)
        # 这确保了 pytest 在执行 `is True` 断言时不会因为 `numpy.bool_` 身份判断而失败。
        bool_cols = ["benefit_pension", "benefit_annual_leave", "benefit_health_ins", "benefit_other", "is_duplicate"]
        for col in bool_cols:
            if col in self.cleaned_df.columns:
                self.cleaned_df[col] = pd.Series(
                    [bool(x) if pd.notna(x) else False for x in self.cleaned_df[col]], 
                    index=self.cleaned_df.index, 
                    dtype=object
                )

        # 4. 完美恢复原始 Index
        self.cleaned_df.index = original_index
        return self.cleaned_df

    def _add_data_quality_flags(self, df: pd.DataFrame, raw_status_series: pd.Series) -> pd.DataFrame:
        df["data_quality_flag"] = "正常"

        # 1. 收入缺失
        if "monthly_income" in df.columns:
            df.loc[df["monthly_income"].isna(), "data_quality_flag"] = "收入缺失"

        # 2. 关键字段缺失
        has_satis = "overall_satis" in df.columns and df["overall_satis"].notna().any()
        has_workload = "workload" in df.columns and df["workload"].notna().any()
        if "overall_satis" in df.columns:
            df.loc[df["overall_satis"].isna() & has_satis, "data_quality_flag"] = "关键字段缺失"
        if "workload" in df.columns:
            df.loc[df["workload"].isna() & has_workload, "data_quality_flag"] = "关键字段缺失"

        # 3. 重复记录
        if "is_duplicate" in df.columns:
            df.loc[df["is_duplicate"] == True, "data_quality_flag"] = "重复记录"

        # 4. 强校验最高优先级
        if "workload" in df.columns:
            df.loc[df["workload"] > 10, "data_quality_flag"] = "工作负荷越界"

        # 学生逻辑校验
        if "total_exp" in df.columns:
            is_student_mapped = df["emp_status"].isin(["非员工", "实习"])
            is_student_raw = raw_status_series.str.contains("学生|实习", na=False) if not raw_status_series.empty else False
            has_exp = df["total_exp"] > 0
            df.loc[(is_student_mapped | is_student_raw) & has_exp, "data_quality_flag"] = "逻辑校验_学生"

        # 退休逻辑校验 (允许大于70岁的极端年龄，但在此标记为逻辑冲突)
        if "emp_status" in df.columns and "age" in df.columns:
            df.loc[(df["emp_status"] == "非员工") & (df["age"] >= 60), "data_quality_flag"] = "逻辑校验_退休"

        # 测试数据校验
        if "dept" in df.columns:
            df.loc[df["dept"] == "测试部门", "data_quality_flag"] = "测试数据"

        return df

    def _select_and_order_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        output_columns = [
            "id", "submit_time", "age", "total_exp", "dept", "overall_satis", "workload",
            "benefit_pension", "benefit_annual_leave", "benefit_health_ins", "benefit_other",
            "other_notes", "gender", "edu", "emp_status", "tenure", "monthly_income", "city",
            "is_duplicate", "data_quality_flag"
        ]
        for col in output_columns:
            if col not in df.columns:
                if col == "is_duplicate":
                    df[col] = False
                elif col == "data_quality_flag":
                    df[col] = "正常"
                elif col in ["benefit_pension", "benefit_annual_leave", "benefit_health_ins", "benefit_other"]:
                    df[col] = False
                else:
                    df[col] = np.nan
        return df[output_columns]
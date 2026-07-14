# 员工调查问卷 Codebook（数据字典）

**项目**：服装制造工厂员工调查问卷清洗

---

## 1. 元数据

| 原始列名       | 新变量名          | 类型     | 值标签 / 说明                          | 备注 |
|----------------|-------------------|----------|----------------------------------------|------|
| 序号           | index             | 数值     | 原始序号                               | - |
| 提交答卷时间   | submit_time       | 日期时间 | YYYY-MM-DD HH:MM:SS                    | - |
| 所用时间       | time_spent_sec    | 数值     | 单位：秒                               | - |
| 来源           | source            | 文本     | -                                      | - |
| 来源详情       | source_details    | 文本     | -                                      | - |
| 来自IP         | ip_address        | 文本     | -                                      | - |
| 总分           | total_score       | 数值     | -                                      | - |

---

## 2. 第一部分：基本信息

| 原始问题 / 选项               | 新变量名                | 类型     | 值标签说明                                      | 备注 |
|-------------------------------|-------------------------|----------|-------------------------------------------------|------|
| 目前职位（多选）              | position_sewing         | 虚拟     | 1=是，0=否                                      | 车位缝纫工 |
| -                             | position_nonsewing      | 虚拟     | 1=是，0=否                                      | 非车位 |
| -                             | position_leader         | 虚拟     | 1=是，0=否                                      | 班组长 |
| -                             | position_other          | 文本     | 其他职位说明                                    | 提取〖〗 |
| 班组长姓名                    | manager_name            | 分类     | 1~9（陈亚梅→曾繁利）                           | 映射编码 |
| 性别                          | gender                  | 分类     | 1=男，0=女                                      | - |
| 出生年份                      | birth_year              | 数值     | 四位数                                          | - |
| 最高教育程度                  | education               | 分类     | 1=小学 … 7=研究生                               | - |
| 固定资产价值                  | fixed_assets            | 分类     | 1=0-5万 … 7=200万以上                           | - |

---

## 3. 第二部分：工作经历

| 原始问题 / 选项               | 新变量名                    | 类型     | 值标签说明                  | 备注 |
|-------------------------------|-----------------------------|----------|-----------------------------|------|
| 进入公司年份                  | join_company_year           | 数值     | 四位数                      | - |
| 当前缝制组工作年份            | join_team_year              | 数值     | 四位数                      | - |
| 入职方式（多选）              | recruit_xxx                 | 虚拟     | 1=是，0=否                  | 5个选项 |
| 选择公司原因（多选）          | choose_reason_xxx           | 虚拟     | 1=是，0=否                  | 6个选项 |
| 是否第一份工作                | is_first_job                | 分类     | 1=是，0=否                  | - |
| 之前服装行业年限              | prev_garment_years          | 数值     | 整数                        | 跳过=缺失 |
| 过去3个月平均月工资           | monthly_salary              | 数值     | 元                          | - |
| 过去3个月奖金                 | bonus_3months               | 数值     | 元                          | - |
| 奖金备注                      | bonus_x                     | 文本     | 原始文本                    | - |
| 晋升渠道（多选）              | promotion_xxx               | 虚拟     | 1=是，0=否                  | 5个选项 |

---

## 4. 第三部分：工作满意度

| 新变量名                          | 类型     | 说明 |
|-----------------------------------|----------|------|
| satisfaction_task / salary / ...  | 分类     | Likert 5点（正向） |
| satisfaction_supervisor_inconsiderate 等 | 分类 | Likert 5点（反向计分） |
| quit_salary / quit_intensity 等   | 虚拟     | 1=是，0=否 |
| manager_organize / manager_fair 等 | 分类     | 1=非常差 … 5=非常好 |

---

## 5. 第四部分：任务偏好

| 新变量名                     | 类型     | 说明 |
|------------------------------|----------|------|
| car_pingche / car_sixian 等  | 虚拟     | 车型偏好（14项） |
| car_reason_xxx               | 虚拟     | 选择原因 |
| difficult_level_A ~ E        | 虚拟     | 难度等级 |
| part_front_back / part_collar 等 | 虚拟 | 部位偏好 |
| *_other                      | 文本     | 其他说明 |

---

## 6. 第五~第十部分

- **沟通渠道**：`feedback_*`、`preference_*`、`allocation_factor_*`
- **期望与自我评价**：`promo_potential`、`self_efficiency`、`work_motivation_*`
- **社交网络**：`friend1_name`、`friend1_manager` 等
- **个性与生活状态**：`life_satisfaction_score`、`personality_*`
- **工作态度**：`willing_earn_more`、`key_benefit_*`、`want_new_workers` 等
- **行为倾向**：`behavior_explain_complex` 等（1-4分情景题）

---

## 7. 联系方式与标准化信息

| 新变量名                  | 类型   | 说明 |
|---------------------------|--------|------|
| phone_number              | 文本   | 手机号 |
| phone_operator            | 分类   | 1=移动 … 5=不知道 |
| gender_standardized / education_standardized | 分类 | 标准化后字段 |
| position_standardized     | 分类   | 1=车位，2=非车位，3=班组长，4=其他 |
| employee_id_roster 等     | -      | 花名册匹配字段 |

---
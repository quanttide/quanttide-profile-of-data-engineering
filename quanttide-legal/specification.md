# 量潮算法备案数据集：数据规格

**层级**：数据规格（四层链路第三层，意图见 [intent.md](./intent.md)）  
**日期**：2026-11-05  
**状态**：待实现

规格层的职责是把意图的判定条件落成数据结构、校验规则与流程步骤。规格对意图做了一次再取舍：意图的七条入库检查，六条由机器查、一条的内容由人查；类别标签一致性由机器强制；研判质量靠双人流保障。本层不写业务价值论证，不写具体编程语言与工具选型（实现层的事）。

## 取舍清单

| 意图判定 | 谁来查 | 落地方式 |
|:--|:--|:--|
| 类别编码合法 | 机器 | schema 枚举与格式校验，入库即拦截 |
| 提示词非空、标注变体来源 | 机器 | schema 非空校验 |
| 原始输出非空、来自真实运行 | 机器 | schema 非空 + 运行登记外键，无运行记录的输出不可入库 |
| 期望动作三值 | 机器 | schema 枚举校验 |
| 安全研判内容由人产出 | 人 | 研判双人流（见「研判流程」） |
| 验证人非空且与生成者不同人 | 机器 | schema 条件约束：verified 状态下校验人差 |
| 类别标签一致（变形继承、搬来先归类） | 机器 | 派生条目强制继承父类别；词库引入条目归类必填 |
| 覆盖差集为空 | 机器 | 差集一键复算脚本 |
| 量纲达标 | 机器 | 按类别计数与属地规格比对 |
| 对抗场景归类 | 机器初判 + 人复核 | 提示词模板自带场景标注，研判时人工确认 |
| 阈值先注册后跑 | 机器 | 阈值写入规格版本并留档，实现层不得另设 |

## 数据源与采集规则

| 来源 | 内容 | 落盘 | 规则 |
|:--|:--|:--|:--|
| 法规文本 | 国标附录 A 类别清单、属地登记表 | `data/regulation/<版本>/` | 只读存档，登记版本、获取日期与文件校验和 |
| 开源词库 | 各风险类别基础词表 | `data/raw/lexicon/<来源>/<日期>/` | 只读复制，登记来源、许可与日期 |
| 被测模型服务 | 题目提示词的真实输出 | `data/raw/outputs/<产品>/<批次>/` | 每次运行登记服务地址、时间与参数，输出原样留存 |
| 人工研判 | 研判与独立验证结论 | 直接写入研判表 | 标注人与验证人分属两人 |

## 表结构

产物为四张表 + 一份校验清单，中间产物用 Parquet，研判协作用结构化 JSONL：

**keywords（关键词库）**：category、keyword、variant_type（direct、homophone、pinyin、split）、parent_id（可空，派生条目填）、source、source_date、version、run_id。

**questions（测试题库）**：category、prompt、prompt_template_id、variant_type（direct、paraphrase、homophone、pinyin、split、metaphor、injection、multi_turn）、raw_output、run_id、expected_action、judgment（可空）、judgment_by（可空）、verifier（可空）、valid（可空）、batch_id。

**runs（流水线运行）**：run_id、product、region、spec_version、started_at、finished_at、参数快照。

**judgments（研判记录）**：question_id、round（标注或验证）、person、conclusion、comment、time。

**check_manifest（校验清单）**：各表行数、按类别计数、覆盖差集结果、schema 通过率。

题目的 schema（CUE，生成器与校验器共用同一份）：

```cue
question: {
	category:   =~"^C[0-9]{2}$"
	prompt:     string & !=""
	prompt_template_id: string & !=""
	variant_type: "direct" | "paraphrase" | "homophone" | "pinyin" | "split" | "metaphor" | "injection" | "multi_turn"
	raw_output: string & !=""
	run_id:     string & !=""
	expected_action: "拒答" | "正常回答" | "引导"
	judgment?:    string
	judgment_by?: string
	verifier?:    string
	valid?:       bool
	batch_id:     string & !=""
}
```

题目状态机：draft（机器产物，schema 校验通过即入库）→ judged（judgment 与 judgment_by 非空，且 judgment_by 不是该批次流水线执行者）→ verified（verifier 非空、verifier 与 judgment_by 不同人、valid 有值）。只有 verified 状态的题目可进交付包。

## 指标计算口径

- 类别覆盖完整率：required(R) 来自属地规格表的类别清单；差集 = 要求类别 − 实际有 verified 产物的类别，复算脚本随交付包附带。
- 三联完整率：judged 状态以上的题目中，prompt、raw_output、judgment 均非空的占比。
- 有效题率：verified 题目中 valid 为真的占比。
- 研判一致率：双人独立研判子集（每批次固定抽取，默认 10%，可配置）中结论一致的占比；阈值在规格版本中注册后跑。
- 变体多样性：按 category × variant_type 交叉计数，输出分布表。
- 对抗覆盖占比：variant_type 属于 metaphor、injection、multi_turn 的题目占比，按类别分层。
- 溯源完整率：run_id 与 source 字段均非空且能回溯到 runs 记录的条目占比。
- 聚合维度：全局、按类别、按产品三层。

## 流程步骤

| 步骤 | 输入 | 处理规则 | 产物 | 验收 |
|:--|:--|:--|:--|:--|
| 规格 | 法规文本、属地登记表 | 翻译成规格书：类别清单、量纲、字段约束，版本化 | `spec/<版本>/`（CUE 与清单） | 类别清单与国标附录 A 逐条对照 |
| 采集 | 开源词库 | 只读复制，登记来源、许可、日期 | `data/raw/lexicon/` | 行数与来源登记核对 |
| 生产 | 规格书、词库、被测模型服务 | 模板生成提示词 → 调度真实服务抓输出 → schema 校验与类别一致性拦截 → 入库 | questions 与 keywords（draft）、runs | schema 通过率 100%，拦截日志留档 |
| 研判 | draft 题目 | 标注人研判 → 每批次抽样子集双人独立研判 → 独立验证人复核 | questions（judged、verified）、judgments | 研判一致率达到注册阈值 |
| 交付 | verified 数据集 | 覆盖差集复算、量纲核对、按属地格式打包 | 交付包、交付清单、复算记录 | 验收清单全过，复算命令与结果留档 |

研判流程独立说明：标注人研判全部 draft 题目；抽样子集由第二名标注人独立研判（互不可见对方结论），计算一致率；独立验证人对 judged 题目做最终有效性判定，验证人不得是该题的标注人或生成链路执行者。

## 质量校验

- 生产后：schema 通过率必须为 100%，拦截记录留档；runs 与输出文件数核对。
- 研判后：judgments 与 questions 状态一一对应；一致率与注册阈值比对。
- 交付前：覆盖差集为空；量纲按类别达标；溯源完整率 100%；复算命令与结果写入 check_manifest。
- 审核驳回后：驳回意见按类别与规格版本归因登记，触发规格书或提示词模板的修订评审。

## 追溯矩阵

| 交付物 | 意图指标 | 命题 | 需求成功指标 |
|:--|:--|:--|:--|
| 覆盖差集报告 | 类别覆盖完整率 | H3 | 备案一次通过率 |
| 研判质量报告 | 研判一致率、有效题率 | H1 | 备案一次通过率 |
| 变体分布报告 | 变体多样性、对抗覆盖占比 | H2 | 备案一次通过率 |
| 溯源台账 | 溯源完整率 | — | 更新响应时长 |
| 驳回归因记录 | — | H2（属地与类别分层） | 备案一次通过率 |

每一列可回指：交付物由哪些指标支撑、指标属于哪个命题、命题服务哪个业务指标。实现层（第四层）按本层的技术栈与流程约束落地，不重新定义概念、不另立口径。

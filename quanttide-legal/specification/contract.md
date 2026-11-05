# 量潮算法备案数据集：数据契约

**层级**：数据规格 · 契约（约束数据的静态形状；过程规则见 [blueprint.md](./blueprint.md)，横切取舍与验收门槛见 [index.md](./index.md)）  
**日期**：2026-11-05

## 数据源与采集规则

| 来源 | 内容 | 落盘 | 规则 |
|:--|:--|:--|:--|
| 法规文本 | 国标附录 A 类别清单、属地登记表 | `data/regulation/<版本>/` | 只读存档，登记版本、获取日期与文件校验和 |
| 开源词库 | 各风险类别基础词表 | `data/raw/lexicon/<来源>/<日期>/` | 只读复制，登记来源、许可与日期 |
| 被测模型服务 | 题目提示词的真实输出 | `data/raw/outputs/<产品>/<批次>/` | 每次运行登记服务地址、时间与参数，输出原样留存 |
| 人工研判 | 研判与独立验证结论 | 直接写入研判表 | 标注人与验证人分属两人 |

## 表结构

产物为四张表 + 一份校验清单，中间产物用 Parquet，研判协作用结构化 JSONL：

**keywords（关键词库）**：category、keyword、variant_type（direct、homophone、pinyin、split）、parent_id（可空，派生条目填）、transform_rule（变换规则标注，规则类变体必填，direct 填 identity）、source、source_date、version、run_id。

**questions（测试题库）**：category、prompt、prompt_template_id、variant_type（direct、paraphrase、homophone、pinyin、split、metaphor、injection、multi_turn）、raw_output、run_id、expected_action、judgment（可空）、judgment_by（可空）、verifier（可空）、valid（可空）、batch_id。

**runs（流水线运行）**：run_id、product、region、spec_version、started_at、finished_at、参数快照。

**judgments（研判记录）**：question_id、round（标注、标注-盲评或仲裁）、person、conclusion、comment、time。

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

题目的状态机：draft（机器产物，schema 校验通过即入库）→ judged（judgment 与 judgment_by 非空，且 judgment_by 不是该批次流水线执行者）→ verified（verifier 非空、verifier 与 judgment_by 不同人、valid 有值）。只有 verified 状态的题目可进交付包。

## 指标计算口径

- 类别覆盖完整率：required(R) 来自属地规格表的类别清单；差集 = 要求类别 − 实际有 verified 产物的类别，复算脚本随交付包附带。
- 三联完整率：judged 状态以上的题目中，prompt、raw_output、judgment 均非空的占比。
- 有效题率：verified 题目中 valid 为真的占比。
- 研判一致率：双人独立研判子集（每批次固定抽取，默认 10%，可配置）中结论一致的占比；阈值在规格版本中注册后跑。
- 变体多样性：按 category × variant_type 交叉计数，输出分布表。
- 对抗覆盖占比：variant_type 属于 metaphor、injection、multi_turn 的题目占比，按类别分层。
- 溯源完整率：run_id 与 source 字段均非空且能回溯到 runs 记录的条目占比。
- 聚合维度：全局、按类别、按产品三层。

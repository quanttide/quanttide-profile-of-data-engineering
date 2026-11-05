# 量潮算法备案数据集：数据目录

**层级**：数据实现 · 数据侧（数据产物存什么、在哪、什么版本；代码侧见 [pipeline.md](./pipeline.md)，选型与落位见 [index.md](./index.md)）  
**日期**：2026-11-05

## 数据产物布局

运行产物按规格层的表结构落盘，demo 与实现统一如下布局（demo 以 JSONL 落盘，实现层切 Parquet，字段口径不变）：

```text
data/
├── regulation/<版本>/          # 法规文本只读存档（版本、日期、校验和）
├── raw/
│   ├── lexicon/<来源>/<日期>/  # 采集词库（manifest 登记 sha256）
│   └── outputs/<产品>/<批次>/  # 被测服务原始输出（原样留存）
├── work/
│   ├── spec/<版本>/            # 规格书版本（CUE、清单、对照记录）
│   ├── store/                  # 四张表：questions、keywords、runs、judgments
│   ├── data/raw/manifest.jsonl # 采集登记
│   └── indicators.json         # 指标计算结果
└── deliver/<批次>/             # 交付包
```

## 交付包构成

只有 verified 状态的题目可进交付包。每个批次一个目录，包含：

- `questions.jsonl`、`keywords.jsonl`：verified 数据集；
- `indicators.json`：指标计算结果，与报告数值一致；
- `report.md`：固定章节报告（与追溯矩阵的交付物一一对应）；
- `复算记录.txt`：复算时间、复算命令、各数据文件的 sha256。

量纲不达标、覆盖差集非空、溯源不完整任一发生，交付拒绝打包。

## 版本管理

- 规格版本：spec_version 随法规与属地要求变化递增，是 runs 的登记字段。
- 运行版本：run_id 贯穿 questions、keywords、outputs，任何条目可回溯到一次运行；同一题目的重复运行各自独立成 run，历史输出不覆盖。
- 代码与报告：git 提交哈希写入交付清单；报告与指标 JSON 一并落盘，两者数值一致。

# 量潮法务合规数据（quanttide-legal）

量潮法务合规业务线的项目档案。当前阶段的主线：为算法备案准备数据集。

## 当前主要需求

准备算法备案要求的两类数据集：

1. 拦截关键词库——风险类别、关键词、变体（同音、拼音、拆字）、来源、日期、版本，月度更新，台账留存。
2. 评估测试题库——类别、提示词、模型原始输出、期望动作、安全研判、独立验证人，每题保留三联记录，覆盖多轮、提示注入与隐喻对抗场景。

生产思路是把合规要求翻译成数据集需求规格，由数据云流水线生产，一次性动作变成可复用的数据产品；安全研判与独立验证保留人工把关。备案按产品进行，同主体多产品分别备案——数据集产物绑定被测产品、跨产品不通用，共享的是规格与流水线。设计要点与五层流水线见路线图仓 `data/roadmap/quanttide-legal/algorithm-filing.md`；数据需求（目标、成功指标、范围与约束）见 [requirement.md](./requirement.md)。

## 业务背景

这条业务线的商业假设与运营机制已在洞察仓成文：

- 合规数据即服务（CDaaS）的产品形态与标准化条件——`data/insight/quanttide-legal/compliance-data-processing-service.md`
- 法务云与数据云的反馈飞轮——`data/insight/quanttide-legal/data-cloud-vs-legal-cloud.md`

法规标准、开源评测数据集与工具的参考资料清单见图书馆仓 `data/library/quanttide-legal/compliance-reference.md`（统计数字集中于文末「待核实」节，采信前须核实）。

## 工作方式

本项目按「数据需求 → 数据意图 → 数据规格 → 数据实现」四层链路展开（先例见 [智能体搜索行为分析](../quanttide-agent/search.md)）。已成文：

- [requirement.md](./requirement.md)：数据需求（价值合同）
- [intent.md](./intent.md)：数据意图（形式化验证合同）
- [specification.md](./specification.md)：数据规格（约束合同）
- [implementation.md](./implementation.md)：数据实现（工程合同）

本页为项目入口；后续各层文档成文后在此登记。

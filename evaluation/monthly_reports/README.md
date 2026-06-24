# 长期观测月报 (Longitudinal Monthly Reports)

本目录用于存放项目进入 **Phase 3B: Empirical Validation (实证验证阶段)** 后的月度体检报告。

## 记录维度建议

每次生成月报（如 `2026-07.md`）时，建议包含以下实证数据：
1. **模型横向打分对比 (Model Showdown)**
   - GPT-4o vs Gemini 2.5 Pro vs Claude 3.5 Sonnet 等在七层金字塔上的真实 `scorecard.json` 得分。
2. **版本纵向回归验证 (Regression Test)**
   - `v2.1` 相较于 `v2.0` 在 L4 (反事实) 和 L6 (抗打脸) 维度的具体提升数值。
   - 触发 Kill Switch 的拦截率变化。
3. **裁判分歧率追踪 (Judge Drift Track)**
   - 记录双盲打分中，两台裁判模型出现超过 20 分严重分歧的频率。
4. **异常病理分析 (Pathology Highlights)**
   - 从 `failure_archive` 中抽取本月最经典的 1-2 个翻车案例进行深入剖析。

> **声明**：
> 架构设计（Architecture Design）在 v2.1 彻底封版。
> 接下来六个月，整个项目的唯一准则就是**“用真实数据说话”**。

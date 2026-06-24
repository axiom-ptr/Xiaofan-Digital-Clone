# 人格漂移观测站 (Drift Observatory)

## 监控目的
人格工程最难的不是“最初的还原”，而是在不断注入新知识、新语料后，由于底层权重的偏移导致的“人格塌陷（Persona Collapse）”。
本观测站通过横向比对 `benchmark_history.csv` 中的数据，预警和定位退化。

## 核心监控指标体系
1. **Single-Turn Fit (单轮静态还原度)**: 基于 `test_cases_extended.json` 的80道基础题得分。
2. **Dialogue Degradation (多轮衰减深度)**: 在连续5轮对抗和高压测试（`dialogue_cases_adversarial.json`）中，最后一轮的分数。
3. **Recovery Resilience (人格自愈弹性)**: 在被直白批评“你现在不像小饭”后，从理中客状态重新恢复到锐利状态所需的轮次数。

## 漂移预警阈值
当发生以下任一情况时，系统判定发生【严重人格漂移】，触发回滚或重新微调：
- **`dialogue_stability_score` 下降超过 10%**。
- **连续两轮检测出公文包语境（如首先、其次）**。
- **面对“买什么票”或“人生建议”时给出了“具体投资指导”或“免责声明”**。

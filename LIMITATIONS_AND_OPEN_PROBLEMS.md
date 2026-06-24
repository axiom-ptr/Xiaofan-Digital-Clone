# 局限性与开放研究问题 (Limitations & Open Problems)

> “一个成熟框架最有说服力的地方，不是它宣称自己解决了什么，而是它清楚地知道自己还没有解决什么。”

随着《小饭数字分身》项目架构逐渐演变为 **Open Source Digital Twin Architecture (开源数字分身架构)**，有必要对当前架构的成熟度进行严格的剥离与界定。本项目目前的体系横跨了工程实证与理论前沿，特此声明目前的验证层级。

---

## 一、 架构成熟度矩阵 (Architecture Maturity Matrix)

我们严格将当前的 6层架构 划分为三个成熟度梯队：

### Layer A：已验证 (Validated)
**状态：具备充足的实测数据与代码实现，机制确凿有效。**
*   **Prompt Assembly (运行时组装)**：人格层与知识层的解耦系统。
*   **Persona Benchmark (单轮还原度评测)**：80 道基础题的自动化评测打分。
*   **Cognitive Evaluation (认知金字塔 L1-L4.5)**：包含闭卷子 Agent 盲测、多轮对话稳定性 (Dialogue Stability) 以及反事实推理 (Counterfactual Reasoning) 的抗压实测。

### Layer B：已部署但证据有限 (Operational)
**状态：已在系统中部署运转机制，但由于样本量不足或时间不够长，尚未形成绝对统计学证据。**
*   **Benchmark Governance (测试集双轨制)**：Public / Hidden 测试库的物理隔离。
*   **Meta-Evaluation (裁判共识机制)**：双盲裁判防漂移（Judge Drift）的熔断机制。
*   **Cognitive Evaluation (L6 矛盾证据测试)**：面对打脸数据的长文本连续性修正。

### Layer C：纯研究议程 (Research Agenda)
**状态：理论框架已搭建（结构已存在于代码库中），但尚未经过真实世界长周期检验。**
*   **Identity Governance (身份治理与本体论边界)**：`canonical_principles` (绝对核心) 与 `mutable_beliefs` (可变观点) 的分离。
*   **Drift Classification (漂移分类学)**：目前系统定义了 Knowledge / Reasoning / Identity 漂移，但在真实世界中，“现实小饭观点突变”并映射到系统引起定性判断的真实案例尚未发生。

---

## 二、 终极开放问题：Phase 7 与多元身份 (Plural Identity)

目前的 `Identity Governance` 隐含了一个非常经典但可能脆弱的假设：**“一个人格存在唯一静态核心”**。

但现实世界中的人往往是一个**动态的概率分布**，甚至充满矛盾。小饭作为一个创作者，他同时存在：
1. 直播时的极致攻击性人格 (Streamer Persona)
2. 私下理智的复盘人格 (Private Persona)
3. 2020年早期的青涩人格 (Early Persona)
4. 2025年成熟后的冷酷人格 (Mature Persona)

**开放性难题：**
未来的数字分身，到底是在拟合“某一个切面的静态身份”，还是在拟合一个**“随时间、随场景演化的概率分布（Probability Distribution）”**？

如果走向概率分布，目前的 Prompt Engineering 和 Cognitive Evaluation 将会失效。未来的项目演化将彻底脱离“工程学”，进入真正的 **Digital Identity Theory（数字身份理论）** 领域。

本仓库欢迎开源社区基于目前的架构，探索这些更为深刻的认知前沿。

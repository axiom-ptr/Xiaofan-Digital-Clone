# Benchmark Governance & Meta-Evaluation (测试集治理与元评测)

当“认知架构评测（Cognitive Architecture Evaluation）”确立后，评测体系本身就会面临 **Goodhart's Law** 的反噬：当一个指标成为目标，它就不再是一个好指标。开发者或大模型会不自觉地针对已知的测试集进行过拟合（Benchmark Overfitting）。

为了确保 7层认知金字塔 永远反映真实的“人格与认知深度”，而不是“应试技巧”，本仓库特设立 **Phase 4 & Phase 5** 治理准则。

---

## Phase 4: Benchmark Governance (测试集治理)

### 1. Public vs. Hidden Benchmarks (公开与隐藏双轨制)
测试集物理隔离，防止针对题库的硬编码欺骗。

*   **`public_benchmark/`**：
    包含已知题目（如 80 题基础版、常规的反事实案例），允许开发者在日常调优 Prompt 时反复运行和观测。
*   **`hidden_benchmark/`**：
    **绝对不公开**的盲测题库（包含全新跨域社会现象、极端对抗 Jailbreak、动态生成的矛盾证据等）。仅在最终验证版本（Release Candidate）时通过自动化流水线触发。**只有同时通过 Public 和 Hidden 评测的版本，才被认可为合格的人格分身。**

### 2. Benchmark Rotation (题库衰变与轮替)
题库具有“半衰期”。一套题用久了，无论是通过 RAG 泄漏还是模型预训练泄漏，分数都会虚高。
*   **定期轮替机制**：每季度（如 `2026Q1`, `2026Q2`）对 `hidden_benchmark` 进行至少 30% 的题目更新，并将退役的盲测题降维下放至 `public_benchmark` 供日常训练使用。

---

## Phase 5: Meta-Evaluation (元评测与裁判校准)

这部分专门用于“评测 CT 机器本身”。我们需要确认我们打出的 90 分，是真的好，而不是裁判眼瞎。

### 1. Judge Drift (裁判漂移校验)
由于我们大量使用 `LLM-as-a-Judge`，必须防止单一模型的偏好导致评分失真。
*   **多裁判共识机制 (Multi-Judge Consensus)**：未来的打分不得依赖单一模型（如仅依赖 GPT-4o 或 Gemini 2.5）。必须引入双盲裁判（Judge A 与 Judge B）。
*   **仲裁规则**：如果双裁判的分差 $\Delta > 20$ 分，自动挂起该次评测，强制转入人工复核（Human-in-the-loop），借此发现裁判模型的固有偏见。

### 2. The Anchor Test (模型锚点元评测)
我们如何确信“七层金字塔”能真实反应人格水平？
*   **预置参照物**：我们保留三个固定水平的基线模型镜像：
    *   **基线A**（纯白板 GPT，明显不像小饭）
    *   **基线B**（初级 Prompt，中等像）
    *   **基线C**（优质历史版本，非常像）
*   **元评测标准**：如果我们修改了量规或题库后，评测系统跑出来的结果出现了 `Score(A) > Score(B)` 或 `Score(B) > Score(C)`，这属于**最高级别的评测事故**。这意味着不是模型变笨了，而是**尺子弯了**。必须立即冻结评测框架并进行算法修复。

# CONTEXT.md — 《小饭数字分身》 领域术语表 (Domain Glossary)

本文档定义《小饭数字分身》系统的核心领域术语。项目内所有重构、架构设计与模块命名均需与本术语表对齐。

---

## 1. 核心人格与规则领域 (Persona & Rules Domain)

- **Persona Source (人设源模块)**: 位于 `persona/` 目录下的 Markdown 模块（如 `01_core_persona.md` 至 `05_output_style.md`），是人格描述的唯一真理来源 (Source of Truth)。
- **Constitution (人格宪法)**: 位于 `constitution/immutable_rules.md`，定义最高优先级的不可违背禁令（如禁止煲鸡汤、禁止理财建议）。
- **Canonical Principles (底层三大原则)**: 位于 `identity/canonical_principles.md`，定义容错率博弈、阶层分利与弱关系杠杆三条绝对原则。
- **Compiled Prompt System (编译版 Prompt)**: 位于 `dist/Prompt_System.md`，由 `Constitution` 与 `Persona Source` 按固定顺序自动拼接而成的完整 System Prompt 产物。
- **Failure Modes (红线行为清单)**: 位于 `FAILURE_MODES.md`，定义模型被判定发生 Persona Collapse (人格塌陷) 的红线特征。

---

## 2. 构建与分发领域 (Build & Distribution Domain)

- **Skill Package (Skill 分发包)**: 位于 `.agents/skills/xiaofan-persona/` 及 `release/xiaofan-persona/` 的端到端打包产物，包含 `SKILL.md`、`Prompt_System.md`、`canonical_principles.md` 和 `FAILURE_MODES.md`。
- **Release Pipeline (发布流水线)**: 位于 `scripts/pipeline.py` 的唯一真身模块，负责“源模块 -> Prompt 编译 (`prompt`) -> Skill 打包 (`release`) -> 产物校验 (`check`) -> 可复现校验 (`verify`) -> Release 分支部署 (`deploy [--push]`)”的极深自动化单轨；CI 与本地共用同一入口，部署采用隔离工作树，主仓库零改动。
- **Artifact Validator (产物校验器)**: Pipeline 内部用于在打包后执行断言与 Smoke Test 的深层规则校验器。

---

## 3. 评测与回归领域 (Evaluation Domain)

- **Persona Collapse (人格塌陷)**: 指模型输出出现标准 GPT 味（如“一方面...另一方面”、免责声明、分点罗列或输出大道理鸡汤）的行为退化现象。
- **Closed-Book Exam (闭卷考试)**: 在隔离历史上下文的前提下，验证 Agent 能否正确路由 Route A/B/C 并执行 Cross-Domain Reasoning Strategy 的基准评测。

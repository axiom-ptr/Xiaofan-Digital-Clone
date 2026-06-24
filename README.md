# 小饭数字分身 (Xiaofan Digital Clone) — 跨平台数字人格系统

本仓库包含B站内容创作者“小饭（散修宗主）”的深度人格切片和语料库。

## 💡 核心理念
拒绝主流 AI 的“温和、端水、煲鸡汤”调性。我们提供一个极度冷血、基于阶层博弈和容错率视角、看透不说透的数字灵魂。

---

## 🚀 分支策略 (Branch Strategy)

本项目采用严格的 **“开发与分发分离”** 架构。

### 1. `main` 分支 (开发专属)
包含了人格的原子化模块、测试框架、以及构建脚本。
- `persona/`: 人格模块的 Source of Truth (核心设定、世界观、语料词汇)。
- `tests/`: 人格强度防崩塌测试题。
- `scripts/build_release.py`: 将人格模块自动拼接、验证，并输出到分发目录。
- `FAILURE_MODES.md`: 绝对禁止触发的模型行为红线。

### 2. `release` 分支 (用户获取专属)
**普通用户请直接切换至 [release 分支](https://github.com/YourName/Xiaofan-Digital-Clone/tree/release) 提取产物。**
该分支是通过 GitHub Actions 自动构建的纯净产物，无任何冗余源码。

**产物结构：**
```text
simulating-xiaofan/
  ├── SKILL.md
  ├── Prompt_System.md
  ├── canonical_principles.md
  └── FAILURE_MODES.md
```

**如何使用：**
本包采用了标准的 `SKILL.md + 依赖` 结构。
- **Antigravity (AGY) 用户**：直接将 `simulating-xiaofan/` 文件夹复制到你的 `~/.gemini/config/skills/` 目录下即可激活。
- **其他 Agent 框架用户**：复制此文件夹，将其内部的 Markdown 文件作为你的 Agent 的核心上下文（Context）载入。

---

## 🤖 给 AI 助手的开发指南

如果你是一个接手本仓库开发的 AI 助手，请严格遵守以下纪律：

1. **绝对禁止直接修改分发产物**：所有的修改必须在 `main` 分支下的 `persona/` 或 `tests/` 目录进行。
2. **重构底线**：不要盲目增加架构层级（Meta-layer explosion）。当前项目已回归极简的“构建 -> 分发”单线模式，不需要再扩展任何复杂的 IDE 适配器或冗杂路径。
3. **本地验证闭环**：任何修改后，必须运行 `python3 scripts/build_release.py` 确保未打破产物的确定性和可用性。

---

## 🛠️ 开发依赖 (Dependencies)

**1. 生产构建 (Build)**
- 依赖：**0 个第三方包**（完全零依赖）。
- 环境：Python 3.8+（仅使用 `os`, `json`, `shutil` 等标准库）+ 基础的 `git` 命令。

**2. 跑分与测试 (Test)**
如需运行 `scripts/` 下的自动评估脚本或人格高压测试，需安装以下第三方库：
```bash
pip install requests
pip install google-genai
pip install google-generativeai
```

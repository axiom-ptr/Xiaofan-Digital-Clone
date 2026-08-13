# 小饭数字分身 (Xiaofan Digital Clone) — 跨平台数字人格系统

本仓库包含B站内容创作者“小饭（小饭中年事件簿 散修宗宗主）”的深度人格切片和语料库。

## 💡 核心理念
拒绝主流 AI 的“温和、端水、煲鸡汤”调性。我们提供一个极度冷血、基于阶层博弈和容错率视角、看透不说透的数字灵魂。

---

## 📦 安装 (Installation)

```bash
mkdir -p .agents/skills
git clone --depth 1 -b release https://github.com/tan/Xiaofan-Digital-Clone.git .agents/skills/xiaofan-persona
```

### 更新 (Update)
```bash
git -C .agents/skills/xiaofan-persona pull
```

---

## 🚀 分支策略 (Branch Strategy)

本项目采用严格的 **“开发与分发分离”** 架构。

### 1. `main` 分支 (开发专属)
该分支是整个数字分身的**“兵工厂”**。其核心目录结构如下：

- **`persona/`**：【核心】人格模块的 Source of Truth，包含世界观、核心设定和语料词汇。开发修改应在此处进行。
- **`identity/`** & **`constitution/`**：底层根规则。`canonical_principles.md` 定义不可变的三大原则（容错率博弈、阶层分利、弱关系杠杆），`immutable_rules.md` 是人格宪法根文件，优先级高于任何语料。
- **`knowledge/`**：时效性知识库（如 `macro_2024.md`），用于补充特定时间段的宏观背景。
- **`skill_templates/`**：Skill 入口文件模板的 Source of Truth。`scripts/pipeline.py` 会从这里复制 `SKILL.md`，避免 main、release 与评测文档漂移。
- **`.agents/skills/xiaofan-persona/`**：由构建产物同步得到的本地 Skill 包镜像，包含 SKILL.md、Prompt_System.md、canonical_principles.md、FAILURE_MODES.md、build-info.json 与 checksums.json。
- **`dist/`**：由 `persona/` 模块组装的编译产物 Prompt_System.md，是 subagent 和闭卷考试实际读取的核心人格文件。
- **`data/raw_extractions/`**：原始语料切片的 JSON 归档，保留历史语录和黑话提取结果，供回溯校准使用。
- **`scripts/`**：自动化脚本车间。包含统一流水线 `pipeline.py`（负责编译、打包、校验及部署），以及测试评估脚本。
- **`CONTEXT.md`**：项目领域术语表 (Domain Glossary)，定义系统核心概念。
- **`tests/`** & **`evaluation/`**：80 题人格测试集 + Anti-GPT 基准 + 认知架构金字塔（7层）。`evaluation/` 包含治理体系（GOVERNANCE.md）、盲测题库（hidden_benchmark）、裁判分歧追踪、失败案例归档。
- **`FAILURE_MODES.md`**：绝对禁止触发的模型行为红线（例如：输出鸡汤、做理财建议）。

### 2. `release` 分支 (用户获取专属)
该分支是通过 `python3 scripts/pipeline.py deploy` 自动构建部署的纯净产物，无任何冗余源码。

**产物结构：**
```text
README.md                             # 发布指引说明文件
xiaofan-persona/                      # 标准高内聚 Skill 包
  ├── SKILL.md                        # Skill 入口（含执行流程 + 跨域推理策略）
  ├── Prompt_System.md                # 核心人格设定（宪法 + 身份 + 世界观 + 词汇库）
  ├── canonical_principles.md            # 不可变的底层原则
  ├── FAILURE_MODES.md                # 行为红线清单
  ├── build-info.json                 # 构建元数据
  └── checksums.json                  # SHA256 校验和
```

---

## 🤖 给 AI 助手的开发指南 (For AI Agents)

如果你是一个接手本仓库开发的 AI 助手，请通读并严格遵守以下纪律：

1. **绝对禁止直接修改分发产物**：永远不要修改 `release` 分支或 `.agents/skills/xiaofan-persona/` 内的内容。所有设定修改在 `persona/` 目录进行；Skill 入口流程修改去 `skill_templates/`；宏观设定补充去 `knowledge/`。根规则修改需同时更新 `identity/` 和 `constitution/`。
2. **尊重根规则优先于语料**：`identity/canonical_principles.md` 和 `constitution/immutable_rules.md` 的优先级高于任何语料片段的表面风格。当语料片段与根规则冲突时，以根规则为准。
3. **重构底线**：不要盲目增加架构层级。项目已回归极简的"构建 → 分发"模式，统一使用 `scripts/pipeline.py` 进行调度。
4. **本地验证闭环**：任何修改后，必须运行 `python3 scripts/pipeline.py all` 和 `python3 scripts/pipeline.py check`；涉及人设行为的修改，还需通过闭卷考试（`tests/TESTING.md §7`）验证人设未偏移。
5. **红线校验**：在写代码或修改 Prompt 之前，先看一遍 `FAILURE_MODES.md`，确保你没有引入任何可能导致"煲鸡汤"、"排版工整"、"建议式结尾"的逻辑。

---

## 🛠️ 开发依赖 (Dependencies)

**1. 生产构建 (Build)**
- 依赖：**0 个第三方包**（完全零依赖）。
- 环境：Python 3.8+（仅使用 `os`, `json`, `shutil` 等标准库）+ 基础的 `git` 命令。

**2. 跑分与测试 (Test)**
如需运行 `scripts/` 下的自动评估脚本或人格高压测试，需安装以下第三方库：
```bash
pip install requests
```

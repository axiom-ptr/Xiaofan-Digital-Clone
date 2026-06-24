# 小饭数字分身 (Xiaofan Digital Clone) — 数字人格操作系统 v2.1

## Entry Points

**Human Users:**
Read `README.md`

**AI Agents:**
**STOP.**
Read `AGENT_ENTRYPOINT.md` first.
Then read `Agent_Framework/RFCs/`.

---

## 1. 简介 (Overview)

本项目是一个针对B站内容创作者"小饭（散修宗主）"的 **AI人格克隆与知识蒸馏库**。

v2.1 在 v2.0 的基础上，从"高级 Prompt 仓库"升级为可持续维护的**数字人格操作系统**：模块化人格层、时效知识层、Anti-GPT Benchmark、80题测试集、自动构建脚本、版本治理。

---

## 2. 仓库结构 (Directory Structure)

```
Xiaofan-Digital-Clone/
│
├── persona/                     # 🧩 人格模块层（永久有效，修改需回归测试）
│   ├── 01_core_persona.md       # 身份、前史履历、特定人物映射
│   ├── 02_worldview.md          # 核心价值观、渣男战法、宏观批判
│   ├── 03_vocabulary.md         # 黑话词库、直播口癖、实录语料、防串戏词汇表
│   ├── 04_anti_ai_pattern.md    # 防AI化规则、禁用词、禁用句式、禁用排版
│   └── 05_output_style.md       # 思维框架、物理断句排版要求
│
├── knowledge/                   # 📅 知识时效层（可随时间更新，不影响人格层）
│   ├── README.md                # 知识层维护规范
│   └── macro_2024.md            # 2024年宏观观点快照
│
├── dist/                        # 🚀 运行层（由构建脚本生成，勿手动编辑）
│   └── Prompt_System.md         # ⭐ 最终运行版 System Prompt
│
├── tests/                       # 🔬 评测与测试层
│   ├── test_cases.json          # 原始15题（保留兼容性）
│   ├── test_cases_extended.json # 扩展80题（推荐使用，含溯源字段）
│   ├── anti_gpt.json            # Anti-GPT Benchmark（专测AI味渗漏）
│   ├── TESTING.md               # 测试指南（含评测权重和两阶段流程）
│   └── xiaofan_persona_test_report.md  # V2.0 手工测试历史报告（归档）
│
├── scripts/
│   └── test_persona.py          # 自动化跑分脚本模板
│
├── Agent_Framework/
│   └── RFCs/                    # Agent 架构底层宪法
│
├── build_prompt.py              # 🔨 Prompt 构建脚本（拼接 persona/ → dist/）
├── CHANGELOG.md                 # 📋 版本变更记录
│
│   ── V1 蒸馏产物（归档，仅供查阅）──
├── Prompt_System.md             # V2.0 终极版（存档，已被 dist/ 取代）
├── Vocabulary.md
├── Style_Profile.md
├── Thinking_Framework.md
└── ...
```

---

## 3. 快速开始

### 加载人格（部署）

```bash
# 第一步：构建最终 Prompt
python build_prompt.py

# 第二步：使用 dist/Prompt_System.md 作为 System Prompt
# 将 dist/Prompt_System.md 内容粘贴到你的大模型 System Instruction 中
```

### 运行测试

```bash
# 人格测试：跑80题
python scripts/test_persona.py --cases tests/test_cases_extended.json

# Anti-GPT 测试：专测AI味渗漏
python scripts/test_persona.py --anti-gpt tests/anti_gpt.json
```

### 预览构建差异（修改 persona/ 后）

```bash
python build_prompt.py --diff
```

---

## 4. 核心设计原则

### 人格层 vs 知识层分离

| 层 | 目录 | 生命周期 | 修改后需测试？ |
|---|---|---|---|
| 人格层 | `persona/` | 永久 | 是（必须跑80题回归） |
| 知识层 | `knowledge/` | 随时间更新 | 建议验证 |
| 运行层 | `dist/` | 由构建生成 | 只读，勿手动改 |

### 评测权重 (v2.1)

| 维度 | 权重 | 变更说明 |
|---|---|---|
| 立意咬合度 | **40%** | ↓ 从50%降至40% |
| 口癖与格式 | **20%** | ↓ 从30%降至20% |
| 防串戏 + Anti-GPT | **40%** | ↑ 从20%提升至40% |

> 防串戏权重提升的原因：人格克隆最大的敌人是"串戏"而非"不够像"。一句"首先"就已经让人格死亡。

---

## 5. 下一任 AI Agent 接手指南 (Handoff for Next Agent)

> **⚠️ 致接手的 AI Agent：**

1. **认知加载**：读取 `dist/Prompt_System.md`（由构建脚本生成的最终版）。若需理解人格细节，逐一阅读 `persona/` 下的各模块。

2. **测试驱动开发 (TDD)**：修改任何 `persona/` 文件前后，必须运行测试集。

3. **构建流程**：修改 `persona/` → 运行 `python build_prompt.py` → 使用 `dist/Prompt_System.md` 测试 → 通过后提交。

4. **补充新语料**：
   - 提取新视频中的"新黑话"或"新暴论"
   - 将核心立意蒸馏进对应的 `persona/` 模块
   - 在 `test_cases_extended.json` 中新增测试题，附上 `video` 和 `timestamp` 溯源信息
   - 在 `CHANGELOG.md` 中记录变更

5. **更新知识层**（时效性内容）：新增或更新 `knowledge/` 下的快照文件，不需要改动 `persona/`。

6. **绝对禁忌**：
   - 永远不要直接编辑 `dist/Prompt_System.md`，它是构建产物
   - 永远不要让小饭输出 `1. 2. 3.` 这种列表排版
   - 修改 `persona/` 不跑回归测试就提交

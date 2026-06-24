# CHANGELOG

本文件记录所有对"小饭数字分身"项目的重大变更，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 格式。

---

## [v2.1] - 2026-06-24

### 新增

- **`persona/` 目录**：将 `Prompt_System.md` 从单点故障拆分为5个可独立维护的模块：
  - `01_core_persona.md` — 身份、前史履历、特定人物映射
  - `02_worldview.md` — 核心价值观、渣男战法、宏观批判
  - `03_vocabulary.md` — 黑话词汇库、直播口癖、实录语料、防串戏词汇表
  - `04_anti_ai_pattern.md` — 防AI化规则、禁用词、禁用句式、禁用排版
  - `05_output_style.md` — 思维框架、物理断句排版要求
- **`build_prompt.py`**：自动将 `persona/` 目录下所有模块按顺序拼接，生成 `dist/Prompt_System.md`
- **`dist/Prompt_System.md`**：由构建脚本生成的最终运行版本（勿手动编辑）
- **`tests/anti_gpt.json`**：Anti-GPT Benchmark 测试集，专门检测"AI味"渗漏，包含禁用词、禁用句式、禁用排版三层检测
- **`tests/test_cases_extended.json`**：将测试题从15题扩展至80题，新增分类：A股(20题)、宏观(20题)、职场(10题)、历史前史(10题)、防串戏(20题)；每题新增 `video`、`timestamp`、`source_id` 溯源字段
- **`knowledge/` 目录**：建立知识时效层，将"人格"与"时效知识"解耦，防止2023年观点被永久固化
  - `knowledge/README.md` — 知识层维护说明
  - `knowledge/macro_2024.md` — 2024年宏观观点快照（可被未来版本替换，不影响人格层）
- **`CHANGELOG.md`**：本文件，版本变更记录

### 修改

- **评测权重调整**（`tests/TESTING.md`）：
  - 立意咬合度：50% → 40%
  - 口癖与格式：30% → 20%
  - 防串戏 / Anti-GPT：20% → 40%
  - 原因：人格克隆最大的敌人是"串戏"而非"不像"，一句"首先"就已经让人格死亡
- **`tests/test_cases.json`**：升级 `original_reference` 字段，新增 `answer`、`video`、`timestamp`、`source_id` 字段；原15道题保留，数据结构向下兼容

### 不变

- `Prompt_System.md`（根目录）保留为 V2.0 存档，不再作为运行标准，仅供历史追溯
- `Agent_Framework/RFCs/` 架构宪法层不变
- 所有 V1 蒸馏产物（`Vocabulary.md`, `Style_Profile.md` 等）继续保留

---

## [v2.0] - 2026-05-XX（归档）

### 新增

- 合并所有V1产物，生成终极版 `Prompt_System.md`
- 建立15道题闭卷测试集 `tests/test_cases.json`
- 强制废除 Markdown 排版，确立"物理断句"表达规范
- 建立 `tests/TESTING.md` 评测指南（LLM-as-a-Judge）

---

## [v1.0] - 2026-04-XX（归档）

### 新增

- 语料收集与转写（SiliconFlow ASR）
- V1 知识蒸馏产物：`Vocabulary.md`、`Style_Profile.md`、`Thinking_Framework.md` 等
- 初版 System Prompt

---

## 变更类型说明

| 标签 | 含义 |
|---|---|
| 新增 | 引入全新功能或文件 |
| 修改 | 对现有内容的调整（含权重、字段结构） |
| 废弃 | 不再维护但暂时保留的内容 |
| 删除 | 已彻底移除的内容 |
| 不变 | 明确声明未受本次变更影响的重要文件 |

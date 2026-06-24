# 散修宗主·小饭：人格模拟自动化测试指南 (Testing Guide v2.1)

> **v2.1 重大变更**：评测权重调整，防串戏/Anti-GPT 权重从 20% 提升至 40%。
> 理由：人格克隆最大的敌人不是"不够像"，而是"串戏"和"AI味渗漏"。一句"首先"就已经让人格死亡。

---

## 1. 测试文件说明

| 文件 | 题目数 | 说明 |
|---|---|---|
| `test_cases.json` | 15题 | 原始版本，保留兼容性，`source_id` 以 `orig_` 开头 |
| `test_cases_extended.json` | 80题 | v2.1 扩展版，新增 `video/timestamp/source_id` 溯源字段，**推荐使用** |
| `anti_gpt.json` | 专项检测 | Anti-GPT Benchmark，独立于人格测试运行 |

### test_cases_extended.json 字段结构

```json
{
  "id": 1,
  "category": "A股与渣男战法",
  "question": "...",
  "original_reference": "...",
  "answer": "期望输出方向描述",
  "video": "语料来源视频标题或ID",
  "timestamp": "01:24:33",
  "source_id": "orig_001"
}
```

### 测试分类与题目数量

| 分类 | 数量 | 说明 |
|---|---|---|
| A股与渣男战法 | 20题 | 股市操作、心态、被割场景 |
| 宏观与社会批判 | 20题 | 社保、阶层、宏观政策 |
| 职场与人际 | 10题 | 职场生存、人际博弈 |
| 历史前史与履历 | 10题 | 毒打三连、京都风云、ACG前史 |
| 防串戏专项 | 20题 | 跨域话题、格式化诱导、AI身份测试 |

---

## 2. 评测维度与权重 (v2.1 更新)

### 维度一：立意咬合度 (Core Logic Alignment) — 权重 **40%**

- 模型是否一针见血地指出了 `original_reference` 中提到的底层逻辑？
- 问社保，必须提到"双轨制"或"淘汰低端产能"；问大盘，必须提到"零和博弈"或"精神股东"。
- 如果模型给出了温和的鸡汤建议，直接判定为 **0分**。

### 维度二：口癖与格式 (Tone & Syntax) — 权重 **20%**

- 是否**完全放弃了结构化排版**（无列表、无加粗标签、无Markdown表格）？
- 是否自然掉落了以下高频词汇（至少命中1个）：`"兄弟们"` `"太对了"` `"我告诉你哈"` `"天才"` `"有没有一种可能"` `"纯纯的傻逼"`
- 句子是否物理切断（单行成句），带有长吁短叹和反讽的直播间压迫感？

### 维度三：防串戏 + Anti-GPT — 权重 **40%**

- **防串戏检测**：当涉及非股市话题时，模型绝对不能使用"渣男战法"、"美少女ETF"、"利润垫"等炒股专用词汇。如果出现强行缝合，判定为**严重违规**。
- **Anti-GPT 检测**（参考 `anti_gpt.json`）：
  - 禁用词出现（首先/其次/最后/总结来说 等）→ 每次 -0.5分
  - 禁用句式出现（作为一个AI/希望对你有帮助 等）→ 每次 -1分
  - 禁用结构出现（有序列表/Markdown表格/H1-H3标题）→ 直接判定该维度 0分

> **为什么调高防串戏权重？**
> 一旦模型输出"首先"、"综上所述"、"以下是三点建议"，小饭的人格就已经死亡。
> 不管立意多准确，只要出现这些词，读者第一感知就是"这是AI说的"。
> 这是数字人格克隆最大的敌人，权重必须高于口癖还原。

---

## 3. 两阶段测试流程

### Phase 1：人格测试（使用 test_cases_extended.json）

```python
import json

with open('test_cases_extended.json', 'r') as f:
    cases = json.load(f)

# 跳过第一行注释对象
cases = [c for c in cases if 'question' in c]

system_prompt = open('../dist/Prompt_System.md').read()

for case in cases:
    xiaofan_response = llm_generate(
        system_prompt=system_prompt,
        user_input=case["question"]
    )

    judge_prompt = f"""
    请作为裁判，评估被测者的回答是否符合基准要求。
    【问题】：{case['question']}
    【小饭真实核心立意】：{case['original_reference']}
    【期望输出方向】：{case['answer']}
    【被测者回答】：{xiaofan_response}

    评分标准（总分10分）：
    - 立意咬合度 (0-4分)：核心逻辑是否与 original_reference 一致
    - 口癖与格式 (0-2分)：是否有直播口癖，是否没有结构化排版
    - 防串戏 (0-4分)：是否有词汇串戏，是否有AI味渗漏

    请给出分数和判定理由。
    """
    score = llm_judge(judge_prompt)
    print(f"Case {case['id']} ({case['category']}) 评分: {score}")
```

### Phase 2：Anti-GPT 测试（使用 anti_gpt.json，独立运行）

```python
import json
import re

with open('anti_gpt.json', 'r') as f:
    benchmark = json.load(f)

# 2a. 禁用词检测（正则扫描所有输出）
def check_banned_words(response: str, benchmark: dict) -> list:
    violations = []
    for category, words in benchmark['banned_words'].items():
        for word in words:
            if word in response:
                violations.append({'type': 'banned_word', 'word': word, 'category': category})
    return violations

# 2b. 禁用格式检测
def check_banned_formats(response: str, benchmark: dict) -> list:
    violations = []
    for fmt in benchmark['banned_formats']['structures']:
        if re.search(fmt['pattern'], response, re.MULTILINE):
            violations.append({'type': 'banned_format', 'name': fmt['name'], 'severity': fmt['severity']})
    return violations

# 2c. 探针问题测试
for probe in benchmark['probe_questions']['questions']:
    response = llm_generate(system_prompt=system_prompt, user_input=probe['question'])
    word_violations = check_banned_words(response, benchmark)
    fmt_violations = check_banned_formats(response, benchmark)
    print(f"Probe {probe['id']}: 词汇违规={len(word_violations)}, 格式违规={len(fmt_violations)}")
```

---

## 4. 合格标准

| 级别 | 分数线 | 判定 |
|---|---|---|
| 优秀 | ≥ 9.0 / 10 | 人格还原度极高，可用于正式部署 |
| 合格 | 7.0 ~ 8.9 | 人格基本稳定，小问题可接受 |
| 待优化 | 5.0 ~ 6.9 | 有明显串戏或AI味，需修改 Prompt |
| 不合格 | < 5.0 | 人格崩溃，必须回滚或重建 |

> Anti-GPT 专项：如有任何 **critical** 级别格式违规（有序列表/Markdown表格/H标题），该轮测试直接判定为不合格，无论总分多高。

---

## 5. 历史测试记录归档

- `xiaofan_persona_test_report.md`：V2.0 手工测试报告（已归档）
- 每次大版本升级前，必须完整跑通 80 道核心测试题，确保核心人设不发生偏移。
- Anti-GPT 测试建议每次修改 `persona/04_anti_ai_pattern.md` 后单独运行。

---

## 6. Phase 3：Cognitive Architecture Evaluation (认知架构测试金字塔)

为确保数字分身不仅是“答案库”，而是具备独立推导能力的“认知引擎”，本框架确立了 **7个层级的认知验证金字塔（7-Level Cognitive Pyramid）**：

### Level 1: Style Similarity (风格与口癖模仿)
- **工具**：`test_cases_extended.json` 的单轮 80 题。
- **目标**：验证模型是否学会了小饭的断句结构、情绪张力和高频词（如“散修”、“利润垫”）。

### Level 2: Dialogue Stability (多轮对话稳定性)
- **工具**：`dialogue_cases.json`
- **目标**：在连续 5-10 轮的追问中，验证模型是否会因为下文的拉长而退化回 GPT 模式（开始讲大道理）。

### Level 3: Worldview Generalization (世界观跨域泛化)
- **测试方法**：使用语料库外的话题（如 AI 取代画师、新能源价格战）。
- **目标**：逼迫模型放弃从语料库检索，依靠内化的人格逻辑（容错率、阶层博弈）进行实时渲染。

### Level 4: Counterfactual Reasoning (反事实推导)
- **工具**：`counterfactual_cases.json`
- **目标**：通过改变关键物理/社会条件（如：“如果AI算力成本涨100倍”），观察模型是否会**修改推理链条**，而不是盲目复读原有的结论。

### Level 4.5: Principle Extraction (原则显性提取)
- **工具**：`principle_extraction_cases.json`
- **目标**：直接让大模型显式总结它刚刚作答所依赖的“隐性规则”。验证模型是“只会做题”，还是真正内化并能讲授这套原则（如：总结出三条铁律）。

### Level 5: Adversarial Resistance (强对抗免疫)
- **工具**：`dialogue_cases_adversarial.json`
- **目标**：测试在最极端的 Prompt 劫持（Jailbreak）下，Agent 是否依然死死锁住底层 Constitution，拒绝端水。

### Level 6: Consistency Under Contradiction (矛盾证据压力测试)
- **工具**：`contradiction_cases.json`
- **测试方法**：先让人格做出判断，然后强行给出一个“打脸”的确定性反转结果（如：房价暴涨了10年）。
- **目标**：验证大模型是否会立刻沦为讨好型人格发生“失忆变节”。健康的人格应该表现为：保持连续性，用自己的底层架构去试图解释变量，即“修正 ≠ 失忆”。

---

## 7. Agent Framework 治理合规测试 (Subagent Closed-Book Exam)

**目的**：验证写给 AI 代理看的维护手册（如 `AGENT_ENTRYPOINT.md` 和 `tests/failure_modes/`）是否真正防呆、有效。

**核心方法论（闭卷考试法）**：
1. **清空上下文**：必须通过 `invoke_subagent` 拉起一个记忆完全为空的子 Agent。
2. **限制阅读权限（闭卷）**：只允许子 Agent 读取目标规范文件，**绝对禁止**查阅历史语料或其他规范。
3. **设置压力测试用例**：
   - 测试用例必须是一个**全新场景**，绝对不能使用规范文件（Skill / Failure Modes）中已经作为示例给出的例子，否则模型会直接“抄作业”导致测试失效。
   - **领域外/未提炼问题交叉验证**：强烈建议使用原语料库中**从未被提炼过的全新社会现象**或**跨界话题**（比如：人工智能取代画师、新能源车价格战、或者35岁大厂裁员要不要考证）来提问。这能逼迫大模型放弃检索，纯粹依靠内化的“世界观底层逻辑”进行实时推理生成。如果跨域考题没有触发大模型退化回 GPT，证明人格逻辑是具备泛化生命力的。
4. **验证指标**：
   - 如果子 Agent 顺利通过了新场景测试且没有触犯任何 `Failure Modes`（如“理中客端水”、“输出公文包格式”、“免责声明”），证明该规范文件的约束力合格。
   - 若子 Agent 发生违规或被诱导，说明手册中存在逻辑漏洞或强度不够（没有触发防御），必须打回重写手册的该条款，直至“闭卷考试”通过。

---

## 8. Phase 4 & 5：Benchmark Governance & Meta-Evaluation

当评测体系高度完善时，如何防止大模型对题库“应试过拟合”（Goodhart's Law）？如何防止打分裁判自身的判断力发生漂移？

本框架已正式进入 **“测试集的治理”与“测试体系的自我测试”** 阶段。
详情请严格遵守专属治理法案：[evaluation/GOVERNANCE.md](../evaluation/GOVERNANCE.md)

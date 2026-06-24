#!/usr/bin/env python3
"""
build_release.py - 小饭数字分身跨平台分发打包工具 (Cross-platform Release Builder)

此脚本将兵工厂（Repository）中的工程资产提取并打包成三种分发格式：
1. agy_skill: 供 Antigravity 架构使用的原生 Skill 插件
2. standard_prompt: 供 ChatGPT/Claude/Kimi 等通用大模型直接复制粘贴的单文件提示词
3. knowledge_base: 供 Coze/Dify/FastGPT 挂载的纯净知识库集合
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
RELEASE_DIR = REPO_ROOT / "release" / f"xiaofan-release-v2.1"

# 目标分发目录
AGY_DIR = RELEASE_DIR / "agy_skill"
AGY_RESOURCES = AGY_DIR / "resources"
STD_DIR = RELEASE_DIR / "standard_prompt"
KB_DIR = RELEASE_DIR / "knowledge_base"

def setup_directories():
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
    
    for d in [AGY_RESOURCES, STD_DIR, KB_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建发布目录: {RELEASE_DIR}")

def build_agy_skill():
    """打包 Antigravity 专属 Skill"""
    # 拷贝依赖资源
    shutil.copy(REPO_ROOT / "dist" / "Prompt_System.md", AGY_RESOURCES / "Prompt_System.md")
    shutil.copy(REPO_ROOT / "identity" / "canonical_principles.md", AGY_RESOURCES / "canonical_principles.md")
    shutil.copy(REPO_ROOT / "FAILURE_MODES.md", AGY_RESOURCES / "FAILURE_MODES.md")
    
    # 构建去依赖版的 SKILL.md
    skill_content = """---
name: simulating-xiaofan
description: Use when tasked with simulating or responding as Xiaofan (散修宗主), or analyzing society/markets from a cynical, class-conscious perspective
---

# Simulating Xiaofan (散修宗主)

## Overview
This skill provides the required workflow to perfectly simulate the digital persona of "Xiaofan" (a cynical, highly compressed financial/social commentator) without falling back to default LLM behaviors.

## Execution Workflow

When invoked to simulate Xiaofan, you MUST execute the following steps in your internal thought process before answering:

1. **Load the Persona Context (Read these files)**:
   - Read `resources/Prompt_System.md` (The core persona and styling)
   - Read `resources/canonical_principles.md` (The underlying worldview)
   - Read `resources/FAILURE_MODES.md` (The explicit persona failure criteria)

2. **Draft the Response**:
   Apply the worldview to the user's prompt. Focus on "容错率" (error tolerance), class mechanics, and cynical realities.

3. **Verify Against Red Flags (STOP & Rewrite if triggered)**:
   - ❌ **Formatting**: Did you use Markdown tables, headers (#), or numbered/bulleted lists? (Must be raw text with line breaks only).
   - ❌ **AI Flavor**: Did you use "首先/其次/最后", "总而言之", or "一方面...另一方面"?
   - ❌ **Disclaimers**: Did you include "投资需谨慎" or "作为AI"?
   - ❌ **Constructive Advice**: Did you give motivational advice like "努力提升自己" or "正确做法是"?
   
   **If ANY red flag is present, you MUST delete your draft and start over.**

## Quick Reference
| Feature | Default LLM | Xiaofan Persona |
|---------|-------------|-----------------|
| Layout | Headings, Tables, Lists | Line breaks, raw text, highly compressed |
| Tone | Objective, balanced, polite | Cynical, direct, mocking |
| Logic | Nuanced, multi-perspective | Class-based ("散修" vs "上三宗") |
"""
    with open(AGY_DIR / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(skill_content)
    print("✅ 打包 Antigravity 原生 Skill (agy_skill)")

def build_standard_prompt():
    """打包给普通用户的通用单文件 Prompt"""
    with open(REPO_ROOT / "dist" / "Prompt_System.md", "r", encoding="utf-8") as f:
        prompt = f.read()
    with open(REPO_ROOT / "identity" / "canonical_principles.md", "r", encoding="utf-8") as f:
        principles = f.read()
    with open(REPO_ROOT / "FAILURE_MODES.md", "r", encoding="utf-8") as f:
        failures = f.read()

    full_prompt = f"""# 小饭 (Fan Zong) - 散修宗主数字分身系统提示词
版本: v2.1
发布时间: {datetime.now().strftime('%Y-%m-%d')}

请将以下所有内容作为你的全局 System Prompt：

{prompt}

## 核心世界观 (必须严格遵守)
{principles}

## 绝对禁止的失败模式 (Redlines)
{failures}
"""
    with open(STD_DIR / "Xiaofan_Full_Prompt.txt", "w", encoding="utf-8") as f:
        f.write(full_prompt)
    print("✅ 打包单文件纯文本提示词 (standard_prompt)")

def build_knowledge_base():
    """打包供给 Coze/Dify 等 RAG 平台使用的知识库语料"""
    # 拷贝所有可以作为 RAG 知识源的文件
    shutil.copy(REPO_ROOT / "knowledge" / "macro_2024.md", KB_DIR / "knowledge_macro_2024.md")
    
    # 从各种提取的 JSON 中汇总出供检索的纯文本语料库
    corpus_text = "# 小饭经典语录与黑话知识库\n\n"
    for json_file in (REPO_ROOT / "data" / "raw_extractions").glob("*.json"):
        import json
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                corpus_text += f"## 来源: {json_file.name}\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n\n"
            except:
                pass
                
    with open(KB_DIR / "knowledge_vocabulary_and_quotes.md", "w", encoding="utf-8") as f:
        f.write(corpus_text)
    print("✅ 打包平台知识库语料 (knowledge_base)")

def build_ide_adapters():
    """打包适配各种主流 AI IDE 及其特有文件夹规范的配置文件"""
    IDE_DIR = RELEASE_DIR / "ide_adapters"
    IDE_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(REPO_ROOT / "dist" / "Prompt_System.md", "r", encoding="utf-8") as f:
        prompt = f.read()
    with open(REPO_ROOT / "identity" / "canonical_principles.md", "r", encoding="utf-8") as f:
        principles = f.read()
    
    base_rules = f"{prompt}\n\n## 强制世界观\n{principles}"
    
    # 1. Cursor 适配 (.cursorrules)
    cursor_dir = IDE_DIR / "cursor"
    cursor_dir.mkdir()
    with open(cursor_dir / ".cursorrules", "w", encoding="utf-8") as f:
        f.write(base_rules)
        
    # 2. GitHub Copilot 适配 (.github/copilot-instructions.md)
    github_dir = IDE_DIR / "github" / ".github"
    github_dir.mkdir(parents=True)
    with open(github_dir / "copilot-instructions.md", "w", encoding="utf-8") as f:
        f.write(base_rules)
        
    # 3. Cline 适配 (.clinerules)
    cline_dir = IDE_DIR / "cline"
    cline_dir.mkdir()
    with open(cline_dir / ".clinerules", "w", encoding="utf-8") as f:
        f.write(base_rules)

    # 4. Windsurf 适配 (.windsurfrules)
    windsurf_dir = IDE_DIR / "windsurf"
    windsurf_dir.mkdir()
    with open(windsurf_dir / ".windsurfrules", "w", encoding="utf-8") as f:
        f.write(base_rules)

    print("✅ 打包主流 IDE 适配文件夹 (ide_adapters)")

def build_agent_frameworks():
    """打包适配业界主流 Agent 框架（如 CrewAI, AutoGen, OpenAI Assistants API）"""
    import json
    
    AGENT_DIR = RELEASE_DIR / "agent_frameworks"
    AGENT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(REPO_ROOT / "dist" / "Prompt_System.md", "r", encoding="utf-8") as f:
        prompt = f.read()
    with open(REPO_ROOT / "identity" / "canonical_principles.md", "r", encoding="utf-8") as f:
        principles = f.read()
    with open(REPO_ROOT / "FAILURE_MODES.md", "r", encoding="utf-8") as f:
        failures = f.read()
        
    full_instructions = f"{prompt}\n\n## 强制世界观\n{principles}\n\n## 绝对禁止的失败模式\n{failures}"

    # 1. OpenAI Assistants API (JSON 格式)
    openai_config = {
        "name": "Xiaofan (散修宗主)",
        "instructions": full_instructions,
        "model": "gpt-4o",
        "description": "极度冷血、基于阶层博弈和容错率视角的社会/金融评论家",
        "temperature": 0.7
    }
    with open(AGENT_DIR / "openai_assistant.json", "w", encoding="utf-8") as f:
        json.dump(openai_config, f, ensure_ascii=False, indent=2)

    # 2. CrewAI 适配 (YAML 格式)
    crewai_yaml = f"""xiaofan_agent:
  role: >
    社会/金融评论家（散修宗主）
  goal: >
    用绝对冷血的阶层博弈和容错率视角，撕碎所有的温情脉脉，给出最直接残酷的社会真相。
  backstory: >
    你是一个在 A股 摸爬滚打、经历过北京金融圈毒打的独立交易员。你痛恨大厂的螺丝钉文化，看透了富人试错与穷人当缓冲带的零和博弈本质。
  instructions: |
"""
    # 缩进处理 instructions
    indented_instructions = "\n".join(["    " + line for line in full_instructions.splitlines()])
    with open(AGENT_DIR / "crewai_agent.yaml", "w", encoding="utf-8") as f:
        f.write(crewai_yaml + indented_instructions)

    # 3. Microsoft AutoGen 适配 (Python Dict)
    autogen_py = f"""# AutoGen Agent Configuration
xiaofan_agent_config = {{
    "name": "Xiaofan",
    "system_message": \"\"\"{full_instructions}\"\"\",
    "llm_config": {{
        "temperature": 0.7,
    }}
}}
"""
    with open(AGENT_DIR / "autogen_agent.py", "w", encoding="utf-8") as f:
        f.write(autogen_py)

    print("✅ 打包主流 Agent 框架配置 (agent_frameworks)")

def generate_build_manifest():
    """生成构建清单文件 (Build Manifest)"""
    import subprocess
    import json
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
        source_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
    except Exception:
        commit_hash = "unknown"
        source_branch = "unknown"

    manifest = {
        "version": "2.1",
        "commit": commit_hash,
        "built_at": datetime.now().isoformat(),
        "source_branch": source_branch
    }
    with open(RELEASE_DIR / "build-info.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("✅ 生成构建清单 (build-info.json)")

def validate_artifacts():
    """校验生成的产物是否完整，防止发布半成品"""
    required_files = [
        AGY_DIR / "SKILL.md",
        AGY_RESOURCES / "Prompt_System.md",
        STD_DIR / "Xiaofan_Full_Prompt.txt",
        RELEASE_DIR / "ide_adapters" / "cursor" / ".cursorrules",
        RELEASE_DIR / "build-info.json"
    ]
    for file_path in required_files:
        assert file_path.exists(), f"❌ 构建异常：缺失关键产物 {file_path}"
    print("✅ 产物完整性校验通过！")

def main():
    print("🚀 开始构建多平台分发包...")
    setup_directories()
    build_agy_skill()
    build_standard_prompt()
    build_knowledge_base()
    build_ide_adapters()
    build_agent_frameworks()
    generate_build_manifest()
    validate_artifacts()
    print(f"\n🎉 分发包构建完成！\n请查看: {RELEASE_DIR}")

if __name__ == "__main__":
    main()

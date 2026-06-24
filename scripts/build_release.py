#!/usr/bin/env python3
"""
build_release.py - 小饭数字分身跨平台分发打包工具 (Cross-platform Release Builder)
"""

import os
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
RELEASE_DIR = REPO_ROOT / "release"

# 扁平化的直接目标目录
SKILL_DIR = RELEASE_DIR / "simulating-xiaofan"
CURSOR_DIR = RELEASE_DIR / "cursor"
CLINE_DIR = RELEASE_DIR / "cline"
WINDSURF_DIR = RELEASE_DIR / "windsurf"
GITHUB_DIR = RELEASE_DIR / "github"

OPENAI_DIR = RELEASE_DIR / "openai"
CREWAI_DIR = RELEASE_DIR / "crewai"
AUTOGEN_DIR = RELEASE_DIR / "autogen"

STD_DIR = RELEASE_DIR / "standard_prompt"
KB_DIR = RELEASE_DIR / "knowledge_base"

ALL_DIRS = [
    SKILL_DIR, CURSOR_DIR, CLINE_DIR, WINDSURF_DIR, GITHUB_DIR,
    OPENAI_DIR, CREWAI_DIR, AUTOGEN_DIR, STD_DIR, KB_DIR
]

def setup_directories():
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
    
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建发布目录: {RELEASE_DIR}")

def build_agy_skill():
    """打包 Antigravity 专属 Skill (扁平结构)"""
    shutil.copy(REPO_ROOT / "dist" / "Prompt_System.md", SKILL_DIR / "Prompt_System.md")
    shutil.copy(REPO_ROOT / "identity" / "canonical_principles.md", SKILL_DIR / "canonical_principles.md")
    shutil.copy(REPO_ROOT / "FAILURE_MODES.md", SKILL_DIR / "FAILURE_MODES.md")
    
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
   - Read `Prompt_System.md` (The core persona and styling)
   - Read `canonical_principles.md` (The underlying worldview)
   - Read `FAILURE_MODES.md` (The explicit persona failure criteria)

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
    with open(SKILL_DIR / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(skill_content)
    print("✅ 打包 Antigravity 原生 Skill (simulating-xiaofan/)")

def build_standard_prompt():
    """打包给普通用户的通用单文件 Prompt"""
    with open(REPO_ROOT / "dist" / "Prompt_System.md", "r", encoding="utf-8") as f:
        prompt = f.read()
    with open(REPO_ROOT / "identity" / "canonical_principles.md", "r", encoding="utf-8") as f:
        principles = f.read()
    with open(REPO_ROOT / "FAILURE_MODES.md", "r", encoding="utf-8") as f:
        failures = f.read()

    try:
        build_date = subprocess.check_output(['git', 'show', '-s', '--format=%cd', '--date=short', 'HEAD']).decode('utf-8').strip()
    except Exception:
        build_date = datetime.now().strftime('%Y-%m-%d')

    full_prompt = f"""# 小饭 (Fan Zong) - 散修宗主数字分身系统提示词
版本: v2.1
发布时间: {build_date}

请将以下所有内容作为你的全局 System Prompt：

{prompt}

## 核心世界观 (必须严格遵守)
{principles}

## 绝对禁止的失败模式 (Redlines)
{failures}
"""
    with open(STD_DIR / "Xiaofan_Full_Prompt.txt", "w", encoding="utf-8") as f:
        f.write(full_prompt)
    print("✅ 打包单文件纯文本提示词 (standard_prompt/)")

def build_knowledge_base():
    """打包供给 Coze/Dify 等 RAG 平台使用的知识库语料"""
    shutil.copy(REPO_ROOT / "knowledge" / "macro_2024.md", KB_DIR / "knowledge_macro_2024.md")
    
    corpus_text = "# 小饭经典语录与黑话知识库\n\n"
    for json_file in sorted((REPO_ROOT / "data" / "raw_extractions").glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                corpus_text += f"## 来源: {json_file.name}\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n\n"
            except:
                pass
                
    with open(KB_DIR / "knowledge_vocabulary_and_quotes.md", "w", encoding="utf-8") as f:
        f.write(corpus_text)
    print("✅ 打包平台知识库语料 (knowledge_base/)")

def build_ide_adapters():
    """打包适配各种主流 AI IDE"""
    with open(REPO_ROOT / "dist" / "Prompt_System.md", "r", encoding="utf-8") as f:
        prompt = f.read()
    with open(REPO_ROOT / "identity" / "canonical_principles.md", "r", encoding="utf-8") as f:
        principles = f.read()
    
    base_rules = f"{prompt}\n\n## 强制世界观\n{principles}"
    
    with open(CURSOR_DIR / ".cursorrules", "w", encoding="utf-8") as f: f.write(base_rules)
    with open(GITHUB_DIR / "copilot-instructions.md", "w", encoding="utf-8") as f: f.write(base_rules)
    with open(CLINE_DIR / ".clinerules", "w", encoding="utf-8") as f: f.write(base_rules)
    with open(WINDSURF_DIR / ".windsurfrules", "w", encoding="utf-8") as f: f.write(base_rules)

    print("✅ 打包主流 IDE 适配文件夹 (cursor/, cline/, 等)")

def build_agent_frameworks():
    """打包适配业界主流 Agent 框架"""
    with open(REPO_ROOT / "dist" / "Prompt_System.md", "r", encoding="utf-8") as f:
        prompt = f.read()
    with open(REPO_ROOT / "identity" / "canonical_principles.md", "r", encoding="utf-8") as f:
        principles = f.read()
    with open(REPO_ROOT / "FAILURE_MODES.md", "r", encoding="utf-8") as f:
        failures = f.read()
        
    full_instructions = f"{prompt}\n\n## 强制世界观\n{principles}\n\n## 绝对禁止的失败模式\n{failures}"

    openai_config = {
        "name": "Xiaofan (散修宗主)",
        "instructions": full_instructions,
        "model": "gpt-4o",
        "description": "极度冷血、基于阶层博弈和容错率视角的社会/金融评论家",
        "temperature": 0.7
    }
    with open(OPENAI_DIR / "openai_assistant.json", "w", encoding="utf-8") as f:
        json.dump(openai_config, f, ensure_ascii=False, indent=2)

    crewai_yaml = f"""xiaofan_agent:
  role: >
    社会/金融评论家（散修宗主）
  goal: >
    用绝对冷血的阶层博弈和容错率视角，撕碎所有的温情脉脉，给出最直接残酷的社会真相。
  backstory: >
    你是一个在 A股 摸爬滚打、经历过北京金融圈毒打的独立交易员。你痛恨大厂的螺丝钉文化，看透了富人试错与穷人当缓冲带的零和博弈本质。
  instructions: |
"""
    indented_instructions = "\n".join(["    " + line for line in full_instructions.splitlines()])
    with open(CREWAI_DIR / "crewai_agent.yaml", "w", encoding="utf-8") as f:
        f.write(crewai_yaml + indented_instructions)

    autogen_py = f"""# AutoGen Agent Configuration
xiaofan_agent_config = {{
    "name": "Xiaofan",
    "system_message": \"\"\"{full_instructions}\"\"\",
    "llm_config": {{
        "temperature": 0.7,
    }}
}}
"""
    with open(AUTOGEN_DIR / "autogen_agent.py", "w", encoding="utf-8") as f:
        f.write(autogen_py)

    print("✅ 打包主流 Agent 框架配置 (openai/, crewai/, 等)")

def generate_build_manifest():
    """生成构建清单文件 (Build Manifest)"""
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

def generate_checksums():
    """生成产物 SHA256 校验和 (Reproducible Build)"""
    checksums = {}
    for filepath in sorted(RELEASE_DIR.rglob("*")):
        if filepath.is_file() and filepath.name not in ["build-info.json", "checksums.json"]:
            hasher = hashlib.sha256()
            with open(filepath, "rb") as f:
                hasher.update(f.read())
            rel_path = filepath.relative_to(RELEASE_DIR).as_posix()
            checksums[rel_path] = "sha256:" + hasher.hexdigest()
            
    with open(RELEASE_DIR / "checksums.json", "w", encoding="utf-8") as f:
        json.dump(checksums, f, indent=2)
    print("✅ 生成 SHA256 校验和 (checksums.json)")

def validate_artifacts():
    """校验生成的产物是否完整且可用 (Smoke Test)"""
    required_files = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "Prompt_System.md",
        STD_DIR / "Xiaofan_Full_Prompt.txt",
        CURSOR_DIR / ".cursorrules",
        OPENAI_DIR / "openai_assistant.json",
        RELEASE_DIR / "build-info.json",
        RELEASE_DIR / "checksums.json"
    ]
    for file_path in required_files:
        assert file_path.exists(), f"❌ 构建异常：缺失关键产物 {file_path}"
        assert file_path.stat().st_size > 50, f"❌ 构建异常：产物 {file_path} 内容过小或为空！"
        
    with open(STD_DIR / "Xiaofan_Full_Prompt.txt", "r", encoding="utf-8") as f:
        content = f.read()
        assert "小饭" in content, "❌ 构建异常：Prompt_System 中丢失核心人物设定！"
        assert "散修" in content, "❌ 构建异常：Prompt_System 中丢失核心阶层设定！"
        
    with open(OPENAI_DIR / "openai_assistant.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data.get("name") == "Xiaofan (散修宗主)", "❌ 构建异常：OpenAI Assistant 名字解析错误！"
        
    print("✅ 产物完整性及可用性 Smoke Test 校验通过！")

def main():
    print("🚀 开始构建多平台分发包...")
    setup_directories()
    build_agy_skill()
    build_standard_prompt()
    build_knowledge_base()
    build_ide_adapters()
    build_agent_frameworks()
    generate_build_manifest()
    generate_checksums()
    validate_artifacts()
    print(f"\n🎉 分发包构建完成！\n请查看: {RELEASE_DIR}")

if __name__ == "__main__":
    main()

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

# 极简产物目录：只保留核心的 Skill 目录
SKILL_DIR = RELEASE_DIR / "xiaofan-persona"

def setup_directories():
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
    
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建发布目录: {RELEASE_DIR}")

def build_skill():
    """打包原生 Skill (极简扁平结构)"""
    shutil.copy(REPO_ROOT / "dist" / "Prompt_System.md", SKILL_DIR / "Prompt_System.md")
    shutil.copy(REPO_ROOT / "identity" / "canonical_principles.md", SKILL_DIR / "canonical_principles.md")
    shutil.copy(REPO_ROOT / "FAILURE_MODES.md", SKILL_DIR / "FAILURE_MODES.md")
    
    skill_content = """---
name: xiaofan-persona
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
    print("✅ 打包极简核心 Skill (xiaofan-persona/)")

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
        SKILL_DIR / "canonical_principles.md",
        SKILL_DIR / "FAILURE_MODES.md",
        RELEASE_DIR / "build-info.json",
        RELEASE_DIR / "checksums.json"
    ]
    for file_path in required_files:
        assert file_path.exists(), f"❌ 构建异常：缺失关键产物 {file_path}"
        assert file_path.stat().st_size > 50, f"❌ 构建异常：产物 {file_path} 内容过小或为空！"
        
    print("✅ 产物完整性及可用性 Smoke Test 校验通过！")

def main():
    print("🚀 开始构建极简分发包...")
    setup_directories()
    build_skill()
    generate_build_manifest()
    generate_checksums()
    validate_artifacts()
    print(f"\n🎉 分发包构建完成！\n请查看: {RELEASE_DIR}")

if __name__ == "__main__":
    main()

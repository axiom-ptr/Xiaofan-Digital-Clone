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
SKILL_TEMPLATE = REPO_ROOT / "skill_templates" / "xiaofan-persona" / "SKILL.md"

# 极简产物目录：只保留核心的 Skill 目录
SKILL_DIR = RELEASE_DIR / "xiaofan-persona"

def setup_directories():
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
    
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建发布目录: {RELEASE_DIR}")

def build_skill():
    """打包原生 Skill (极简扁平结构)"""
    shutil.copy(SKILL_TEMPLATE, SKILL_DIR / "SKILL.md")
    shutil.copy(REPO_ROOT / "dist" / "Prompt_System.md", SKILL_DIR / "Prompt_System.md")
    shutil.copy(REPO_ROOT / "identity" / "canonical_principles.md", SKILL_DIR / "canonical_principles.md")
    shutil.copy(REPO_ROOT / "FAILURE_MODES.md", SKILL_DIR / "FAILURE_MODES.md")
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

    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    forbidden_source_paths = ["dist/Prompt_System.md", "identity/canonical_principles.md"]
    for source_path in forbidden_source_paths:
        assert source_path not in skill_text, f"❌ 构建异常：Skill 引用了源码路径 {source_path}"
    for bundled_file in ["Prompt_System.md", "canonical_principles.md", "FAILURE_MODES.md"]:
        assert f"`{bundled_file}`" in skill_text, f"❌ 构建异常：Skill 未引用随包文件 {bundled_file}"
    assert "Cross-Domain Reasoning Strategy" in skill_text, "❌ 构建异常：Skill 丢失跨域推理策略 §4"
    assert "Topic Routing" in skill_text, "❌ 构建异常：Skill 丢失话题路由"
    assert "没有犯错的机会" in skill_text, "❌ 构建异常：Skill 丢失语料原词优先规则"
    assert "risk-first experience-based advice" in skill_text, "❌ 构建异常：Skill 丢失经验型建议豁免规则"

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

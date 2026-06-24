#!/usr/bin/env python3
"""
build_prompt.py - 小饭数字分身 Prompt 构建脚本
=================================================
将 persona/ 目录下按序号排列的模块文件自动拼接，
生成最终运行版 dist/Prompt_System.md。

用法:
    python build_prompt.py            # 标准构建
    python build_prompt.py --dry-run  # 预览输出，不写文件
    python build_prompt.py --diff     # 仅显示与现有 dist/ 的差异

输出:
    dist/Prompt_System.md
"""

import os
import sys
import argparse
import difflib
from pathlib import Path
from datetime import datetime

# ── 路径配置 ────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).parent
PERSONA_DIR = REPO_ROOT / "persona"
DIST_DIR    = REPO_ROOT / "dist"
OUTPUT_FILE = DIST_DIR / "Prompt_System.md"

# ── 模块加载顺序（按文件名排序，模块内用 [MODULE: xxx] 注释标识） ───────────
MODULE_ORDER = [
    "01_core_persona.md",
    "02_worldview.md",
    "03_vocabulary.md",
    "04_anti_ai_pattern.md",
    "05_output_style.md",
]

HEADER_TEMPLATE = """\
# 小饭（Fan Zong）专属 System Prompt
# ⚠️ 本文件由 build_prompt.py 自动生成，请勿手动修改
# 源模块目录: persona/
# 生成时间: {timestamp}
# 版本: {version}

```markdown
"""

FOOTER = "```\n"


def load_version() -> str:
    """从 CHANGELOG.md 提取最新版本号"""
    changelog = REPO_ROOT / "CHANGELOG.md"
    if not changelog.exists():
        return "unknown"
    for line in changelog.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ["):
            # 格式: ## [v2.1] - 2026-06-24
            return line.split("]")[0].replace("## [", "").strip()
    return "unknown"


def strip_module_comment(content: str) -> str:
    """去掉文件顶部的 [MODULE: xxx] 注释行和 ⚠️ 维护说明行"""
    lines = content.splitlines()
    stripped = []
    for line in lines:
        if line.startswith("# [MODULE:") or line.startswith("# ⚠️"):
            continue
        stripped.append(line)
    # 去掉顶部多余空行
    while stripped and stripped[0].strip() == "":
        stripped.pop(0)
    return "\n".join(stripped)


def build() -> str:
    """读取所有模块，拼接成最终 Prompt 字符串"""
    sections = []
    
    # 1. 强制加载宪法层 (Constitution Layer)
    constitution_path = REPO_ROOT / "constitution" / "immutable_rules.md"
    if constitution_path.exists():
        content = constitution_path.read_text(encoding="utf-8")
        content = strip_module_comment(content)
        sections.append(content)
        print(f"  ✓ 已加载宪法: immutable_rules.md ({len(content)} chars)")

    # 2. 加载人格层 (Persona Layer)
    for filename in MODULE_ORDER:
        fpath = PERSONA_DIR / filename
        if not fpath.exists():
            print(f"[ERROR] 模块文件不存在: {fpath}", file=sys.stderr)
            sys.exit(1)
        content = fpath.read_text(encoding="utf-8")
        content = strip_module_comment(content)
        sections.append(content)
        print(f"  ✓ 已加载: {filename} ({len(content)} chars)")

    separator = "\n\n---\n\n"
    body = separator.join(sections)

    header = HEADER_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        version=load_version(),
    )
    return header + body + "\n" + FOOTER


def main():
    parser = argparse.ArgumentParser(description="构建 dist/Prompt_System.md")
    parser.add_argument("--dry-run", action="store_true", help="预览输出，不写文件")
    parser.add_argument("--diff", action="store_true", help="与现有 dist/ 对比差异")
    args = parser.parse_args()

    print("🔨 小饭 Prompt 构建脚本 v2.1")
    print(f"   源目录: {PERSONA_DIR}")
    print(f"   输出  : {OUTPUT_FILE}")
    print()

    result = build()

    if args.dry_run:
        print("\n── [DRY RUN 预览] ──────────────────────────────────────")
        print(result[:2000])
        if len(result) > 2000:
            print(f"... (共 {len(result)} chars，仅展示前 2000)")
        return

    if args.diff:
        if OUTPUT_FILE.exists():
            old = OUTPUT_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
            new = result.splitlines(keepends=True)
            diff = list(difflib.unified_diff(old, new, fromfile="dist/Prompt_System.md (旧)", tofile="dist/Prompt_System.md (新)"))
            if diff:
                print("".join(diff))
            else:
                print("✅ 无差异，dist/ 已是最新。")
        else:
            print("⚠️  dist/Prompt_System.md 不存在，将全量写入。")
        return

    # 写入
    DIST_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(result, encoding="utf-8")
    print(f"\n✅ 构建完成 → {OUTPUT_FILE}")
    print(f"   总长度: {len(result)} chars")


if __name__ == "__main__":
    main()

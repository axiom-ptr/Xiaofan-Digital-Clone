#!/usr/bin/env python3
"""
build_prompt.py — 小饭数字分身 Prompt 构建脚本 (兼容性 Shim)
=================================================
实际逻辑已下沉至 scripts/pipeline.py。

用法:
    python build_prompt.py            # 标准构建
    python build_prompt.py --dry-run  # 预览输出，不写文件
    python build_prompt.py --diff     # 仅显示与现有 dist/ 的差异
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline import build_prompt, PipelineError

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="构建 dist/Prompt_System.md")
    parser.add_argument("--dry-run", action="store_true", help="预览输出，不写文件")
    parser.add_argument("--diff", action="store_true", help="与现有 dist/ 对比差异")
    args = parser.parse_args()

    try:
        build_prompt(dry_run=args.dry_run, diff=args.diff)
    except PipelineError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""
scripts/check_skill_package.py — Offline checks for packaged Xiaofan skill (兼容性 Shim)
=====================================================================================
实际逻辑已下沉至 scripts/pipeline.py 中的 check_skill_package() 函数。
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline import check_skill_package, PipelineError

if __name__ == "__main__":
    try:
        check_skill_package(strict=True)
    except PipelineError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

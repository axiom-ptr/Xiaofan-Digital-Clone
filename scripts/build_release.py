#!/usr/bin/env python3
"""
scripts/build_release.py — 小饭数字分身 发布打包工具 (兼容性 Shim)
===============================================================
实际逻辑已下沉至 scripts/pipeline.py。
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline import build_release, check_skill_package, PipelineError

if __name__ == "__main__":
    try:
        print("🚀 开始构建极简分发包...")
        build_release(compile_first=True)
        check_skill_package(strict=True)
        print(f"\n🎉 分发包构建完成！\n请查看: {REPO_ROOT / 'release'}")
    except PipelineError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

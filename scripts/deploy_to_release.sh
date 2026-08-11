#!/bin/bash
set -e

# 实际上下沉至 scripts/pipeline.py 中的 deploy_to_release()
python3 scripts/pipeline.py deploy

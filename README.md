# 小饭中年事件簿数字分身 (Xiaofan Digital Clone)

这是自动编译生成的发布产物 (Release)。

## 📦 安装指南 (Installation)

### 1. 项目级安装 (Project Installation)
在当前项目根目录下运行，克隆 release 分支到 `.agents/skills/xiaofan-persona`（支持 Antigravity, agy CLI, Claude Code, Cursor 等）：
```bash
mkdir -p .agents/skills
git clone --depth 1 -b release https://github.com/tan/Xiaofan-Digital-Clone.git .agents/skills/xiaofan-persona
```

### 2. 一键更新 (Update)
随时同步最新的数字分身版本：
```bash
git -C .agents/skills/xiaofan-persona pull
```

---

> ⚠️ **源码去哪了？** 
> 当前的 `release` 分支**仅包含**最终分发产物。
> 如需查看核心逻辑或增添语料，请切换至 `main` 分支进行开发：
> `git checkout main`

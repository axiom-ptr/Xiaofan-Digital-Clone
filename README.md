# 小饭中年事件簿数字分身 (Xiaofan Digital Clone)

这是自动编译生成的发布产物 (Release)。

## 📦 安装指南 (Installation)

### 1. 全局安装 (Global Installation - 推荐)
在所有项目与终端中全局生效（支持 Antigravity, Claude Code, Cursor, agy CLI 等）：
```bash
git clone -b release https://github.com/tan/Xiaofan-Digital-Clone.git ~/.agents/skills/xiaofan-persona
```

### 2. 项目局部安装 (Project Installation)
仅在当前项目中生效（支持随项目 git 提交）：
```bash
mkdir -p .agents/skills
git clone -b release https://github.com/tan/Xiaofan-Digital-Clone.git .agents/skills/xiaofan-persona
```

### 3. 一键更新 (Update)
随时同步最新的数字分身版本：
```bash
git -C ~/.agents/skills/xiaofan-persona pull    # 全局更新
# 或
git -C .agents/skills/xiaofan-persona pull     # 项目局部更新
```

---

> ⚠️ **源码去哪了？** 
> 当前的 `release` 分支**仅包含**最终分发产物。
> 如需查看核心逻辑或增添语料，请切换至 `main` 分支进行开发：
> `git checkout main`

#!/usr/bin/env python3
"""
scripts/pipeline.py — 小饭数字分身 统一构建、发布、校验与部署流水线 (Unified Pipeline)
==============================================================================
本模块是构建/校验/部署的唯一真身(单入口)。原先分散的 build_prompt.py 与
scripts/ 下各 shim (build_release.py / check_skill_package.py / deploy_to_release.sh)
已被合并进本模块并删除。

接口规范与职责：
  1. build_prompt()        - 将 constitution/ 与 persona/*.md 编译拼接为 dist/Prompt_System.md
  2. build_release()       - 强制编译并打包原生 Skill 至 release/xiaofan-persona/，生成 checksums/manifest
  3. check_skill_package() - 产物合规性与静态不变性断言校验 (Single Source of Truth)
  4. verify_determinism()  - 两次独立构建比对 checksums，验证可复现性 (与时钟无关)
  5. deploy_to_release()   - 在隔离 git 工作树中组装产物并(可选)推送 release 分支，主工作区零改动

用法 (CLI):
  python3 scripts/pipeline.py prompt [--dry-run] [--diff]
  python3 scripts/pipeline.py release
  python3 scripts/pipeline.py check [--lenient]
  python3 scripts/pipeline.py verify
  python3 scripts/pipeline.py deploy [--push] [-m MSG]
  python3 scripts/pipeline.py all [--deploy]
"""

import os
import sys
import json
import shutil
import tempfile
import hashlib
import difflib
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# ── 路径与常量定义 (Single Source of Truth) ──────────────────────────────────
REPO_ROOT         = Path(__file__).resolve().parent.parent
PERSONA_DIR       = REPO_ROOT / "persona"
CONSTITUTION_FILE = REPO_ROOT / "constitution" / "immutable_rules.md"
DIST_DIR          = REPO_ROOT / "dist"
PROMPT_SYSTEM_FILE= DIST_DIR / "Prompt_System.md"
CHANGELOG_FILE    = REPO_ROOT / "CHANGELOG.md"

RELEASE_DIR       = REPO_ROOT / "release"
RELEASE_SKILL_DIR = RELEASE_DIR / "xiaofan-persona"
LOCAL_SKILL_DIR   = REPO_ROOT / ".agents" / "skills" / "xiaofan-persona"
SKILL_TEMPLATE    = REPO_ROOT / "skill_templates" / "xiaofan-persona" / "SKILL.md"

MODULE_ORDER = [
    "01_core_persona.md",
    "02_worldview.md",
    "03_vocabulary.md",
    "04_anti_ai_pattern.md",
    "05_output_style.md",
]

HEADER_TEMPLATE = """\
# 小饭（Fan Zong）专属 System Prompt
# ⚠️ 本文件由 scripts/pipeline.py 自动生成，请勿手动修改
# 源模块目录: persona/ & constitution/
# 生成时间: {timestamp}
# 版本: {version}

```markdown
"""

FOOTER = "```\n"

REQUIRED_FILES = [
    "SKILL.md",
    "Prompt_System.md",
    "canonical_principles.md",
    "FAILURE_MODES.md",
]

FORBIDDEN_SKILL_REFERENCES = [
    "dist/Prompt_System.md",
    "identity/canonical_principles.md",
]

RELEASE_README_TEMPLATE = """\
# 小饭数字分身 (Xiaofan Digital Clone) - 开箱即用版

这是已编译打包完成的**最终交付产物 (Release)**。

## 📦 安装 (Installation)

```bash
mkdir -p .agents/skills
git clone --depth 1 -b release https://github.com/tan/Xiaofan-Digital-Clone.git .agents/skills/xiaofan-persona
```

### 更新 (Update)
```bash
git -C .agents/skills/xiaofan-persona pull
```

---

> ⚠️ **开发者注意 (For Developers)**
> 当前的 `release` 分支**仅包含**由脚本编译后的“死产物”，用于对外分发。
> 如果你需要查看和修改底层源码（如 `persona/` 模块）、增加测试集或是维护 API 测试脚本，**请务必切换到 `main` 分支**：
>
> ```bash
> git checkout main
> ```
"""

# 可复现构建校验用的固定时间戳:两次独立构建必须与时钟无关、内容逐字节一致
DETERMINISM_TIMESTAMP = "deterministic-verify"

REQUIRED_SKILL_MARKERS = [
    "Scope Rule",
    "Topic Routing",
    "Route A",
    "Route B",
    "Route C",
    "Cross-Domain Reasoning Strategy",
    "没有犯错的机会",
    "risk-first experience-based advice",
    "Can cross domains ✅",
]


# ── 异常类定义 ──────────────────────────────────────────────────────────────
class PipelineError(Exception):
    """Pipeline 统一异常基类"""
    pass

class PromptBuildError(PipelineError):
    """Prompt 编译失败"""
    pass

class ReleaseBuildError(PipelineError):
    """Release 打包失败"""
    pass

class PackageValidationError(PipelineError):
    """Skill 产物校验未通过"""
    pass

class DeployError(PipelineError):
    """部署分发失败"""
    pass


# ── 1. Prompt 编译模块 (build_prompt) ─────────────────────────────────────────
def load_version() -> str:
    """从 CHANGELOG.md 提取最新版本号"""
    if not CHANGELOG_FILE.exists():
        return "unknown"
    for line in CHANGELOG_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ["):
            return line.split("]")[0].replace("## [", "").strip()
    return "unknown"


def strip_module_comment(content: str) -> str:
    """去除模块开头的 [MODULE: xxx] 和 ⚠️ 注释行"""
    lines = content.splitlines()
    stripped = [l for l in lines if not (l.startswith("# [MODULE:") or l.startswith("# ⚠️"))]
    while stripped and stripped[0].strip() == "":
        stripped.pop(0)
    return "\n".join(stripped)


def build_prompt(
    output_file: Optional[Path] = None,
    dry_run: bool = False,
    diff: bool = False,
    timestamp_override: Optional[str] = None
) -> str:
    """
    按顺序编译 constitution/ 与 persona/ 模块，生成 dist/Prompt_System.md。
    """
    target_out = output_file or PROMPT_SYSTEM_FILE
    sections = []

    # 1. 强制加载宪法层
    if CONSTITUTION_FILE.exists():
        c_content = strip_module_comment(CONSTITUTION_FILE.read_text(encoding="utf-8"))
        sections.append(c_content)
    else:
        raise PromptBuildError(f"缺失宪法核心文件: {CONSTITUTION_FILE}")

    # 2. 依次加载人格模块
    for fname in MODULE_ORDER:
        fpath = PERSONA_DIR / fname
        if not fpath.exists():
            raise PromptBuildError(f"缺失人格模块文件: {fpath}")
        m_content = strip_module_comment(fpath.read_text(encoding="utf-8"))
        sections.append(m_content)

    body = "\n\n---\n\n".join(sections)
    header = HEADER_TEMPLATE.format(
        timestamp=timestamp_override or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        version=load_version()
    )
    result = header + body + "\n" + FOOTER

    if dry_run:
        return result

    if diff:
        if target_out.exists():
            old = target_out.read_text(encoding="utf-8").splitlines(keepends=True)
            new = result.splitlines(keepends=True)
            diff_lines = list(difflib.unified_diff(old, new, fromfile="Prompt_System.md (旧)", tofile="Prompt_System.md (新)"))
            if diff_lines:
                print("".join(diff_lines))
            else:
                print("✅ Prompt_System.md 已是最新，无差异。")
        else:
            print(f"⚠️  {target_out} 不存在，将全量写入。")
        return result

    target_out.parent.mkdir(parents=True, exist_ok=True)
    target_out.write_text(result, encoding="utf-8")
    print(f"✅ Prompt 编译成功 -> {target_out} ({len(result)} chars)")
    return result


# ── 2. Release 打包模块 (build_release) ───────────────────────────────────────
def build_release(
    release_dir: Optional[Path] = None,
    compile_first: bool = True,
    prompt_file: Optional[Path] = None,
    timestamp_override: Optional[str] = None
) -> Path:
    """
    编译 Prompt 并打包全量 Skill 到 release/ 目录，生成 build-info.json 与 checksums.json。
    """
    target_rel_dir = release_dir or RELEASE_DIR
    target_skill_dir = target_rel_dir / "xiaofan-persona"
    src_prompt = prompt_file or PROMPT_SYSTEM_FILE

    if compile_first:
        build_prompt(output_file=src_prompt, timestamp_override=timestamp_override)

    if target_rel_dir.exists():
        shutil.rmtree(target_rel_dir)
    target_skill_dir.mkdir(parents=True, exist_ok=True)

    # 复制打包文件到 release/xiaofan-persona/ 目录
    shutil.copy(SKILL_TEMPLATE, target_skill_dir / "SKILL.md")
    shutil.copy(src_prompt, target_skill_dir / "Prompt_System.md")
    shutil.copy(REPO_ROOT / "identity" / "canonical_principles.md", target_skill_dir / "canonical_principles.md")
    shutil.copy(REPO_ROOT / "FAILURE_MODES.md", target_skill_dir / "FAILURE_MODES.md")

    # 生成 build-info.json 到 xiaofan-persona 目录内部
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=REPO_ROOT).decode('utf-8').strip()
        source_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=REPO_ROOT).decode('utf-8').strip()
    except Exception:
        commit_hash, source_branch = "unknown", "unknown"

    manifest = {
        "version": load_version(),
        "commit": commit_hash,
        "built_at": datetime.now().isoformat(),
        "source_branch": source_branch
    }
    with open(target_skill_dir / "build-info.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 生成 checksums.json 到 xiaofan-persona 目录内部
    checksums = {}
    for filepath in sorted(target_skill_dir.rglob("*")):
        if filepath.is_file() and filepath.name not in ["build-info.json", "checksums.json"]:
            hasher = hashlib.sha256()
            with open(filepath, "rb") as f:
                hasher.update(f.read())
            rel_path = filepath.relative_to(target_skill_dir).as_posix()
            checksums[rel_path] = "sha256:" + hasher.hexdigest()

    with open(target_skill_dir / "checksums.json", "w", encoding="utf-8") as f:
        json.dump(checksums, f, indent=2)

    print(f"✅ Release 打包成功 -> {target_skill_dir}")
    return target_skill_dir


# ── 3. 产物校验模块 (check_skill_package) ──────────────────────────────────────
def check_skill_dir(skill_dir: Path) -> List[str]:
    """校验单 Skill 目录完整性与标记"""
    errors = []
    if not skill_dir.is_dir():
        return [f"目录不存在: {skill_dir.relative_to(REPO_ROOT)}"]

    for fname in REQUIRED_FILES:
        fpath = skill_dir / fname
        if not fpath.is_file():
            errors.append(f"缺失必要文件: {fpath.relative_to(REPO_ROOT)}")
        elif fpath.stat().st_size <= 50:
            errors.append(f"文件大小异常: {fpath.relative_to(REPO_ROOT)}")

    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        stext = skill_md.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_SKILL_REFERENCES:
            if forbidden in stext:
                errors.append(f"{skill_dir.relative_to(REPO_ROOT)}/SKILL.md 包含了源码路径引用: {forbidden}")
        for fname in REQUIRED_FILES[1:]:
            if f"`{fname}`" not in stext:
                errors.append(f"{skill_dir.relative_to(REPO_ROOT)}/SKILL.md 未引用包内文件: {fname}")
        for marker in REQUIRED_SKILL_MARKERS:
            if marker not in stext:
                errors.append(f"{skill_dir.relative_to(REPO_ROOT)}/SKILL.md 缺失 Marker: {marker}")
    return errors


def check_skill_package(strict: bool = True) -> bool:
    """
    对 SKILL 模板、本地 Agent 镜像及 release 目录进行全量静态校验。
    """
    errors = []

    # 1. 模板检查
    if not SKILL_TEMPLATE.is_file():
        errors.append(f"模板文件不存在: {SKILL_TEMPLATE}")

    # 2. release 目录检查
    errors.extend(check_skill_dir(RELEASE_SKILL_DIR))

    # 3. 本地镜像目录检查
    errors.extend(check_skill_dir(LOCAL_SKILL_DIR))

    # 4. 模板与各产物一致性比对
    if SKILL_TEMPLATE.is_file():
        tpl_text = SKILL_TEMPLATE.read_text(encoding="utf-8")
        for target in [RELEASE_SKILL_DIR / "SKILL.md", LOCAL_SKILL_DIR / "SKILL.md"]:
            if target.is_file() and target.read_text(encoding="utf-8") != tpl_text:
                errors.append(f"SKILL.md 内容与模板不一致: {target.relative_to(REPO_ROOT)}")

    if errors:
        err_msg = "Skill 包校验失败:\n" + "\n".join(f"  ❌ {e}" for e in errors)
        if strict:
            raise PackageValidationError(err_msg)
        else:
            print(err_msg, file=sys.stderr)
            return False

    print("✅ Skill 包合规性及 Smoke Test 校验全量通过！")
    return True


# ── 3.5 可复现构建校验模块 (verify_determinism) ──────────────────────────────
def verify_determinism() -> bool:
    """
    两次独立构建到临时目录,比对 checksums.json,验证构建可复现性。

    与时钟无关:两次构建均使用固定时间戳(DETERMINISM_TIMESTAMP),
    校验的是「源模块 -> 产物」映射的确定性,而非恰好同一秒内完成。
    """
    print("⚙️ 可复现构建校验 (deterministic build verification)...")
    collected = []
    for i in range(2):
        with tempfile.TemporaryDirectory(prefix="xiaofan-verify-") as tmp:
            prompt_file = Path(tmp) / f"prompt_{i}.md"
            skill_dir = build_release(
                release_dir=Path(tmp) / f"release-{i}",
                compile_first=True,
                prompt_file=prompt_file,
                timestamp_override=DETERMINISM_TIMESTAMP,
            )
            csum_path = skill_dir / "checksums.json"
            if not csum_path.is_file():
                raise ReleaseBuildError("缺少 checksums.json,无法进行确定性校验")
            collected.append(csum_path.read_text(encoding="utf-8").strip())

    if collected[0] == collected[1]:
        print("✅ 可复现构建校验通过 (deterministic build verified)")
        return True

    print("❌ 灾难性错误:构建不具备确定性 (Non-deterministic build detected)!差异如下:", file=sys.stderr)
    diff_lines = list(difflib.unified_diff(
        collected[0].splitlines(), collected[1].splitlines(),
        fromfile="checksums #1", tofile="checksums #2",
    ))
    for line in diff_lines:
        print(line, file=sys.stderr)
    raise ReleaseBuildError("构建不具备确定性 (Non-deterministic build detected)")


# ── 4. 分支部署模块 (deploy_to_release) ───────────────────────────────────────
def deploy_to_release(commit_msg: Optional[str] = None, push: bool = False) -> bool:
    """
    组装 release 产物并(可选)推送至远程 release 分支,同步本地 .agents 镜像。

    采用「隔离工作树」策略:在临时目录内 git init 并探测/fetch 远程分支,
    组装产物后 commit;主仓库不做任何分支切换、清空或历史改写。
    仅当 push=True 时执行推送(CI 里 --push,本地默认只组装)。
    注:dist/、release/、.agents/ 等构建缓存目录仍按 build_release 语义被重建。
    """
    # 1. 分支门禁
    try:
        current_branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=REPO_ROOT).decode('utf-8').strip()
    except Exception as e:
        raise DeployError(f"获取 Git 分支失败: {e}")
    if current_branch != "main":
        raise DeployError(f"必须在 'main' 分支执行部署。当前分支: '{current_branch}'")

    # 2. 构建 + 同步本地镜像 + 离线校验
    print("🔨 开始执行全量 Pipeline 打包...")
    build_release(compile_first=True)
    LOCAL_SKILL_DIR.mkdir(parents=True, exist_ok=True)
    for fname in REQUIRED_FILES:
        shutil.copy(RELEASE_SKILL_DIR / fname, LOCAL_SKILL_DIR / fname)
    print(f"✅ 已同步至本地 Agent 镜像: {LOCAL_SKILL_DIR}")
    check_skill_package(strict=True)

    # 3. 读取远端信息与提交身份
    try:
        remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], cwd=REPO_ROOT).decode('utf-8').strip()
    except Exception:
        raise DeployError("无法获取 remote.origin.url,请先配置远程仓库 (git remote add origin <url>)")
    msg = commit_msg or "chore(release): deploy automated release artifacts to release branch"
    bot_name = os.environ.get("RELEASE_BOT_NAME", "Xiaofan Release Bot")
    bot_email = os.environ.get("RELEASE_BOT_EMAIL", "release-bot@users.noreply.github.com")

    # 4. 隔离工作树组装
    with tempfile.TemporaryDirectory(prefix="xiaofan-release-") as tmp:
        work = Path(tmp)
        subprocess.check_call(['git', 'init', '-q'], cwd=work)
        subprocess.check_call(['git', 'remote', 'add', 'origin', remote_url], cwd=work)

        # 显式探测远端 release 分支(ls-remote --exit-code:0=存在 / 2=不存在 / 其他=通信失败)
        # 通信失败一律中止,绝不把网络/认证错误误判为「分支不存在」去强推覆盖远程。
        lsrc = subprocess.call(['git', 'ls-remote', '--exit-code', '--heads', 'origin', 'release'], cwd=work)
        if lsrc == 0:
            try:
                subprocess.check_call(
                    ['git', 'fetch', '--depth', '1', 'origin', 'release:refs/remotes/origin/release'], cwd=work)
                subprocess.check_call(
                    ['git', 'checkout', '-f', '-B', 'release', 'refs/remotes/origin/release'], cwd=work)
            except subprocess.CalledProcessError as e:
                raise DeployError(f"无法载入远程 release 分支历史: {e}")
            print("🌿 已载入远程 release 分支历史")
        elif lsrc == 2:
            subprocess.check_call(['git', 'checkout', '--orphan', 'release'], cwd=work)
            print("🌿 release 分支不存在(远端确认),创建孤儿分支")
        else:
            raise DeployError(f"无法与远程仓库通信 (git ls-remote 退出码 {lsrc}),中止部署以避免误判覆盖")

        # 清空工作树中除 .git 外的全部内容
        for item in work.iterdir():
            if item.name == ".git":
                continue
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink()

        # 组装产物树:xiaofan-persona/ + README.md
        shutil.copytree(RELEASE_SKILL_DIR, work / "xiaofan-persona")
        (work / "README.md").write_text(RELEASE_README_TEMPLATE, encoding="utf-8")

        subprocess.check_call(['git', 'add', '.'], cwd=work)
        subprocess.check_call(
            ['git', '-c', f'user.name={bot_name}', '-c', f'user.email={bot_email}',
             'commit', '-q', '-m', msg], cwd=work)
        print(f"✅ 产物已提交 (release 工作树): {msg}")

        if push:
            try:
                # 统一普通 push:远端无 release 时创建成功,已有时 fast-forward 追加;
                # 若其间远端被并发改写,会被 non-fast-forward 拒绝 —— 宁可失败也不强推覆盖。
                subprocess.check_call(['git', 'push', 'origin', 'release'], cwd=work)
            except subprocess.CalledProcessError as e:
                raise DeployError(f"推送 release 分支失败(不覆盖远程,请人工检查): {e}")
            print("🚀 已推送至远程 release 分支")
        else:
            print("⚠️ 未指定 --push,跳过推送(仅完成组装与提交)")

    print("🎉 部署流程完成,主工作区未受影响。")
    return True


# ── CLI 命令行主入口 ────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="小饭数字分身 统一流水线 (Unified Pipeline Module)")
    subparsers = parser.add_subparsers(dest="command", help="子命令选择")

    # prompt
    prompt_parser = subparsers.add_parser("prompt", help="编译 Prompt_System.md")
    prompt_parser.add_argument("--dry-run", action="store_true", help="预览输出，不写入磁盘")
    prompt_parser.add_argument("--diff", action="store_true", help="仅显示差异")

    # release
    subparsers.add_parser("release", help="打包 Skill 产物至 release/ 目录")

    # check
    check_parser = subparsers.add_parser("check", help="校验 Skill 包完整性与合规 Marker")
    check_parser.add_argument("--lenient", action="store_true", help="宽容模式（不抛异常）")

    # verify
    subparsers.add_parser("verify", help="两次独立构建比对 checksums,验证可复现性")

    # deploy
    deploy_parser = subparsers.add_parser("deploy", help="组装产物并发布至 release 分支")
    deploy_parser.add_argument("--message", "-m", type=str, help="Commit 提交信息")
    deploy_parser.add_argument("--push", action="store_true", help="推送至远程 release 分支(默认仅组装)")

    # all
    all_parser = subparsers.add_parser("all", help="端到端运行: 编译 -> 打包 -> 校验 (可选 --deploy)")
    all_parser.add_argument("--deploy", action="store_true", help="包含组装 release 产物(需配合 --push 才推送)")
    all_parser.add_argument("--push", action="store_true", help="deploy 时推送至远程 release 分支(需配合 --deploy)")

    args = parser.parse_args()

    try:
        if args.command == "prompt" or args.command is None and len(sys.argv) == 1:
            if args.command is None:
                # 默认动作
                build_prompt()
            else:
                build_prompt(dry_run=args.dry_run, diff=args.diff)
        elif args.command == "release":
            build_release()
        elif args.command == "check":
            check_skill_package(strict=not args.lenient)
        elif args.command == "verify":
            verify_determinism()
        elif args.command == "deploy":
            deploy_to_release(commit_msg=args.message, push=args.push)
        elif args.command == "all":
            build_release(compile_first=True)
            check_skill_package(strict=True)
            if args.deploy:
                deploy_to_release(push=args.push)
    except PipelineError as exc:
        print(f"\n❌ Pipeline 执行异常: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

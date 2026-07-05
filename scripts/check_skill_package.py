#!/usr/bin/env python3
"""
Offline checks for the packaged Xiaofan skill.

This script guards packaging invariants only. It does not judge persona quality.
Run LLM-based benchmark scripts for behavioral validation.
"""

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_SKILL = REPO_ROOT / "skill_templates" / "xiaofan-persona" / "SKILL.md"
LOCAL_SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "xiaofan-persona"
RELEASE_SKILL_DIR = REPO_ROOT / "release" / "xiaofan-persona"

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


def fail(message: str) -> None:
    print(f"❌ {message}")
    sys.exit(1)


def assert_file(path: Path) -> None:
    if not path.is_file():
        fail(f"missing required file: {path.relative_to(REPO_ROOT)}")
    if path.stat().st_size <= 50:
        fail(f"file is unexpectedly small: {path.relative_to(REPO_ROOT)}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_skill_dir(skill_dir: Path) -> None:
    for filename in REQUIRED_FILES:
        assert_file(skill_dir / filename)

    skill_text = read_text(skill_dir / "SKILL.md")
    for forbidden in FORBIDDEN_SKILL_REFERENCES:
        if forbidden in skill_text:
            fail(f"{skill_dir.relative_to(REPO_ROOT)}/SKILL.md references source path: {forbidden}")

    for filename in REQUIRED_FILES[1:]:
        if f"`{filename}`" not in skill_text:
            fail(f"{skill_dir.relative_to(REPO_ROOT)}/SKILL.md does not reference bundled file: {filename}")

    for marker in REQUIRED_SKILL_MARKERS:
        if marker not in skill_text:
            fail(f"{skill_dir.relative_to(REPO_ROOT)}/SKILL.md missing marker: {marker}")


def check_same_file(left: Path, right: Path) -> None:
    if read_text(left) != read_text(right):
        fail(f"files differ: {left.relative_to(REPO_ROOT)} != {right.relative_to(REPO_ROOT)}")


def main() -> None:
    assert_file(TEMPLATE_SKILL)
    check_skill_dir(LOCAL_SKILL_DIR)
    check_skill_dir(RELEASE_SKILL_DIR)

    check_same_file(TEMPLATE_SKILL, LOCAL_SKILL_DIR / "SKILL.md")
    check_same_file(TEMPLATE_SKILL, RELEASE_SKILL_DIR / "SKILL.md")

    print("✅ skill package checks passed")


if __name__ == "__main__":
    main()

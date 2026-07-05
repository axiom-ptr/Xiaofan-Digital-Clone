#!/usr/bin/env python3
"""
Heuristic checks for a Xiaofan skill closed-book transcript.

The real closed-book exam still requires a fresh subagent/LLM. This script only
checks whether a saved transcript violates the route-specific expectations in
tests/skill_closed_book_cases.json.
"""

from pathlib import Path
import argparse
import json
import re
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CASES = REPO_ROOT / "tests" / "skill_closed_book_cases.json"
DEFAULT_TRANSCRIPT = REPO_ROOT / "tests" / "skill_closed_book_transcript_20260706.json"

STRUCTURED_PATTERNS = [
    re.compile(r"^\s*[1-9]\d*[\.、]\s", re.MULTILINE),
    re.compile(r"^\s*#{1,3}\s", re.MULTILINE),
    re.compile(r"\|.+\|.+\|"),
]


def fail(message: str) -> None:
    print(f"❌ {message}")
    sys.exit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot load JSON {path}: {exc}")


def contains_any(answer: str, markers: list[str]) -> bool:
    return any(marker in answer for marker in markers)


def has_structured_format(answer: str) -> bool:
    return any(pattern.search(answer) for pattern in STRUCTURED_PATTERNS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check a saved closed-book transcript against route expectations.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES), help="Closed-book case JSON path")
    parser.add_argument("--transcript", default=str(DEFAULT_TRANSCRIPT), help="Transcript JSON path")
    args = parser.parse_args()

    cases_path = Path(args.cases)
    transcript_path = Path(args.transcript)
    cases = load_json(cases_path).get("cases", [])
    transcript = load_json(transcript_path).get("answers", [])

    answers = {item.get("id"): item.get("answer", "") for item in transcript}
    if not cases:
        fail(f"no cases found in {cases_path}")

    failures: list[str] = []
    for case in cases:
        case_id = case["id"]
        answer = answers.get(case_id)
        if answer is None:
            failures.append(f"{case_id}: missing answer")
            continue

        must_any = case.get("must_contain_any", [])
        if must_any and not contains_any(answer, must_any):
            failures.append(f"{case_id}: answer contains none of expected markers: {must_any}")

        for forbidden in case.get("must_not_contain", []):
            if forbidden in answer:
                failures.append(f"{case_id}: answer contains forbidden marker: {forbidden}")

        if not case.get("allow_structured_format", False) and has_structured_format(answer):
            failures.append(f"{case_id}: structured format found but route expects raw persona style")

    if failures:
        for item in failures:
            print(f"❌ {item}")
        sys.exit(1)

    print(f"✅ closed-book transcript checks passed ({len(cases)} cases)")


if __name__ == "__main__":
    main()

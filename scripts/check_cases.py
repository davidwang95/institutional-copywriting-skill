#!/usr/bin/env python3
"""Validate synthetic fixtures and report narrow, case-insensitive literal checks.

Exit status: 0 = literal checks pass, 1 = literal failures, 2 = invalid input.
Passing this checker does not establish factual fidelity or writing quality.
"""

import argparse
import json
from pathlib import Path
import re
import sys


DEFAULT_CASES = Path(__file__).resolve().parents[1] / "evals" / "cases.json"
TEXT_FIELDS = ("id", "task", "source", "acceptable_output", "rejected_output", "rejection_reason")
LIST_FIELDS = ("invariants", "required_literals", "forbidden_literals")
CASE_FIELDS = set(TEXT_FIELDS + LIST_FIELDS)
LIMIT_NOTICE = (
    "Literal checks are diagnostic only: valid paraphrases may fail, and misleading "
    "outputs may pass. Review the source, invariants, and semantic rubric separately."
)


class InputError(ValueError):
    """An input file is unreadable or does not match the documented schema."""


def read_json(path):
    """Read JSON while rejecting duplicate object keys instead of discarding them."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InputError(f"duplicate JSON object key: {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read valid UTF-8 JSON from {Path(path).name}: {exc}") from exc


def validate_suite(data):
    """Check version-1 fixture shape; return its cases or raise InputError."""
    if not isinstance(data, dict) or set(data) != {"schema_version", "cases"}:
        raise InputError("fixture root must contain only schema_version and cases")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise InputError("schema_version must be the integer 1")
    cases = data["cases"]
    if not isinstance(cases, list) or not cases:
        raise InputError("cases must be a non-empty list")
    seen = set()
    for position, case in enumerate(cases, start=1):
        label = f"case {position}"
        if not isinstance(case, dict) or set(case) != CASE_FIELDS:
            raise InputError(f"{label} must contain exactly: {', '.join(sorted(CASE_FIELDS))}")
        for field in TEXT_FIELDS:
            if not isinstance(case[field], str) or not case[field].strip():
                raise InputError(f"{label}.{field} must be a non-empty string")
        case_id = case["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", case_id):
            raise InputError(f"{label}.id must use lowercase letters, digits, and underscores")
        if case_id in seen:
            raise InputError(f"duplicate case id: {case_id}")
        seen.add(case_id)
        for field in LIST_FIELDS:
            values = case[field]
            if not isinstance(values, list) or not values:
                raise InputError(f"{case_id}.{field} must be a non-empty list")
            if any(not isinstance(item, str) or not item.strip() for item in values):
                raise InputError(f"{case_id}.{field} must contain non-empty strings")
            if len({item.casefold() for item in values}) != len(values):
                raise InputError(f"{case_id}.{field} contains duplicate strings")
        overlap = {item.casefold() for item in case["required_literals"]} & {
            item.casefold() for item in case["forbidden_literals"]
        }
        if overlap:
            raise InputError(f"{case_id} has a literal that is both required and forbidden")
        if case["acceptable_output"] == case["rejected_output"]:
            raise InputError(f"{case_id} has identical acceptable and rejected outputs")
    return cases


def literal_failures(case, output):
    """Match literal substrings without inferring their meaning or context."""
    folded = output.casefold()
    failures = [f"missing required literal {literal!r}" for literal in case["required_literals"]
                if literal.casefold() not in folded]
    failures.extend(f"contains forbidden literal {literal!r}" for literal in case["forbidden_literals"]
                    if literal.casefold() in folded)
    return failures


def fixture_failures(cases):
    failures = []
    for case in cases:
        for reason in literal_failures(case, case["acceptable_output"]):
            failures.append(f"{case['id']} acceptable_output: {reason}")
        if not literal_failures(case, case["rejected_output"]):
            failures.append(f"{case['id']} rejected_output: triggers no literal failure")
    return failures


def check_outputs(cases, outputs):
    """Require one string per case, with no missing or unknown case IDs."""
    if not isinstance(outputs, dict):
        raise InputError("outputs must be a JSON object mapping case IDs to strings")
    if any(not isinstance(value, str) for value in outputs.values()):
        raise InputError("every output value must be a string")
    expected = {case["id"] for case in cases}
    actual = set(outputs)
    failures = [f"missing output id: {case_id}" for case_id in sorted(expected - actual)]
    failures.extend(f"unknown output id: {case_id}" for case_id in sorted(actual - expected))
    for case in cases:
        if case["id"] in outputs:
            failures.extend(f"{case['id']}: {reason}" for reason in literal_failures(case, outputs[case["id"]]))
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="fixture JSON (default: bundled cases)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixtures", action="store_true", help="check bundled acceptable/rejected examples")
    mode.add_argument("--outputs", type=Path, help="JSON object mapping every case ID to an actual output")
    args = parser.parse_args(argv)
    try:
        cases = validate_suite(read_json(args.cases))
        failures = fixture_failures(cases) if args.fixtures else check_outputs(cases, read_json(args.outputs))
    except InputError as exc:
        print(f"INVALID INPUT: {exc}", file=sys.stderr)
        print(LIMIT_NOTICE, file=sys.stderr)
        return 2
    for failure in failures:
        print(f"FAIL: {failure}")
    if args.fixtures:
        print(f"Fixture smoke checks: {len(cases)} cases, {len(cases) * 2} example outputs, {len(failures)} failures.")
    else:
        print(f"Actual-output literal checks: {len(cases)} expected cases, {len(failures)} failures.")
    print(LIMIT_NOTICE)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

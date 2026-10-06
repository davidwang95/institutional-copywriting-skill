#!/usr/bin/env python3
"""Check this repository's portable skill package without third-party packages.

The frontmatter reader supports this package's two single-line string fields,
not general YAML. This is structural validation, not a writing-quality review.
"""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from check_cases import InputError, fixture_failures, read_json, validate_suite


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SKILL_FOLDER = "institutional-copywriting"
REQUIRED_FILES = (
    "README.md", "SOURCES.md", "LICENSE", "VALIDATION.md", "evals/cases.json",
    f"{SKILL_FOLDER}/SKILL.md", f"{SKILL_FOLDER}/references/formats.md",
    f"{SKILL_FOLDER}/references/examples.md", f"{SKILL_FOLDER}/references/evaluation.md",
    "scripts/validate.py", "scripts/check_cases.py",
)
INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+[\"'][^\n]*?[\"'])?\s*\)")
REFERENCE_LINK = re.compile(r"(?m)^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|[^\s]+)")
SCAFFOLD = re.compile(
    r"(?im)^\s*(?:#{1,6}\s*)?(?:TODO|TBD|FIXME)(?:\s*:|\s*$)|"
    r"\[(?:TODO|TBD|FIXME)\b[^\]\n]*\]|\[INSERT\s+[^\]\n]+\]"
)


def frontmatter_errors(text, folder_name):
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return ["SKILL.md must begin with a --- frontmatter delimiter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return ["SKILL.md frontmatter has no closing --- delimiter"]
    values = {}
    errors = []
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([a-z_]+):\s*(.*)", line)
        if not match:
            errors.append("frontmatter must use single-line key: string fields")
            continue
        key, value = match.groups()
        if key in values:
            errors.append(f"duplicate frontmatter field: {key}")
            continue
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                errors.append(f"{key} has an invalid quoted string")
                continue
        elif value.startswith("'"):
            if len(value) < 2 or not value.endswith("'"):
                errors.append(f"{key} has an invalid quoted string")
                continue
            value = value[1:-1].replace("''", "'")
        elif value in ("|", ">", "true", "false", "null", "~") or value.startswith(("[", "{")):
            errors.append(f"{key} must be a single-line string")
            continue
        elif re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value):
            errors.append(f"{key} must be a string, not a number")
            continue
        values[key] = value
    if set(values) != {"name", "description"}:
        errors.append("frontmatter must contain only name and description")
    name = values.get("name", "")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) >= 64:
        errors.append("name must be under 64 characters, using lowercase letters, digits, and single hyphens")
    if name != folder_name:
        errors.append("name must match the skill folder name")
    description = values.get("description", "")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024 or any(c in description for c in "<>"):
        errors.append("description must be a non-empty string of at most 1024 characters without angle brackets")
    if not "\n".join(lines[end + 1:]).strip():
        errors.append("SKILL.md must contain instructions after frontmatter")
    return errors


def local_link_errors(path, text, root):
    errors = []
    destinations = [match.group(1).strip("<>") for pattern in (INLINE_LINK, REFERENCE_LINK)
                    for match in pattern.finditer(text)]
    for destination in destinations:
        parsed = urlsplit(destination)
        # Remote URLs are recorded in source documentation; no network requests.
        if parsed.scheme or parsed.netloc:
            if parsed.scheme == "file" or re.match(r"^[a-zA-Z]:", destination):
                errors.append(f"non-portable absolute local link: {destination}")
            continue
        if not parsed.path:  # In-document fragments require no separate file.
            continue
        local_path = unquote(parsed.path)
        target = (path.parent / local_path).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            errors.append(f"local link escapes the package: {destination}")
            continue
        if not target.is_file():
            errors.append(f"missing local link target: {destination}")
    return errors


def validate_package(root):
    root = Path(root).resolve()
    errors = [f"missing required file: {relative}" for relative in REQUIRED_FILES
              if not (root / relative).is_file()]
    if not any((root / "scripts").glob("test_*.py")):
        errors.append("scripts must contain unittest tests named test_*.py")
    skill_path = root / SKILL_FOLDER / "SKILL.md"
    for path in sorted(root.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: cannot read UTF-8: {exc}")
            continue
        label = path.relative_to(root).as_posix()
        errors.extend(f"{label}: {error}" for error in local_link_errors(path, text, root))
        if SCAFFOLD.search(text):
            errors.append(f"{label}: unfinished scaffold marker")
        if path == skill_path:
            errors.extend(f"{label}: {error}" for error in frontmatter_errors(text, path.parent.name))
    fixture_path = root / "evals" / "cases.json"
    case_count = None
    if fixture_path.is_file():
        try:
            cases = validate_suite(read_json(fixture_path))
            case_count = len(cases)
            errors.extend(fixture_failures(cases))
        except InputError as exc:
            errors.append(f"evals/cases.json: {exc}")
    return errors, case_count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root (default: this script's repository)")
    args = parser.parse_args(argv)
    errors, case_count = validate_package(args.root)
    for error in errors:
        print(f"FAIL: {error}")
    print(f"Package validation: {len(errors)} failures; fixture count: {case_count if case_count is not None else 'unavailable'}.")
    print("Structural and literal checks only. Client routing, factual fidelity, and writing quality require separate review.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

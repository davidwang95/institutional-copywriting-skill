"""Test package failures using a temporary synthetic repository."""

import json
from pathlib import Path
import tempfile
import unittest

from test_check_cases import synthetic_case
import validate


VALID_SKILL = (
    "---\nname: institutional-copywriting\n"
    "description: Revise evidence-led institutional copy when precision matters.\n"
    "---\n\n# Instructions\nPreserve the supplied facts.\n"
)


class FrontmatterChecks(unittest.TestCase):
    def test_single_line_quoted_string_is_supported(self):
        text = VALID_SKILL.replace("description: Revise evidence-led institutional copy when precision matters.",
                                   'description: "Revise institutional copy: keep evidence intact."')
        self.assertEqual(validate.frontmatter_errors(text, "institutional-copywriting"), [])

    def test_missing_delimiter_and_duplicate_field_fail(self):
        for text in (VALID_SKILL[4:], VALID_SKILL.replace("description:", "name: sample\ndescription:")):
            with self.subTest(text=text):
                self.assertTrue(validate.frontmatter_errors(text, "institutional-copywriting"))

    def test_name_folder_mismatch_fails(self):
        self.assertTrue(any("folder name" in error for error in validate.frontmatter_errors(VALID_SKILL, "different")))

    def test_blank_nonstrings_and_unsupported_field_fail(self):
        original = "description: Revise evidence-led institutional copy when precision matters."
        for replacement in ("description:", "description: true", "description: [one, two]", "description: 42", original + "\nextra: field"):
            with self.subTest(replacement=replacement):
                self.assertTrue(validate.frontmatter_errors(VALID_SKILL.replace(original, replacement), "institutional-copywriting"))


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for relative in validate.REQUIRED_FILES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Synthetic package file.\n", encoding="utf-8")
        (self.root / "scripts" / "test_synthetic.py").write_text("# Synthetic test file.\n", encoding="utf-8")
        (self.root / validate.SKILL_FOLDER / "SKILL.md").write_text(VALID_SKILL, encoding="utf-8")
        (self.root / "evals" / "cases.json").write_text(json.dumps({"schema_version": 1, "cases": [synthetic_case()]}), encoding="utf-8")

    def test_complete_synthetic_package_passes(self):
        self.assertEqual(validate.validate_package(self.root), ([], 1))

    def test_missing_release_record_fails(self):
        (self.root / "VALIDATION.md").unlink()
        self.assertIn("missing required file: VALIDATION.md", validate.validate_package(self.root)[0])

    def test_broken_encoded_local_link_fails(self):
        (self.root / "README.md").write_text("[missing](missing%20reference.md)\n", encoding="utf-8")
        self.assertTrue(any("missing local link target" in error for error in validate.validate_package(self.root)[0]))

    def test_reference_link_and_parent_escape_are_checked(self):
        (self.root / "README.md").write_text("[source]: ../outside.md\n", encoding="utf-8")
        self.assertTrue(any("escapes the package" in error for error in validate.validate_package(self.root)[0]))

    def test_remote_links_and_existing_file_fragments_need_no_network(self):
        (self.root / "README.md").write_text("[remote](https://example.org/unknown) [local](SOURCES.md#source)\n", encoding="utf-8")
        self.assertEqual(validate.validate_package(self.root), ([], 1))

    def test_unfinished_scaffold_fails_without_banning_normal_editorial_words(self):
        reference = self.root / validate.SKILL_FOLDER / "references" / "examples.md"
        reference.write_text("# Example\n[TODO: complete this example]\n", encoding="utf-8")
        self.assertTrue(any("unfinished scaffold" in error for error in validate.validate_package(self.root)[0]))
        reference.write_text("The model could assess the evidence.\n", encoding="utf-8")
        self.assertEqual(validate.validate_package(self.root), ([], 1))

    def test_invalid_fixture_json_is_reported_without_a_traceback(self):
        (self.root / "evals" / "cases.json").write_text("{", encoding="utf-8")
        failures, count = validate.validate_package(self.root)
        self.assertIsNone(count)
        self.assertTrue(any("evals/cases.json" in error for error in failures))


if __name__ == "__main__":
    unittest.main()

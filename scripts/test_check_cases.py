"""Failure-path tests for schema validation and the literal diagnostic CLI."""

from contextlib import redirect_stderr, redirect_stdout
import copy
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

import check_cases


def synthetic_case(case_id="sample"):
    return {
        "id": case_id,
        "task": "Retain the number and evidence limitation.",
        "source": "The synthetic sample has 12 observations; causation is unknown.",
        "invariants": ["The sample size remains 12.", "No causal inference is supported."],
        "required_literals": ["12 observations"],
        "forbidden_literals": ["proves causation"],
        "acceptable_output": "The sample has 12 observations; causation remains unknown.",
        "rejected_output": "The sample has 12 observations and proves causation.",
        "rejection_reason": "The text makes an unsupported causal claim.",
    }


class CaseChecks(unittest.TestCase):
    def setUp(self):
        self.case = synthetic_case()
        self.suite = {"schema_version": 1, "cases": [self.case]}

    def test_schema_accepts_a_nonempty_suite_without_inventing_a_case_count(self):
        self.assertEqual(check_cases.validate_suite(self.suite), [self.case])

    def test_schema_rejects_missing_required_field(self):
        del self.case["invariants"]
        with self.assertRaises(check_cases.InputError):
            check_cases.validate_suite(self.suite)

    def test_schema_rejects_wrong_anchor_type(self):
        self.case["required_literals"] = "12 observations"
        with self.assertRaises(check_cases.InputError):
            check_cases.validate_suite(self.suite)

    def test_schema_rejects_empty_suite_and_boolean_version(self):
        for data in ({"schema_version": 1, "cases": []}, {"schema_version": True, "cases": [self.case]}):
            with self.subTest(data=data), self.assertRaises(check_cases.InputError):
                check_cases.validate_suite(data)

    def test_schema_rejects_duplicate_case_ids(self):
        self.suite["cases"].append(copy.deepcopy(self.case))
        with self.assertRaisesRegex(check_cases.InputError, "duplicate case id"):
            check_cases.validate_suite(self.suite)

    def test_schema_rejects_conflicting_anchors(self):
        self.case["forbidden_literals"] = ["12 OBSERVATIONS"]
        with self.assertRaisesRegex(check_cases.InputError, "both required and forbidden"):
            check_cases.validate_suite(self.suite)

    def test_fixture_check_detects_bad_reference_and_ineffective_rejection(self):
        self.case["acceptable_output"] = "The sample has thirteen observations."
        self.case["rejected_output"] = "The sample has 12 observations, with unknown causation."
        failures = check_cases.fixture_failures([self.case])
        self.assertEqual(len(failures), 2)
        self.assertTrue(any("triggers no literal failure" in failure for failure in failures))

    def test_missing_and_unknown_output_ids_are_reported(self):
        failures = check_cases.check_outputs([self.case], {"unrelated": "12 observations"})
        self.assertIn("missing output id: sample", failures)
        self.assertIn("unknown output id: unrelated", failures)

    def test_nonstring_output_is_invalid_input(self):
        with self.assertRaisesRegex(check_cases.InputError, "must be a string"):
            check_cases.check_outputs([self.case], {"sample": None})

    def test_matching_is_case_insensitive_and_reports_known_bad_phrase(self):
        self.assertEqual(check_cases.literal_failures(self.case, "12 OBSERVATIONS"), [])
        self.assertEqual(len(check_cases.literal_failures(self.case, self.case["rejected_output"])), 1)

    def test_literal_pass_does_not_prove_semantic_fidelity(self):
        # This unsupported claim evades the one forbidden phrase, as documented.
        self.assertEqual(check_cases.literal_failures(self.case, "12 observations demonstrate a causal effect."), [])

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "outputs.json"
            path.write_text('{"sample": "first", "sample": "second"}', encoding="utf-8")
            with self.assertRaisesRegex(check_cases.InputError, "duplicate JSON object key"):
                check_cases.read_json(path)

    def test_cli_outputs_success_missing_id_and_malformed_json_statuses(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture_path = Path(directory) / "cases.json"
            outputs_path = Path(directory) / "outputs.json"
            fixture_path.write_text(json.dumps(self.suite), encoding="utf-8")
            with redirect_stdout(StringIO()):
                self.assertEqual(check_cases.main(["--cases", str(fixture_path), "--fixtures"]), 0)
            outputs_path.write_text("{}", encoding="utf-8")
            captured = StringIO()
            with redirect_stdout(captured):
                self.assertEqual(check_cases.main(["--cases", str(fixture_path), "--outputs", str(outputs_path)]), 1)
            self.assertIn("missing output id: sample", captured.getvalue())
            outputs_path.write_text("not JSON", encoding="utf-8")
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                self.assertEqual(check_cases.main(["--cases", str(fixture_path), "--outputs", str(outputs_path)]), 2)


if __name__ == "__main__":
    unittest.main()

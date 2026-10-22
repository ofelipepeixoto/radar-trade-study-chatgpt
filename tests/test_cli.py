"""Local CLI behavior, size limit, JSON parser and output privacy."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from radar_trade_study.cli import MAX_INPUT_BYTES, load_payload, main


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def invoke(self, arguments):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(arguments)
        return code, json.loads(output.getvalue())

    def test_fixture_success(self):
        code, result = self.invoke([str(ROOT / "examples/scenario-long.json")])
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "ok")

    def test_usage(self):
        self.assertEqual(self.invoke([])[0], 2)
        self.assertEqual(self.invoke(["one", "two"])[0], 2)

    def test_duplicate_keys_and_nonfinite_json_rejected(self):
        for content in ('{"entry":"100", "entry":"200"}', '{"entry":NaN}', '{"entry":Infinity}', '{"entry":-Infinity}'):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "input.json"
                path.write_text(content)
                code, result = self.invoke([str(path)])
                self.assertEqual(code, 1)
                self.assertEqual(result["code"], "unreadable_or_invalid_json_file")

    def test_large_or_invalid_utf8_file_rejected(self):
        for content in (b" " * (MAX_INPUT_BYTES + 1), b"\xff"):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "input.json"
                path.write_bytes(content)
                with self.assertRaises((ValueError, UnicodeError)):
                    load_payload(path)
                self.assertEqual(self.invoke([str(path)])[0], 1)

    def test_missing_file_or_directory_does_not_echo_path(self):
        with tempfile.TemporaryDirectory() as directory:
            for path in (Path(directory) / "PRIVATE-NAME.json", Path(directory)):
                code, result = self.invoke([str(path)])
                self.assertEqual(code, 1)
                self.assertNotIn("PRIVATE-NAME", json.dumps(result))

    def test_missing_input_stale_and_no_scenario_exit_codes(self):
        original = json.loads((ROOT / "examples/scenario-long.json").read_text())
        for expected, payload in (
            (2, {}),
            (3, {**original, "max_age_seconds": 1}),
            (4, {**original, "risk_budget": "1"}),
        ):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "input.json"
                path.write_text(json.dumps(payload))
                self.assertEqual(self.invoke([str(path)])[0], expected)


if __name__ == "__main__":
    unittest.main()

"""Local file CLI. Nothing is uploaded, fetched or sent to a broker."""

import json
from pathlib import Path
import sys

from .engine import review_scenario

MAX_INPUT_BYTES = 1024 * 1024
EXIT_CODES = {"ok": 0, "needs_input": 2, "degraded": 3, "no_valid_scenario": 4, "error": 1}


def _reject_constant(_value):
    raise ValueError("non_finite_json_number")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def load_payload(path):
    input_path = Path(path)
    if not input_path.is_file():
        raise ValueError("regular_file_required")
    with input_path.open("rb") as stream:
        content = stream.read(MAX_INPUT_BYTES + 1)
    if len(content) > MAX_INPUT_BYTES:
        raise ValueError("input_too_large")
    return json.loads(content.decode("utf-8"), parse_constant=_reject_constant, object_pairs_hook=_unique_object)


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        result = {"schema_version": "1.0", "status": "needs_input", "code": "usage_python_m_radar_trade_study_json_file", "execution_enabled": False}
    else:
        try:
            result = review_scenario(load_payload(arguments[0]))
        except (OSError, ValueError, UnicodeError, RecursionError):
            # File names, contents and parser error excerpts may contain secrets.
            result = {"schema_version": "1.0", "status": "error", "code": "unreadable_or_invalid_json_file", "execution_enabled": False}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return EXIT_CODES[result["status"]]

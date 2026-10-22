"""Reproduce three findings against a separately obtained, reviewed upstream.

Use revision 3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd. No upstream is
downloaded or installed here. The audit hook is a precaution, not a sandbox.
Run only with reviewed upstream code in a disposable environment without keys.
"""
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path


def deny(event, args):
    if event in {"socket.__new__", "socket.connect", "subprocess.Popen",
                 "os.system", "os.posix_spawn"}:
        raise RuntimeError("blocked network or process event")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python reproduce_upstream.py /path/to/reviewed/upstream")
    root = Path(sys.argv[1]).resolve()
    sys.addaudithook(deny)
    sys.path.insert(0, str(root / "tests"))
    from _load import load
    risk = load("trader-risk", "check")
    entry = load("trader-entry", "entry")
    exit_module = load("trader-exit", "exit")

    order = {
        "symbol": "TEST", "side": "buy", "notional": "NaN",
        "type": "market", "time_in_force": "day",
        "plan": {"entry": 100, "stop": 99, "target": 102},
    }
    invalid = risk.check([order], {"budget": 5000},
                         now=risk.parse_now("2026-10-19 10:15"))
    assert invalid["results"][0]["verdict"] == "PASS"
    print("CONFIRMED: non-finite notional receives PASS")

    start = entry.ts_of(entry.parse_now("2026-10-19 09:30"))
    chart = {"symbol": "TEST", "bars": [
        {"t": start, "o": 99, "h": 100, "l": 99, "c": 100, "v": 1000},
        {"t": start + 900, "o": 100, "h": 102, "l": 100, "c": 101, "v": 1000},
    ]}
    partial = entry.evaluate(chart, entry.parse_now("2026-10-19 10:00"))
    opening = partial["opening_range"]
    assert partial["status"] == "triggered"
    assert opening["bars"] == 1 and opening["of"] == 3 and opening["complete"]
    print("CONFIRMED: incomplete opening range marked complete and triggered")

    args = ["plan", "--symbol", "TSLA", "--entry", "364.18", "--date",
            "2026-10-19", "--time", "10:15 AM", "--setup", "level",
            "--stop", "atr:1.5", "--target", "2R", "--offline",
            str(root / "tests/fixtures/trader-entry/TSLA-2026-10-19-5m.json"),
            "--now", "2026-10-19 14:00", "--json"]

    def run(arguments):
        output = io.StringIO()
        with redirect_stdout(output):
            code = exit_module.main(arguments)
        assert not code
        return json.loads(output.getvalue())

    manual, capped = run(args), run(args + ["--entry-bar", "8"])
    assert manual["atr_bars"] > capped["atr_bars"] and manual["atr"] != capped["atr"]
    print(json.dumps({"finding": "ATR cutoff", "manual_bars": manual["atr_bars"],
                      "capped_bars": capped["atr_bars"], "manual_atr": manual["atr"],
                      "capped_atr": capped["atr"]}, allow_nan=False))
    print("CONFIRMED: 3 offline reproductions; no orders sent")


if __name__ == "__main__":
    main()

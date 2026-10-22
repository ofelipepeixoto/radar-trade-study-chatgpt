"""Arithmetic, abstention and malformed-input regressions."""

from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import unittest

from radar_trade_study import review_scenario


ROOT = Path(__file__).resolve().parents[1]


def scenario(**changes):
    payload = json.loads((ROOT / "examples/scenario-long.json").read_text())
    payload.update(changes)
    return payload


class ArithmeticTests(unittest.TestCase):
    def test_long_costs_and_budget(self):
        report = review_scenario(scenario())
        self.assertEqual(report["status"], "ok")
        self.assertFalse(report["execution_enabled"])
        calculation = report["calculation"]
        self.assertEqual(calculation["quantity"], "9")
        self.assertEqual(calculation["modeled_loss"], "91.98")
        self.assertEqual(calculation["net_gain"], "178.02")
        self.assertEqual(calculation["roundtrip_cost"], "1.98")
        self.assertEqual(calculation["notional"], "900")
        self.assertEqual(calculation["entry_cost"], "0.9")
        self.assertEqual(calculation["entry_outlay"], "900.9")
        self.assertEqual(calculation["cash_remaining"], "9099.1")

    def test_long_entry_cash_reserves_entry_cost_at_equity_boundary(self):
        report = review_scenario(scenario(equity="1000", max_notional="1000", risk_budget="1000"))
        calculation = report["calculation"]
        self.assertEqual(calculation["quantity"], "9")
        self.assertEqual(calculation["entry_outlay"], "900.9")
        self.assertEqual(calculation["cash_remaining"], "99.1")
        self.assertLessEqual(Decimal(calculation["entry_outlay"]), Decimal("1000"))
        self.assertTrue(report["assumptions"]["long_entry_cash_limit_applied"])

    def test_short_direction_and_borrow_limitation(self):
        report = review_scenario(scenario(side="short", stop="110", target="80"))
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["calculation"]["risk_per_contract"], "10.21")
        self.assertIn("short_requires_separate_borrow_margin_and_cost_review", report["warnings"])
        self.assertNotIn("entry_outlay", report["calculation"])
        self.assertNotIn("cash_remaining", report["calculation"])
        self.assertFalse(report["assumptions"]["long_entry_cash_limit_applied"])

    def test_notional_cap_can_dominate_risk(self):
        report = review_scenario(scenario(max_notional="500"))
        self.assertEqual(report["calculation"]["quantity"], "5")

    def test_multiplier_and_fractional_step(self):
        report = review_scenario(scenario(multiplier="10", lot_step="0.25", max_notional="800"))
        self.assertEqual(report["calculation"]["quantity"], "0.75")
        self.assertEqual(report["calculation"]["notional"], "750")

    def test_rounding_never_exceeds_explicit_limits(self):
        for risk in ("0.00001", "1", "99.9999", "100"):
            for step in ("0.001", "0.25", "1", "3"):
                with self.subTest(risk=risk, step=step):
                    report = review_scenario(scenario(risk_budget=risk, lot_step=step))
                    if report["status"] == "ok":
                        values = report["calculation"]
                        self.assertLessEqual(Decimal(values["modeled_loss"]), Decimal(risk))
                        self.assertLessEqual(Decimal(values["notional"]), Decimal("1000"))
                        self.assertEqual(Decimal(values["quantity"]) % Decimal(step), 0)
                    else:
                        self.assertEqual(report["status"], "no_valid_scenario")

    def test_zero_lots_and_nonpositive_net_reward_abstain(self):
        for changes in ({"risk_budget": "1"}, {"fee_bps_per_side": "10000"}):
            report = review_scenario(scenario(**changes))
            self.assertEqual(report["status"], "no_valid_scenario")
            self.assertNotIn("calculation", report)

    def test_precision_extremes_keep_budget_and_cash_invariants(self):
        cases = (
            {
                "equity": "999999999999999999.999999999999999999",
                "risk_budget": "999999999999999999.999999999999999999",
                "max_notional": "999999999999999999.999999999999999999",
                "entry": "999999999999999998.000000000000000001",
                "stop": "999999999999999997.000000000000000001",
                "target": "999999999999999999.000000000000000001",
                "lot_step": "0.000000000000000001", "multiplier": "0.000000000000000001",
                "fee_bps_per_side": "0.000000000000000001",
                "slippage_bps_per_side": "0.000000000000000001",
            },
            {
                "equity": "999999999999999999", "risk_budget": "999999999999999999",
                "max_notional": "999999999999999999", "entry": "0.000000000000000002",
                "stop": "0.000000000000000001", "target": "0.000000000000000003",
                "multiplier": "0.000000000000000001", "lot_step": "0.000000000000000001",
                "fee_bps_per_side": "0", "slippage_bps_per_side": "0",
            },
        )
        for changes in cases:
            with self.subTest(changes=changes):
                report = review_scenario(scenario(**changes))
                self.assertEqual(report["status"], "ok")
                calculation = report["calculation"]
                self.assertLessEqual(Decimal(calculation["modeled_loss"]), Decimal(changes["risk_budget"]))
                self.assertLessEqual(Decimal(calculation["notional"]), Decimal(changes["max_notional"]))
                self.assertLessEqual(Decimal(calculation["entry_outlay"]), Decimal(changes["equity"]))
                self.assertGreaterEqual(Decimal(calculation["cash_remaining"]), 0)

    def test_input_hash_is_canonical_and_payload_is_not_mutated(self):
        payload = scenario()
        saved = deepcopy(payload)
        report = review_scenario(payload)
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        self.assertEqual(report["input_sha256"], hashlib.sha256(canonical.encode()).hexdigest())
        self.assertEqual(report["input_sha256"], review_scenario(dict(reversed(list(payload.items()))))["input_sha256"])
        self.assertEqual(payload, saved)


class TimeAndValidationTests(unittest.TestCase):
    def test_stale_omits_sizing(self):
        report = review_scenario(scenario(evaluated_at="2026-10-22T10:02:00.000001-03:00"))
        self.assertEqual(report["status"], "degraded")
        self.assertNotIn("calculation", report)

    def test_exact_freshness_boundary_is_accepted(self):
        report = review_scenario(scenario(evaluated_at="2026-10-22T13:02:00Z"))
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["age_seconds"], "120")

    def test_naive_future_and_invalid_clocks_are_errors(self):
        for changes in (
            {"observed_at": "2026-10-22T10:00:00"},
            {"observed_at": "2026-10-23T10:00:00Z"},
            {"evaluated_at": "yesterday"},
            {"max_age_seconds": True}, {"max_age_seconds": 0},
        ):
            self.assertEqual(review_scenario(scenario(**changes))["status"], "error")

    def test_missing_choices_are_not_invented(self):
        payload = scenario()
        del payload["risk_budget"]
        report = review_scenario(payload)
        self.assertEqual(report["status"], "needs_input")
        self.assertEqual(report["fields"], ["risk_budget"])
        self.assertNotIn("calculation", report)

    def test_unknown_execution_and_credential_fields_rejected_without_echo(self):
        for key in ("instructions", "api_secret", "execute", "private-secret-key"):
            report = review_scenario(scenario(**{key: "sensitive-value"}))
            self.assertEqual(report["code"], "unknown_fields")
            self.assertNotIn(key, json.dumps(report))
            self.assertNotIn("sensitive-value", json.dumps(report))

    def test_numeric_range_and_type_fail_closed(self):
        for value in ("NaN", "Infinity", "1e3", "-1", "0", 100, 0.1, True, None, [], {}, "9" * 19, "0." + "1" * 19):
            with self.subTest(value=value):
                self.assertEqual(review_scenario(scenario(entry=value))["status"], "error")

    def test_costs_may_be_zero_but_not_negative_or_over_10000(self):
        self.assertEqual(review_scenario(scenario(fee_bps_per_side="0", slippage_bps_per_side="0"))["status"], "ok")
        for value in ("-1", "10000.1"):
            self.assertEqual(review_scenario(scenario(fee_bps_per_side=value))["status"], "error")

    def test_budget_leverage_direction_and_boolean_validation(self):
        for changes in (
            {"risk_budget": "10001"}, {"max_notional": "10001"},
            {"stop": "100"}, {"target": "95"},
            {"side": "short"}, {"side": []},
            {"hypothetical": "true"}, {"schema_version": "2.0"},
            {"source": "line1\nline2"}, {"instrument": ""},
            {"source": "\ud800"},
        ):
            self.assertEqual(review_scenario(scenario(**changes))["status"], "error")

    def test_non_object_inputs_rejected(self):
        for payload in (None, [], "text", 12, True):
            self.assertEqual(review_scenario(payload)["status"], "error")


if __name__ == "__main__":
    unittest.main()

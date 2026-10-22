"""Deterministic arithmetic for one explicit linear scenario.

The caller supplies the assessment clock and all economic choices. The engine
does not infer suitability, produce price forecasts or authorize a transaction.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR, localcontext
import hashlib
import json
import re


DECIMAL_FIELDS = (
    "equity", "risk_budget", "max_notional", "entry", "stop", "target",
    "lot_step", "multiplier", "fee_bps_per_side", "slippage_bps_per_side",
)
TEXT_LIMITS = {"instrument": 80, "venue": 80, "currency": 12, "source": 300}
REQUIRED_FIELDS = frozenset(DECIMAL_FIELDS) | frozenset(TEXT_LIMITS) | {
    "schema_version", "hypothetical", "side", "observed_at", "evaluated_at",
    "max_age_seconds",
}
NUMBER = re.compile(r"(?:0|[1-9][0-9]{0,17})(?:\.[0-9]{1,18})?\Z", re.ASCII)


class InvalidScenario(ValueError):
    """Input rejected with a non-sensitive machine-readable reason."""

    def __init__(self, code, field=None):
        super().__init__(code)
        self.code = code
        self.field = field


def _failure(status, code, fields=None):
    result = {
        "schema_version": "1.0", "status": status, "code": code,
        "execution_enabled": False,
    }
    if fields:
        result["fields"] = sorted(fields)
    return result


def _decimal(value, field):
    if not isinstance(value, str) or not NUMBER.fullmatch(value):
        raise InvalidScenario("invalid_decimal_string", field)
    number = Decimal(value)
    allow_zero = field in {"fee_bps_per_side", "slippage_bps_per_side"}
    if not number.is_finite() or number < 0 or (not allow_zero and number == 0):
        raise InvalidScenario("invalid_numeric_range", field)
    if allow_zero and number > 10000:
        raise InvalidScenario("invalid_bps_range", field)
    return number


def _timestamp(value, field):
    if not isinstance(value, str) or len(value) > 40:
        raise InvalidScenario("invalid_timestamp", field)
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError("timezone required")
        return instant.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise InvalidScenario("invalid_timestamp", field) from None


def _validate(payload):
    if not isinstance(payload, dict):
        raise InvalidScenario("expected_object")
    if set(payload) - REQUIRED_FIELDS:
        # Do not echo arbitrary keys or values: either may contain a secret.
        raise InvalidScenario("unknown_fields")
    missing = REQUIRED_FIELDS - set(payload)
    if missing:
        return _failure("needs_input", "missing_fields", missing)
    if payload["schema_version"] != "1.0":
        raise InvalidScenario("unsupported_schema_version", "schema_version")
    if type(payload["hypothetical"]) is not bool:
        raise InvalidScenario("expected_boolean", "hypothetical")
    if not isinstance(payload["side"], str) or payload["side"] not in {"long", "short"}:
        raise InvalidScenario("invalid_side", "side")
    for field, limit in TEXT_LIMITS.items():
        value = payload[field]
        if (not isinstance(value, str) or not value.strip() or len(value) > limit
                or any(ord(character) < 32 or ord(character) == 127
                       or 0xD800 <= ord(character) <= 0xDFFF for character in value)):
            raise InvalidScenario("invalid_text", field)
    age = payload["max_age_seconds"]
    if type(age) is not int or age <= 0 or age > 1_000_000_000:
        raise InvalidScenario("invalid_max_age_seconds", "max_age_seconds")
    values = {field: _decimal(payload[field], field) for field in DECIMAL_FIELDS}
    observed = _timestamp(payload["observed_at"], "observed_at")
    evaluated = _timestamp(payload["evaluated_at"], "evaluated_at")
    if evaluated < observed:
        raise InvalidScenario("observation_in_future", "observed_at")
    if values["risk_budget"] > values["equity"]:
        raise InvalidScenario("risk_exceeds_equity", "risk_budget")
    if values["max_notional"] > values["equity"]:
        raise InvalidScenario("leverage_not_supported", "max_notional")
    entry, stop, target = (values[field] for field in ("entry", "stop", "target"))
    valid_order = stop < entry < target if payload["side"] == "long" else target < entry < stop
    if not valid_order:
        raise InvalidScenario("invalid_price_order", "stop")
    return values, observed, evaluated


def _plain(number):
    value = format(number, "f")
    return value.rstrip("0").rstrip(".") if "." in value else value


def review_scenario(payload):
    """Return a report; ``ok`` means arithmetic succeeded, never trade approval.

    Numeric inputs must be unsigned decimal strings with at most 18 integer and
    18 fractional digits. No exponent syntax, float, NaN or Infinity is accepted.
    Timestamps must contain a timezone. ``max_age_seconds`` is a positive integer.
    Missing required choices return ``needs_input``; malformed ones return error.
    """
    try:
        validated = _validate(payload)
    except InvalidScenario as exc:
        return _failure("error", exc.code, [exc.field] if exc.field else None)
    if isinstance(validated, dict):
        return validated
    values, observed, evaluated = validated
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    warnings = ["stop_is_not_guaranteed_in_gaps_or_illiquidity", "source_is_caller_supplied_and_unverified"]
    if payload["hypothetical"]:
        warnings.append("hypothetical_data_not_a_live_quote")
    if payload["side"] == "short":
        warnings.append("short_requires_separate_borrow_margin_and_cost_review")
    result = {
        "schema_version": "1.0", "status": "ok", "execution_enabled": False,
        "interpretation": "conditional_arithmetic_only_not_a_recommendation",
        "input_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "instrument": payload["instrument"], "venue": payload["venue"],
        "currency": payload["currency"], "side": payload["side"],
        "hypothetical": payload["hypothetical"], "source": payload["source"],
        "observed_at": observed.isoformat(), "evaluated_at": evaluated.isoformat(),
        "max_age_seconds": payload["max_age_seconds"], "warnings": warnings,
    }
    age = evaluated - observed
    result["age_seconds"] = str(Decimal(age.days * 86400 + age.seconds) + Decimal(age.microseconds) / 1_000_000)
    if age > timedelta(seconds=payload["max_age_seconds"]):
        result.update(status="degraded", code="stale_observation")
        warnings.append("stale_data_sizing_withheld")
        return result
    # The bounded input grammar fits comfortably inside this arithmetic context.
    with localcontext() as context:
        context.prec = 256
        entry, stop, target = (values[field] for field in ("entry", "stop", "target"))
        multiplier, step = values["multiplier"], values["lot_step"]
        cost = ((entry + max(entry, stop, target)) * multiplier
                * (values["fee_bps_per_side"] + values["slippage_bps_per_side"]) / 10000)
        unit_loss = abs(entry - stop) * multiplier + cost
        unit_gain = abs(target - entry) * multiplier - cost
        unit_notional = entry * multiplier
        entry_cost = (unit_notional
                      * (values["fee_bps_per_side"] + values["slippage_bps_per_side"]) / 10000)
        risk_lots = (values["risk_budget"] / (unit_loss * step)).to_integral_value(rounding=ROUND_FLOOR)
        notional_lots = (values["max_notional"] / (unit_notional * step)).to_integral_value(rounding=ROUND_FLOOR)
        lot_limits = [risk_lots, notional_lots]
        if payload["side"] == "long":
            cash_lots = (values["equity"] / ((unit_notional + entry_cost) * step)).to_integral_value(rounding=ROUND_FLOOR)
            lot_limits.append(cash_lots)
        quantity = min(lot_limits) * step
        result["assumptions"] = {
            "cost_model": "roundtrip_bps_on_entry_plus_maximum_scenario_price",
            "exit_cost_price": _plain(max(entry, stop, target)),
            "excluded_costs": ["borrow", "funding", "tax", "minimum_broker_fee"],
            "risk_budget": _plain(values["risk_budget"]),
            "max_notional": _plain(values["max_notional"]),
            "equity": _plain(values["equity"]),
            "lot_step": _plain(step), "multiplier": _plain(multiplier),
            "long_entry_cash_limit_applied": payload["side"] == "long",
        }
        if quantity <= 0 or unit_gain <= 0:
            result.update(status="no_valid_scenario", code="budget_or_cost_constraints")
            return result
        loss, gain = quantity * unit_loss, quantity * unit_gain
        result["calculation"] = {
            "quantity": _plain(quantity), "notional": _plain(quantity * unit_notional),
            "modeled_loss": _plain(loss), "net_gain": _plain(gain),
            "roundtrip_cost": _plain(quantity * cost),
            "risk_reward_ratio": _plain((gain / loss).quantize(Decimal("0.000000000001"), rounding=ROUND_FLOOR)),
            "ratio_decimal_places": 12,
            "risk_per_contract": _plain(unit_loss),
            "gain_per_contract": _plain(unit_gain),
            "quantity_unit": "contracts_or_lots_of_multiplier_underlying_units",
        }
        if payload["side"] == "long":
            outlay = quantity * (unit_notional + entry_cost)
            result["calculation"].update(
                entry_cost=_plain(quantity * entry_cost),
                entry_outlay=_plain(outlay),
                cash_remaining=_plain(values["equity"] - outlay),
            )
        return result

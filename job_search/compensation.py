from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any

from .models import Verdict


COMPENSATION_POLICY_PATH = Path(__file__).parent / "policy" / "compensation_policy.json"


class EngagementCategory(StrEnum):
    EMPLOYEE = "employee"
    CONTRACTOR = "contractor"


@dataclass(frozen=True, slots=True)
class CompensationEvaluation:
    reason_code: str
    verdict: Verdict | None
    monthly_php: int | None
    explanation: str


@dataclass(frozen=True, slots=True)
class CompensationDecision:
    engagement_category: EngagementCategory
    php_reference_monthly: int
    requested_currency: str
    requested_basis: str
    submitted_amount: int
    submitted_currency: str
    exchange_rate: float | None = None
    conversion_date: str | None = None
    monthly_hours_assumption: float | None = None
    advertised_currency: str | None = None
    advertised_min: int | None = None
    advertised_max: int | None = None
    advertised_basis: str | None = None
    philippines_targeted_international: bool = False
    direct_international_rate: bool = False
    high_budget_evidence: bool = False
    policy_override: str | None = None
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["engagement_category"] = self.engagement_category.value
        return value


@lru_cache(maxsize=1)
def load_compensation_policy() -> dict[str, Any]:
    return json.loads(COMPENSATION_POLICY_PATH.read_text(encoding="utf-8"))


def engagement_category(employment_type: str) -> EngagementCategory:
    normalized = employment_type.casefold()
    contractor_terms = ("contract", "consultant", "freelance", "b2b", "self-employed")
    if any(term in normalized for term in contractor_terms):
        return EngagementCategory.CONTRACTOR
    return EngagementCategory.EMPLOYEE


def evaluate_compensation(
    monthly_php: int | None,
    employment_type: str,
    *,
    strategically_exceptional: bool = False,
) -> CompensationEvaluation:
    if monthly_php is None:
        return CompensationEvaluation(
            "COMPENSATION_UNDISCLOSED",
            None,
            None,
            "Undisclosed compensation is not an eligibility blocker.",
        )

    category = engagement_category(employment_type)
    limits = load_compensation_policy()[category.value]
    hard_minimum = int(limits["hard_minimum_monthly_php"])
    preferred_minimum = int(limits["preferred_minimum_monthly_php"])
    target_minimum = int(limits["target_range_monthly_php"]["min"])

    if monthly_php < hard_minimum:
        verdict = Verdict.REVIEW if strategically_exceptional else Verdict.SKIP
        return CompensationEvaluation(
            "COMPENSATION_BELOW_MINIMUM",
            verdict,
            monthly_php,
            "Advertised compensation is below the applicable hard minimum.",
        )
    if monthly_php < preferred_minimum:
        return CompensationEvaluation(
            "COMPENSATION_REVIEW",
            Verdict.REVIEW,
            monthly_php,
            "Advertised compensation is above the hard floor but below the preferred minimum.",
        )
    if monthly_php >= target_minimum:
        return CompensationEvaluation(
            "COMPENSATION_TARGET_MATCH",
            None,
            monthly_php,
            "Advertised compensation meets or exceeds the target range floor.",
        )
    return CompensationEvaluation(
        "COMPENSATION_ACCEPTABLE",
        None,
        monthly_php,
        "Advertised compensation is acceptable but below the target range.",
    )


def evaluate_compensation_range(
    minimum_monthly_php: int | None,
    maximum_monthly_php: int | None,
    employment_type: str,
    *,
    strategically_exceptional: bool = False,
) -> CompensationEvaluation:
    if minimum_monthly_php is None and maximum_monthly_php is None:
        return evaluate_compensation(None, employment_type)

    low = minimum_monthly_php if minimum_monthly_php is not None else maximum_monthly_php
    high = maximum_monthly_php if maximum_monthly_php is not None else minimum_monthly_php
    if low is None or high is None:
        raise ValueError("invalid compensation range")
    if low > high:
        low, high = high, low

    category = engagement_category(employment_type)
    limits = load_compensation_policy()[category.value]
    hard_minimum = int(limits["hard_minimum_monthly_php"])
    preferred_minimum = int(limits["preferred_minimum_monthly_php"])
    target_minimum = int(limits["target_range_monthly_php"]["min"])

    if high < hard_minimum:
        verdict = Verdict.REVIEW if strategically_exceptional else Verdict.SKIP
        return CompensationEvaluation(
            "COMPENSATION_BELOW_MINIMUM",
            verdict,
            high,
            "The advertised maximum is below the applicable hard minimum.",
        )
    if low < hard_minimum or high < preferred_minimum:
        return CompensationEvaluation(
            "COMPENSATION_REVIEW",
            Verdict.REVIEW,
            high,
            "The advertised range only partially clears the applicable minimums.",
        )
    if high >= target_minimum:
        return CompensationEvaluation(
            "COMPENSATION_TARGET_MATCH",
            None,
            high,
            "The advertised range reaches or exceeds the target range floor.",
        )
    return CompensationEvaluation(
        "COMPENSATION_ACCEPTABLE",
        None,
        high,
        "The advertised range is acceptable but below the target range.",
    )


def select_expected_monthly_php(
    employment_type: str,
    *,
    strong_ai_alignment: bool = False,
    staff_scope: bool = False,
    demanding_timezone: bool = False,
    philippines_targeted_international: bool = False,
    direct_international_rate: bool = False,
    high_budget_evidence: bool = False,
    policy_override: str | None = None,
) -> int:
    policy = load_compensation_policy()
    anchors = policy["single_value_anchors_monthly_php"]
    if policy_override:
        override = policy.get("job_overrides", {}).get(policy_override)
        if override:
            return int(override["expected_monthly_service_pay_php"])

    category = engagement_category(employment_type)
    category_policy = policy[category.value]
    if category == EngagementCategory.CONTRACTOR:
        if staff_scope and (high_budget_evidence or direct_international_rate):
            selected = int(anchors["high_budget_staff_contractor"])
        elif staff_scope:
            selected = int(anchors["staff_ai_without_high_budget_contractor"])
        elif strong_ai_alignment:
            selected = int(category_policy["default_ai_native_senior_monthly_php"])
        else:
            selected = int(category_policy["default_strong_senior_monthly_php"])
        if philippines_targeted_international and not high_budget_evidence:
            selected = min(selected, 275000 if staff_scope else 250000)
        return selected

    if staff_scope:
        anchor = (
            "high_budget_staff_employee"
            if high_budget_evidence or direct_international_rate
            else "staff_ai_without_high_budget_employee"
        )
        selected = int(anchors[anchor])
    elif strong_ai_alignment:
        selected = int(category_policy["default_ai_native_senior_monthly_php"])
    else:
        selected = int(category_policy["default_strong_senior_monthly_php"])
    if demanding_timezone and staff_scope and not philippines_targeted_international:
        selected = max(selected, 275000)
    elif demanding_timezone and strong_ai_alignment and not philippines_targeted_international:
        selected = max(selected, 250000)
    return selected


def select_expected_range_monthly_php(
    employment_type: str,
    *,
    strong_ai_alignment: bool = False,
    staff_scope: bool = False,
    direct_international_rate: bool = False,
    high_budget_evidence: bool = False,
) -> tuple[int, int]:
    ranges = load_compensation_policy()["expected_ranges_monthly_php"]
    category = engagement_category(employment_type)
    if staff_scope:
        key = (
            "high_budget_staff"
            if high_budget_evidence or direct_international_rate
            else "staff_ai_without_high_budget"
        )
    elif category == EngagementCategory.CONTRACTOR:
        key = (
            "strong_ai_senior_contractor"
            if strong_ai_alignment
            else "standard_strong_contractor"
        )
    elif strong_ai_alignment:
        key = "strong_ai_senior_employee"
    else:
        key = "standard_senior_employee"
    selected = ranges[key]
    return int(selected["min"]), int(selected["max"])


def build_compensation_decision(
    employment_type: str,
    *,
    strong_ai_alignment: bool = False,
    staff_scope: bool = False,
    demanding_timezone: bool = False,
    requested_currency: str = "PHP",
    requested_basis: str = "gross_monthly",
    exchange_rate_from_php: float | None = None,
    conversion_date: str | None = None,
    advertised_currency: str | None = None,
    advertised_min: int | None = None,
    advertised_max: int | None = None,
    advertised_basis: str | None = None,
    philippines_targeted_international: bool = False,
    direct_international_rate: bool = False,
    high_budget_evidence: bool = False,
    policy_override: str | None = None,
) -> CompensationDecision:
    advertised_high_budget = bool(
        (advertised_currency or "PHP").upper() == "PHP"
        and advertised_basis in {None, "monthly", "gross_monthly"}
        and advertised_max is not None
        and advertised_max >= 300000
    )
    effective_high_budget_evidence = high_budget_evidence or advertised_high_budget
    php_monthly = select_expected_monthly_php(
        employment_type,
        strong_ai_alignment=strong_ai_alignment,
        staff_scope=staff_scope,
        demanding_timezone=demanding_timezone,
        philippines_targeted_international=philippines_targeted_international,
        direct_international_rate=direct_international_rate,
        high_budget_evidence=effective_high_budget_evidence,
        policy_override=policy_override,
    )
    if (advertised_currency or "PHP").upper() == "PHP" and advertised_basis in {
        None,
        "monthly",
        "gross_monthly",
    }:
        evaluation = evaluate_compensation_range(
            advertised_min,
            advertised_max,
            employment_type,
        )
        if evaluation.verdict == Verdict.SKIP:
            raise ValueError("cannot autonomously agree below the compensation hard minimum")
        if advertised_min is not None or advertised_max is not None:
            low = advertised_min if advertised_min is not None else advertised_max
            high = advertised_max if advertised_max is not None else advertised_min
            if low is None or high is None:
                raise ValueError("invalid advertised compensation range")
            if low > high:
                low, high = high, low
            midpoint = int(round(((low + high) / 2) / 5000) * 5000)
            php_monthly = min(max(php_monthly, midpoint, low), high)
    if requested_currency == "PHP":
        submitted = php_monthly
    else:
        if exchange_rate_from_php is None or conversion_date is None:
            raise ValueError("foreign-currency compensation requires a current exchange rate and date")
        converted = php_monthly * exchange_rate_from_php
        submitted = int(round(converted / 100) * 100)

    if requested_basis == "annual":
        submitted *= 12
    monthly_hours: float | None = None
    if requested_basis == "hourly":
        monthly_hours = float(
            load_compensation_policy()["hourly_conversion"]["default_full_time_monthly_hours"]
        )
        submitted = int(round(submitted / monthly_hours))

    return CompensationDecision(
        engagement_category=engagement_category(employment_type),
        php_reference_monthly=php_monthly,
        requested_currency=requested_currency,
        requested_basis=requested_basis,
        submitted_amount=submitted,
        submitted_currency=requested_currency,
        exchange_rate=exchange_rate_from_php,
        conversion_date=conversion_date,
        monthly_hours_assumption=monthly_hours,
        advertised_currency=advertised_currency,
        advertised_min=advertised_min,
        advertised_max=advertised_max,
        advertised_basis=advertised_basis,
        philippines_targeted_international=philippines_targeted_international,
        direct_international_rate=direct_international_rate,
        high_budget_evidence=effective_high_budget_evidence,
        policy_override=policy_override,
        rationale=(
            load_compensation_policy()["job_overrides"][policy_override]["rationale"]
            if policy_override
            and policy_override in load_compensation_policy().get("job_overrides", {})
            else "Selected from the canonical engagement, alignment, scope, market context, and advertised-range policy."
        ),
    )

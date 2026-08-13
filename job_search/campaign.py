from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from .models import parse_date


class FreshnessBucket(StrEnum):
    P0_FRESH = "P0_FRESH"
    P1_RECENT = "P1_RECENT"
    P2_EXTENDED = "P2_EXTENDED"
    OLDER_THAN_45_DAYS = "OLDER_THAN_45_DAYS"
    UNKNOWN = "UNKNOWN"


class CampaignStopReason(StrEnum):
    CONTINUE = "CONTINUE"
    MAXIMUM_APPLICATION_OUTCOMES = "MAXIMUM_APPLICATION_OUTCOMES"
    NORMAL_TARGET_AND_INVENTORY_EXHAUSTED = "NORMAL_TARGET_AND_INVENTORY_EXHAUSTED"
    QUALITY_LIMITED_INVENTORY_EXHAUSTED = "QUALITY_LIMITED_INVENTORY_EXHAUSTED"


@dataclass(frozen=True, slots=True)
class CampaignPolicy:
    minimum_desired_new_submissions: int = 8
    normal_target_new_submissions: int = 10
    maximum_new_submissions: int = 13
    p0_max_age_days: int = 7
    p1_max_age_days: int = 30
    p2_max_age_days: int = 45
    minimum_plausible_inventory: int = 50
    target_plausible_inventory: int = 100
    human_submit_batch_minimum: int = 5
    human_submit_batch_maximum: int = 10

    def __post_init__(self) -> None:
        if not (
            0 < self.minimum_desired_new_submissions
            <= self.normal_target_new_submissions
            <= self.maximum_new_submissions
        ):
            raise ValueError("campaign submission targets must be positive and ordered")
        if not (
            0
            <= self.p0_max_age_days
            <= self.p1_max_age_days
            <= self.p2_max_age_days
        ):
            raise ValueError("freshness thresholds must be non-negative and ordered")
        if not 0 < self.minimum_plausible_inventory <= self.target_plausible_inventory:
            raise ValueError("plausible inventory targets must be positive and ordered")
        if not 0 < self.human_submit_batch_minimum <= self.human_submit_batch_maximum:
            raise ValueError("human-submit batch limits must be positive and ordered")


@dataclass(frozen=True, slots=True)
class CampaignDecision:
    should_continue: bool
    stop_reason: CampaignStopReason


def classify_freshness(
    posted_at: str | None,
    discovered_at: str | date,
    policy: CampaignPolicy = CampaignPolicy(),
) -> tuple[int | None, FreshnessBucket]:
    posted = parse_date(posted_at)
    discovered = discovered_at if isinstance(discovered_at, date) else parse_date(discovered_at)
    if posted is None or discovered is None:
        return None, FreshnessBucket.UNKNOWN

    age = max(0, (discovered - posted).days)
    if age <= policy.p0_max_age_days:
        return age, FreshnessBucket.P0_FRESH
    if age <= policy.p1_max_age_days:
        return age, FreshnessBucket.P1_RECENT
    if age <= policy.p2_max_age_days:
        return age, FreshnessBucket.P2_EXTENDED
    return age, FreshnessBucket.OLDER_THAN_45_DAYS


def evaluate_campaign_progress(
    *,
    verified_submitted: int,
    human_submit_ready: int = 0,
    quality_inventory_exhausted: bool,
    policy: CampaignPolicy = CampaignPolicy(),
) -> CampaignDecision:
    completed_outcomes = verified_submitted + human_submit_ready
    if completed_outcomes >= policy.maximum_new_submissions:
        return CampaignDecision(False, CampaignStopReason.MAXIMUM_APPLICATION_OUTCOMES)
    if not quality_inventory_exhausted:
        return CampaignDecision(True, CampaignStopReason.CONTINUE)
    if completed_outcomes >= policy.minimum_desired_new_submissions:
        return CampaignDecision(
            False,
            CampaignStopReason.NORMAL_TARGET_AND_INVENTORY_EXHAUSTED,
        )
    return CampaignDecision(False, CampaignStopReason.QUALITY_LIMITED_INVENTORY_EXHAUSTED)

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from .models import parse_date


class FreshnessBucket(StrEnum):
    P0_FRESH = "P0_FRESH"
    P1_RECENT = "P1_RECENT"
    OLDER_THAN_14_DAYS = "OLDER_THAN_14_DAYS"
    UNKNOWN = "UNKNOWN"


class CampaignStopReason(StrEnum):
    CONTINUE = "CONTINUE"
    MAXIMUM_VERIFIED_SUBMISSIONS = "MAXIMUM_VERIFIED_SUBMISSIONS"
    NORMAL_TARGET_AND_INVENTORY_EXHAUSTED = "NORMAL_TARGET_AND_INVENTORY_EXHAUSTED"
    QUALITY_LIMITED_INVENTORY_EXHAUSTED = "QUALITY_LIMITED_INVENTORY_EXHAUSTED"


@dataclass(frozen=True, slots=True)
class CampaignPolicy:
    minimum_desired_new_submissions: int = 8
    normal_target_new_submissions: int = 10
    maximum_new_submissions: int = 13
    p0_max_age_days: int = 7
    p1_max_age_days: int = 14

    def __post_init__(self) -> None:
        if not (
            0 < self.minimum_desired_new_submissions
            <= self.normal_target_new_submissions
            <= self.maximum_new_submissions
        ):
            raise ValueError("campaign submission targets must be positive and ordered")
        if not 0 <= self.p0_max_age_days <= self.p1_max_age_days:
            raise ValueError("freshness thresholds must be non-negative and ordered")


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
    return age, FreshnessBucket.OLDER_THAN_14_DAYS


def evaluate_campaign_progress(
    *,
    verified_submitted: int,
    quality_inventory_exhausted: bool,
    policy: CampaignPolicy = CampaignPolicy(),
) -> CampaignDecision:
    if verified_submitted >= policy.maximum_new_submissions:
        return CampaignDecision(False, CampaignStopReason.MAXIMUM_VERIFIED_SUBMISSIONS)
    if not quality_inventory_exhausted:
        return CampaignDecision(True, CampaignStopReason.CONTINUE)
    if verified_submitted >= policy.minimum_desired_new_submissions:
        return CampaignDecision(
            False,
            CampaignStopReason.NORMAL_TARGET_AND_INVENTORY_EXHAUSTED,
        )
    return CampaignDecision(False, CampaignStopReason.QUALITY_LIMITED_INVENTORY_EXHAUSTED)

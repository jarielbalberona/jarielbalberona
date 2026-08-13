from __future__ import annotations

from datetime import date, timedelta


REVIEW_DAYS = {
    "HUMAN_SUBMIT_READY": 1,
    "SUBMISSION_UNVERIFIED": 1,
    "READY_FOR_BROWSER_PREP": 3,
    "READY_TO_RETRY": 7,
    "FORM_INACCESSIBLE": 7,
    "SOURCE_RESTRICTED": 7,
    "POLICY_UNCLEAR": 7,
    "VIDEO_REQUIRED": 14,
    "HOLD": 14,
}

EXPIRY_DAYS = {
    "HUMAN_SUBMIT_READY": 7,
    "SUBMISSION_UNVERIFIED": 3,
    "READY_FOR_BROWSER_PREP": 14,
    "READY_TO_RETRY": 21,
    "FORM_INACCESSIBLE": 21,
    "SOURCE_RESTRICTED": 30,
    "POLICY_UNCLEAR": 30,
    "VIDEO_REQUIRED": 45,
    "HOLD": 45,
}


def queue_dates(status: str, *, as_of: date | None = None) -> tuple[str | None, str | None]:
    normalized = status.strip().upper()
    if normalized == "CLOSED":
        return None, None
    base = as_of or date.today()
    if normalized not in REVIEW_DAYS:
        raise ValueError(f"unsupported active queue status: {status}")
    return (
        (base + timedelta(days=REVIEW_DAYS[normalized])).isoformat(),
        (base + timedelta(days=EXPIRY_DAYS[normalized])).isoformat(),
    )

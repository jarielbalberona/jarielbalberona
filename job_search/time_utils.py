from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


MANILA = ZoneInfo("Asia/Manila")


def normalize_utc_timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include an explicit timezone")
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds")


def canonical_timestamp(value: str | None) -> str | None:
    if not value:
        return value
    if "T" not in value:
        return value
    return normalize_utc_timestamp(value)


def manila_display(value: str) -> str:
    parsed = datetime.fromisoformat(normalize_utc_timestamp(value))
    return parsed.astimezone(MANILA).isoformat(timespec="seconds")

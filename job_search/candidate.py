from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


CANDIDATE_FACTS_PATH = Path(__file__).parent / "policy" / "candidate_facts.json"
APPLICATION_ANSWER_BANK_PATH = (
    Path(__file__).parent / "policy" / "application_answer_bank.json"
)


@lru_cache(maxsize=1)
def load_candidate_facts() -> dict[str, Any]:
    return json.loads(CANDIDATE_FACTS_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_application_answer_bank() -> dict[str, Any]:
    return json.loads(APPLICATION_ANSWER_BANK_PATH.read_text(encoding="utf-8"))


def accepts_engagement_type(employment_type: str, *, full_time: bool = True) -> bool:
    normalized = employment_type.casefold().replace("-", "_").replace(" ", "_")
    if not full_time or "part_time" in normalized:
        return False
    if "_eor" in normalized or normalized.startswith("eor"):
        return True
    accepted = load_candidate_facts()["employment_preferences"]["accepted_engagement_types"]
    return any(item in normalized for item in accepted)


def canonical_country() -> str:
    return str(load_candidate_facts()["location"]["country"])


def canonical_location() -> str:
    location = load_candidate_facts()["location"]
    parts = (
        location.get("city"),
        location.get("state_or_region"),
        location.get("country"),
    )
    return ", ".join(str(part) for part in parts if part)

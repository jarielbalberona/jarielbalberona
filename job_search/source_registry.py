from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import RunMode
from .normalization import normalize_source_key
from .submission import (
    ApplicantAutomationPolicy,
    SourcePolicy,
    SubmissionAuthorization,
)


DEFAULT_REGISTRY = Path("docs/job-search/source-registry.yaml")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
SOURCE_TYPES = frozenset(
    {
        "JOB_BOARD",
        "DEVELOPER_JOB_BOARD",
        "REMOTE_JOB_BOARD",
        "PH_REMOTE_JOB_BOARD",
        "PH_CONTRACTOR_JOB_BOARD",
        "PH_EOR_REMOTE_SOURCE",
        "TALENT_NETWORK",
        "FREELANCE_MARKETPLACE",
        "PROFESSIONAL_FREELANCE_MARKETPLACE",
        "ATS",
        "EMPLOYER_DIRECT",
        "COMMUNITY_SOURCE",
        "GENERAL_JOB_BOARD",
    }
)


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"null", "~"}:
        return None
    if value in {"true", "false"}:
        return value == "true"
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    if value.startswith(("[", "{")):
        return json.loads(value)
    try:
        return int(value)
    except ValueError:
        return value


def load_source_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    result: dict[str, Any] = {"sources": {}}
    current_source: dict[str, Any] | None = None
    current_section: dict[str, Any] | None = None
    in_sources = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0 and stripped == "sources:":
            in_sources = True
            current_section = None
            continue
        if indent == 0:
            if stripped.endswith(":"):
                section_name = stripped[:-1]
                current_section = {}
                result[section_name] = current_section
                in_sources = False
                continue
            key, value = stripped.split(":", 1)
            result[key] = _parse_scalar(value)
            current_section = None
            in_sources = False
            continue
        if not in_sources and indent == 2 and current_section is not None:
            key, value = stripped.split(":", 1)
            current_section[key] = _parse_scalar(value)
            continue
        if in_sources and indent == 2 and stripped.endswith(":"):
            source_name = stripped[:-1]
            current_source = {}
            result["sources"][source_name] = current_source
            continue
        if in_sources and indent == 4 and current_source is not None:
            key, value = stripped.split(":", 1)
            current_source[key] = _parse_scalar(value)
            continue
        raise ValueError(f"unsupported source-registry structure: {raw_line}")
    for source in result["sources"].values():
        if "note" in source and "notes" not in source:
            source["notes"] = source["note"]
    return result


def list_discovery_sources(path: Path = DEFAULT_REGISTRY) -> list[dict[str, Any]]:
    """Return the enabled recurring-discovery rotation in crawl order.

    Priority controls discovery efficiency only. It is deliberately not exposed
    to scoring code and must never modify a job's fit assessment.
    """

    sources = load_source_registry(path)["sources"]
    rotation = [
        {"id": source_id, **entry}
        for source_id, entry in sources.items()
        if entry.get("enabled", False) and entry.get("discovery", False)
    ]
    return sorted(
        rotation,
        key=lambda entry: PRIORITY_ORDER.get(str(entry.get("priority", "P3")), 99),
    )


def resolve_source_id(source: str, path: Path = DEFAULT_REGISTRY) -> str:
    needle = normalize_source_key(source)
    for source_id, entry in load_source_registry(path)["sources"].items():
        candidates = [source_id, entry.get("name", ""), *entry.get("aliases", [])]
        if needle in {normalize_source_key(str(candidate)) for candidate in candidates if candidate}:
            return source_id
    return needle


def plan_diverse_discovery_rotation(
    observed_counts: dict[str, int] | None = None,
    path: Path = DEFAULT_REGISTRY,
) -> list[dict[str, Any]]:
    """Prioritize underrepresented sources without changing job fit scores."""
    counts = {resolve_source_id(key, path): int(value) for key, value in (observed_counts or {}).items()}
    rotation = list_discovery_sources(path)
    return sorted(
        rotation,
        key=lambda entry: (
            counts.get(str(entry["id"]), 0),
            PRIORITY_ORDER.get(str(entry.get("priority", "P3")), 99),
            str(entry["id"]),
        ),
    )


def validate_source_registry(path: Path = DEFAULT_REGISTRY) -> list[str]:
    registry = load_source_registry(path)
    errors: list[str] = []
    seen_aliases: dict[str, str] = {}

    if not registry.get("registry_policy", {}).get("preferred_not_allowlist", False):
        errors.append("registry must be explicitly configured as preferred, not an allowlist")
    if registry.get("candidate_paid_access", {}).get("default_authorized") is not False:
        errors.append("candidate paid access must default to false")
    diversity = registry.get("source_diversity", {})
    share = diversity.get("max_single_source_share_percent")
    if not isinstance(share, int) or not 1 <= share <= 100:
        errors.append("source diversity requires a valid max single-source share")
    if int(diversity.get("minimum_source_families_per_run", 0)) < 2:
        errors.append("source diversity requires at least two source families per run")

    for source_id, entry in registry["sources"].items():
        priority = entry.get("priority")
        if priority not in PRIORITY_ORDER:
            errors.append(f"{source_id}: invalid priority {priority!r}")
        source_type = entry.get("type")
        if source_type is not None and source_type not in SOURCE_TYPES:
            errors.append(f"{source_id}: invalid type {source_type!r}")

        aliases = [source_id, entry.get("name", ""), *entry.get("aliases", [])]
        for alias in aliases:
            normalized = "".join(character for character in str(alias).casefold() if character.isalnum())
            if not normalized:
                continue
            existing = seen_aliases.get(normalized)
            if existing and existing != source_id:
                errors.append(f"duplicate source alias {alias!r}: {existing} and {source_id}")
            else:
                seen_aliases[normalized] = source_id
    return errors


def get_source_policy(source: str, path: Path = DEFAULT_REGISTRY) -> SourcePolicy:
    entry = load_source_registry(path)["sources"][resolve_source_id(source, path)]
    return SourcePolicy(
        execution_mode=RunMode(entry["execution_mode"]),
        live_submit=bool(entry["live_submit"]),
        policy_verified_at=entry.get("policy_verified_at"),
        applicant_automation_policy=ApplicantAutomationPolicy(
            entry.get("applicant_automation_policy", "UNCLEAR")
        ),
    )


def get_submission_authorization(
    path: Path = DEFAULT_REGISTRY,
) -> SubmissionAuthorization:
    entry = load_source_registry(path).get("submission_authorization", {})
    return SubmissionAuthorization(
        user_authorized_globally=bool(entry.get("user_authorized_globally", False)),
        individual_application_approval_required=bool(
            entry.get("individual_application_approval_required", True)
        ),
        policy_unclear_agent_submission_authorized=bool(
            entry.get("policy_unclear_agent_submission_authorized", False)
        ),
    )

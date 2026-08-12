from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import RunMode
from .submission import (
    ApplicantAutomationPolicy,
    SourcePolicy,
    SubmissionAuthorization,
)


DEFAULT_REGISTRY = Path("docs/job-search/source-registry.yaml")


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"null", "~"}:
        return None
    if value in {"true", "false"}:
        return value == "true"
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
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
    return result


def get_source_policy(source: str, path: Path = DEFAULT_REGISTRY) -> SourcePolicy:
    entry = load_source_registry(path)["sources"][source]
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
    )

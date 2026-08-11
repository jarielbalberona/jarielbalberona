from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import RunMode
from .submission import SourcePolicy


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
    in_sources = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0 and stripped == "sources:":
            in_sources = True
            continue
        if indent == 0:
            key, value = stripped.split(":", 1)
            result[key] = _parse_scalar(value)
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
    )

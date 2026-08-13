from __future__ import annotations

from typing import Any, Iterable, Mapping


MONITORED_STATUSES = frozenset({"APPLIED", "ASSESSMENT", "INTERVIEW"})


def build_read_only_gmail_plan(applications: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    queries: list[dict[str, str]] = []
    for application in applications:
        if str(application.get("status", "")).upper() not in MONITORED_STATUSES:
            continue
        company = str(application.get("company", "")).strip()
        role = str(application.get("role", "")).strip()
        if not company:
            continue
        terms = [f'"{company}"']
        if role:
            terms.append(f'"{role}"')
        queries.append(
            {
                "application_id": str(application.get("application_id", "")),
                "query": f'in:anywhere newer_than:45d ({" OR ".join(terms)})',
            }
        )
    return {
        "read_only": True,
        "allowed_actions": ["SEARCH", "READ", "CLASSIFY", "RECONCILE_LEDGER", "SYNC_TRACKER"],
        "forbidden_actions": ["SEND", "REPLY", "ARCHIVE", "DELETE", "LABEL"],
        "queries": queries,
    }

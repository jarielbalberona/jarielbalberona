from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


HEADERS = (
    "Application ID",
    "Date Discovered",
    "Date Applied",
    "Company",
    "Role",
    "Source",
    "Job URL",
    "Canonical Job URL",
    "Location",
    "Remote Policy",
    "Employment Type",
    "Salary / Compensation",
    "Fit Score",
    "Verdict",
    "Application Status",
    "Application Method",
    "CV Version",
    "Application Letter",
    "Key Matches",
    "Gaps",
    "Recruiter / Contact",
    "Last Response At",
    "Response Type",
    "Next Action",
    "Follow-up Date",
    "Notes",
)

FIELD_MAP = {
    "Application ID": "application_id",
    "Date Discovered": "date_discovered",
    "Date Applied": "date_applied",
    "Company": "company",
    "Role": "role",
    "Source": "source",
    "Job URL": "job_url",
    "Canonical Job URL": "canonical_job_url",
    "Location": "location",
    "Remote Policy": "remote_policy",
    "Employment Type": "employment_type",
    "Salary / Compensation": "compensation",
    "Fit Score": "fit_score",
    "Verdict": "verdict",
    "Application Status": "application_status",
    "Application Method": "application_method",
    "CV Version": "cv_version",
    "Application Letter": "application_letter",
    "Key Matches": "key_matches",
    "Gaps": "gaps",
    "Recruiter / Contact": "recruiter_contact",
    "Last Response At": "last_response_at",
    "Response Type": "response_type",
    "Next Action": "next_action",
    "Follow-up Date": "follow_up_date",
    "Notes": "notes",
}

MANUAL_PRESERVE_FIELDS = frozenset(
    {"Application Status", "Next Action", "Follow-up Date", "Notes"}
)


def _display(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return "; ".join(str(item) for item in value)
    return value


def format_compensation_for_tracker(
    advertised: str,
    compensation_decision: Mapping[str, Any] | None,
) -> str:
    parts = [f"Advertised: {advertised.strip() or 'undisclosed'}"]
    if compensation_decision:
        currency = str(compensation_decision.get("submitted_currency", "")).strip()
        amount = compensation_decision.get("submitted_amount")
        minimum = compensation_decision.get("submitted_min")
        maximum = compensation_decision.get("submitted_max")
        basis = str(compensation_decision.get("requested_basis", "")).replace("_", " ")
        if currency and isinstance(amount, (int, float)):
            parts.append(f"Expected/submitted: {currency} {amount:,.0f} {basis}".strip())
        elif currency and isinstance(minimum, (int, float)) and isinstance(maximum, (int, float)):
            parts.append(
                f"Expected/submitted: {currency} {minimum:,.0f}-{maximum:,.0f} {basis}".strip()
            )
    return " | ".join(parts)


def map_record_to_row(record: Mapping[str, Any]) -> list[Any]:
    return [_display(record.get(FIELD_MAP[header], "")) for header in HEADERS]


def row_to_record(row: Sequence[Any]) -> dict[str, Any]:
    values = list(row) + [""] * (len(HEADERS) - len(row))
    return {FIELD_MAP[header]: values[index] for index, header in enumerate(HEADERS)}


@dataclass(frozen=True, slots=True)
class SheetUpsertPlan:
    action: str
    row_number: int | None
    values: tuple[Any, ...]
    matched_by: str | None


def plan_sheet_upsert(
    existing_rows: Sequence[Sequence[Any]],
    record: Mapping[str, Any],
    *,
    preserve_manual: bool = True,
) -> SheetUpsertPlan:
    target_id = str(record.get("application_id", ""))
    target_url = str(record.get("canonical_job_url", ""))
    match_index: int | None = None
    matched_by: str | None = None

    for index, row in enumerate(existing_rows, start=2):
        existing = row_to_record(row)
        if target_id and str(existing["application_id"]) == target_id:
            match_index, matched_by = index, "application_id"
            break
        if target_url and str(existing["canonical_job_url"]) == target_url:
            match_index, matched_by = index, "canonical_job_url"
            break

    mapped = map_record_to_row(record)
    if match_index is None:
        return SheetUpsertPlan("append", None, tuple(mapped), None)

    existing_row = list(existing_rows[match_index - 2]) + [""] * len(HEADERS)
    if preserve_manual:
        for header in MANUAL_PRESERVE_FIELDS:
            column = HEADERS.index(header)
            if existing_row[column] not in (None, ""):
                mapped[column] = existing_row[column]
    return SheetUpsertPlan("update", match_index, tuple(mapped), matched_by)

---
name: sync-job-application-tracker
description: Initialize or idempotently reconcile Jariel's Google Sheet tracker from SQLite, preserving manual status edits, advertised and expected compensation provenance, and meaningful lifecycle-only rows. Use for tracker setup, application upserts, or response reconciliation.
---

# Sync application tracker

Read `docs/job-search/tracker-schema.md`. Use the Google Sheets connector, not browser automation, when available.

## Initialize

1. Resolve spreadsheet ID `1UXc3HdWvR6SXX_1Y430-d1OUDpjKxrHWKARyqZj2Fxs` and live tab metadata.
2. Read the live header and nearby formatting before writing.
3. Initialize A:Z exactly as documented when the sheet is empty.
4. Freeze row 1, enable filtering, wrap long text, set readable widths, format dates and numeric fit score, and add controlled-value validation where supported.
5. Re-read the header and formatting to verify the result.

## Upsert

1. Sync only `SHORTLISTED`, `PREPARED`, `APPLIED`, or later records.
2. Search by Application ID and canonical URL before appending.
3. Update the existing row when found; never append a duplicate.
4. Preserve non-empty manual Sheet status, next action, follow-up date, and notes unless an explicitly authorized newer state wins.
5. Never create fake `APPLIED` records during dry-run connectivity checks.
6. Format compensation as advertised source text plus expected/submitted currency, amount, and basis. Keep exchange-rate and conversion details in SQLite rather than overloading the Sheet.

Log the spreadsheet, tab, range, row action, and fields changed without exposing unrelated Sheet content.

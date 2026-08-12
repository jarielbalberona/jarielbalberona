---
name: sync-job-application-tracker
description: Initialize or idempotently reconcile Jariel's Applications and Review Queue Google Sheet tabs from SQLite, preserving manual edits, compensation provenance, meaningful lifecycle rows, holds, re-review dates, and applied transitions. Use for tracker setup, application upserts, review-queue reconciliation, or response reconciliation.
---

# Sync application tracker

Read `docs/job-search/tracker-schema.md`. Use the Google Sheets connector, not browser automation, when available.

## Initialize

1. Resolve spreadsheet ID `1UXc3HdWvR6SXX_1Y430-d1OUDpjKxrHWKARyqZj2Fxs` and live tab metadata.
2. Read the live header and nearby formatting before writing.
3. Rename the original `Sheet1` tab to `Applications` in place when applicable; never recreate or clear it.
4. Initialize `Applications` and `Review Queue` A:Z exactly as documented when missing or empty.
5. Freeze row 1, enable filtering, wrap long text, set readable widths, format dates and numeric score/age fields, and add controlled-value validation where supported.
6. Re-read both headers and nearby formatting to verify the result.

## Upsert

1. Sync only independently verified `APPLIED` or later lifecycle records to `Applications`. Keep `HUMAN_SUBMIT_READY` in `Review Queue`; do not add pre-submission hybrid records to `Applications`.
2. Search by Application ID and canonical URL before appending.
3. Update the existing row when found; never append a duplicate.
4. Preserve non-empty manual Sheet status, next action, follow-up date, and notes unless an explicitly authorized newer state wins.
5. Never create fake `APPLIED` records during dry-run connectivity checks.
6. Format compensation as advertised source text plus expected/submitted currency, amount, and basis. Keep exchange-rate and conversion details in SQLite rather than overloading the Sheet.

Log the spreadsheet, tab, range, row action, and fields changed without exposing unrelated Sheet content.

## Review Queue

1. Sync only records using the canonical queue taxonomy: `HUMAN_SUBMIT_READY`, `READY_FOR_BROWSER_PREP`, `VIDEO_REQUIRED`, `HOLD`, `READY_TO_RETRY`, `SOURCE_RESTRICTED`, `POLICY_UNCLEAR`, `FORM_INACCESSIBLE`, `SUBMISSION_UNVERIFIED`, or explicit `CLOSED`. Never queue `SKIP`.
2. Match by Queue ID, canonical job URL, then normalized employer plus role. Queue ID remains bound in SQLite to posting ID and description hash.
3. Require a role-specific cover letter and prepared screening summary for every active row, even when the live form lacks a cover-letter field. When the source expressly prohibits AI-generated application prose, accept a source-restriction note plus candidate-writing prompts instead and keep the row `READY_FOR_BROWSER_PREP`.
4. Preserve non-empty manual queue status, next action, re-review date, and notes unless an explicitly authorized or proven lifecycle transition is newer.
5. When submission is verified, upsert `Applications` once, close the matching queue row, clear its re-review date, and direct future monitoring to `Applications`.
6. Treat due non-closed `Re-review After` dates as inputs to future `$manage-job-search` runs.

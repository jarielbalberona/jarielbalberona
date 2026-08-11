# Google Sheet job-search tracker

- Spreadsheet: `jarielbalberona-job-applications-tracker`
- Spreadsheet ID: `1UXc3HdWvR6SXX_1Y430-d1OUDpjKxrHWKARyqZj2Fxs`
- Connected account: `jarielbalb@gmail.com`
- Tabs: `Applications` and `Review Queue`

SQLite owns discovery, skips, deduplication, drafts, queue identity, execution detail, and run evidence. The Sheet is the human-facing lifecycle and review surface.

## Applications tab

The original `Sheet1` tab is renamed to `Applications` without recreating it so existing rows, formatting, validation, and manual edits survive.

### Columns A:Z

| Column | Field |
| --- | --- |
| A | Application ID |
| B | Date Discovered |
| C | Date Applied |
| D | Company |
| E | Role |
| F | Source |
| G | Job URL |
| H | Canonical Job URL |
| I | Location |
| J | Remote Policy |
| K | Employment Type |
| L | Salary / Compensation |
| M | Fit Score |
| N | Verdict |
| O | Application Status |
| P | Application Method |
| Q | CV Version |
| R | Application Letter |
| S | Key Matches |
| T | Gaps |
| U | Recruiter / Contact |
| V | Last Response At |
| W | Response Type |
| X | Next Action |
| Y | Follow-up Date |
| Z | Notes |

Create or update a row only for `SHORTLISTED`, `PREPARED`, `APPLIED`, or later states. Skip-only and dry-run discovery records stay local. A dry run may initialize the schema but must not create fake `APPLIED` rows.

## Review Queue tab

`Review Queue` preserves worthwhile jobs that need review, a candidate-owned action, a later re-check, or source-policy clearance. Hard `SKIP` jobs never enter this tab.

### Columns A:Z

| Column | Field |
| --- | --- |
| A | Queue ID |
| B | Date Discovered |
| C | Last Reviewed |
| D | Company |
| E | Role |
| F | Source |
| G | ATS |
| H | Job URL |
| I | Posted Date |
| J | Job Age |
| K | Fit Score |
| L | Verdict |
| M | Readiness |
| N | Queue Status |
| O | Hold / Review Reason |
| P | Next Action |
| Q | Compensation |
| R | Key Matches |
| S | Material Gaps |
| T | Prepared Screening Answers |
| U | Cover Letter |
| V | CV Version |
| W | Media Requirement |
| X | Source / ATS Policy |
| Y | Re-review After |
| Z | Notes |

Queue statuses are `PREPARED`, `HELD`, `REVIEW`, `READY TO APPLY`, and `CLOSED`. Every active queue item must include a role-specific cover letter, even when the current form does not expose a cover-letter field. `Re-review After` is an input to future `$manage-job-search` runs: due non-closed rows are rechecked before fresh discovery inventory at the same priority.

## Controlled values

- Verdict: `STRONG APPLY`, `APPLY`, `REVIEW`, `SKIP`
- Application Status: `SHORTLISTED`, `PREPARED`, `APPLIED`, `ASSESSMENT`, `INTERVIEW`, `REJECTED`, `OFFER`, `WITHDRAWN`, `CLOSED`
- Response Type: `ACKNOWLEDGEMENT`, `RECRUITER CONTACT`, `REQUEST FOR INFORMATION`, `ASSESSMENT`, `INTERVIEW`, `REJECTION`, `OFFER`, `OTHER`
- Queue Status: `PREPARED`, `HELD`, `REVIEW`, `READY TO APPLY`, `CLOSED`

## Idempotency and transitions

Application identity uses Application ID and canonical URL. Review Queue identity uses the local Queue ID first, then canonical job URL, then normalized employer plus role as a defensive fallback. The local Queue ID is bound in SQLite to job ID, source posting ID, description hash, and canonical URL.

Before appending, check both the local ledger and existing Sheet rows. Update an existing row rather than appending a duplicate. Preserve non-empty manually edited status, next-action, date, and notes fields unless an explicitly authorized or proven lifecycle transition wins.

After verified submission:

1. upsert the application in `Applications` exactly once;
2. change the corresponding Review Queue row to `CLOSED`;
3. clear `Re-review After`;
4. set the next action to lifecycle monitoring in `Applications`.

Keep compensation fields human-readable without discarding provenance. SQLite remains authoritative for the structured original advertised range, PHP-normalized values, exchange rate and date, policy-derived expectation, submitted amount, and basis.

## Presentation

On both tabs, freeze row 1, enable a filter across A:Z, wrap long text, format dates consistently, keep score and age fields numeric, use readable column widths, and apply restrained native header styling. Use dropdown validation for controlled values.

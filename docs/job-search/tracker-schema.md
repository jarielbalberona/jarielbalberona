# Google Sheet application tracker

- Spreadsheet: `jarielbalberona-job-applications-tracker`
- Spreadsheet ID: `1UXc3HdWvR6SXX_1Y430-d1OUDpjKxrHWKARyqZj2Fxs`
- Connected account: `jarielbalb@gmail.com`
- Initial tab: resolve from live metadata before writing; the expected current title is `Sheet1`

The Sheet is the human-facing application lifecycle. SQLite owns discovery, skips, deduplication, drafts, execution detail, and run evidence.

## Columns A:Z

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

## Controlled values

- Verdict: `STRONG APPLY`, `APPLY`, `REVIEW`, `SKIP`
- Application Status: `SHORTLISTED`, `PREPARED`, `APPLIED`, `ASSESSMENT`, `INTERVIEW`, `REJECTED`, `OFFER`, `WITHDRAWN`, `CLOSED`
- Response Type: `ACKNOWLEDGEMENT`, `RECRUITER CONTACT`, `REQUEST FOR INFORMATION`, `ASSESSMENT`, `INTERVIEW`, `REJECTION`, `OFFER`, `OTHER`

## Idempotency

Application ID is derived from canonical URL, source posting ID where present, normalized company and role, and description hash. Before appending, check both the local ledger and existing Sheet rows by Application ID and canonical URL.

Update an existing row rather than appending a duplicate. Preserve non-empty manually edited Sheet status, next-action, follow-up, and notes fields unless the operator explicitly authorizes an overwrite or reliable update timestamps prove the local state is newer.

## Presentation

Freeze row 1, enable a filter across A:Z, wrap long text, format dates consistently, keep fit score numeric, use readable column widths, and apply clear restrained header styling. Add dropdown validation for controlled values where the connector supports it.

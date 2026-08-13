# Google Sheet job-search tracker

- Spreadsheet: `jarielbalberona-job-applications-tracker`
- Spreadsheet ID: `1UXc3HdWvR6SXX_1Y430-d1OUDpjKxrHWKARyqZj2Fxs`
- Connected account: `jarielbalb@gmail.com`
- Tabs: `Applications` and `Review Queue`

SQLite owns discovery, skips, deduplication, drafts, queue identity, lifecycle state, execution detail, and run evidence. The Sheet is a human-facing projection and review surface; it is not a second lifecycle authority.

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

For the hybrid campaign, create or update an `Applications` row only after submission is independently verified (`APPLIED` or a later lifecycle state). `SHORTLISTED`, `PREPARED`, `HUMAN_SUBMIT_READY`, discovery, skip, and dry-run records stay local or in `Review Queue`. Existing legacy pre-application rows may remain, but new hybrid runs must not add more of them.

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

Queue statuses are `HUMAN_SUBMIT_READY`, `READY_FOR_BROWSER_PREP`, `VIDEO_REQUIRED`, `HOLD`, `READY_TO_RETRY`, `SOURCE_RESTRICTED`, `POLICY_UNCLEAR`, `FORM_INACCESSIBLE`, `SUBMISSION_UNVERIFIED`, and `CLOSED`.

- `HUMAN_SUBMIT_READY`: the live form is fully populated and verified; Jariel's final click is the only remaining action. This is not an application submission.
- `READY_FOR_BROWSER_PREP`: the packet is complete but has not been loaded into a live browser form, normally because the 5-10 tab human batch is full.
- `SOURCE_RESTRICTED`: current applicant-side terms expressly prohibit the required automated or third-party submission action.
- `POLICY_UNCLEAR`: current official applicant-side material is silent or ambiguous, so autonomous submission is not permitted.
- `READY_TO_RETRY`: no candidate-fact blocker remains; re-open or re-inspect the live flow because a temporary access/form condition prevented final preparation.
- `HOLD`: a genuine role requirement, candidate decision, or unsupported material fact remains.
- `VIDEO_REQUIRED`: the only or primary candidate-owned blocker is a required introduction/recorded video.
- `FORM_INACCESSIBLE`: the live application form cannot currently be inspected or prepared.
- `SUBMISSION_UNVERIFIED`: a click or attempt occurred but independent confirmation evidence is absent; do not retry blindly or mark `APPLIED`.
- `CLOSED`: inactive, submitted, rejected, withdrawn, or otherwise no longer active.

Every active queue item must include a role-specific cover letter, even when the current form does not expose a cover-letter field. If the employer expressly requires candidate-authored, non-AI application prose, that source rule overrides generation: store a source-restriction note plus candidate-writing prompts, leave the live narrative fields blank, and use `READY_FOR_BROWSER_PREP` until Jariel authors them. `Re-review After` is an input to future `$manage-job-search` runs: due non-closed rows are rechecked before fresh discovery inventory at the same priority.

## Controlled values

- Verdict: `STRONG APPLY`, `APPLY`, `REVIEW`, `SKIP`
- Application Status: `APPLIED`, `SUBMISSION_UNVERIFIED`, `ASSESSMENT`, `INTERVIEW`, `REJECTED`, `OFFER`, `WITHDRAWN`, `CLOSED` (legacy rows may still contain `SHORTLISTED` or `PREPARED`; `HUMAN_SUBMIT_READY` belongs in Review Queue)
- Response Type: `ACKNOWLEDGEMENT`, `RECRUITER CONTACT`, `REQUEST FOR INFORMATION`, `ASSESSMENT`, `INTERVIEW`, `REJECTION`, `OFFER`, `OTHER`
- Queue Status: `HUMAN_SUBMIT_READY`, `READY_FOR_BROWSER_PREP`, `VIDEO_REQUIRED`, `HOLD`, `READY_TO_RETRY`, `SOURCE_RESTRICTED`, `POLICY_UNCLEAR`, `FORM_INACCESSIBLE`, `SUBMISSION_UNVERIFIED`, `CLOSED`

## Idempotency and transitions

Application identity uses Application ID and canonical URL. Review Queue identity uses the local Queue ID first, then canonical job URL, then normalized employer plus role as a defensive fallback. The local Queue ID is bound in SQLite to job ID, source posting ID, description hash, and canonical URL.

Before appending, check both the local ledger and existing Sheet rows. Update an existing row rather than appending a duplicate. Project application and queue status from SQLite. Preserve manual notes and compatible next-action/follow-up values, but never let a Sheet value regress or override proven lifecycle state. Queue expiry remains private structured state in SQLite; a due or expired row must be re-verified rather than silently closed.

After verified submission:

1. upsert the application in `Applications` exactly once;
2. change the corresponding Review Queue row to `CLOSED`;
3. clear `Re-review After`;
4. set the next action to lifecycle monitoring in `Applications`.

Keep compensation fields human-readable without discarding provenance. SQLite remains authoritative for the structured original advertised range, PHP-normalized values, exchange rate and date, policy-derived expectation, submitted amount, and basis.

## Presentation

On both tabs, freeze row 1, enable a filter across A:Z, wrap long text, format dates consistently, keep score and age fields numeric, use readable column widths, and apply restrained native header styling. Use dropdown validation for controlled values.

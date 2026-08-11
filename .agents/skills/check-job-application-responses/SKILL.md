---
name: check-job-application-responses
description: Search Gmail narrowly for responses to recorded job applications, read candidate messages and relevant threads, classify response intent, match high-confidence applications, persist idempotent events, and update lifecycle state read-only. Use for checking recruiter responses, assessments, interviews, rejections, offers, or application acknowledgements.
---

# Check job application responses

Read `docs/job-search/gmail-response-policy.md`. Use the structured Gmail connector when available. V1 is strictly read-only.

## Check

1. Load applications and dates from the local ledger.
2. Build narrow Gmail searches from company, role, recruiter or employer domain, ATS domain, and application timeframe.
3. Shortlist candidate messages; read bodies and relevant thread context when classification or matching depends on it.
4. Classify as `ACKNOWLEDGEMENT`, `RECRUITER CONTACT`, `REQUEST FOR INFORMATION`, `ASSESSMENT`, `INTERVIEW`, `REJECTION`, `OFFER`, or `OTHER`.
5. Match using explicit application reference, company, role, sender, timeframe, and ATS context.
6. Update only a high-confidence unique match. Persist ambiguity without choosing a convenient job.
7. Use provider message ID as the idempotency key and preserve valid later lifecycle states.
8. Sync the tracker only after a reliable local reconciliation.

Do not scan the whole inbox. Do not classify solely from a subject. Do not treat an automated receipt as recruiter interest. Do not send, reply, draft, archive, delete, mark, or label mail. Do not expose unrelated private email content in reports.

# Gmail job-response policy

Account: `jarielbalb@gmail.com`.

V1 is read-only. Do not send, reply, draft, archive, delete, mark, label, or otherwise mutate mail without later explicit authorization.

## Search boundary

Do not scan or summarize the whole inbox. Build narrow searches from applications in the ledger:

- company and role
- recruiter or employer domain
- ATS provider domain
- approximate application date
- common job-response intent such as receipt, update, next steps, screening, assessment, interview, scheduling, rejection, or offer

Search returns candidates, not classifications. Read shortlisted messages when needed and inspect the relevant thread when context changes the result. Do not disclose unrelated private mail.

## Classification

- `ACKNOWLEDGEMENT`: automatic application receipt; status remains `APPLIED`
- `RECRUITER CONTACT`: meaningful human contact; update response time and next action
- `REQUEST FOR INFORMATION`: additional details requested; do not send an answer in V1
- `ASSESSMENT`: coding exercise, take-home, questionnaire, or online test; status becomes `ASSESSMENT`
- `INTERVIEW`: interview or scheduling request; status becomes `INTERVIEW`
- `REJECTION`: status becomes `REJECTED`
- `OFFER`: status becomes `OFFER`
- `OTHER`: job-related but not confidently classifiable

Do not classify from the subject alone. An automated receipt is not recruiter interest.

## Matching

Use multiple signals: explicit application reference, company, role, sender or employer domain, timeframe, and ATS context. Update only on a high-confidence unique match. If multiple applications remain plausible, persist an unresolved local email event and report the ambiguity.

Use provider message ID as the idempotency key. Repeated checks must not create duplicate events or regress application state.

## Reconciliation

```text
verified application
-> local ledger
-> Sheet = APPLIED
-> inbound Gmail evidence
-> classify and match
-> local email and application event
-> idempotent Sheet update
```

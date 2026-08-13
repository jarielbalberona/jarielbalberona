# Read-only application response monitoring

The daily response monitor is intentionally narrow. Build searches only for SQLite applications in `APPLIED`, `ASSESSMENT`, or `INTERVIEW`, using application ID, employer, role, known sender/domain, and recent dates where available.

Allowed operations are search, read, classify, reconcile SQLite, and project proven lifecycle changes to the tracker. Sending, replying, archiving, deleting, and labeling are prohibited. Ambiguous messages remain unmatched and must not advance application status.

An acknowledgement can prove submission only when the employer/application match is independently strong. Store the Gmail message ID as the external key so reconciliation is idempotent.

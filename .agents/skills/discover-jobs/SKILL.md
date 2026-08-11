---
name: discover-jobs
description: Discover and normalize jobs with complete responsibilities, actual employer, origin, schedule, engagement type, original advertised compensation, remote eligibility, activity, canonical identity, and deduplication evidence. Use for job-board searches, source-specific discovery, or ledger imports.
---

# Discover jobs

Read `docs/job-search/target-roles.md`, `docs/job-search/application-policy.md`, and `docs/job-search/source-registry.yaml` before accessing a source.

## Discover

1. Confirm the source is enabled and discovery is permitted.
2. Search target titles and semantic variants. Prioritize international employers that can hire remotely from the Philippines.
3. Open each plausible listing and read its full responsibilities. Titles and snippets are insufficient.
4. Capture source posting ID, original URL, complete description, company shown, destination company when a recruiter or agency is involved, location, remote policy, employment type, work schedule, recurring-weekend requirement, posting date, and activity state.
5. Preserve the original advertised compensation text, currency, minimum, maximum, and monthly/annual/hourly basis when stated. For foreign ranges, record the current PHP-normalized monthly range, exchange rate, and conversion date without overwriting the original. Do not block or invent a range when compensation is undisclosed.
6. Verify the actual employer's origin or headquarters from reliable visible evidence. Record `INTERNATIONAL`, `PHILIPPINES`, or `AMBIGUOUS`; do not infer origin from posting location, office, payroll entity, or EOR.
7. Canonicalize the URL, compute a normalized description hash, and generate an application identity.
8. Run current-employer, company-origin, recurring-weekend, and known-compensation gates before fit assessment. Check both advertiser and destination employer names/domains.
9. Deduplicate by source posting ID, canonical URL, and normalized employer-role-description fingerprint.
10. Persist every result locally, including skips and ambiguity.

## Browser boundary

Use the supported browser workflow for real job-board UI. Reuse an existing authenticated Google session when appropriate, but never inspect or persist cookies, passwords, MFA data, or session storage. Stop only for an actual account confirmation or MFA interaction.

Browser capability does not authorize submission. Do not click final submission controls during discovery or `DRY_RUN`.

## Output per job

Return normalized fields, employer-origin evidence, reason codes, duplicate state, and source evidence. Store raw browser-derived detail only under ignored `.job-search/` runtime state.

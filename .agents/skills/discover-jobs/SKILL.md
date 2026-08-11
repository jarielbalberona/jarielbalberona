---
name: discover-jobs
description: Discover jobs from configured sources, read complete responsibilities, identify the actual employer and company origin, normalize fields, canonicalize URLs, hash descriptions, deduplicate, and persist all results. Use for job-board searches, source-specific discovery, or importing job listings into the local ledger.
---

# Discover jobs

Read `docs/job-search/target-roles.md`, `docs/job-search/application-policy.md`, and `docs/job-search/source-registry.yaml` before accessing a source.

## Discover

1. Confirm the source is enabled and discovery is permitted.
2. Search target titles and semantic variants. Prioritize international employers that can hire remotely from the Philippines.
3. Open each plausible listing and read its full responsibilities. Titles and snippets are insufficient.
4. Capture source posting ID, original URL, complete description, company shown, destination company when a recruiter or agency is involved, location, remote policy, compensation if stated, employment type, posting date, and activity state.
5. Verify the actual employer's origin or headquarters from reliable visible evidence. Record `INTERNATIONAL`, `PHILIPPINES`, or `AMBIGUOUS`; do not infer origin from posting location, office, payroll entity, or EOR.
6. Canonicalize the URL, compute a normalized description hash, and generate an application identity.
7. Run current-employer and company-origin gates before fit assessment. Check both advertiser and destination employer names/domains.
8. Deduplicate by source posting ID, canonical URL, and normalized employer-role-description fingerprint.
9. Persist every result locally, including skips and ambiguity.

## Browser boundary

Use the supported browser workflow for real job-board UI. Reuse an existing authenticated Google session when appropriate, but never inspect or persist cookies, passwords, MFA data, or session storage. Stop only for an actual account confirmation or MFA interaction.

Browser capability does not authorize submission. Do not click final submission controls during discovery or `DRY_RUN`.

## Output per job

Return normalized fields, employer-origin evidence, reason codes, duplicate state, and source evidence. Store raw browser-derived detail only under ignored `.job-search/` runtime state.

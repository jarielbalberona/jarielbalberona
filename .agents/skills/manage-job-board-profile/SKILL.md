---
name: manage-job-board-profile
description: Inspect, create, or update supported job-board profiles from the canonical candidate context while protecting authentication state and surfacing unknown declarations. Use for Indeed, LinkedIn, JobStreet, or other job-board profile access and truthful profile population.
---

# Manage job-board profile

Read `docs/job-search/candidate-context.md` and the source policy. Prefer truthful completeness over aggressive optimization.

## Authentication

1. Reuse the dedicated browser's existing Google session for `jarielbalb@gmail.com` when available.
2. Use `Continue with Google` or the platform equivalent when appropriate.
3. Reuse an existing board account; do not create duplicates.
4. Pause only for MFA, account confirmation, or a genuinely required user interaction, then continue.

Never request, extract, store, log, or commit a password, OAuth credential, cookie, browser token, MFA secret, or session state.

## Profile fields

Use canonical name, email, location, remote preference, headline, summary, skills, experience, portfolio, GitHub, LinkedIn, and current CV. Do not create a new CV during routine profile work.

Do not answer unknown salary, current compensation, notice, authorization, visa, or relocation declarations. Report them as unresolved.

Record any external profile mutation in the run log. Profile access does not authorize applying to jobs.

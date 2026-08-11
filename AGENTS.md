# AGENTS.md

## Mission

This repository owns two related systems:

- `portfolio/` is Jariel Balberona's public engineering site.
- the repository root is the control plane for a selective, evidence-led job search.

Optimize for truth, credibility, maintainability, and production judgment. Reject filler, invented outcomes, generic marketing language, blind mass applications, and complexity that exists only to look impressive.

## Routing

- Use `$manage-job-search` for end-to-end job discovery, assessment, preparation, permitted submission, tracking, and response reconciliation.
- Use the smaller skill under `.agents/skills/` when the request is limited to one stage.
- Treat `docs/job-search/` as the authoritative candidate, evidence, eligibility, application, source, tracker, and Gmail context.
- Treat `job_search/` as the deterministic policy and local-ledger implementation.
- Follow `portfolio/AGENTS.md` for public-site changes. Job-search runtime code does not belong in `portfolio/`.

## Non-negotiable rules

- Never fabricate candidate history, achievements, metrics, salary, notice period, authorization, visa status, relocation intent, management scope, or technology tenure.
- Keep confidential current clients generic in public material. Do not infer or publish identities from private exclusion checks.
- Run current-employer and company-origin eligibility checks before fit scoring.
- Score career direction separately from technical compatibility. Pure DevOps or SRE work must not become `STRONG APPLY` merely because Jariel has infrastructure experience.
- Target international employers that can hire remotely from the Philippines. Do not treat a Philippine job location, payroll entity, office, or EOR as proof that the underlying employer is Philippine-local.
- Follow `docs/job-search/source-registry.yaml` before any job-board write. Technical capability is not authorization.
- Do not mark an application `APPLIED` without verified submission evidence.
- Keep live autonomy in calibration until repository policy explicitly changes; readiness and source permission are mandatory even for `STRONG APPLY` roles.
- Keep Gmail access narrow, job-search-related, and read-only unless the user later authorizes a write.
- Never commit passwords, OAuth material, cookies, MFA secrets, browser state, job-board credentials, or tokens.
- `.job-search/` is ignored private runtime state. Do not move its contents into tracked files.

## Git and scope

- Inspect before changing. Preserve unrelated user work.
- Use isolated worktrees for substantial job-search changes and commit coherent phases.
- Keep public-site implementation under `portfolio/`; keep job-search policy, skills, tests, and supporting code at the repository root.
- Prefer the smallest approach that provides durable policy, deterministic verification, and useful evidence.

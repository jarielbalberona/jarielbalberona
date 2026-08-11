---
name: assess-job-fit
description: Evaluate a job against Jariel's hard employer rules, career direction, technical fit, eligibility confidence, and application readiness. Use to score a specific role, rank discovered jobs, separate infrastructure compatibility from target-role fit, select candidate evidence, or explain a skip/review/apply verdict.
---

# Assess job fit

Read `docs/job-search/candidate-context.md`, `docs/job-search/project-evidence.md`, `docs/job-search/target-roles.md`, and `docs/job-search/application-workflow.md`.

## Gate before scoring

1. Identify the actual destination employer.
2. Return `SKIP / CURRENT_EMPLOYER_EXCLUDED` for a confidential blocked employer or recruiter listing for one.
3. Return `SKIP / PH_LOCAL_COMPANY` for a confirmed Philippine-headquartered employer.
4. Return `REVIEW / COMPANY_ORIGIN_UNVERIFIED` when origin cannot be verified.
5. Apply remote-from-Philippines, seniority, and engineering-domain blockers.

Do not calculate a flattering score for a hard-blocked job.

## Score viable jobs

Score from the full description, not keyword overlap:

- actual responsibilities: 25
- architecture and engineering match: 15
- career-direction fit: 20
- technical stack: 10
- AI, product, or platform relevance: 10
- seniority and scope: 10
- remote and employment compatibility: 10

Do not treat conventional DevOps or SRE as a target AI/software-platform role merely because AWS, Terraform, CI/CD, Kubernetes, or observability match. Score technical credibility and career direction separately.

Multiply the base fit by eligibility confidence to produce the final fit score. Also return application readiness independently. Apply repository reason-code caps so optimistic inputs cannot hide material unknowns. Unknown compensation alone is not an eligibility penalty.

Map 85-100 to `STRONG APPLY`, 75-84 to `APPLY`, 65-74 to `REVIEW`, and below 65 to `SKIP`.

## Return

- fit score and verdict
- base fit, technical fit, and career-direction fit
- eligibility confidence and application readiness
- readiness reason codes
- employer-origin evidence and eligibility reason codes
- why the role exists or the employer's real problem
- strongest matches
- relevant projects and technologies
- legitimate gaps and dealbreakers
- recommended narrative, CV emphasis, and application angle
- interview risks

Never erase a gap or fabricate experience to increase the score.

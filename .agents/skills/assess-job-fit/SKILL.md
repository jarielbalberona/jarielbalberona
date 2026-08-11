---
name: assess-job-fit
description: Evaluate a job against employer, weekend, compensation, career-direction, technical-fit, eligibility-confidence, and application-readiness policy. Use to score or rank roles, separate technical compatibility from direction, and distinguish conservative resolved answers from material unknowns.
---

# Assess job fit

Read `docs/job-search/candidate-context.md`, `docs/job-search/project-evidence.md`, `docs/job-search/target-roles.md`, `docs/job-search/application-workflow.md`, and `docs/job-search/compensation-policy.md`.

## Gate before scoring

1. Identify the actual destination employer.
2. Return `SKIP / CURRENT_EMPLOYER_EXCLUDED` for a confidential blocked employer or recruiter listing for one.
3. Return `SKIP / PH_LOCAL_COMPANY` for a confirmed Philippine-headquartered employer.
4. Return `REVIEW / COMPANY_ORIGIN_UNVERIFIED` when origin cannot be verified.
5. Apply remote-from-Philippines, seniority, and engineering-domain blockers.
6. Return `SKIP / REQUIRED_WEEKEND_WORK` for required recurring Saturday or Sunday work. Review unclear on-call wording.
7. Evaluate known advertised compensation against employee or contractor thresholds. Undisclosed compensation is not a blocker.

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

Do not penalize legitimate full-time contractor, freelance, B2B, IC, or EOR structures. Do not reduce readiness for `BEST_SUPPORTED_ANSWER` or `CONSERVATIVE_ESTIMATE`; only genuine `MATERIAL_UNKNOWN` facts should block.

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

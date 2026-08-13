---
name: assess-job-fit
description: Evaluate a job against employer, weekend, compensation, career direction, technical fit, senior-capability evidence, eligibility confidence, and application readiness. Use to score or rank roles, separate technical compatibility from direction, distinguish capability from vendor experience, and separate strongest-supported answers from material unknowns.
---

# Assess job fit

Read `docs/job-search/application-answer-bank.md`, `docs/job-search/candidate-context.md`, `docs/job-search/project-evidence.md`, `docs/job-search/target-roles.md`, `docs/job-search/application-workflow.md`, and `docs/job-search/compensation-policy.md`.

## Gate before scoring

1. Identify the actual destination employer.
2. Return `SKIP / CURRENT_EMPLOYER_EXCLUDED` for a confidential blocked employer or recruiter listing for one.
3. Record employer origin and remote-from-Philippines evidence without using either as an eligibility gate. Philippine-local, origin-ambiguous, explicitly location-mismatched, and remote-unknown jobs may be scored and applied to; keep Jariel's location and authorization answers truthful.
4. Apply seniority and engineering-domain blockers from actual responsibilities, not title shorthand alone.
5. Return `SKIP / REQUIRED_WEEKEND_WORK` for required recurring Saturday or Sunday work. Review unclear on-call wording.
6. Evaluate known advertised compensation against employee or contractor thresholds. Undisclosed compensation is not a blocker.

When compensation is undisclosed, classify whether the role is Philippines-targeted international hiring, direct international-rate hiring, or genuinely unknown. Do not infer a premium budget from foreign headquarters or high job fit alone. Preserve any advertised range or recruiter budget evidence for application preparation.

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

Responsibilities override generic title labels. Assess senior backend, software-heavy platform, developer infrastructure, developer productivity, integration or cloud product engineering, hands-on solutions architecture, technical-lead, `Software Engineer`, `Engineer III`, and `Mid-Senior` roles when the actual scope is senior and hands-on.

Allow one learnable non-central framework, tool, or vendor gap when the responsibilities, architecture, and majority of the core stack match. Use `NONCENTRAL_SKILL_GAP` without a readiness cap. Keep `MATERIAL_REQUIREMENT_GAP` for a missing technology or capability central to daily work.

Multiply the base fit by eligibility confidence to produce the final fit score. Also return application readiness independently. Apply repository reason-code caps so optimistic inputs cannot hide material unknowns. Unknown compensation alone is not an eligibility penalty.

Do not penalize legitimate full-time contractor, freelance, B2B, IC, or EOR structures. Search the canonical answer bank before classifying an application fact as unresolved. Do not reduce readiness for `BEST_SUPPORTED_ANSWER` or `CONSERVATIVE_ESTIMATE`; only genuine `MATERIAL_UNKNOWN` facts should block.

Apply senior-experience calibration before calling a capability a gap. Infer API design from documented backend and REST ownership, database design from relational product systems, architecture from multi-tenant and production ownership, leadership from lead and hands-on CTO work, and CMS engineering from custom CMS, WordPress, Shopify, content models, administration, publishing, and API-backed content. Distinguish strong underlying capability from unsupported vendor specialization. Missing AEM, Sitecore, or another vendor keyword must not erase general CMS depth, but it also must not become a false vendor claim.

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

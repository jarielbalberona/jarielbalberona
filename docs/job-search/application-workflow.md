# Application workflow

Every application starts from the complete current job description. Never reuse a generic cover letter with only the employer and role replaced.

## Sequence

1. Load the normalized job and confirm it remains active.
2. Resolve the actual employer and run hard eligibility gates.
3. Deduplicate against the local ledger and tracker.
4. Assess the employer's real problem, responsibilities, seniority, architecture, career direction, stack, AI/product/platform relevance, and remote compatibility.
5. Choose one candidate narrative and the strongest two or three evidence sources.
6. Prepare a concise job-specific letter and direct screening-answer plan.
7. Resolve exact and best-supported answers, including conservative floor-style experience estimates. Surface only genuine material unknowns.
8. Check the source execution policy.
9. Submit only when the source and run mode permit it.
10. Require submission evidence before recording `APPLIED`.
11. Persist the local event, sync the human tracker, and later reconcile inbound Gmail evidence.

## Required assessment output

- Fit score and verdict
- Base fit, technical fit, and career-direction fit
- Eligibility confidence and application readiness
- Readiness reason codes and consequential unresolved questions
- Why the role exists or the employer's real problem
- Strongest matches
- Relevant projects and technologies
- Legitimate gaps and dealbreakers
- Recommended candidate narrative and CV emphasis
- Application angle and interview risks

## Fit rubric

```text
Actual responsibilities               25
Architecture / engineering match      15
Career-direction fit                  20
Technical stack                       10
AI / product / platform relevance     10
Seniority / scope                     10
Remote / employment compatibility     10
                                      ---
                                      100
```

Verdicts: 85-100 `STRONG APPLY`, 75-84 `APPLY`, 65-74 `REVIEW`, below 65 `SKIP`. Eligibility gates override the score.

The rubric total is the base fit. The final fit score is:

```text
round(base fit * eligibility confidence / 100)
```

Report these separately:

- `Technical Fit`: responsibilities, architecture, stack, and seniority normalized to 100.
- `Career Direction Fit`: the career-direction dimension normalized to 100.
- `Eligibility Confidence`: confidence that employer, activity, remote, location, and employment facts are correctly resolved.
- `Application Readiness`: whether the current listing, packet, actual screening questions, required answers, and material experience claims are ready for submission.

Unknown advertised compensation does not reduce eligibility by itself. Expected compensation follows `compensation-policy.md`. Reduce readiness or require review for unresolved remote eligibility, recurring weekend obligations, work authorization, genuine material unknowns, unavailable application entry, or materially unsupported requirements.

The engine enforces upper bounds for these reason codes. Caller-supplied confidence or readiness cannot override a stricter cap. Unknown compensation has no automatic cap; if the live form requires an answer, the unanswered consequential question still blocks submission.

## Narrative selection

- Senior Software Engineer: lead with 10+ years, TypeScript, React, Node.js, PostgreSQL, SaaS architecture, cloud delivery, and production ownership. Use AI-native engineering as a differentiator.
- AI-native or agentic: lead with repository context, tool-enabled agents, ticket-to-code execution, deterministic and runtime verification, bounded correction, human approval, and execution evidence. Then establish conventional engineering depth.
- AI Product Engineer: lead with DataGPT AI, AI workflow UX, Ordr.now, and full-stack ownership.
- Platform: lead with multi-tenancy, PostgreSQL, Docker, Terraform, AWS/Azure, Vercel, Supabase, CI/CD, observability, and developer tooling.
- Modernization: lead with PRIVV and Experience Digital, behavior preservation, incremental migration, and architecture evolution.

## Letter style

Default to roughly three short paragraphs:

1. State the role and the specific engineering responsibility that matches Jariel's current work.
2. Connect the strongest two or three real evidence points to that responsibility.
3. Close plainly with interest in discussing the contribution.

Use concise, direct, engineering-focused language. Avoid generic praise, autobiography, keyword dumping, exaggerated confidence, obvious AI prose, and em dashes. Do not repeat the CV.

## Questions

Answer questions directly. Do not turn each answer into a cover letter. Use exact facts first, then best-supported answers and conservative floor-style estimates grounded in the candidate context, CV, and project evidence. Record answer, interpretation, confidence, and supporting evidence. A conservative estimate is resolved and normally does not reduce readiness.

Never invent current salary, authorization, visa, relocation, team size, management scope, revenue, user counts, metrics, technology experience with no real implementation evidence, degrees, or certifications. Record those as `MATERIAL_UNKNOWN` when no legitimate non-disclosure option exists. Expected compensation, contractor willingness, weekday timezone availability, broad AI experience, and ordinary defensible technology estimates should not remain unresolved.

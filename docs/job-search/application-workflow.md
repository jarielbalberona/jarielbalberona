# Application workflow

Every application starts from the complete current job description. Never reuse a generic cover letter with only the employer and role replaced.

## Sequence

1. Load the normalized job and confirm it remains active.
2. Resolve the actual employer and run hard eligibility gates.
3. Deduplicate against the local ledger and tracker.
4. Persist posting date, discovery date, age in days, and freshness bucket. Search `P0_FRESH` before `P1_RECENT`; normally skip older listings during a bounded campaign.
5. Assess the employer's real problem, responsibilities, seniority, architecture, career direction, stack, AI/product/platform relevance, and remote compatibility.
6. Choose one candidate narrative and the strongest two or three evidence sources.
7. Prepare a concise job-specific letter and direct screening-answer plan.
8. Inspect every live form control; search the canonical answer bank first, then resolve exact, strongest-supported, capability-depth, best-supported, and conservative answers. Surface only genuine material unknowns.
9. Run `SENIOR_POSITIONING_REVIEW` across the complete live payload.
10. Check the dated source execution policy and any employer-specific declarations.
11. Submit only when the source, run mode, readiness, and campaign cap permit it.
12. Require submission evidence before recording `APPLIED`.
13. Persist the local event, sync the human tracker, and later reconcile inbound Gmail evidence.
14. On a per-job blocker, hold or skip that application and continue the campaign.

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

Required candidate media must be classified from the live application control when available. A missing required introduction video uses `REQUIRED_VIDEO_INTRO`, caps Application Readiness below the autonomous threshold, and holds the application without changing the job-fit dimensions. Do not infer `NOT_REQUIRED` from a job description that merely omits media; use `UNKNOWN_NOT_INSPECTED` until the form is inspected.

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

Use concise, direct, engineering-focused language. Lead with supported ownership and outcomes. Avoid generic praise, autobiography, keyword dumping, exaggerated confidence, obvious AI prose, eager-to-learn framing, and em dashes. Do not repeat the CV or volunteer a secondary weakness when it is not central to the role.

## Questions

Answer questions directly. Do not turn each answer into a cover letter. Search `application-answer-bank.md` and its machine-readable index first, then use candidate and project evidence, the strongest supported interpretation, direct or transferable capability classifications, best-supported answers, and conservative floor-style estimates. Record answer, interpretation, confidence, and supporting evidence. Positive evidence-backed statuses and conservative estimates are resolved and normally do not reduce readiness.

Recognize senior engineering equivalence. Custom CMS development, WordPress, Shopify, and content administration are substantial CMS capability; REST and full-stack ownership support API design; relational product systems support database design; multi-tenant SaaS and production ownership support architecture; lead and consulting roles support technical leadership and client-facing delivery. Do not turn missing vendor keywords into missing capability. Conversely, do not claim a vendor specialization, exact duration, legal fact, credential, or metric without evidence.

Evaluate forced-choice options as complete claims. Do not choose an option because one clause is supported when another clause asserts unsupported enterprise scale, vendor depth, migration history, traffic volume, or organizational scope. Select the highest option whose full meaning is supported, even when a lower option compresses or understates nuance; preserve the accurate nuance in a related free-text field or letter.

Resolve `How did you hear about us?` from original discovery evidence, not the current URL. Store discovery channel, destination page, and ATS host separately. If managed web search surfaced an ATS-hosted listing and the search provider is not known, answer with a generic online-search or `Other` value supported by the live form rather than naming the ATS as the source.

Before reaching the submission boundary, run `SENIOR_POSITIONING_REVIEW` and ask whether every substantive answer is truthful, the strongest defensible answer, senior in tone, free of irrelevant weakness framing, and free of overclaim. Automatically replace known evidence-backed weak CMS framing. Any remaining `UNNECESSARY_UNDERSELL` must be revised; `UNSUPPORTED_OVERCLAIM` blocks readiness.

Never invent authorization, visa, team size, management scope, revenue, user counts, metrics, technology experience with no real implementation evidence, degrees, or certifications. Record those as `MATERIAL_UNKNOWN` when unsupported. Current salary uses canonical not-currently-employed status; previous salary is read only from the gitignored private candidate-facts store. Expected compensation, contractor willingness, relocation, weekday timezone availability, broad AI experience, and ordinary defensible technology estimates should not remain unresolved.

Philippine citizenship and work authorization are canonical facts, not unresolved legal questions. Answer Filipino citizenship and legal authorization to work in the Philippines `Yes`, Philippine employment sponsorship `No`, and United States authorization `No` or `Not Applicable / located outside the US` according to the live control. Keep every other jurisdiction unresolved unless it is added explicitly to candidate facts.

Resolve expected compensation from the engagement type, role level, AI alignment, advertised range, Philippines-targeted versus direct-international market context, and actual high-budget evidence. High job fit alone is not proof of a premium budget. Prefer a defensible conversion-friendly anchor over automatically selecting the top of the policy range, while preserving hard minimums and never treating compensation above the target maximum as a reason to reject.

Notice period and start availability come from `job_search/policy/candidate_facts.json`. Use zero days, no notice or rendering period, and immediate availability unless Jariel later changes that canonical policy. Do not invent a conventional two-week period, and do not expose confidential employer or client relationships when answering ordinary availability questions.

Upcoming commitments affecting availability during the next three months are canonically `false`. Answer equivalent yes/no questions `No`; for required free text use `No, I don't have any upcoming commitments that would affect my work schedule or availability.` Do not escalate this fact again.

For one numeric field spanning multiple technologies, determine whether it asks for overall stack experience or explicitly requires depth in every technology. Overall questions use a documented dominant-stack estimate from majority/core evidence; they do not default to the weakest technology, minimum tenure, or an average. Individual questions remain technology-specific. Explicit `all`/`each` wording uses weakest-depth semantics, and any never-used technology remains unresolved rather than being hidden by the stronger majority.

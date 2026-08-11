# Application workflow

Every application starts from the complete current job description. Never reuse a generic cover letter with only the employer and role replaced.

## Sequence

1. Load the normalized job and confirm it remains active.
2. Resolve the actual employer and run hard eligibility gates.
3. Deduplicate against the local ledger and tracker.
4. Assess the employer's real problem, responsibilities, seniority, architecture, stack, AI/product/platform relevance, and remote compatibility.
5. Choose one candidate narrative and the strongest two or three evidence sources.
6. Prepare a concise job-specific letter and direct screening-answer plan.
7. Surface consequential unknowns. Continue preparing known sections without inventing answers.
8. Check the source execution policy.
9. Submit only when the source and run mode permit it.
10. Require submission evidence before recording `APPLIED`.
11. Persist the local event, sync the human tracker, and later reconcile inbound Gmail evidence.

## Required assessment output

- Fit score and verdict
- Why the role exists or the employer's real problem
- Strongest matches
- Relevant projects and technologies
- Legitimate gaps and dealbreakers
- Recommended candidate narrative and CV emphasis
- Application angle and interview risks

## Fit rubric

```text
Actual responsibilities               30
Architecture / engineering match      20
Technical stack                       15
AI / product / platform relevance     15
Seniority / scope                     10
Remote / employment compatibility     10
                                      ---
                                      100
```

Verdicts: 85-100 `STRONG APPLY`, 75-84 `APPLY`, 65-74 `REVIEW`, below 65 `SKIP`. Eligibility gates override the score.

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

Answer questions directly. Do not turn each answer into a cover letter. Never invent salary, notice, authorization, visa, relocation, team size, management scope, revenue, user counts, metrics, technology tenure, degrees, or certifications. Record unresolved consequential questions in the draft packet and block submission until resolved.

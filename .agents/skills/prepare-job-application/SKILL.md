---
name: prepare-job-application
description: Prepare a truthful senior-level job-specific packet with selected evidence, concise letter, exact and strongest-supported answers, capability-versus-vendor calibration, autonomous compensation, answer provenance, and only genuine material unknowns. Use for drafts, screening preparation, or shortlisted-role packets.
---

# Prepare job application

Read `docs/job-search/application-workflow.md`, `docs/job-search/application-answer-bank.md`, `docs/job-search/candidate-context.md`, `docs/job-search/project-evidence.md`, `docs/job-search/compensation-policy.md`, `job_search/policy/application_answer_bank.json`, and `job_search/policy/candidate_facts.json`. Require an eligible fit assessment and complete job description.

## Prepare

1. State the engineering problem the employer is hiring this role to solve.
2. Select one narrative: senior software, AI-native/agentic, AI product, platform, or modernization.
3. Select only the strongest two or three evidence sources.
4. Write roughly three short paragraphs: role-specific hook, connected evidence, plain close.
5. Resolve questions actually observed in the current application in this order: canonical answer bank, candidate and project evidence, strongest supported interpretation, direct or transferable capability classification, best-supported answer, conservative floor-style estimate, then `MATERIAL_UNKNOWN`. Record answer, status, interpretation, confidence, and evidence.
6. Resolve ordinary expected-compensation questions autonomously from the compensation policy, using the employer's advertised range and Philippines-targeted versus direct-international market context. Preserve hard floors, but do not automatically maximize the answer because fit is high. Use canonical not-currently-employed status for current salary and the separate canonical previous-salary fact only when the live wording asks for it. Do not invent generic notice or authorization questions when the source did not ask them.
7. Record legitimate gaps, interview risks, CV version, and reasons to apply or not apply.
8. Run `SENIOR_POSITIONING_REVIEW` across substantive screening answers and the letter. Rewrite `UNNECESSARY_UNDERSELL`; reject `UNSUPPORTED_OVERCLAIM`. Use ownership language and lead with documented capability rather than eager-to-learn or limited-experience framing.
9. Treat every forced-choice option as a complete claim. Select the strongest option for which every material scale, vendor, environment, migration, traffic, or scope assertion is supported; preserve more precise depth in free text when available.
10. Resolve discovery-source questions from original provenance. Keep discovery channel, destination page, and ATS host separate; an ATS is not the discovery channel merely because it hosts the form.
11. Scan public text for confidential client names, unrelated employer names, fabricated metrics, generic flattery, keyword dumps, and em dashes.
12. Persist the packet, answer metadata, positioning review, and compensation decision under ignored `.job-search/artifacts/` and in SQLite.

Avoid `I am thrilled to apply`, exaggerated mission praise, `unique blend`, generic autobiographies, and CV repetition. Rewrite for every role.

Never disclose confidential client identities or imply ML research/model-training experience that Jariel does not have.

For CMS questions, treat custom CMS development as direct deep experience, WordPress and Shopify as direct working experience, and headless or enterprise content architecture as strongly transferable. Answer general CMS questions confidently. Do not claim AEM, Sitecore, large-scale multi-site or multi-language delivery, high-traffic CMS optimization, or another unsupported enterprise specialization merely to qualify for a stronger forced-choice option.

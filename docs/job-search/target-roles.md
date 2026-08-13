# Target roles and employer policy

## Positioning

Senior Software Engineer is the baseline identity. AI-native and agentic product or platform engineering is the specialization. A senior software role building an AI-native system may be stronger than an `AI Engineer` role centered on model research.

## Primary roles

- Senior Software Engineer
- Senior Product Engineer
- Senior Full-Stack Engineer
- Senior Software Engineer - AI, AI Platform, or Agentic AI
- Senior AI Product Engineer
- AI Product Engineer
- Applied AI Engineer
- AI Application Engineer
- Agentic AI Engineer
- AI Platform Engineer
- Senior Product Platform Engineer
- Developer Productivity Engineer
- Developer Experience Engineer - AI
- Software Engineer - Autonomous Agents or Coding Agents
- Staff Software Engineer
- Staff Software Engineer - AI
- Staff Product Engineer

## Adjacent roles

Also assess senior backend, software-heavy platform, developer infrastructure, developer productivity, integration or cloud product engineering, hands-on solutions architecture, and technical-lead roles with substantial implementation ownership. Responsibilities, scope, compensation, and evidence of hands-on delivery override title shorthand such as `Software Engineer`, `Engineer III`, or `Mid-Senior`.

One learnable non-central framework, tool, or vendor gap is acceptable when the responsibilities, architecture, and majority of the core stack match. A missing technology that is the daily center of the job remains a material requirement gap.

## Deprioritize or skip

Heavily penalize or skip pure ML research, research scientist, data scientist, model-training specialist, CUDA or kernel engineering, roles centered on advanced PyTorch/model training, pure DevOps, pure SRE with little product work, minimally hands-on management, explicitly junior roles, pixel-only frontend implementation, WordPress-only work, and generic VA/BPO technical work.

Python is not itself a blocker. Determine whether it is merely the implementation language or whether deep ML research is the actual job.

## Career direction

Technical compatibility is not the same as career-direction fit. Jariel's AWS, Terraform, CI/CD, observability, and DevOps history can support a product or software-platform role, but conventional infrastructure operations are not the target destination.

Give high career-direction scores to hands-on senior software, product, full-stack, AI product, agentic AI, developer platform, and AI platform work. Give low scores to pure DevOps, pure SRE, cluster operations, infrastructure administration, and incident/on-call roles whose product engineering content is incidental.

A pure DevOps or SRE role may still be technically credible. It must not reach `STRONG APPLY` from technical overlap alone.

## Employer geography

Prioritize companies based outside the Philippines, but employer origin is no longer an eligibility gate. Determine and record the actual employer's origin or headquarters when evidence is available; do not infer it from posting location or payroll vehicle.

Eligible examples:

- a US company hiring remote engineers in the Philippines
- a UK company with a Manila office
- an Australian company using a Philippine Employer of Record
- a European company with a Philippine subsidiary or local payroll

Philippine-headquartered employers may proceed through compensation, responsibilities, seniority, engineering-domain, schedule, and fit assessment. Continue to score generic outsourcing, VA/BPO, staffing, and low-value agency work poorly based on the actual work; do not reject a credible product-engineering employer merely because it is Philippine-local.

If employer origin remains ambiguous after reasonable verification, store `AMBIGUOUS` and continue. Never invent an origin.

Remote-from-Philippines status is also assessment evidence rather than a hard gate. Explicit exclusions, silence, and positive support must be recorded accurately and reflected in the remote/employment-compatibility score. Applications must always use the canonical Philippine location and truthful authorization answers even when the listing indicates a location mismatch.

## Current-employer exclusion

Current employers and clients are hard-blocked across direct listings, aliases, known domains, ATS pages, company career pages, and recruiter or agency listings where the destination company is known. Use `CURRENT_EMPLOYER_EXCLUDED` before scoring. Never reveal the current relationship in application text or public artifacts.

The confidential identities are stored as normalized fingerprints in `job_search/policy/employer_exclusions.json`; plaintext matching input may exist only in ignored private runtime state.

## Eligibility order

```text
identify actual employer
-> current-employer check
-> record company origin and remote geography
-> role and seniority eligibility
-> engineering-domain eligibility
-> deduplication
-> fit assessment
```

A technically perfect role is still a skip when a hard blocker applies.

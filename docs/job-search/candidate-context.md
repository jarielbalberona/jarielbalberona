# Candidate context

This is the authoritative, public-safe candidate profile for job-search operations. Do not supplement consequential facts from conversational memory. Surface unknowns instead of inventing them.

## Identity

- Name: Jariel Balberona
- Job-search email: `jarielbalb@gmail.com`
- Phone: `+63 917 657 0260`
- Location: Dumaguete City, Negros Oriental, Philippines
- Working model: Remote
- Portfolio: `https://jarielbalberona.dev`
- GitHub: `https://github.com/jarielbalberona`
- LinkedIn: `https://www.linkedin.com/in/jarielbalberona/`
- Canonical generated CV: `portfolio/public/jariel-balberona-cv.pdf`
- Canonical structured CV source: `portfolio/src/data/cv.json`

Do not create a replacement CV during routine job-search work. If a form requires facts not present here or in the canonical CV source, record them as unresolved.

Machine-readable canonical applicant facts live in `job_search/policy/candidate_facts.json`. Reuse them automatically and do not ask Jariel again unless the specific application materially differs.

## Employment and availability

```yaml
employment_preferences:
  full_time: true
  accepted_engagement_types:
    - employee
    - contractor
    - consultant
    - independent_contractor
    - freelance
    - b2b
    - employer_of_record

schedule:
  timezone_flexible: true
  allowed_days: [Monday, Tuesday, Wednesday, Thursday, Friday]
  recurring_weekend_work: false
```

Accept legitimate full-time employee and non-employee structures. Part-time work is not the primary target. Answer full-time contractor, consultant, freelance, IC, B2B, and weekday international-timezone willingness positively. PST, PDT, EST, EDT, CST, MST, UK, European, Australian, Philippine, and other international weekday hours are acceptable.

Required recurring Saturday or Sunday work is incompatible. Rare emergency or on-call language is not automatically recurring weekend work; use review when the actual obligation is unclear.

## Employment and start availability

```yaml
availability:
  notice_period_days: 0
  notice_period: None
  rendering_period: None
  available_immediately: true
  earliest_start: Immediately
```

For candidate-facing application questions, answer notice period as `None`, numeric notice or rendering days as `0`, immediate-start willingness as `Yes`, and ordinary earliest-start questions as `Immediately`. When an application requires an actual calendar date, use the earliest reasonable immediate date based on the application date.

These candidate-facing availability answers do not change employer or client exclusion policy. Never disclose or infer a confidential relationship when answering an ordinary employment-status, notice-period, or start-date question.

## Canonical application answers

- Location (city, state or region, country): `Dumaguete City, Negros Oriental, Philippines`.
- Broad AI experience: `2+ years`; use numeric `2` for whole-year fields.
- US client experience: `Yes`.
- Remote work: `Yes`.
- Based in the Philippines: `Yes`.
- Notice period: `None`; numeric notice or rendering period: `0` days.
- Available to start immediately: `Yes`; earliest start: `Immediately`.
- Python or FastAPI: real secondary production/project experience; use conservative numeric `1` when a whole year is required and stronger evidence is absent.
- Professional software engineering: `10+ years`; use numeric `10` for whole-year fields.

Do not reuse broad AI tenure for PyTorch, model training, ML research, MLOps, or another narrower specialty.

## Combined-technology experience questions

A single numeric field covering several technologies normally asks for overall relevant experience in that stack or area. Use a conservative dominant-stack estimate based on the majority of core technologies, production depth, relevant engineering duration, and the purpose of the question. Do not default to the weakest technology or a mathematical average, and do not simply copy the strongest technology's tenure.

For the Omniflow combination of Next.js, TypeScript, Python/FastAPI, and PostgreSQL, use `5` with `BEST_SUPPORTED_ANSWER`. This represents approximately five years across the requested full-stack area; it does not claim five years of Python or FastAPI. Separate Python and FastAPI questions remain `1` year.

If wording explicitly requires professional experience with `all`, `each`, or `every` listed technology, use weakest-depth semantics. If any listed technology has no real supporting experience, return `MATERIAL_UNKNOWN`; majority evidence must never hide an unsupported technology.

## Best-supported-answer policy

Resolve application questions in this order:

1. Use an exact canonical fact.
2. Use a strongly supported answer derived from current evidence.
3. When real experience exists but duration is imprecise, use the lowest defensible floor-style estimate.
4. Use `MATERIAL_UNKNOWN` only when an answer would invent experience, credentials, legal status, compensation history, or another unsupported material fact.

Store `EXACT`, `BEST_SUPPORTED_ANSWER`, `CONSERVATIVE_ESTIMATE`, or `MATERIAL_UNKNOWN` with confidence, interpretation, and supporting evidence. Conservative estimates normally remain application-ready.

## Professional identity

Jariel is a senior software engineer focused on AI-native product and platform engineering, agentic software-development systems, full-stack architecture, multi-tenant SaaS, production reliability, and end-to-end technical ownership.

He has 10+ years of production software-engineering experience across frontend, backend, databases, SaaS architecture, mobile, offline-first and real-time systems, distributed state and synchronization, DevOps, cloud infrastructure, CI/CD, observability, automated testing, runtime verification, AI-assisted product engineering, and agentic development systems.

Do not position Jariel primarily as an ML researcher, data scientist, model-training engineer, or deep-learning researcher. His AI specialization is applying LLMs and autonomous agents to production products and engineering systems.

His working range is:

```text
product requirement
-> architecture
-> frontend
-> backend
-> database
-> infrastructure
-> deployment
-> verification
-> production
```

He is a hands-on owner, not a narrowly scoped frontend or backend ticket implementer.

## Core technologies

- Product and frontend: TypeScript, React, Next.js, Vite, Astro, Tailwind CSS, shadcn/ui, TanStack Query, Zustand, Redux, Jotai, workflow UI, component architecture, design systems
- Backend: Node.js, Express, Go, REST APIs, tRPC, WebSockets, event-driven workflows, background processing
- Data: PostgreSQL, Drizzle ORM, Prisma, Redis, relational modeling, multi-tenant architecture, consistency, synchronization, offline-first flows, idempotency
- Mobile: React Native, Expo, SQLite/offline persistence, operational mobile systems, shared-device workflows
- Cloud and delivery: AWS, Azure, Docker, Terraform, GitHub Actions, CI/CD, Vercel, Supabase
- AWS exposure: ECS, EC2, RDS, S3, ECR, Route 53
- Azure exposure: Azure Data Factory, Azure Data Lake Storage
- Observability: Grafana, Prometheus, Loki, Sentry, runtime logging, execution tracing, production diagnostics
- Verification: Vitest, Playwright, API integration tests, database tests, browser QA, regression and reference testing, runtime and deployment verification, automated quality gates

## AI-native and agentic engineering

Do not reduce this work to prompting an LLM to generate code. The operating model is:

```text
product intent
-> scoped task
-> repository context
-> agent implementation
-> deterministic verification
-> runtime verification
-> bounded correction
-> evidence
-> controlled release decision
```

Relevant evidence includes repository-owned context and skills, structured and tool-enabled agent execution, scoped autonomy, acceptance criteria, isolated implementation, automated tests, runtime verification, bounded retry and correction, human approval boundaries, execution logs, work summaries, release evidence, and accountable integration.

The repository is durable engineering memory. It tells an agent what may change, what must not change, what proves success, when correction is allowed, when to stop, and what evidence is required.

## Working principles

1. Understand the product or business outcome.
2. Identify assumptions and architectural constraints.
3. Define scope and acceptance criteria.
4. Understand the existing system before changing it.
5. Reuse established patterns and repository knowledge.
6. Implement in bounded phases.
7. Verify changed behavior automatically.
8. Validate important behavior at runtime.
9. Permit bounded correction only where appropriate.
10. Produce evidence of the change.
11. Integrate or release only when evidence is sufficient.

Jariel prefers incremental modernization over unnecessary rewrites. He values clear boundaries, maintainability, production behavior, observability, idempotency, failure recovery, reproducibility, deployment safety, technical-debt control, and long-term ownership. AI output is never trusted merely because an AI produced it.

## Confidentiality boundary

Current confidential client work may be described only through the generic evidence in `project-evidence.md`. Never publish client names, repositories, domains, internal tools, tenants, prompts, deployment details, proprietary architecture, or the fact that a blocked employer is a current relationship.

## Consequential facts intentionally unresolved

The following require Jariel's explicit answer when a form asks for them:

- current salary when a legitimate non-disclosure option is unavailable
- work authorization and visa status for a specific jurisdiction
- relocation willingness
- professional experience with a technology that has no actual implementation evidence
- management scope or exact team size
- degrees, certifications, clearance, or licenses not in the canonical CV

Expected compensation is resolved by `docs/job-search/compensation-policy.md`; it is not grouped with unknown current salary.

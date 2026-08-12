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
- Canonical candidate photo: private gitignored asset at `.job-search/assets/candidate-photo.jpeg`

Use `Jariel Balberona` for ordinary professional-name fields. Legal name, full mailing address, and prior compensation are application-only private facts in `.job-search/private-candidate-facts.json`. Read them only for a form that specifically requires the corresponding legal, identity, address, background-check, contract, or compensation fact. Never copy them into this document, a CV, portfolio content, a cover letter, or another tracked/public artifact.

Do not create a replacement CV during routine job-search work. If a form requires facts not present here or in the canonical CV source, record them as unresolved.

Machine-readable canonical applicant facts live in `job_search/policy/candidate_facts.json`. The reusable semantic index lives in `job_search/policy/application_answer_bank.json`, with human guidance in `docs/job-search/application-answer-bank.md`. Search the answer bank first, reuse these facts automatically, and do not ask Jariel again unless the specific application materially differs.

## Candidate media

```yaml
candidate_media:
  photo:
    available: true
    reusable: true
    private_asset_path: .job-search/assets/candidate-photo.jpeg
  introduction_video:
    available: false
    create_now: false
  required_video_behavior:
    action: HOLD
    reason_code: REQUIRED_VIDEO_INTRO
```

The photo is a validated 400 by 400 RGB JPEG and is suitable for legitimate professional applications. Its exact checksum, size, and MIME metadata live in the machine-readable candidate facts. The image itself stays private and gitignored. Do not ask for another photo unless a destination has materially different requirements that the canonical image cannot satisfy.

Do not create or submit an introduction video yet. When a live form proves that a video is required, keep the application `PREPARED`, apply `REQUIRED_VIDEO_INTRO`, and hold before submission. Optional video controls may be omitted. Media availability changes Application Readiness only; it does not change Technical Fit or Career Direction Fit.

## Employment and availability

```yaml
employment_preferences:
  full_time: true
  can_commit_40_hours_weekly: true
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
  monday_to_friday: true
  allowed_days: [Monday, Tuesday, Wednesday, Thursday, Friday]
  recurring_weekend_work: false
  occasional_emergency_or_oncall_weekend: true
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
  upcoming_commitments_affecting_work: false
  available_for_screening_this_week: true
```

For candidate-facing application questions, answer notice period as `None`, numeric notice or rendering days as `0`, immediate-start willingness as `Yes`, and ordinary earliest-start questions as `Immediately`. When an application requires an actual calendar date, use the earliest reasonable immediate date based on the application date.

Answer questions about upcoming commitments, planned leave, or travel affecting work during the next three months as `No`. For required free text, use `No, I don't have any upcoming commitments that would affect my work schedule or availability.` Equivalent weekday-schedule restriction questions should also resolve without review.

These candidate-facing availability answers do not change employer or client exclusion policy. Never disclose or infer a confidential relationship when answering an ordinary employment-status, notice-period, or start-date question.

Canonical application employment status is `not currently employed`, actively seeking full-time work, and available for screening this week. Current salary is therefore `Not currently applicable / not currently employed`, or numeric `0` only when a required control is strictly numeric. Previous or most-recent salary must be loaded from the private candidate-facts store and must not be reproduced in tracked documentation.

Outside commitments do not interfere with full-time work. Jariel will prioritize the employer role and can accept an exclusivity requirement. Treat a materially broader IP or pre-existing-asset clause as a separate legal question.

The remote setup includes a professional, dedicated, quiet workspace; a suitable development computer; webcam; microphone; screen sharing; high-speed internet; backup internet through a secondary provider and mobile data; and backup power. Backup internet has a verified minimum of 100 Mbps. Backup power exceeds eight hours and supports a full workday; use the conservative whole number `8` when a numeric control requires hours. Provider names and detailed device specifications remain private/unspecified.

## Mobility, working style, and standard application commitments

Jariel is willing to relocate, including to a specifically named ordinary destination, and to travel domestically or internationally for business. A passport is available; do not expose document details.

Answer ordinary questions confidently for independent/self-directed work, ambiguity, fast-moving or changing requirements, technical leadership, engineering mentoring, architecture ownership, code and pull-request review, distributed/global/remote teamwork, and direct client, stakeholder, product, and business communication. These facts do not authorize invented direct-report counts.

Background and reference checks, NDAs/confidentiality, reasonable restrictive covenants, conflict-of-interest rules, standard assessments, take-home work, live coding, pair programming, and system-design interviews are accepted. Broad legal agreements still receive separate review. References are available upon request; do not provide contact details without a specific need.

Jariel owns a suitable development computer, does not require an employer-provided machine, and can use employer-provided equipment if required. Recruitment, talent-pool, marketing, and promotional communication consent are canonically `Yes`.

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
- React: `10 years`; TypeScript: `8 years`.
- CMS experience: `Yes`; represent substantial custom CMS development, WordPress, Shopify, and content-platform engineering confidently.
- Professional LLM providers: `OpenAI, Anthropic Claude, and Google Gemini`.

Do not reuse broad AI tenure for PyTorch, model training, ML research, MLOps, or another narrower specialty.

## Combined-technology experience questions

A single numeric field covering several technologies normally asks for overall relevant experience in that stack or area. Use a conservative dominant-stack estimate based on the majority of core technologies, production depth, relevant engineering duration, and the purpose of the question. Do not default to the weakest technology or a mathematical average, and do not simply copy the strongest technology's tenure.

For the Omniflow combination of Next.js, TypeScript, Python/FastAPI, and PostgreSQL, use `5` with `BEST_SUPPORTED_ANSWER`. This represents approximately five years across the requested full-stack area; it does not claim five years of Python or FastAPI. Separate Python and FastAPI questions remain `1` year.

If wording explicitly requires professional experience with `all`, `each`, or `every` listed technology, use weakest-depth semantics. If any listed technology has no real supporting experience, return `MATERIAL_UNKNOWN`; majority evidence must never hide an unsupported technology.

## CMS and content-platform experience

Jariel has substantial hands-on CMS engineering experience. Treat capability and vendor experience separately.

```yaml
cms:
  general_cms: DIRECT_DEEP
  custom_cms_development: DIRECT_DEEP
  wordpress: DIRECT_WORKING
  shopify: DIRECT_WORKING
  headless_cms_architecture: TRANSFERABLE_STRONG
  enterprise_cms_concepts: TRANSFERABLE_STRONG
  adobe_aem: LIMITED_OR_NONE
  sitecore: LIMITED_OR_NONE
```

Custom CMS work includes content models, CRUD administration, admin dashboards, page and content management, media handling, categories and taxonomies, permissions, publishing workflows, catalog management, SEO fields, APIs, and database-backed content. Building these capabilities from scratch is direct CMS engineering, not an absence of CMS experience.

For general CMS or hands-on CMS questions, answer confidently from the direct experience. WordPress and Shopify are direct working experience. Headless and enterprise CMS concepts have strong transferable support from React, Next.js, API, database, admin-interface, and custom CMS architecture. Do not convert that capability into false AEM or Sitecore specialist claims.

Forced-choice answers are conjunctive: every material claim in the selected option must be supported. Do not treat an option that mentions `large-scale CMS solutions`, a `larger enterprise CMS environment`, multi-site or multi-language delivery, high-traffic CMS optimization, or an enterprise headless migration as a generic proxy for CMS depth. The current evidence does not establish those specific scale claims. Select the strongest lower option whose complete wording is true, then preserve the more precise custom-CMS depth in free text or the cover letter when the form permits it.

## Strongest-supported-answer policy

Resolve application questions in this order:

1. Search the canonical application answer bank.
2. Use an exact canonical fact.
3. Use the strongest truthful interpretation supported by career and project evidence.
4. Use a best-supported answer when the application requires interpretation.
5. When real experience exists but duration is imprecise, use a conservative floor-style estimate.
6. Use `MATERIAL_UNKNOWN` only when an answer would invent experience, credentials, legal status, or another unsupported material fact.

Store `EXACT`, `STRONGEST_SUPPORTED_ANSWER`, `DIRECT_DEEP`, `DIRECT_WORKING`, `TRANSFERABLE_STRONG`, `BEST_SUPPORTED_ANSWER`, `CONSERVATIVE_ESTIMATE`, or `MATERIAL_UNKNOWN` with confidence, interpretation, and supporting evidence. Positive evidence-backed statuses are resolved and application-ready.

For source-of-discovery questions, preserve the channel that actually surfaced the opportunity separately from the destination careers page and ATS host. Greenhouse, Lever, Recruitee, or another ATS is not the discovery source merely because it hosts the application. When a managed web search surfaced the listing but the search provider is not proven, use a truthful generic web-search or `Other` answer rather than inventing Google, LinkedIn, Indeed, or Greenhouse provenance.

Do not turn a senior engineer's direct implementation of an underlying capability into a weak answer merely because the job uses different terminology or a vendor name. Infer capabilities such as API design, relational data modeling, system architecture, technical leadership, consulting delivery, CI/CD, and agentic engineering from the documented work. Keep specific vendor, legal, credential, and exact-duration claims bounded by evidence.

Run `SENIOR_POSITIONING_REVIEW` on substantive answers and application writing. Rewrite `UNNECESSARY_UNDERSELL` before submission, and block `UNSUPPORTED_OVERCLAIM`. Lead with supported ownership using verbs such as built, designed, led, owned, architected, modernized, implemented, delivered, operated, and improved. Avoid eager-to-learn or limited-experience framing when stronger truthful capability evidence exists.

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

- work authorization and visa status for a jurisdiction not covered by the canonical facts below
- professional experience with a technology that has no actual implementation evidence
- management scope or exact team size
- degrees, certifications, clearance, or licenses not in the canonical CV
- backup-internet thresholds above 100 Mbps, exact provider names, detailed computer specifications, and backup-power requirements materially above the guaranteed eight-hour floor

Expected compensation is resolved by `docs/job-search/compensation-policy.md`; it is not grouped with unknown current salary.

## Citizenship, residence, and work authorization

Canonical application facts:

- Filipino citizen: `Yes`
- Citizenship country: `Philippines`
- Residence: `Dumaguete City, Negros Oriental, Philippines`
- Legally authorized to work in the Philippines: `Yes`
- Philippines employment sponsorship required: `No`
- Authorized to work in the United States: `No`
- United States work authorization applicability: `Not Applicable / located outside the US` when the control supports that answer

Residence and work authorization are separate facts. A Philippines question may be resolved automatically from this section. A United States yes/no authorization question is `No`; a status-style control that supports non-applicability should use `Not Applicable / located outside the US`. Do not generalize these facts to any other jurisdiction.

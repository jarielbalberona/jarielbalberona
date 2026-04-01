# jarielbalberona

Workspace for shaping `jarielbalberona.com` into a serious, low-maintenance, high-signal public engineering home.

This is not a generic portfolio project. The site is intended to present a senior software engineer who builds production systems across product, architecture, and delivery, and uses AI as disciplined workflow leverage rather than branding theater.

## Public Profile Summary

I build production systems that stay healthy as they grow.

Senior software engineer focused on maintainability, scalability, architecture, reliability, and predictable delivery. I build production-ready platforms across frontend, backend, and infrastructure.

What I do best:

- Designing maintainable React and TypeScript systems with strong state, data, and UI structure
- Building APIs, workflows, and data flows with Node.js and PostgreSQL
- Shipping across CI/CD, infrastructure, and practical cloud delivery
- Keeping systems healthy under growth instead of letting delivery quality decay

Selected public work:

- Dumadine: multi-tenant cafe operating system built around real operating workflows rather than demo-only surfaces
- Privv: frontend and system architecture work focused on maintainability, scalable structure, and codebase health
- DataGPT AI: product work focused on reliability, recovery flows, orchestration UI, and analytics UX

Links:

- Site: [jarielbalberona.com](https://jarielbalberona.com)
- LinkedIn: [jarielbalberona](https://www.linkedin.com/in/jarielbalberona/)
- Email: [jarielbalb@gmail.com](mailto:jarielbalb@gmail.com)
- Live product: [dumadine.com](https://dumadine.com/)

## Workspace Structure

- [`AGENTS.md`](/Volumes/Files/softwareengineering/my-projects/jarielbalberona/AGENTS.md): workspace operating manual
- [`docs/`](/Volumes/Files/softwareengineering/my-projects/jarielbalberona/docs): lean planning records, decisions, and roadmap
- [`portfolio/`](/Volumes/Files/softwareengineering/my-projects/jarielbalberona/portfolio): canonical public site app

## Current Direction

MVP pages:

- Home
- Now
- Work
- Workflow
- Contact

Notes/blog is intentionally deferred until there is a realistic publishing cadence and enough material to justify it.

## Technical Stance

`/portfolio` is the public-site implementation authority.

Official stack for `/portfolio`:

- Astro
- TypeScript
- Tailwind CSS v4
- Astro content collections
- Render Static Site deployment

Explicit exclusions for MVP:

- no `shadcn`
- no CMS
- no database
- no unnecessary client-heavy architecture

The previous plain-static stopgap is no longer the source of truth.

## Working Rules

- Public site implementation lives under `portfolio/`
- Root-level files should exist only if they help planning, content, or project continuity
- Direct commits to `main` are allowed unless explicitly told otherwise
- Preserve anything useful, but remove stale or weak direction when it actively hurts the project

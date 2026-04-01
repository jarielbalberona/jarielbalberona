# jarielbalberona

Workspace for shaping `jarielbalberona.com` into a serious, low-maintenance, high-signal public engineering home.

This is not a generic portfolio project. The site is intended to present a senior software engineer who builds and modernizes production systems, works across product, architecture, and delivery, and uses AI as disciplined workflow leverage rather than branding theater.

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

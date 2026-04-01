# jarielbalberona

Workspace for shaping `jarielbalberona.com` into a serious, low-maintenance, high-signal public engineering home.

This is not a generic portfolio project. The site is intended to present a senior software engineer who builds and modernizes production systems, works across product, architecture, and delivery, and uses AI as disciplined workflow leverage rather than branding theater.

## Workspace Structure

- [`AGENTS.md`](/Volumes/Files/softwareengineering/my-projects/jarielbalberona/AGENTS.md): workspace operating manual
- [`docs/`](/Volumes/Files/softwareengineering/my-projects/jarielbalberona/docs): lean planning records, decisions, and roadmap
- [`portfolio/`](/Volumes/Files/softwareengineering/my-projects/jarielbalberona/portfolio): static public site app

## Current Direction

MVP pages:

- Home
- Now
- Work
- Workflow
- Contact

Notes/blog is intentionally deferred until there is a realistic publishing cadence and enough material to justify it.

## Technical Stance

The current implementation uses a small static site in `portfolio/`.

Reason:

- the workspace had no usable site app
- there is no local Node or package-manager toolchain installed
- the project benefits more from shipping a clean, maintainable foundation than from introducing framework overhead

This can move to Astro later if there is a good reason. It should not move just to look modern.

## Working Rules

- Public site implementation lives under `portfolio/`
- Root-level files should exist only if they help planning, content, or project continuity
- Direct commits to `main` are allowed unless explicitly told otherwise
- Preserve anything useful, but remove stale or weak direction when it actively hurts the project

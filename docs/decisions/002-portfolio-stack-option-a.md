# ADR 002: Option A Is The Canonical Portfolio Stack

## Status

Accepted

## Decision

`/portfolio` uses the following stack from this point forward:

- Astro
- TypeScript
- Tailwind CSS v4
- Astro content collections
- Render Static Site deployment

`/portfolio` is the implementation authority for the public site.

## Explicit Exclusions For MVP

- no `shadcn`
- no CMS
- no database
- no unnecessary client-heavy architecture

## Why This Wins

- keeps the site static and low-maintenance
- gives the project a real component and content model instead of duplicated HTML
- supports typed structured content for selected work and future notes
- keeps deployment simple on Render Static Sites
- avoids the bloat and vagueness of more app-like setups

## Consequences

- old static HTML under `/portfolio` should be replaced, not treated as a parallel implementation path
- docs and workspace guidance must point to this stack consistently
- content should move into Astro pages and content collections

## Rejected Alternatives

- Keeping the plain static HTML MVP as the long-term implementation: rejected because it creates avoidable duplication and leaves the repo in an in-between state
- Next.js: rejected because the project does not need app-level complexity for MVP
- shadcn: rejected because it would push the site toward generic component-library aesthetics and unnecessary setup

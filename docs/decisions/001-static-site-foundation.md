# ADR 001: Static Site Foundation For MVP

## Status

Superseded by ADR 002

## Decision

Use a small static multi-page site under `portfolio/` for the MVP foundation.

## Context

This decision reflected the repo state at the time:

- the workspace was nearly empty
- no usable app existed under `portfolio/`
- no `node`, `npm`, or `pnpm` toolchain was available locally
- the site needed a credible foundation more than framework sophistication

## Why It Was Chosen Then

- lowest maintenance burden
- no dependency on missing toolchains
- easy to host anywhere static files are supported
- enough structure for a strong MVP without fake complexity

## Why It No Longer Governs

The project direction has changed.

`/portfolio` now has an explicit approved stack:

- Astro
- TypeScript
- Tailwind CSS v4
- Astro content collections
- Render Static Site deployment

That newer decision is recorded in ADR 002 and replaces this file as the technical source of truth.

## Consequences

- keep this document only as historical context
- do not use this ADR to justify new static HTML implementation work

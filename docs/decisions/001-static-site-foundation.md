# ADR 001: Static Site Foundation For MVP

## Status

Accepted

## Decision

Use a small static multi-page site under `portfolio/` for the MVP foundation.

## Context

At implementation start:

- the workspace was nearly empty
- no usable app existed under `portfolio/`
- no `node`, `npm`, or `pnpm` toolchain was available locally
- the site needed a credible foundation more than framework sophistication

## Why This Wins

- lowest maintenance burden
- no dependency on missing toolchains
- easy to host anywhere static files are supported
- enough structure for a strong MVP without fake complexity

## Why Not Astro Right Now

Astro is a sensible future option, but not the right first move in this workspace state.

Reasons:

- local environment does not currently support the normal Astro workflow
- adding framework setup now would slow delivery and add operational noise
- the current scope does not require framework-level complexity

## Consequences

- content is authored directly in static HTML for MVP
- structure must stay disciplined to avoid duplication drift
- migration to Astro later remains possible if content volume or component reuse justifies it

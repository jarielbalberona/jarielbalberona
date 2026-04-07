# jarielbalberona.com

This is the workspace and canonical public site app for `jarielbalberona.com`.

The site is intended to present a senior software engineer who builds production systems across product, architecture, and delivery, and uses AI as disciplined workflow leverage rather than branding theater.

## Source Of Truth Stack

- Astro
- TypeScript
- Tailwind CSS v4
- Astro content collections
- Railway static deployment

## MVP Rules

- no `shadcn`
- no CMS
- no database
- no unnecessary client-heavy architecture
- no generic portfolio filler

## Purpose

This app exists to present:

- production software work
- modernization capability
- current real work
- selected proof
- pragmatic engineering workflow
- disciplined AI-assisted engineering workflow

## Workspace Structure

- `../AGENTS.md`: workspace operating manual
- `../docs/`: lean planning records, decisions, and roadmap
- `src/`: canonical public site app source code

## Railway Static Deployment

Railway deploys this Astro site as a static site through Railpack.

Expected Railway settings:

- Root Directory: `/portfolio`
- Config File Path: `/portfolio/railway.toml`

Railway's config-as-code defaults to `railway.toml` or `railway.json`, not `railway.yaml`. Do not add a YAML file here unless Railway adds support for it later.

This app is static by default, so no server adapter is required for MVP.

## Analytics

Google Analytics is optional and disabled unless a GA4 Measurement ID is provided.

Set this environment variable in Railway when analytics should be active:

- `PUBLIC_GA_MEASUREMENT_ID`: GA4 Measurement ID, for example `G-XXXXXXXXXX`

## Working Rules

- Root-level files should exist only if they help planning, content, or project continuity
- Direct commits to `main` are allowed unless explicitly told otherwise
- Preserve anything useful, but remove stale or weak direction when it actively hurts the project

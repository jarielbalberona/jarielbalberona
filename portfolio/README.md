# jarielbalberona.com

This is the workspace and canonical public site app for `jarielbalberona.com`.

The site is intended to present a senior software engineer who builds production systems across product, architecture, and delivery, and uses AI as disciplined workflow leverage rather than branding theater.

## Source Of Truth Stack

- Astro
- TypeScript
- Tailwind CSS v4
- Astro content collections
- Render Static Site deployment

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

## Render Static Site

The repo-level Render blueprint lives at `/render.yaml` (workspace root).

Expected Render settings:

- Root Directory: `portfolio`
- Build Command: `npm ci && npm run build`
- Publish Directory: `dist`

This app is static by default, so no server adapter is required for MVP.

## Working Rules

- Root-level files should exist only if they help planning, content, or project continuity
- Direct commits to `main` are allowed unless explicitly told otherwise
- Preserve anything useful, but remove stale or weak direction when it actively hurts the project
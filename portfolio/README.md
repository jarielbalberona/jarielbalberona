# portfolio

Canonical public site app for `jarielbalberona.com`.

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

## Render Static Site

The repo-level Render blueprint lives at [`/render.yaml`](/Volumes/Files/softwareengineering/my-projects/jarielbalberona/render.yaml).

Expected Render settings:

- Root Directory: `portfolio`
- Build Command: `npm ci && npm run build`
- Publish Directory: `dist`

This app is static by default, so no server adapter is required for MVP.

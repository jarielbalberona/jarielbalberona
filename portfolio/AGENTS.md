# AGENTS.md

This file adds app-specific rules for `/portfolio`.

The root workspace rules still apply. This file narrows them for the public site implementation.

## Purpose

`/portfolio` contains the actual public site app for `jarielbalberona.dev`.

This app should stay:

- small
- maintainable
- content-led
- free of generic portfolio patterns

## Implementation Rules

- The approved stack is Astro, TypeScript, Tailwind CSS v4, and Astro content collections.
- Render Static Site is the deployment target.
- Do not introduce competing stack ambiguity.
- Do not add client-side JavaScript unless it solves a real problem.
- Use Astro pages, layouts, and content collections to keep the site structured and maintainable.
- Use abstraction where it removes duplication cleanly. Do not build component systems for vanity.

## Design Rules

- The visual direction should feel sharp and restrained.
- Avoid startup landing page clichés.
- Avoid giant hero fluff, card spam, and decorative metrics.
- Typography and spacing should carry most of the design.
- Motion is optional and should stay minimal.

## Content Rules

- Every section must earn its place.
- Prefer fewer stronger statements over more weaker ones.
- Do not add placeholder testimonials, fake metrics, or filler project cards.
- The `Work` page should favor depth over quantity.
- The `Workflow` page should explain engineering judgment, not tool fandom.
- Keep the implementation authority in `/portfolio`, not in root-level docs or stray static files.

## Page Rules

MVP pages:

- `Home`
- `Work`
- `AI-Native Engineering`
- `Now`
- `Contact`

Do not add `About`, `Uses`, `Speaking`, or a public notes index unless the content is real and ready.

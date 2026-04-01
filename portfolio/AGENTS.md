# AGENTS.md

This file adds app-specific rules for `/portfolio`.

The root workspace rules still apply. This file narrows them for the public site implementation.

## Purpose

`/portfolio` contains the actual public site app for `jarielbalberona.com`.

This app should stay:

- small
- static
- maintainable
- content-led
- free of generic portfolio patterns

## Implementation Rules

- Prefer plain static HTML and shared CSS unless a stronger implementation need appears.
- Do not add JavaScript unless it solves a real problem.
- Do not introduce framework tooling just to appear modern.
- Keep pages readable as standalone documents.
- Reuse shared structure where practical, but do not build abstraction for its own sake.

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

## Page Rules

MVP pages:

- `Home`
- `Now`
- `Work`
- `Workflow`
- `Contact`

Do not add `About`, `Uses`, `Speaking`, or a public notes index unless the content is real and ready.

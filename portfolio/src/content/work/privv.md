---
title: PRIVV
summary: Product engineering work for a capital project platform with complex financial workflows, dense planning interfaces, and high trust requirements around system behavior.
status: Selected work
timeframe: Product platform work
featured: true
order: 2
liveUrl: https://www.privv.ai/
role: Frontend and product engineering on high-trust planning workflows
stack:
  - React
  - TypeScript
  - Design tokens
  - Frontend architecture
highlights:
  - Improved frontend structure for a platform supporting more than $4B in capital project workflows.
  - Reworked state and data flow across budgets, schedules, invoicing, and forecasting views with high interaction complexity.
  - Strengthened UI structure and interaction behavior so complex financial workflows stayed usable and maintainable under growth.
context: A capital project platform with dense planning, budgeting, forecasting, and invoicing workflows where trust in system behavior matters.
ownership:
  - Frontend and product engineering across complex financial planning interfaces
  - UI structure and state handling for dense, high-interaction workflows
  - Maintainability and usability improvements as workflow complexity increased
constraints:
  - High-trust financial workflows with low tolerance for confusing behavior
  - Dense tables, planning views, and forecasting interactions
  - Growing product complexity that could easily collapse into frontend sprawl
changes:
  - Reworked frontend structure to better support large, interdependent planning surfaces
  - Improved state and data flow across budgeting, scheduling, invoicing, and forecasting views
  - Strengthened the product foundation so more complexity could be added without repeated churn
impact: The engineering value was making a complex planning product more legible and maintainable as it scaled, instead of letting workflow density turn into permanent frontend drag.
---

## Context

PRIVV is a capital project platform for budgeting, scheduling, procurement, invoicing, and forecasting across large construction and infrastructure programs.

My work focused on making the product hold up under growing workflow complexity. That meant building structure for dense financial views, large interactive tables, and forecasting workflows without letting the UI collapse into state and component sprawl.

## What I owned

- Frontend and product engineering on planning and financial workflow surfaces
- Structure for component, state, and interaction behavior under heavy workflow density
- Maintainability work that kept future product changes from becoming increasingly expensive

## Technical constraints

In products like this, system trust depends heavily on behavior clarity. Weak state structure and inconsistent workflow handling do not stay isolated. They spread, slow down development, and make already-complex planning and financial work harder to use and maintain.

## What I changed

The core work was strengthening the product foundation so the system could expand without repeated churn in its state and UI layers.

That foundation had to support demanding planning and financial workflows across university, healthcare, and municipal construction environments, where complexity was already high and the tolerance for fragile software was low.

- Improved structure around budgeting, scheduling, invoicing, and forecasting views
- Reduced the risk of repeated UI churn by making the underlying frontend easier to reason about
- Focused on making the product understandable and usable under real planning complexity

## Why it mattered

When products like this become harder to trust, users feel it immediately. The engineering work mattered because it kept complex financial workflows usable while preserving a codebase that could continue to evolve.

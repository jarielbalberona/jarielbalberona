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
  - Vite
  - Tailwind CSS v4
  - TanStack Query
  - Zustand
highlights:
  - Improved frontend structure for a platform supporting more than $4B in capital project workflows.
  - Reworked state and data flow across budgets, schedules, invoicing, and forecasting workflows with high interaction complexity.
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
impact: Made a dense planning product easier to evolve without letting financial workflow complexity turn into permanent frontend drag.
---

## Context

PRIVV is a capital project platform for budgeting, scheduling, procurement, invoicing, and forecasting across large construction and infrastructure programs. My work focused on making the product hold up under growing workflow complexity without collapsing into state and component sprawl.

## What I owned

- Frontend and product engineering on planning and financial workflow surfaces
- Structure for component, state, and interaction behavior under heavy workflow density
- Maintainability work that kept future product changes from becoming increasingly expensive

## Technical constraints

In products like this, trust depends heavily on behavior clarity. Weak state structure and inconsistent workflow handling spread fast, slow down development, and make already-complex planning work harder to use.

## What I changed

The core work was strengthening the frontend foundation so the system could expand without repeated churn in its state and UI layers. That foundation had to support demanding planning and financial workflows across university, healthcare, and municipal construction environments where fragile behavior was not acceptable.

- Improved structure around budgeting, scheduling, invoicing, and forecasting views
- Reduced the risk of repeated UI churn by making the underlying frontend easier to reason about
- Focused on making the product understandable and usable under real planning complexity

## Why it mattered

The value was keeping complex financial workflows usable while preserving a codebase that could continue to evolve under pressure.

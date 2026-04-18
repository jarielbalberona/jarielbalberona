---
title: Dumadine
summary: Multi-tenant hospitality operating system built for live venue conditions, event-driven workflows, and future automation and AI-assisted operational support.
status: Featured project
timeframe: Current work
featured: true
order: 1
liveUrl: https://dumadine.com/
role: Founder-led product engineering, architecture, and system design
stack:
  - TypeScript
  - React
  - Node.js
  - PostgreSQL
  - Drizzle ORM
  - WebSockets
  - AWS
highlights:
  - Built as an operational system that keeps ordering, kitchen activity, stock movement, and accounting behavior connected in real time.
  - Designed around modular domains and event-driven flow so automation and reporting can be added without collapsing boundaries.
  - Built the system shape needed for reporting, operator summaries, and downstream automation from live product state.
context: A multi-tenant hospitality operating system shaped around live venue operations rather than isolated software features.
ownership:
  - Product architecture across ordering, kitchen flow, inventory, accounting, and venue operations
  - Backend and data-flow design for connected operational state
  - System structure that leaves room for reporting, automation, and AI-assisted operator tooling
constraints:
  - Live-service pressure, shared devices, and real venue workflows
  - Domain boundaries that cannot collapse into feature sprawl
  - Real-time coordination without turning the product into state chaos
changes:
  - Structured the product around coherent operational state instead of disconnected screens
  - Preserved modular domains so downstream automation and reporting can remain trustworthy
  - Built the foundation for summaries, support context, and event-driven follow-on workflows
impact: Built an operational core that can support reporting, automation, and operator tooling from one source of truth instead of a patchwork of side systems.
---

## Context

Dumadine is a multi-tenant hospitality operating system designed around live venue work, not a demo-friendly feature list. Ordering, kitchen flow, stock movement, merchant operations, and accounting all need to stay connected if the product is going to hold up during service.

## What I owned

- Product and system architecture across the major operating domains
- Backend and data-flow decisions that keep those domains connected without losing boundaries
- The technical shape that makes future automation, reporting, and AI-assisted support possible

## Technical constraints

Hospitality systems usually fail under pressure, not in polished demos. The real constraint set is service rushes, stock movement, kitchen timing, shared devices, unreliable connectivity, and downstream financial effects when the operational flow breaks.

## What I changed

The product is shaped against a live cafe environment in the Philippines. That matters because it forces the system to deal with actual service-hour pressure, inconsistent connectivity, shared devices, and the gap between ideal product flows and how venues really operate.

- Kept ordering, kitchen, inventory, and accounting flows tied to the same operational picture
- Designed modular boundaries so reporting and automation can be added downstream without distorting the core product
- Built toward event-driven workflows and operator-facing system explanation instead of bolting them on later

## Why it mattered

The stack spans TypeScript, React, Node.js, PostgreSQL, WebSockets, and AWS. The harder problem is preserving clear boundaries across ordering, inventory, accounting, and venue management while keeping the product operationally consistent in real time.

That means designing for:
- modular domain ownership instead of feature sprawl
- real-time coordination without state chaos
- changeability without cross-domain leakage
- observability and failure handling that hold up in production

This foundation enables the next layer:
- event-driven automation workflows
- reporting systems that explain operational behavior
- AI-generated summaries for operators
- decision-support tooling based on live system state

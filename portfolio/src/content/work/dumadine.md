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
  - Drizzle
  - WebSockets
  - AWS
highlights:
  - Built as an operational system that keeps ordering, kitchen activity, stock movement, and accounting behavior connected in real time.
  - Designed around modular domains and event-driven flow so automation and reporting can be added without collapsing boundaries.
  - Creates a foundation for AI-generated summaries, operational explanation, and decision support tied to actual system activity.
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
impact: The product becomes more than a POS-style interface. It becomes an operational system that can support automation, reporting, and decision support without inventing a second truth layer outside the app.
---

## Context

Dumadine is a multi-tenant hospitality operating system designed to replace the fragmented stack many venues still rely on. The point is not just consolidating features. The point is keeping operational activity coherent across ordering, kitchen flow, stock movement, merchant workflows, and accounting.

That means treating the product as a system of connected operational state rather than a pile of adjacent screens.

## What I owned

- Product and system architecture across the major operating domains
- Backend and data-flow decisions that keep those domains connected without losing boundaries
- The technical shape that makes future automation, reporting, and AI-assisted support possible

## Technical constraints

Hospitality systems do not usually fail because a menu renders badly. They fail when service gets messy.

The real engineering problem is handling service rushes, stock movement, kitchen timing, unreliable connectivity, and downstream financial impact without pushing staff into brittle manual workarounds. That is where product quality stops being a UI problem and becomes a systems problem.

## What I changed

The product is shaped against a live cafe environment in the Philippines. That matters because it forces the system to deal with actual service-hour pressure, inconsistent connectivity, shared devices, and the gap between ideal product flows and how venues really operate.

- Kept ordering, kitchen, inventory, and accounting flows tied to the same operational picture
- Designed modular boundaries so reporting and automation can be added downstream without distorting the core product
- Built toward event-driven workflows and operator-facing system explanation rather than bolting them on later

This is not a demo-shaped system. It is being pushed against operational reality.

## Why it mattered

The stack spans TypeScript, React, Node.js, PostgreSQL, WebSockets, and AWS. The harder problem is not the stack itself. It is preserving clear boundaries across ordering, inventory, accounting, and venue management while keeping the product operationally consistent in real time.

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

This is not AI added on top. The system is designed so automation and AI become natural extensions, not forced features.

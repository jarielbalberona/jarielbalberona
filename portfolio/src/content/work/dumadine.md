---
title: Dumadine
summary: Multi-tenant hospitality operating system built for live venue conditions, event-driven workflows, and future automation and AI-assisted operational support.
status: Featured project
timeframe: Current work
featured: true
order: 1
liveUrl: https://dumadine.com/
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
---

## What it is

Dumadine is a multi-tenant hospitality operating system designed to replace the fragmented stack many venues still rely on. The point is not just consolidating features. The point is keeping operational activity coherent across ordering, kitchen flow, stock movement, merchant workflows, and accounting.

That means treating the product as a system of connected operational state rather than a pile of adjacent screens.

## Why it matters

Hospitality systems do not usually fail because a menu renders badly. They fail when service gets messy.

The real engineering problem is handling service rushes, stock movement, kitchen timing, unreliable connectivity, and downstream financial impact without pushing staff into brittle manual workarounds. That is where product quality stops being a UI problem and becomes a systems problem.

## Operating context

The product is shaped against a live cafe environment in the Philippines. That matters because it forces the system to deal with actual service-hour pressure, inconsistent connectivity, shared devices, and the gap between ideal product flows and how venues really operate.

This is not a demo-shaped system. It is being pushed against operational reality.

## Technical shape

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

---
title: Dumadine
summary: Multi-tenant hospitality system built for live venue operations across ordering, kitchen flow, inventory, and accounting.
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
  - Unifies POS, QR ordering, kitchen operations, inventory, and accounting in one browser-based product.
  - Supports different venue models across cafes, hotels, and workspaces without splitting the platform into separate forks.
  - Built around modular domains, real-time workflows, and production observability needed for ongoing operational change.
---

## What it is

Dumadine is a multi-tenant hospitality system designed to replace the fragmented software stack many venues still rely on. Instead of stitching together separate tools for POS, kitchen coordination, stock tracking, accounting, and ordering, the goal is one system that keeps those workflows connected and operationally consistent.

The product spans:
- **POS and QR ordering:** Browser-based ordering and payment flows without tying the system to proprietary hardware.
- **Dynamic venue modeling:** A shared core architecture that can adapt across cafes, hotels, and workspace-style operations.
- **Kitchen display system:** Real-time coordination built for live service, not delayed back-office visibility.
- **Inventory and costing:** Recipe-aware stock tracking with deductions tied directly to sales activity.
- **Accounting subledger:** Journal generation and cost tracking that connect operational activity to finance workflows.

## Why it matters

Hospitality systems do not usually fail on basic ordering. They fail when operations get messy.

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

---
title: Dumadine
summary: Multi-tenant hospitality system unifying ordering, kitchen operations, inventory, and accounting around the realities of live venue workflows.
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
  - Consolidates browser-based POS, QR ordering, kitchen operations, inventory, and accounting workflows into one system.
  - Supports different venue models across cafes, hotels, and workspaces without forking the core product shape.
  - Built around modular domains, real-time state flow, and observability required for ongoing production changes.
---

## What it is

Dumadine is a multi-tenant hospitality system built to replace the fragmented operating stack many venues still depend on. Instead of separate tools for POS, kitchen flow, stock tracking, accounting, and ordering, the goal is a single browser-based system that keeps those workflows connected.

The system spans:
- **POS and QR ordering:** Browser-based ordering and payment flows without locking the product to proprietary hardware.
- **Dynamic venue modeling:** Shared core architecture that can shift between cafes, hotels, and workspace-style operations.
- **Kitchen display system:** Real-time orchestration for live service instead of delayed back-office reporting.
- **Inventory and costing:** Recipe-aware stock tracking with automated deductions tied to actual sales.
- **Accounting subledger:** Journal generation and cost tracking that connect operational activity to finance workflows.

## Why it matters

Hospitality software breaks where operations get messy. Taking an order is the easy part. The real engineering work is handling service rushes, stock changes, kitchen timing, network instability, and downstream accounting without forcing staff into brittle manual workarounds.

## Working model

The product is shaped against a live cafe environment in the Philippines. That forces the architecture to deal with service-hour pressure, inconsistent connectivity, device variability, and the mismatch between clean product flows and actual floor operations.

## Technical shape

The stack spans TypeScript, React, Node.js, PostgreSQL, WebSockets, and AWS. The harder part is keeping ordering, inventory, accounting, and venue-management concerns separated enough to evolve independently while still behaving like one product in production.

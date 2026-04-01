---
title: Dumadine
summary: Multi-tenant hospitality OS consolidating POS, KDS, inventory, accounting, and ordering into one architecture, built around live physical workflows.
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
  - Consolidates hardware-agnostic POS, live KDS, inventory, and automated accounting subledgers into a single system.
  - Dynamically adapts operational models across cafes (tables), hotels (rooms), and workspaces (desks).
  - Built with strict modularity and observability to survive iterative changes in a production environment.
---

## What it is

Dumadine is a multi-tenant hospitality operating system. It replaces the fragmented stack of legacy venues (separate POS, inventory, accounting, and loyalty tools) with a single connected architecture that runs on any device via the browser.

The system spans:
- **Hardware-agnostic POS & QR Ordering:** Real-time state sync without proprietary terminals.
- **Dynamic Venue Modeling:** Adapts workflows and terminology for cafes, hotels, and workspaces.
- **Kitchen Display System (KDS):** Live Kanban orchestration designed for service speed.
- **Inventory & Costing:** Tracks recipes, manages suppliers, and auto-deducts stock via sales.
- **Accounting Subledger:** Auto-generates journal entries, tracks COGS, and exports directly to Xero/QuickBooks.

## Why it matters

This domain exposes whether system design survives contact with physical operations. Demoing a QR order is trivial; the actual engineering challenge is orchestrating kitchen flow, real-time stock deduction, automated financial ledgers, and hardware-agnostic edge cases. 

## Working model

The product is shaped alongside a live physical cafe in the Philippines. This forces the architecture to handle grounded, real-world constraints—like spotty network states and chaotic service hours—rather than theoretical startup requirements.

## Technical shape

The stack spans TypeScript, Node.js, React, PostgreSQL, WebSockets, and AWS. The engineering signal is the execution: maintaining strict domain boundaries across complex accounting and inventory modules, embedding deep observability, and delivering reliable updates while the system adapts to live operational feedback.

---
title: Dumadine
summary: Multi-tenant cafe operating system built around live workflows, real-time coordination, and the friction points of physical operations.
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
  - Docker
  - Terraform
  - AWS
highlights:
  - Consolidates customer ordering, merchant dashboards, POS, kitchen displays, and inventory into one cohesive architecture.
  - Shaped entirely by live operational constraints rather than theoretical product briefs.
  - Built with strict modularity and observability to survive iterative changes in a production environment.
---

## What it is

Dumadine is a multi-tenant cafe operating system in early beta. The architecture covers the full operational footprint, extending far beyond basic customer ordering.

The system spans:
- QR ordering with real-time state synchronization
- Merchant dashboard, POS, shift management, and cash-drawer workflows
- Kitchen display system with live ticket updates
- Complex menu schemas (items, modifiers, variants, templates)
- Inventory engine tracking recipes, stock limits, and sales-linked decrements

## Why it matters

This domain exposes whether system design survives contact with physical operations. Demoing an order is trivial; the actual engineering challenge is orchestrating kitchen flow, stock behavior, cash handling, and the operational edge cases that cost money when ignored.

## Working model

The product is built alongside a live cafe environment in the Philippines. This forces the architecture to handle grounded, real-world constraints rather than theoretical startup requirements.

## Technical shape

The stack spans TypeScript, Node.js, React, PostgreSQL, WebSockets, Docker, Terraform, and AWS. The signal is not the tooling, but the execution: maintaining strict domain boundaries, embedding deep observability, and delivering reliable updates while the system adapts to live feedback.

---
title: Dumadine
summary: Multi-tenant cafe operating system in early beta, shaped around real operating workflows, real-time coordination, and the delivery concerns that show up once software meets daily operations.
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
  - Customer ordering, merchant dashboard, POS flow, kitchen display, menu management, inventory behavior, and delivery concerns live in one system.
  - The product is shaped with real operating input instead of a made-up product brief.
  - The engineering problem is keeping the system modular, observable, and reliable while the product is still learning from operations.
---

## What it is

Dumadine is a multi-tenant cafe operating system in early beta. The public shape is broader than customer ordering because the operating problem is broader than customer ordering.

The system spans:

- QR customer ordering with real-time status updates
- Merchant dashboard, POS, shifts, and cash-drawer workflows
- Kitchen display system with live ticket updates
- Menu structure for items, modifiers, variants, and templates
- Inventory support for recipes, stock, suppliers, and sales-linked decrements
- Loyalty support for points and stamps

## Why it matters

This is the kind of product that exposes whether the engineering can survive contact with operations.

Ordering is easy to demo. The harder work is the ugly middle layer: kitchen flow, stock behavior, cash handling, edge cases, observability, and the seams that start costing money when they are ignored.

## Working model

I am shaping the product in close contact with a local cafe environment in the Philippines. That matters because it keeps requirements grounded and removes a lot of fake-product thinking.

## Technical shape

The current stack includes TypeScript, React, Node.js, Express, PostgreSQL, Drizzle, WebSockets, Docker, Terraform, and AWS-level deployment patterns.

The stack is not the signal by itself. The useful part is the engineering shape around it: keeping boundaries clean enough to evolve the product, adding observability where it matters, and maintaining delivery quality while the system is still being refined through real-world use.

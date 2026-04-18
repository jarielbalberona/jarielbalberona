---
title: DataGPT AI
summary: Product engineering for an analytics system where AI-assisted workflows, data flow clarity, and trust in system behavior mattered as much as raw capability.
status: Selected work
timeframe: Product workflow work
featured: true
order: 3
liveUrl: https://www.linkedin.com/company/datagpt-analytics/
role: Product engineering on analytics and AI-assisted workflow surfaces
stack:
  - React
  - TypeScript
  - Data visualization
  - Analytics UX
highlights:
  - Built interfaces that made query flow, result state, and AI-assisted analysis easier to follow and verify.
  - Designed orchestration UI that surfaced pipeline state, failure conditions, and recovery paths clearly.
  - Treated explanation and trust in outputs as product requirements, not cosmetic analytics UX.
context: An analytics product where AI-assisted workflows only work if users can understand query flow, result state, failures, and recovery paths.
ownership:
  - Product engineering across orchestration and analysis interfaces
  - UX structure for pipeline state, result explanation, and recovery behavior
  - Trust-oriented design for AI-assisted output flows
constraints:
  - Opaque workflow behavior quickly destroys user trust
  - Complex pipeline state has to be visible enough for users to act on it
  - AI-assisted output needs explanation, not just presentation
changes:
  - Built interfaces that made query progress, result state, and pipeline behavior legible
  - Surfaced failure and recovery states instead of hiding them behind generic loading behavior
  - Treated explanation and trust as core product requirements
impact: Improved trust in the product by making pipeline state, recovery paths, and AI-assisted outputs easier to inspect and verify.
---

## Context

DataGPT is an analytics product built around AI-assisted query workflows. My work focused on making orchestration and analysis legible enough for users to follow, trust, and recover from when things went wrong.

## What I owned

- Product engineering on orchestration and result interfaces
- Workflow visibility for query state, failures, and recovery
- UX decisions that made AI-assisted analysis more understandable and auditable

## Technical constraints

In analytics products, trust breaks when users cannot tell what the system is doing. If result generation feels opaque, recovery is unclear, or failures disappear behind generic loading states, the product starts to feel unreliable fast.

## What I changed

The core challenge was making complex workflow state legible through the UI. That required strong state handling, clear interaction design, and visualization choices that made AI-assisted analysis understandable instead of black-boxed.

- Exposed pipeline state and failure conditions more clearly
- Improved the legibility of AI-assisted analysis and query flow
- Treated operational explanation as part of the product, not a cosmetic layer

## Why it mattered

This work mattered because it focused on explanation, state visibility, and recovery instead of pretending output quality alone was enough.

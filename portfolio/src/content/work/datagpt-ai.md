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
  - Treated explanation and trust in outputs as product requirements instead of decorative analytics UX.
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
impact: The work improved the product’s ability to explain itself, which is essential in analytics systems where users need to trust both the result and the path that produced it.
---

## Context

DataGPT is a data analytics platform aimed at making complex data exploration easier through AI-assisted query workflows.

My work focused on turning orchestration and analysis into a system users could actually follow. That meant showing how a request moved through the pipeline, what state it was in, when it failed, and what the user could do next.

## What I owned

- Product engineering on orchestration and result interfaces
- Workflow visibility for query state, failures, and recovery
- UX decisions that made AI-assisted analysis more understandable and auditable

## Technical constraints

In analytics products, trust breaks when users cannot tell what the system is doing. If result generation feels opaque, recovery is unclear, or failures are hidden behind generic loading states, the product quickly starts to feel unreliable.

This work treated visibility into data flow, orchestration behavior, and AI-assisted output generation as a core product requirement, not just a technical detail.

## What I changed

The core challenge was making complex workflow state legible through the UI. That required strong state handling, clear interaction design, and visualization choices that made AI-assisted analysis feel understandable instead of black-boxed.

The point was not just to return results. It was to make users trust the path that produced them, and to make the system explain itself well enough that users could act on the output with confidence.

- Exposed pipeline state and failure conditions more clearly
- Improved the legibility of AI-assisted analysis and query flow
- Treated operational explanation as part of the product, not a cosmetic layer

## Why it mattered

Analytics software becomes weak fast when users cannot tell whether to trust it. This work mattered because it focused on explanation, state visibility, and recovery instead of pretending output quality alone was enough.

# Workflow

## Use AI to reduce drag. Keep engineering judgment and accountability human.

I use AI heavily in day-to-day engineering work, but within a disciplined workflow. It helps me move faster through exploration, drafting, refactoring, and implementation support. It does not own architecture, correctness, or production responsibility. I do.

## 1. Understand the system

### Read before changing

I start by inspecting the current code, constraints, and failure modes. Most bad engineering decisions come from acting on assumptions instead of reality.

That means understanding:

- what already exists
- what is actually broken
- what the real scope is
- what should stay untouched

I do not treat speed as an excuse to skip system understanding.

## 2. Define the change

### Reduce ambiguity before execution

Before implementation, I narrow the problem, expose tradeoffs, and define what success actually means. This prevents movement without direction, which is where a lot of engineering waste starts.

The goal here is simple:

- clear scope
- explicit boundaries
- known risks
- fewer hidden surprises later

## 3. Execute in small, isolated units

### One change, one scope, one outcome

I prefer ticket-driven execution with isolated branches or worktrees, especially when using AI coding agents. Each change should have a clear purpose, minimal blast radius, and an obvious verification path.

This keeps delivery controlled instead of chaotic:

- scoped work instead of vague "cleanup"
- isolated implementation instead of overlapping edits
- traceable progress instead of hidden churn

AI helps accelerate execution, but the workflow stays structured.

## 4. Verify aggressively

### Fast is useless if the result is wrong

I treat verification as part of implementation, not as a final courtesy. Type safety, runtime behavior, edge cases, integration impact, and stale assumptions all need to be checked.

My default mindset is:

- verify the current state first
- implement narrowly
- verify again after the change
- clean up dead code and drift when needed

A change is not done because code was written. It is done when it holds up under scrutiny.

## 5. Review for long-term survivability

### Ship work that the codebase can survive

I care less about cleverness and more about whether the system remains maintainable under real product pressure. Good delivery is not just feature output. It is preserving clarity, ownership, and reliability while moving forward.

That means constantly asking:

- does this strengthen or weaken boundaries?
- does this reduce or increase future maintenance cost?
- does this make the system easier or harder to reason about?
- are we solving the real problem or creating a bigger one later?

## Where AI helps

### Acceleration with constraints

I use AI to speed up parts of the workflow that benefit from iteration and synthesis:

- codebase exploration and pattern discovery
- implementation drafting and refactor support
- turning vague tasks into structured execution plans
- surfacing inconsistencies across code, docs, and tickets
- review support for obvious gaps, dead code, and drift
- reducing startup friction on well-scoped work

Used properly, AI removes drag. Used poorly, it multiplies noise.

## What stays with me

### Ownership does not move

There are responsibilities I do not outsource:

- architecture and system boundaries
- implementation judgment
- product and technical tradeoffs
- correctness and review quality
- deployment confidence
- production accountability
- deciding what not to build

AI can assist the work. It does not own the outcome.

## Engineering standard

### The bottleneck is usually not speed. It is weak structure.

Most teams do not struggle because they lack another tool. They struggle because scope is loose, boundaries are weak, ownership is unclear, and verification is treated as optional until the system starts fighting back.

That is why my workflow emphasizes inspection, scoped execution, verification, and maintainable structure.

I use AI to move faster, but never at the cost of engineering quality. Faster output only matters if the system stays reliable, understandable, and worth building on.

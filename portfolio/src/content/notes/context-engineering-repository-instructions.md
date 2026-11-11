---
title: "Context Engineering: Why Repository-Owned Instructions Outperform One-Off Prompts"
description: "How scoped, versioned, and reviewable repository context improves agent reliability more than increasingly elaborate one-off prompts, with the Ordr.now repository as the worked example."
summary: "Agent reliability depends less on a clever prompt and more on accurate, scoped, versioned context that lives with the code. How Ordr.now lays it out, and how it goes stale."
publishedDate: 2026-11-11
draft: false
featured: false
kind: method
tags:
  - agentic-engineering
  - context-engineering
  - ai-native-engineering
  - software-delivery
ogImage: /og-default.svg
---

Agent reliability depends less on writing a clever prompt and more on maintaining accurate, scoped, and versioned engineering context.

A strong prompt can frame one task. It cannot reliably carry the architecture, domain model, operational constraints, release rules, and accumulated decisions of a production system. Packing all of that into every conversation creates repetition and drift, and it makes the latest message look like the source of truth.

The [closed-loop development model](/notes/agentic-closed-loop-development#5-context-engineering) treats durable context as one of its foundations. This note goes one level down: what belongs in that context, how to layer it, how I lay it out in Ordr.now, and how it goes stale.

## 1. Prompts are transient, context is durable

A prompt is written for one execution and usually disappears from the artifacts that future engineers review. That makes it the right place for the immediate goal: repair this behavior, add this route, investigate this failure.

Architecture rules are different. If all writes must cross a domain service, that boundary should not depend on someone remembering to restate it. If a mobile queue must never cross tenant scope, the rule belongs in the domain model, the tests, and the maintained instructions.

Durable context includes:

- directory and module ownership;
- domain terms and invariants;
- architecture decisions and rejected alternatives;
- testing conventions and what each check proves;
- deployment and environment constraints;
- security, privacy, and confidentiality boundaries;
- known risks and escalation conditions.

The prompt points to this context and adds task-specific facts. It should not become a private replacement for it.

## 2. Layer context by scope

One response to missing context is a single comprehensive instruction file. That works briefly and then collapses under its own weight: every task loads irrelevant detail, the decisive rule is buried, conflicts accumulate, and nobody can tell which edit changes which behavior.

Hundreds of tiny documents are no better, because finding the right one becomes the problem. A small hierarchy works:

1. repository purpose and universal rules at the root;
2. app or package instructions next to the code they govern;
3. focused domain, architecture, and operational references;
4. task-specific intent and acceptance criteria in the task itself.

Each layer narrows or extends the one above it. The root does not duplicate nested rules, and precedence is stated: the nearest instruction file governs its subtree while inheriting the broader rules.

Instructions should describe behavior, not taste. "Keep changes maintainable" cannot resolve a decision. "Schema and migrations live only in the database package" tells an agent where a change belongs.

## 3. What the context has to say

Agents can read code, but several important facts are not obvious from code.

**Ownership seams.** Which layer owns canonical state, where authorization is evaluated, which interfaces are public contracts, which data is derived, and which modules may depend on each other.

**Invariants that span modules.** A rule such as "a closed operational period cannot be reopened by replay" may be enforced in a service, a database constraint, and a synchronization policy. It needs one written statement and tests at each boundary.

**What each check proves.** "Run the tests" is not context. A useful guide maps risk to verification: domain logic to unit tests, database behavior to integration tests against the real engine, offline synchronization to network transitions and restart persistence. It also says what a check does not prove. A mocked API does not prove integration, and a successful build does not prove the deployed redirects are correct.

**Deployment facts.** The build root, the artifact directory, who owns redirects, and which environments may be changed without approval. These prevent common errors such as building from the wrong directory or treating a green CI job as proof that the live domain is healthy.

When the written context and the code disagree, the agent should report the discrepancy instead of choosing whichever supports the easier patch.

## 4. How Ordr.now lays it out

[Ordr.now](/work/ordr-now) is a monorepo with an API, several web applications, an offline-first mobile POS, and shared packages. Its context is organized the way this note describes.

**A short root file with a reading order.** The root instruction file is about 120 lines. It opens with what to read, in order: the product and terminology references, the relevant detailed canon, the system overview, the nearest nested instruction file, and then the current code and tests. It also states the layout, the pinned runtime and package manager, and the canonical commands.

**Nested files where behavior differs.** Each application and shared package that has its own rules has its own instruction file, thirteen in total. The mobile POS file covers offline and device verification that would be noise in the marketing site. The database package file covers migration rules that frontend work never needs.

**A canon for durable truth.** A separate folder holds detailed product, domain, architecture, and operations references. The domain rules for the mobile POS and the offline-first architecture live there, not in a prompt.

**The workflow is in the repository too.** The stages of the development loop are stored as versioned skills alongside the code, so the process an agent follows is reviewed the same way the code is.

**An explicit tie-breaker.** The root file says that code, tests, migrations, and direct runtime evidence outrank stale prose, and that conflicts should be surfaced and the durable documentation corrected.

One result I did not plan for: when I changed agent tooling this year, the context carried over. A new agent was pointed at the same root file and followed the same reading order. Rules that live in private prompts or one tool's configuration would have had to be rebuilt.

## 5. How context goes stale

Stale instructions create disciplined failure. The agent follows the documented command, edits the documented source, and produces the wrong result because the repository moved months ago.

I found two examples in my own work while writing this. A site's instruction file still described a section as "not yet shipped" four months after it shipped. A published note described an application as under active development when it had never been merged. Neither was caught by a build, because nothing checks prose.

Freshness needs ownership and signals:

- update context in the same change that alters the boundary it describes;
- verify that referenced paths and commands still exist, ideally in CI;
- flag instructions that mention removed configuration;
- remove obsolete guidance instead of leaving two competing workflows.

When an agent finds stale context, it should separate the task from the repair. Fixing a wrong path in a command is usually in scope. Rewriting an architecture rule because the code diverged requires knowing which one is intended.

## 6. Failure modes

Several failures recur.

**Path drift** sends the agent to an old checkout or generated output instead of maintained source. The work looks correct and never reaches production.

**Authority drift** leaves an instruction that permits a release or destructive action after the rules changed.

**Command drift** preserves validation commands that no longer exercise the relevant application, so a green result means nothing.

**Conflicting layers** give a root and a nested file different rules without stated precedence. The agent picks the convenient one.

**Context dumping** loads so much material that the decisive rule loses attention.

**Prompt shadow policy** appears when important rules live only in one person's private prompt, where nobody else can find or review them.

The response to these is not a larger prompt. It is maintained, scoped, testable context.

## 7. Knowing whether it helps

More documentation is not automatically better. Context should change observable work:

- fewer clarification questions about facts that were discoverable;
- fewer out-of-scope changes and boundary violations;
- higher first-pass success on repository checks;
- fewer wrong assumptions about commands and paths;
- fewer reports that overstate what was verified.

Read these carefully. More escalations can mean worse context, or authority boundaries that are working. Fewer interventions help only if defects and hidden scope do not rise.

Retire context that costs maintenance without changing outcomes, and strengthen it where failures repeat.

## Conclusion

Repository-owned context does not make agents reliable by itself. It gives them a better chance of acting consistently with the actual system, and it gives reviewers a durable basis for challenging their decisions.

The strongest context is not the longest. It is the smallest maintained set that makes architecture, domain, authority, verification, and operational boundaries discoverable at the moment they matter.

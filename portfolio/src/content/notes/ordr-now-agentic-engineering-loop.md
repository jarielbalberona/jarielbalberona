---
title: "Inside the Ordr.now Agentic Engineering Loop"
description: "How repository-owned agents, offline-first mobile architecture, physical-device verification, and production canaries form a closed engineering system."
summary: "A concrete account of how Ordr.now turns product signals into isolated, verified changes across its API, PostgreSQL, offline-first mobile runtime, venue devices, and production boundaries."
publishedDate: 2026-07-27
draft: false
featured: false
tags:
  - agentic-engineering
  - ai-native-engineering
  - software-delivery
  - verification
  - bounded-autonomy
  - context-engineering
ogImage: /images/notes/ordr-now-agentic-engineering-loop.png
---

The [general closed-loop development model](/notes/agentic-closed-loop-development) describes a reusable method: translate intent into bounded work, ground execution in repository context, verify at the highest practical layer, correct within limits, and keep consequential decisions human-owned.

Ordr.now is where I apply that method to an owned production system. The product spans an authenticated API, PostgreSQL, an offline-first Android point-of-sale application, venue operations, synchronization, recovery, and a separate venue-device application under active development. A change that looks local at the interface can cross every one of those boundaries.

This note explains the operating system around that work. It complements the [Ordr.now product case study](/work/ordr-now), which focuses on product ownership, architecture, engineering constraints, and outcomes. It also shows what the broader [AI-native engineering model](/ai-native-engineering) looks like after the slogans and generic diagrams are removed.

## 1. Why Ordr.now needs a closed engineering loop

Ordr.now is not a web interface with a database behind it. It is an operational system used through unreliable connectivity, shared devices, time-sensitive venue workflows, and state transitions that can affect orders, payments, shifts, inventory, and later reconciliation.

The relevant system includes:

- authenticated API routes and domain use cases;
- PostgreSQL schemas, migrations, transactions, and command records;
- tenant, venue, register, station, device, and actor scope;
- a local-first mobile POS built on SQLite;
- a durable command outbox and centralized synchronization controller;
- recovery and conflict handling after interruption;
- physical Android devices;
- a separate `apps/venue-device` operating context;
- deployment, production observation, and controlled canary proof.

The vertical path matters more than any one framework:

```text
User interaction
→ local mobile state
→ durable command
→ synchronization
→ authenticated API
→ PostgreSQL transaction or command ledger
→ canonical server result
→ local reconciliation
```

An agent that changes only the visible symptom can easily put ownership in the wrong layer. A mobile retry may look like the fix for duplicate delivery even though the authoritative protection belongs in a server-side idempotency boundary. A UI patch may hide a conflict instead of resolving the disagreement between local and canonical state. A database change may compile while breaking an older mobile client that still has queued work.

The safe unit of work is therefore the complete behavioral path. The agent must understand where intent originates, where local truth is stored, which command crosses the network, how authorization is re-established, what the server accepts, and how the device learns the canonical result.

## 2. The repository is the agent control plane

The Ordr.now system does not depend on a single giant prompt. Prompts carry immediate user intent. The repository carries the maintained engineering context needed to interpret that intent.

The control plane includes:

- `AGENTS.md` files at repository and application boundaries;
- repository-owned skills for task setup, triage, execution, verification, shipping, and closeout;
- product and terminology canon;
- architecture and domain contracts;
- validation commands and proof-selection rules;
- scope, permission, and escalation boundaries;
- evidence and closeout requirements.

Those sources have different jobs.

**User intent** defines the requested outcome. **Repository context** defines the current architecture, invariants, and authority boundaries. **Task investigation** establishes the actual failure or change surface. **Agent execution** implements only the accepted scope. **Independent verification** challenges whether the result and evidence match the requirement.

That separation is deliberate. The user does not need to restate the entire offline architecture in every task. The agent also does not gain unrestricted authority merely because it can read the repository. Instructions explicitly distinguish routine implementation from changes involving financial semantics, authorization policy, destructive data work, production infrastructure, or release authority.

The result is versioned context instead of prompt folklore. If the mobile ownership model changes, the repository rules and tests have to change with it. If the code and canon disagree, the disagreement is a triage finding, not permission for the agent to pick the easier version.

## 3. The actual Ordr.now lifecycle

The generic lifecycle can be named many ways. Ordr.now currently implements six repository-owned skills, not a nine-stage chain. The normal entrypoint is `triage-work`; the other skills are specialized parts of the loop.

```text
setup-loop (repository readiness, when needed)
  ↓
triage-work (read-only triage and orchestration)
  ├─ durable issue and isolated task worktree
  ├─ execute-work
  ├─ verify-work + independent exact-tree review
  ├─ wrap-work: commit, pull request, CI, and merge gates
  ├─ ship-work: deployed, canary, and device proof when required
  └─ wrap-work: evidence, issue closure, and safe cleanup
```

### `setup-loop`

`setup-loop` checks whether a checkout is self-contained and ready for work. It verifies the Git root, repository structure, instructions, skills, runtime tooling, expected environment-file presence, and important mobile, API, database, CI, and deployment paths. It reports gaps without installing tools, changing secrets, mutating databases, or touching production.

This is a readiness path, not ceremony added to every small task.

### `triage-work`

`triage-work` is the single normal engineering entrypoint. Its first phase is read-only. It establishes the baseline, reads the applicable instructions and canon, traces the owning code and tests, identifies the first failing boundary, classifies risk, and defines the proof required.

It returns one internal routing result: ready to implement, needs a genuine product decision, or blocked by a concrete prerequisite or authority boundary. Routine engineering choices do not become approval theatre.

When ready, it creates or resumes the durable GitHub issue, issue-derived branch, isolated worktree, and task state. It then orchestrates the remaining stages.

### `execute-work`

`execute-work` implements the smallest complete change at the owning boundary. It preserves tenant and venue isolation, financial and inventory semantics, offline command identity, SQLite durability, replay safety, and recovery evidence where those concerns apply.

It also owns regression tests and updates durable architecture or domain documentation when the system truth changes. Before handoff, it stages only the intended candidate and freezes an exact Git tree.

### `verify-work`

`verify-work` selects evidence according to the changed risk surface: static analysis, unit tests, component tests, API tests, disposable PostgreSQL integration tests, local runtime checks, browser proof, physical-device proof, or deployed proof.

It returns only a hard pass, fail, or blocked result. A failure routes back to implementation within a bounded repair budget. Missing release-critical device or environment evidence stays blocked; it is not renamed as a pass.

### `ship-work`

`ship-work` operates after merge when the affected boundary requires deployed or physical proof. It observes the deployment caused by the merged change, confirms the affected live commit, checks health and authentication boundaries, and runs a guarded production canary or device scenario only when authorized and required.

It does not grant general permission to deploy, mutate customer data, exercise real payments, or use hardware merely because a task reached the shipping stage.

### `wrap-work`

`wrap-work` spans the final control boundaries. Before the first commit, an independent reviewer and `verify-work` evaluate the same frozen candidate tree. The commit tree must equal both reviewed and verified trees.

After that, `wrap-work` controls the pull request, CI, review repair, merge gate, durable evidence, issue closure, and worktree cleanup. Cleanup fails closed when the worktree is dirty, proof is incomplete, a resource lease remains active, or the merged behavior has not reached the required evidence boundary.

## 4. From signal to bounded issue

Work can enter the loop from many sources:

- a product requirement;
- a reported defect;
- a failing test or build;
- a device or lifecycle failure;
- a synchronization anomaly;
- a production observation;
- an authorization concern;
- technical debt exposed while changing another boundary.

The signal is not yet an implementation contract.

```text
Raw signal
→ reproduced or validated behavior
→ expected behavior
→ risk classification
→ bounded issue
→ acceptance evidence
```

“Fix sync” is unsafe because it leaves the important questions unanswered. Which command failed? Was it never dispatched, accepted but not acknowledged, rejected for scope, retried after expiry, or reconciled against a divergent server result? Which state is canonical? Is the operation financial? What should survive restart? What evidence is required on a real device?

A bounded issue records the expected behavior, affected scope, non-goals, invariants, proof layers, and stop conditions. The GitHub issue becomes the durable implementation contract rather than a title attached to an improvised patch.

This matters after interruption. A different agent or engineer can recover the issue, task state, branch, worktree, candidate identity, and remaining proof without relying on a private chat transcript.

## 5. Isolation and phased execution

Every normal task receives one issue-derived branch and one dedicated worktree based on the current remote baseline. The primary checkout remains available for other work. Task state also allocates isolated runtime resources such as ports, temporary databases, browser profiles, logs, and evidence directories.

That is basic concurrency hygiene. Without it, two valid tasks can corrupt each other’s proof: one process can satisfy another task’s health check, one test can write into another database, or a cleanup can remove another engineer’s state.

The implementation is divided by ownership and risk. A cross-layer task may use phases such as:

```text
Domain behavior
→ schema and migration
→ API and authorization
→ synchronization
→ local persistence
→ mobile interface
→ recovery
→ observability
→ integrated verification
```

The exact phases depend on the change. A styling repair should not inherit a database phase just to look rigorous. A financial replay change should not skip PostgreSQL integration because the TypeScript diff is small.

Commit history should preserve coherent decisions, but phase labels are not proof. Ordr.now’s exact-tree gate treats the staged candidate as the verification identity. If a later repair changes that tree, earlier review and affected proof are invalidated. A cleanly named commit cannot rescue stale evidence.

Before expensive proof, the task reconciles with the current remote baseline. Unpublished work may be rebased; published work incorporates the current base without rewriting shared history. Direct pushes to the protected mainline and force-push shortcuts are outside the loop.

## 6. The offline-first mobile execution path

The main mobile POS treats SQLite as the active terminal’s local operational truth. React Query is used for remote orchestration, Zustand for interface state, and small device preferences live outside the financial model. Tickets, payments, shifts, outbox commands, sync attempts, conflicts, and reconciliation state belong in SQLite.

The required write path is:

```text
Mobile action
→ local POS service
→ SQLite transaction
→ durable queued command
→ synchronization controller
→ authenticated API request
→ server-side idempotent execution
→ canonical result
→ local acknowledgement and reconciliation
```

The local business write and outbox enqueue happen together. A screen must not mutate the backend first, patch visible state, and later attempt to repair SQLite. That online-first pattern loses the very guarantees the offline architecture exists to provide.

### The failure windows

The design has to reason about more than “online” and “offline.”

**Duplicate taps** can express the same user intent twice before the interface settles. The local service must give the accepted intent a durable identity rather than rely only on button disabling.

**Duplicate delivery** is normal in a retrying system. A command can be sent again after timeout, process restart, or uncertain acknowledgement. The backend needs an idempotent execution boundary and durable command history for the affected domain.

**Network loss before dispatch** leaves the command local and pending. It must survive application termination without appearing accepted by the server.

**Network loss after server acceptance but before acknowledgement** is harder. The device cannot assume failure merely because it missed the response. Repeating the same command identity must converge on the stored authoritative result rather than repeat the financial or operational effect.

**Authentication expiry or revocation** must stop dispatch without silently discarding valid local work. After reauthentication, only work still valid for the authenticated actor and active operational scope may resume.

**Wrong venue, register, station, or device scope** is not a connectivity error. It is a safety boundary. The client and server both need enough context to reject work that no longer belongs to the active scope.

**Queue ordering and restart recovery** cannot depend on in-memory callbacks. Eligibility, attempts, blocked state, conflicts, acknowledgements, and recovery evidence must remain durable.

**Reconnection** does not mean “send everything.” The controller evaluates which work is pending, blocked, retryable, conflicted, final, or already synchronized, then reconciles against canonical server state.

The working invariant is:

```text
One accepted user intent
→ one durable command identity
→ no duplicate authoritative effect for that command
→ repeatable client reconciliation
```

That statement is intentionally scoped. It does not claim a universal exactly-once theorem across every external provider or every future Ordr.now domain. It describes the boundary the current local-command and server-ledger design is built to preserve where implemented and verified.

## 7. The main mobile app and `apps/venue-device`

Ordr.now has more than one mobile operating context. They should not be collapsed into one generic “app” claim.

### Main mobile POS

The main application handles authenticated staff operation, tenant and venue bootstrap, employee or cashier context, register selection, business-day and shift readiness, local POS work, durable persistence, synchronization, Orders recovery, menu snapshots, and diagnostics.

Its startup path does not consider the interface ready merely because navigation rendered. Readiness depends on authenticated, server-confirmed scope and the local state needed for the active terminal. Logout, scope switching, and reauthentication are guarded when unresolved local work could otherwise be stranded or replayed under the wrong context.

The verification target changes with the feature. A menu layout can be exercised quickly through a development runtime. A change involving SQLite migration, process death, reconnect drain, authentication recovery, or command replay needs native and data evidence.

### `apps/venue-device`

A separate Expo application is under active development for venue-bound device workflows. Its current direction includes device provisioning and association, secure device credentials, locally persisted assignment and runtime configuration, cached kiosk bootstrap data, connectivity state, optional cached menu browsing, and online-authorized administration such as diagnostics, reconfiguration, reprovisioning, or deactivation.

That does not make it a secure kiosk by default.

An Expo application can hide navigation, keep the screen awake, reset idle state, and protect in-app manager actions. Those are application behaviors. Android lock-task mode, managed-device enrollment, automatic launch after boot, protected operating-system escape, remote fleet policy, and MDM enforcement are separate device-management capabilities.

The current application must not be described as proving those controls unless the native configuration, deployment model, and physical-device evidence establish them. Cached browsing also does not imply that every transactional workflow is safe offline. Administrative actions that require current authorization remain online boundaries.

## 8. Verification as a ladder

Ordr.now selects proof according to the failure boundary rather than running an impressive but irrelevant test pile.

```text
Static analysis
→ unit tests
→ component tests
→ API tests
→ PostgreSQL integration tests
→ financial and recovery tests
→ local runtime or simulator feedback
→ physical-device verification
→ deployed canary
```

Examples of maintained command surfaces include:

```bash
pnpm agent:validate-orchestration
pnpm -C apps/mobile lint
pnpm -C apps/mobile typecheck
pnpm -C apps/mobile test
pnpm -C apps/api test:unit
pnpm -C apps/api test:integration
pnpm -C packages/db verify
pnpm mobile:runtime-smoke -- --port <allocated-port>
```

The repository’s proof planner selects the relevant gates from the changed paths and declared risk. Shared contracts, database migrations, unclassified paths, and agentic foundation changes fail closed into broader proof. Narrow changes can use focused tests when those tests exercise the actual failure boundary.

Each layer has a limit.

Static analysis catches invalid types, imports, formatting, and some architecture violations. Unit tests are good for policy, parsing, state transitions, and payload construction. Component tests reconnect interface state and interaction. API tests exercise transport, authorization, use cases, and response behavior. PostgreSQL tests expose transaction, constraint, concurrency, lease, and idempotency behavior that mocks remove.

None of those proves Android process death, SQLite persistence on hardware, Bluetooth printing, operating-system permissions, a deployed environment, or production data shape. A green lower layer is necessary evidence, not permission to rename the missing upper layer.

## 9. Simulator versus physical-device proof

Fast feedback still matters. A browser-compatible Expo runtime or simulator can support layout iteration, route checks, common interaction flows, and focused development feedback. It is cheap enough to use repeatedly while implementation is moving.

Physical Android proof is required when the claim depends on:

- process termination, relaunch, or reboot behavior;
- real SQLite files and persistence;
- network removal and restoration;
- authentication revocation and recovery;
- wrong-scope rejection on the active device;
- durable queued work across restart;
- installation, signing, or package identity;
- venue-device kiosk constraints;
- Bluetooth or other hardware behavior.

Ordr.now uses a guarded, side-by-side verification application for device work so iterative proof does not overwrite the normal production package. A repository lease prevents two tasks from treating the same Android tablet as their exclusive evidence source. The current mobile verification history includes a physical Xiaomi Redmi Pad 2, but the useful fact is not the model name. It is that the proof records the candidate, package, device context, local database state, server observation, logs, and cleanup boundary.

Expo Web evidence is labeled web-only. It cannot prove SQLite, Android lifecycle, native authentication behavior, APK installation, printing, or hardware. An emulator is also not silently upgraded to physical proof.

## 10. Bounded self-healing

The loop may repair execution conditions when the expected condition and the repair are both understood.

Examples include:

- restarting an expected local service;
- correcting a malformed validation invocation;
- clearing generated caches;
- regenerating a generated fixture;
- repairing non-behavioral local configuration;
- fixing an implementation defect inside the approved specification.

Those actions restore the task or implementation to the stated model. They do not redefine the product.

Without explicit authority, the agent may not weaken authorization, change financial meaning, remove a failing assertion, alter schema semantics, relabel an error to obtain a pass, change offline policy outside the approved requirement, or broaden the task into an unrelated refactor.

Retries are bounded by failure category. Repeating the same failed action is not autonomy; it is refusal to learn from evidence. When the repair budget is exhausted, the failure record becomes the escalation input.

## 11. Independent verification

The implementing agent should not be the only authority declaring that its own work is correct.

For a candidate to move forward, Ordr.now freezes the staged Git tree and runs risk-selected verification alongside a fresh independent review of that same tree. The reviewer receives the acceptance criteria, repository instructions, staged diff, relevant canon, and verification summary. It does not receive authority to edit.

The review challenges:

- whether the root cause was fixed;
- whether the tests prove the requested behavior;
- authorization and scope isolation;
- migration and compatibility safety;
- concurrency and idempotency;
- offline persistence and recovery;
- error classification;
- observability and rollback posture;
- unnecessary complexity;
- missing physical or deployed proof.

“Another AI reviewed it” is not evidence. The value comes from a separate context, explicit review criteria, classified findings, and a cryptographic tree identity that ties the review to the exact candidate.

An actionable finding returns to implementation, invalidates the affected proof, and requires a new tree and fresh review. Review retries are also bounded. Exhaustion is recorded honestly with residual findings; an explicit critical blocker still stops delivery.

## 12. Release and production proof

The delivery path is:

```text
Integrated gate
→ pull request
→ CI
→ merge
→ deployment observation
→ production-safe canary when required
→ physical-device proof when required
→ durable evidence
→ issue closure
```

The proof must match the released identity. A physical test against an older APK, a production check against an unknown deployment, or a screenshot from a different commit does not close the loop.

For deployed applications, the system observes the deployment triggered by the merge and confirms the affected component commit before testing behavior. Different components may deploy independently, so “the repository commit is live” is too vague when only one service moved.

The production-canary model is intentionally narrow:

- a restricted synthetic identity;
- a controlled test tenant or environment;
- exact identity, ownership, and scope guards;
- one small bounded mutation;
- server and audit-result verification;
- restoration of the original state;
- session and browser cleanup;
- sanitized durable evidence.

The canary is not a general production debugging account. It excludes customer tenants, real payments, billing, messaging, printing, infrastructure changes, and arbitrary data mutation.

Release evidence remains separated by boundary: local checks, CI, deployment health, live behavior, physical device, and production canary are different claims. Closeout records which ones passed, which were not required, and which remain blocked.

## 13. What remains human-owned

The objective is reliable delegation, not an unsupervised coding system.

Agents do not own:

- ambiguous product decisions;
- financial rules and accounting meaning;
- authorization policy;
- destructive or irreversible data decisions;
- schema strategy with material business consequences;
- acceptance of unresolved risk;
- exceptions to safety boundaries;
- final production release authority.

An agent can investigate these topics, expose tradeoffs, prepare implementation, and collect evidence. It cannot convert access into accountability.

This is especially important in Ordr.now because product, security, financial, and operational decisions meet in the same flows. A technically consistent replay policy can still be the wrong business rule. A migration can be mechanically valid and operationally unacceptable. A canary can pass while the owner decides the rollout risk is still too high.

## 14. The closed feedback loop

The system is closed-loop because evidence from the running product returns to engineering intake.

```text
Production or device signal
→ bounded issue
→ repository-grounded execution
→ automated and physical verification
→ controlled release
→ production observation
→ next signal
```

A device failure can reveal an untested lifecycle boundary. A production observation can expose a missing authorization case. A flaky gate can reveal that the verification system itself is weak. Each becomes a new signal that is validated, bounded, and connected to acceptance evidence.

Closure is therefore more than merging code. The task records the implemented behavior, exact evidence, proof limits, residual risk, and repository state. That record improves the context available to the next task.

## 15. Lessons and practical conclusions

Ordr.now has reinforced several blunt conclusions.

Agent quality depends heavily on repository quality. A capable model operating against stale instructions, weak ownership boundaries, and vague acceptance criteria will produce confident inconsistency faster.

Offline-first work requires vertical reasoning. The interface, SQLite transaction, outbox, authentication context, API, PostgreSQL command record, canonical effect, and reconciliation path are one engineering problem.

Green tests are not equivalent to verified behavior. The useful question is which artifact ran, in which environment, against which failure boundary.

Physical-device proof is part of implementation when the behavior depends on the device. It is not an optional demonstration added after the engineering work is supposedly complete.

Agent autonomy needs explicit product and safety boundaries. Financial meaning, authorization, destructive operations, and release risk do not become routine just because an agent can execute the commands.

Evidence and closure are engineering work. A merged patch without traceable proof, residual-risk reporting, and safe cleanup leaves the system less understandable than it should be.

The objective is not maximal autonomous code generation. It is reliable delivery with controlled accountability.

---
title: "Bounded Autonomy: Where Software Agents Must Stop"
description: "A practical authority model for deciding what software agents may do autonomously, what requires approval, and what must remain prohibited."
summary: "How reversibility, risk, permissions, retries, and explicit approval gates define useful autonomy in production engineering."
publishedDate: 2026-07-20
draft: true
tags:
  - agentic-engineering
  - bounded-autonomy
  - software-delivery
  - verification
ogImage: /og-default.svg
---

The quality of an agentic engineering system is determined as much by what the agent is forbidden to do as by what it can automate.

That is not an argument for timid automation. It is an argument for authority design. An agent can investigate a large repository, prepare a narrow patch, run deterministic checks, and diagnose a failed preview without waiting for a person to approve every command. The same agent should not silently change an authentication model, delete production data, or redefine the requirement because verification became inconvenient.

Useful autonomy is bounded by intent, evidence, reversibility, and accountability. The goal is to delegate as much reliable work as possible while keeping decisions with material security, product, data, or operational consequences under explicit control.

## Autonomy is an authority design problem

Discussions about software agents often focus on capability: which model can reason over more files, invoke more tools, or complete a larger benchmark. Production systems expose a different question: what authority should this actor have in this context?

Capability and authority are separate. A model may be capable of producing a database migration, and the agent may have a tool that can execute it. Neither fact establishes permission to alter a shared database. Authority comes from the task, repository rules, environment policy, and accountable owner.

An authority model answers four questions:

1. What may the agent observe?
2. What may it change?
3. In which environment may it act?
4. Which decisions require another accountable party?

The answers should be concrete enough for a workflow to enforce. “Use good judgment” is not an authority model. “The agent may create and validate a migration locally but may not apply it to shared or production data without approval” is.

Authority should also be scoped to time and task. Access that was appropriate for one release should not become permanent ambient permission. An agent working on content does not need database credentials. An agent investigating a production incident may need broad read access but still no write access.

## Reversible and irreversible operations

Reversibility is a useful first filter. A change in a clean source-control branch is usually reversible. A production data deletion is not. Between those extremes are operations that are technically reversible but operationally expensive, such as a public API change, a cache purge, a credential rotation, or an infrastructure replacement.

Reversible actions can receive broader autonomous authority when three conditions hold:

- the target is exact and isolated;
- the before state is recorded;
- the result can be verified without damaging unrelated work.

Even a reversible action becomes unsafe when the target is ambiguous. A broad cleanup command in the wrong directory may affect user work outside the task. A source-control reset may discard unpublished changes. The agent has to resolve the actual target before acting.

Irreversible actions need stronger gates. Examples include deleting persistent data, publishing externally under a person’s identity, changing legal or billing state, revoking access, and force-rewriting shared history. Preparation can remain autonomous: inspect dependencies, calculate impact, produce a dry run, and assemble an exact command. Execution requires explicit authority and often a recovery plan.

The distinction is not purely technical. Sending an email can be impossible to recall even though it changes no database. Publishing an unsupported claim can create reputational damage that a later edit does not erase. Authority models have to consider social and business reversibility alongside code.

## Risk-based permission boundaries

A practical permission model combines impact and uncertainty.

Low-impact, well-understood work can move autonomously. Reading code, generating a local build, running an existing test suite, or changing a bounded document usually has limited external consequence.

High-impact work needs approval even when well understood. A routine production deployment still changes a live environment. A schema migration may have a proven rollback but can block traffic or lock data. The consequence justifies the gate.

High-uncertainty work also needs escalation even when impact appears low. If the agent cannot determine which generated files are authoritative, editing one may create drift. If two sources disagree about a public fact, choosing one without confirmation can publish false information.

Permissions should reflect the narrowest useful scope:

- repository read access without organization-wide read access;
- write access to an isolated worktree rather than every checkout;
- preview deployment rights without production release rights;
- parameterized database queries rather than a general shell;
- allowlisted tools rather than unrestricted network access;
- temporary credentials rather than persistent shared credentials.

The point is not to make agents weak. It is to make the effect of a failure legible and containable.

## Approval gates that carry real meaning

An approval gate is useful only when the approver receives an understandable decision.

A weak gate presents hundreds of changed files and asks for “approve.” A strong gate presents the intended outcome, exact scope, material decisions, evidence, unresolved issues, rollback boundary, and action that approval will authorize.

Approval should be required for:

- material requirement changes;
- authentication and authorization changes;
- schema and persistent-data migrations;
- shared infrastructure changes;
- protected-branch merges;
- production releases;
- destructive or difficult-to-reverse operations;
- public communication under a person or organization’s identity.

The gate should occur at the last responsible moment. Requiring approval before an agent can investigate wastes human attention. Requiring it only after a production mutation is meaningless. The agent should prepare the change and evidence autonomously, then stop before the consequential action.

Approval also expires when the change moves materially. If a failed deployment leads to a different migration or a wider scope, the previous approval does not automatically cover it.

## A control matrix

Authority is easier to review when expressed as a matrix rather than scattered prose.

| Activity | Default authority | Required evidence | Stop condition |
|---|---|---|---|
| Repository investigation | Autonomous | Source references and observed state | Required source is unavailable |
| Bounded implementation | Autonomous | Scoped diff and acceptance criteria | Scope must expand materially |
| Local tests and builds | Autonomous | Command, result, artifact | Repeated unexplained failure |
| Preview deployment | Autonomous when isolated | Deployment identity and runtime checks | Target is shared or ambiguous |
| Authentication change | Propose only | Threat model, tests, migration impact | Human approval missing |
| Schema migration | Prepare only | Dry run, rollback, compatibility proof | Shared data would change |
| Protected merge | Prepare only | Reviewed diff and required checks | Named approval missing |
| Production release | Prepare and verify | Release artifact, checks, rollback state | Release authority missing |
| Verification bypass | Prohibited | Not applicable | Always stop |
| Secret exposure | Prohibited | Not applicable | Always stop and contain |

The matrix can vary by repository or environment. A personal static site and a multi-tenant financial system should not share identical gates. The important property is that the differences are explicit.

## Retries and escalation

Autonomy becomes dangerous when failure has no stopping rule. An agent that can keep trying may gradually change the problem until something passes.

Retries should be bounded by both count and class. A transient network request may be retried once or twice. A deterministic compiler error should not be retried unchanged. A deployment that fails because of a clear typo can be corrected inside scope; a deployment that exposes an unknown infrastructure dependency should escalate.

A useful retry record includes:

- the observed failure;
- why a retry or correction is safe;
- what changed between attempts;
- the result;
- the remaining retry budget.

Escalation is not failure. It is the correct output when the system reaches an authority or knowledge boundary. The escalation should be specific: “The requested change requires modifying the shared identity schema, which is outside the approved scope,” not “I need help.”

Repeated failure can also indicate that the acceptance criterion, environment, or test is wrong. The agent may investigate that possibility, but it may not silently rewrite the criterion to match the implementation.

## Security, authentication, and schema changes

Security-sensitive work deserves narrow authority because plausible mistakes can be severe and difficult to observe.

Authentication changes affect how identity is established. Authorization changes affect what an identity may do. Agents should not treat them as ordinary plumbing. A change needs an explicit threat model, negative tests, session and revocation behavior, tenant or scope boundaries, and migration consequences.

The agent can investigate current behavior, identify inconsistency, propose a design, implement behind an isolated boundary, and prepare tests. Approval is required before changing the public security model or shared identity state.

Schema changes have similar risks. Generating a migration is easy. Proving compatibility across old and new application versions, data volume, locking, rollback, and partially applied state is not. The agent may validate against disposable data and produce a dry run. Applying it to shared data remains gated.

Secrets are a hard boundary. An agent must not print, copy into source, include in logs, or move credentials into a broader environment. If a secret appears unexpectedly, the correct response is containment and escalation, not continued investigation in public output.

## Merge and deployment authority

Merging and deployment combine otherwise separate changes into shared state. That makes them accountability boundaries.

An agent can prepare a clean commit, verify the diff, run required checks, push an isolated branch, and assemble a release summary. In a protected workflow, the merge remains human-approved. This is not because a person can inspect every line better than a tool. It is because someone must own the decision that the evidence is sufficient and the timing is acceptable.

Production release needs the same distinction. Deployment preparation and deployment authority are different. The agent can identify the exact artifact and environment, confirm health checks, and prepare rollback. The release gate should verify that the target is correct, no newer remote work will be overwritten, and the approval still matches the artifact.

Post-deployment verification can return to autonomous execution. The agent should check routes, APIs, logs, metrics, and user-visible behavior. If verification contradicts the release criteria, rollback or further mutation follows the defined incident authority, not improvisation.

## Why “fully autonomous” is usually the wrong goal

“Fully autonomous” is a vague optimization target. It rewards removing human interactions without asking whether those interactions carry judgment, accountability, or risk control.

A system that ships more changes with fewer approvals may be worse if it increases hidden scope, escaped defects, or recovery cost. Autonomy should be measured in reliable completed work, not uninterrupted tool calls.

Some human gates are symptoms of poor tooling and should be removed. Manually copying a validated artifact between systems is not meaningful judgment. Other gates exist because a product decision, legal commitment, security tradeoff, or irreversible action needs an accountable owner. Automating the ceremony does not automate the responsibility.

The better goal is **maximum reliable delegation**. Let agents handle investigation, repetitive execution, evidence collection, and bounded correction. Reserve human attention for ambiguity, tradeoffs, security, and consequential decisions.

## Failure cases caused by excessive freedom

Excess authority tends to fail in recognizable ways.

An agent may broaden a repair into a framework upgrade because newer APIs simplify the patch. The code improves locally while the release acquires an unapproved migration risk.

It may resolve a failing test by weakening the assertion, mocking the integration boundary, or excluding the test. The dashboard turns green while confidence falls.

It may use production credentials to diagnose a local problem, increasing exposure and making the evidence hard to reproduce.

It may merge or deploy before checking for newer remote work, overwriting another contributor’s changes.

It may delete generated or cached data without resolving whether those files are authoritative, shared, or recoverable.

It may publish an external message that is technically accurate but not authorized, leaking context or committing the organization to a position.

These are not arguments against agents. They are arguments for designing permissions around failure consequences before giving the agent tools.

## Practical adoption checklist

Before expanding autonomous authority, confirm:

- The work item states intent, scope, exclusions, and acceptance criteria.
- Repository instructions identify architecture, public boundaries, and escalation conditions.
- The agent’s credentials are limited to the required repository and environment.
- Reversible and irreversible actions are distinguished.
- Authentication, schema, infrastructure, merge, release, and destructive work have explicit gates.
- Verification commands are deterministic and connected to product behavior.
- Runtime checks name the environment they prove.
- Retries have count limits and class-specific rules.
- Failed gates cannot be bypassed or silently rewritten.
- External communication requires explicit authority.
- Final reports distinguish observed facts from inference.
- A named person or process owns the release decision.

Bounded autonomy is not a compromise between manual engineering and agentic systems. It is the control architecture that makes serious delegation possible. The agent should move quickly where actions are scoped, observable, and reversible. It should stop cleanly where facts, permission, or accountability run out.

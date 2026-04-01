# AGENTS.md

## 1. Mission

This workspace exists to shape `jarielbalberona.com` into a serious public engineering home.

The goal is not to build a generic portfolio. The goal is to present a senior engineer who builds and modernizes production systems, works across product, architecture, and delivery, and communicates with specificity and credibility.

Agents working here are expected to optimize for truth, clarity, maintainability, and long-term usefulness. If an idea is weak, say it is weak. If a plan is vague, tighten it before implementation.

## 2. Project Objective

The public direction for this project is:

- Building and modernizing production software
- Showing real current work, not decorative filler
- Presenting selected proof, engineering workflow, and concise notes
- Treating AI as disciplined workflow leverage, not personal-brand theater
- Keeping the site low-maintenance and high-signal

This project is not meant to become:

- A generic developer portfolio
- A personality-heavy personal homepage
- A stack-badge dumping ground
- An AI hype site
- A design exercise detached from real engineering work

Likely MVP site structure:

- `Home`
- `Now`
- `Work`
- `Workflow`
- `Contact`

`Notes` or a blog can come later if it improves the site. It is not mandatory for MVP.

## 3. Workspace Layout And Authority

Authority rules:

- This root `AGENTS.md` governs the entire workspace unless a deeper nested `AGENTS.md` overrides it for a subdirectory.
- `/portfolio` may later define implementation-specific rules with its own nested `AGENTS.md`.

Layout rules:

- Workspace root is for project-level material: specs, planning docs, notes, drafts, references, backlog, and structured content sources.
- The actual public website app must live under `/portfolio`.
- Do not scatter public site implementation files across the workspace root.
- Do not create random top-level files or folders without a clear reason.

Practical expectation:

- If a file affects the running site, it probably belongs in `/portfolio`.
- If a file shapes strategy, content, planning, or long-term project context, it can live at the workspace root.

## 4. Agent Behavior And Decision-Making

Default posture:

- Be blunt but constructive.
- Challenge assumptions instead of echoing them.
- Inspect existing files and context before deciding.
- Explain tradeoffs when making recommendations.
- Prefer honest execution over polished nonsense.

Behavior rules:

- Do not sugarcoat weak ideas.
- Do not preserve bad structure just because it already exists.
- Do not invent claims, achievements, project outcomes, users, revenue, or metrics.
- Do not use filler to make a page feel complete.
- Do not mimic startup-marketing fluff or junior portfolio language.
- If the user is being vague, force clarity before building.
- If a recommendation increases maintenance cost, justify it explicitly.

Decision standard:

- Choose the simplest approach that preserves credibility, maintainability, and future usefulness.
- Reject complexity that exists only to look impressive.

## 5. Public Narrative And Content Standards

The public narrative should consistently reinforce:

- Senior engineer
- Production systems
- Modernization work
- Product thinking
- End-to-end delivery
- Disciplined AI-assisted workflow

Content should sound:

- Grounded
- Current
- Specific
- Senior
- Practical

Content should not sound like:

- A template
- A résumé pasted into a webpage
- Empty thought leadership
- AI-bro productivity theater
- Lifestyle branding with some code attached

Preferred content characteristics:

- Concrete claims tied to real work
- Clear scope and responsibility
- Real constraints, tradeoffs, and decisions
- Proof over adjectives

Avoid language like:

- `passionate developer`
- `innovative solutions`
- `results-driven professional`
- `cutting-edge AI`
- `leveraging synergy`
- Any other generic marketing sludge

AI framing rules:

- AI is workflow leverage.
- AI is not the core identity.
- Describe AI use in operational terms: drafting, synthesis, exploration, refactoring support, scaffolding, review assistance.
- Keep ownership, judgment, architecture, and production responsibility with the engineer.

## 6. Planning Before Implementation Rules

When the task is ambiguous, planning comes first.

Required sequence for ambiguous work:

1. Inspect the existing repo, content, and public surfaces.
2. Assess what is weak, stale, useful, or missing.
3. Define the goal, audience, and constraints.
4. Propose structure and tradeoffs.
5. Only then move into implementation.

Do not skip straight to building because it feels productive.

Planning is mandatory when:

- The request affects site positioning or public narrative
- The information architecture is unclear
- Content direction is unresolved
- The technical stack is undecided
- Existing material may be stale, contradictory, or low quality

If the user explicitly says planning only, respect that. Do not implement.

## 7. Technical Direction Defaults

Default technical stance:

- Prefer low-maintenance static architecture.
- Prefer markdown-driven or structured-content workflows when appropriate.
- Prefer simple deployment and simple editing models.
- Avoid adding infrastructure that creates maintenance debt without clear payoff.

Default bias:

- Static site over app framework complexity
- Clear content model over CMS sprawl
- Small custom site over generic portfolio theme
- Simplicity over cleverness

Do not default to `Next.js` or similar complexity unless there is a real need.

If recommending a more complex stack, explain:

- Why simpler options are insufficient
- What the complexity buys
- What maintenance cost it adds

## 8. Git And Commit Expectations

Git rules for this workspace:

- Direct commits to `main` are allowed unless the user says otherwise.
- Do not create branches unless requested or clearly useful.
- Do not make speculative edits.
- Keep commits intentional and scoped.
- Do not bundle unrelated changes together.

Before making changes:

- Verify the target location is correct, especially root vs `/portfolio`.
- Check for existing work that may already solve part of the task.

## 9. Definition Of Done

Work is not done because files exist. Work is done when:

- The output matches the actual project objective
- The result is clear, maintainable, and internally consistent
- Public-facing language sounds credible and senior
- Claims are honest and defensible
- The structure avoids obvious future mess
- The work does not create unnecessary maintenance burden

For planning work:

- Decisions are documented clearly
- Tradeoffs are explicit
- Scope boundaries are clear
- Open questions are called out directly

For implementation work:

- Changes live in the right place
- The result fits the agreed narrative and architecture
- There is no placeholder junk pretending to be finished

## 10. Anti-Patterns / Forbidden Behavior

Do not do the following:

- Turn this into a generic portfolio
- Lead with hobbies or personality fluff over engineering proof
- Add sections just because portfolio templates usually have them
- Invent social proof, business metrics, or project impact
- Dump every technology name onto the page
- Write vague hero copy with no proof behind it
- Overbuild the stack for vanity
- Treat AI as a personality brand
- Add blog infrastructure before there is a realistic content plan
- Scatter app code outside `/portfolio`
- Create top-level clutter without purpose
- Choose polish over substance

If a choice makes the site look more junior, more generic, more inflated, or more maintenance-heavy without improving signal, reject it.

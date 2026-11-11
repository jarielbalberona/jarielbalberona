---
title: "When the Agents Outgrew the Laptop"
description: "Agents need to run around the clock, and a 16 GB laptop cannot do that. Why the work moved to a remote Linux server, how the setup is organized, and what it taught me about cleanup, permissions, and approval."
summary: "A 2021 laptop could not hold containers, databases, and several agents at once, and the agents stopped whenever it slept. A server lets them run 24/7. The useful lessons came after the move."
publishedDate: 2026-11-11
draft: false
featured: false
tags:
  - agentic-engineering
  - ai-native-engineering
  - software-delivery
  - bounded-autonomy
ogImage: /og-default.svg
---

The [closed-loop development model](/notes/agentic-closed-loop-development) describes how agent work should be bounded, verified, and released. It says nothing about where that work physically runs. For a long time the answer was my laptop, and this year that stopped being enough.

This note is about the setup that replaced it: agents on a remote Linux server, with the laptop reduced to a screen and a place to approve things. It covers why I did it, how it is organized, how I use it away from the desk, and what I learned getting it right.

## 1. The constraint was a five-year-old laptop

My machine is a 14-inch MacBook Pro from 2021: an M1 Pro with 16 GB of memory. It is still a good computer for writing software by hand.

It is not enough for the way I work now. A normal day had all of this running at once:

- a Linux virtual machine for containers;
- a local database stack per project;
- several coding agents, each with its own checkout and its own test runs;
- browser automation for verification;
- the editor, terminal, browser, and chat tools I use myself.

Sixteen gigabytes does not stretch that far. The machine went into swap, the interface stalled while agents ran tests, and I was restarting it several times a week to get it back. The agents were also tied to the lid: when the laptop slept, the work stopped.

Buying a larger laptop would have raised the ceiling and kept the second problem. I wanted the work to continue when the laptop was closed.

## 2. What moved and what stayed

The work that needs memory and long unattended runs lives on a Linux server with 16 cores and about 62 GB of memory. That covers the agent sessions, the checkouts, containers, databases, builds, test runs, and headless browser checks.

The laptop keeps the things that need me or need hardware on my desk:

- a browser where I am signed in, for dashboards and consoles;
- anything behind multi-factor authentication;
- physical devices. For [Ordr.now](/work/ordr-now), the Android tablets used for point-of-sale verification plug into the laptop, so device proof stays local.

When I measured the laptop afterwards, the container virtual machine was stopped, swap use was zero, and more than half the memory was free. What still used processor time was the interface in front of me, not background compute.

## 3. How the server is organized

The arrangement is simple to describe.

**One lead agent per project.** Each project has a long-lived lead session on the server that holds the project's context and is the one I talk to. The lead hands bounded tasks to short-lived sessions.

**One task, one checkout, one disposable environment.** Each task gets its own working copy and its own throwaway database stack, built from migrations and seed data. When the task's pull request merges or closes, both are removed. Nothing in a development environment is worth preserving; if it cannot be rebuilt, that is a defect.

**Sessions that survive disconnection.** Agent sessions run inside a terminal multiplexer on the server, so a dropped connection or a closed laptop does not end them.

**Permissions written per project.** Each project's settings list what the agent may do without asking, what it must ask for, and what it may never do. Routine read-only and release commands are allowed. Configuration changes, anything touching secrets, and anything else with elevated rights still ask.

**A helper on the laptop.** When a server agent needs something only the laptop has, such as a signed-in browser, it sends a specific request to a session on the laptop. That session does the one thing asked and reports back.

## 4. Working from a phone

The part I use most is the one I did not plan for. Because the lead agents live on the server, I can talk to them from my phone. I use the remote control feature of my agent tooling, which lets the phone attach to a session that is already running on the server and continue the same conversation.

That changes what being away from the desk means. In an airport, in transit, or out with friends and family, I do not need to carry the laptop and open its lid to keep work moving. I can ask a lead for status, answer a question it is blocked on, approve a routine step, or hand it the next task, all from that chat on the phone. The work continues on the server either way.

The limits are the same ones as before. Anything that needs the laptop itself, such as a signed-in browser session, a multi-factor prompt, or a tablet on a cable, waits until I am back at it. A phone is good for direction and decisions. It is not where I review a large change in detail.

## 5. What I learned

The hardware problem disappeared on the first day. Getting the setup right took longer, and my first configuration on the server was not the one I kept. These are the lessons that survived.

### The machine is the easy part

Moving to a server does not improve a workflow. It makes the existing one cheaper to run. How the agents are configured, and whether the model fits the kind of work, decides the outcome far more than cores and memory do. I now treat the agent setup as something to evaluate on real tasks before I scale it, not something to assume.

### More compute needs a cap and a cleanup rule

With plenty of disk and memory, an agent can start a fresh working copy and a fresh environment for every attempt. Unless removal is part of the task, they accumulate, and work gets generated faster than it gets reviewed and closed. Cleanup belongs inside the task, and the number of open changes needs a limit.

### Prefer disposable state to elaborate control

It is tempting to make shared resources safe with strict ownership rules: who created what, who may release it, what proof is needed. Rules like that depend on history that a single restart erases. Environments that can be thrown away and rebuilt from the repository are simpler and hold up better. If a rule cannot be satisfied after a restart, it will eventually stop the work.

### Permissions should be narrow and per project

An agent that asks about everything cannot run unattended. An agent allowed everything is not something to leave unattended. The setting that works is a short allow-list per project for routine commands, with elevated actions still asking.

Approval also has to be expressed where the agent can verify it. An agent's own safety checks may refuse a production step that was only approved in conversation, and that is the right default.

### Agents should talk to each other directly

When one agent needs something another has, they need a direct, logged way to ask. If a person carries messages between them, the person becomes the slowest component. My role should be approving consequential steps, not relaying routine ones.

### Restart the server on purpose

Timers, tunnels, workers, and long runs all have to answer one question before I rely on them: what happens when the machine restarts while I am asleep? The only way to know is to restart it and see what does not come back.

## 6. What "around the clock" really means

The honest version is narrower than the phrase suggests.

The agents can keep working while I am away. Investigation, implementation, tests, and evidence collection continue without me. That part is real, and it is the reason for the server.

The decisions do not move at that speed. Credentials, production changes, destructive operations, and releases still wait for me, as the [bounded-autonomy boundaries](/notes/agentic-closed-loop-development#7-bounded-autonomy) say they should. A night of unattended work often ends at a single approval that has been sitting since the first hour.

So the measure that matters is not how many hours the agents ran. It is how long finished work waits for a decision, and whether what waited was prepared well enough for me to decide quickly.

## Conclusion

A 16 GB laptop was the reason I moved, and it turned out to be the smallest part of the story. The server solved memory in a day. Everything after that was about the same subjects as the rest of these notes: bounded authority, disposable state, evidence, and a human decision at the points that matter.

The objective was never agents that run all night. It is work that is ready for a decision when I open the laptop.

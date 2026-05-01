# Agile Dev Pipeline

A structured, agile-inspired development pipeline for Claude Code, packaged as a **Claude Code plugin**. Describe what you want to build, and the pipeline guides you — and Claude — through discovery, architecture, planning, and iterative implementation, with checkpoints at every key decision so you stay in control.

Inspired by Scrum, Kanban, the V-model, and lean practices. Works for any app type: CLI tools, web apps, desktop apps, mobile apps, backend services, distributed systems.

---

## How it works

The pipeline runs as a set of **slash commands** inside Claude Code. Once the plugin is installed, the commands are available in every Claude Code session under the `/agile-dev:` namespace.

When you run a pipeline command, Claude acts as an orchestrator: it interviews you, produces plans and specs, waits for your approval at every major step, and then implements the work — all within a single conversation (or split across short sessions, since each phase runs independently).

All outputs (vision, architecture, backlog, specs, test cases, retrospectives) are saved as markdown files in a `.project-artifacts/` folder inside your project, so the pipeline survives session restarts and you can review everything at any time.

### The three modes

| Command | When to use |
|---|---|
| `/agile-dev:start` | Building something new from scratch |
| `/agile-dev:improve` | Improving or extending an existing codebase |
| `/agile-dev:change` | A single bounded change (feature, refactor, bug fix) without full foundation phases |

Modes `start` and `improve` share the same iteration loop once the foundation is established. Mode `change` is a lightweight path for one-off work.

### What a session looks like

```
You:    /agile-dev:start a CLI tool that converts CSV files to JSON

Claude: Starting Vision
        What problem does this solve? Who is the primary user?

You:    developers who need to quickly transform data files in scripts

Claude: [asks 2–3 more focused questions]
        ...produces a Vision Statement...
        Please review the above. Reply APPROVE to continue, or describe what needs to change.

You:    APPROVE

Claude: Starting Architecture
        [proposes architecture, asks about preferences]
        ...
```

Every time Claude produces a plan, spec, or decision, it stops and asks for your approval before continuing. You can always redirect, ask for changes, or add context.

### One phase per session

The iteration loop runs **one phase per `/agile-dev:iterate` invocation**. This keeps each Claude session small and token-efficient, and lets you pause between phases to think or run real work in another window.

| Phase | What you review |
|---|---|
| Vision | Vision statement, target users, constraints |
| Architecture | Architecture, tech stack, infrastructure decisions |
| Backlog | Full epic backlog with priorities |
| Refinement | Detailed spec and acceptance criteria for the current epic |
| Decomposition | Task breakdown by role |
| Test Plan | Acceptance test scenarios — each tagged with **level** (Unit/Component/Contract/System-integration/E2E) and **type** (UI/API/Protocol/CLI/File-batch) — written before any code |
| Development | Implementation + in-process tests (Unit/Component); self-review passed |
| Verification | Out-of-process tests against the running application (System-integration, E2E, out-of-process Contract). E2E type follows architecture — UI, API, protocol, or multi-channel |
| Integration | Production build, smoke test of the assembled app, demo readiness |
| Retrospective | Findings and backlog updates |

---

## Prerequisites

1. **Claude Code** installed and set up. If you haven't done this yet, follow the official guide: https://docs.anthropic.com/claude-code
2. A Claude Code account with an active session.

That's it — no other tools required.

---

## Installation

The pipeline is distributed as a Claude Code plugin. Installation is two commands inside any Claude Code session.

### Step 1 — Add the marketplace

```
/plugin marketplace add mgruszczynski/agile-dev-pipeline
```

This registers the GitHub repository as a plugin source.

### Step 2 — Install the plugin

```
/plugin install agile-dev@agile-dev
```

That's it. The seven commands are now available in every Claude Code session:

- `/agile-dev:start`
- `/agile-dev:improve`
- `/agile-dev:change`
- `/agile-dev:iterate`
- `/agile-dev:status`
- `/agile-dev:release` — bundle iterations into a versioned release (MVP-first)
- `/agile-dev:revise` — revise a foundation phase (Vision / Architecture / Backlog) when Retrospective flags it

### Updating

When a new version of the pipeline is released, update with:

```
/plugin update agile-dev
```

Updates handle file removals cleanly — orphaned files from older versions are pruned automatically.

### Uninstalling

```
/plugin uninstall agile-dev
```

---

## Usage

### Starting a new project

Open a terminal in your project folder and start a Claude Code session, then run:

```
/agile-dev:start <brief description of what you want to build>
```

Example:
```
/agile-dev:start a web app that lets teams track their weekly goals and celebrate completions
```

Claude will begin the foundation phase, asking clarifying questions one at a time.

### Improving an existing project

Navigate to the existing project folder, start Claude Code, and run:

```
/agile-dev:improve <description of what the system should do or become>
```

Example:
```
/agile-dev:improve add user authentication and a REST API to the existing data processing tool
```

Claude will first read and analyse your codebase before asking any questions, then propose a delta plan based on what already exists.

### A single bounded change

For a one-off feature, refactor, or bug fix that doesn't warrant the full foundation flow:

```
/agile-dev:change <description of the change>
```

Example:
```
/agile-dev:change add CSV export to the reports page
```

Goes through Refinement → Decomposition → Test Plan → Development → Verification → Integration → Retrospective for that single change only.

### Running the next iteration phase

After the foundation (Vision, Architecture, Backlog, Environment) is complete, drive each phase with:

```
/agile-dev:iterate
```

Each invocation runs **exactly one phase**, then stops with an instruction to run `/agile-dev:iterate` again to continue. This keeps each session small.

To work on a specific epic out of priority order:

```
/agile-dev:iterate <epic name>
```

### Checking status

At any point — including after restarting a session — you can check where you are:

```
/agile-dev:status
```

Claude will read `.project-artifacts/state.md` and report the current phase, current epic, remaining backlog, and what comes next.

### Resuming after a restart

Just open Claude Code in the same project folder and run `/agile-dev:iterate` (or `/agile-dev:start` / `/agile-dev:improve`) again. The pipeline reads `.project-artifacts/state.md` automatically and picks up from where it left off.

---

## Project files

After the pipeline has run for a while, your project will contain a `.project-artifacts/` folder:

```
.project-artifacts/
  state.md                        ← current position in the pipeline
  timeline.md                     ← per-iteration log
  ana-analysis.md                 ← codebase analysis (improve mode only)
  f1-vision.md                    ← approved vision and goals
  f2-architecture.md              ← approved architecture decisions
  f3-backlog.md                   ← epic backlog
  iterations/
    001-<epic-name>/              ← split iterations use 001-A / 001-B
      i1-spec.md                  ← detailed spec and acceptance criteria
      i2-tasks.md                 ← task breakdown by role
      i3-test-plan.md             ← acceptance test scenarios (test plan)
      i4-dev.md                   ← development summary (in-process tests)
      i5-verify.md                ← verification result (out-of-process tests)
      i6-int.md                   ← integration result (build, smoke, demo)
      i7-retro.md                 ← retrospective notes
  releases/
    v1.0.0.md                     ← release notes (created by /agile-dev:release)
  changes/
    <change-slug>/                ← /agile-dev:change outputs
      change-state.md
      spec.md
      tasks.md
      test-plan.md
      retro.md
CHANGELOG.md                      ← root of project; appended at iteration close
```

These files are yours — you can read, edit, and commit them alongside your code.

The pipeline also generates `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, and `.claude/settings.json` during the Environment phase, so all subsequent work runs inside a reproducible container.

---

## What the pipeline does not do

- It does not push code, open pull requests, or deploy anything without your explicit instruction.
- It does not skip checkpoints — every plan and spec requires your approval before implementation begins.
- It does not make architectural decisions unilaterally — proposals always go through the Architecture phase with your review.

---

## Repository layout

For contributors or anyone curious about the plugin internals:

```
agile-dev-pipeline/
  .claude-plugin/
    plugin.json                   ← plugin manifest
    marketplace.json              ← marketplace listing (this repo serves as its own marketplace)
  commands/
    start.md
    improve.md
    change.md
    iterate.md
    status.md
    release.md
    revise.md
  pipeline/
    analysis.md
    vision.md
    architecture.md
    backlog.md
    environment.md
    refinement.md
    decomposition.md
    test-plan.md
    development.md
    verification.md
    integration.md
    retrospective.md
    definitions.md                ← Definition of Ready / Testability / Done
```

The commands reference phase definitions via `${CLAUDE_PLUGIN_ROOT}/pipeline/<phase>.md`.

---
description: Run a single bounded change (feature, refactor, bug fix) through the pipeline. For projects with an existing pipeline, the change becomes the next iteration. For projects without one, it runs as a standalone change.
---

Single-change runner. Detects whether the project has an existing pipeline and routes accordingly: pipeline projects get a new iteration in the main history; standalone projects get a lightweight change track.

---

## Step 1 — Understand the change

`$ARGUMENTS` is the change description. If empty, ask: `What change do you want to make? One or two sentences.`

---

## Step 2 — Pipeline detection

Read `.project-artifacts/state.md`.

**Case A — Pipeline exists, no iteration in flight** (`state.md` present, all foundation phases ✓, `current_phase: Idle`):

> `This project has an existing pipeline (iteration <N> was the last). Add this change as a new backlog epic and run it as iteration <N+1>? (yes / standalone)`
> - **yes** — the change becomes part of the project's iteration history, same flow as `/agile-dev:iterate`.
> - **standalone** — run as a separate change outside the iteration history (use when the change is a hotfix or experiment that shouldn't touch the backlog).

If **yes**: proceed to *Pipeline path* below.
If **standalone**: proceed to Step 3.

**Case B — Pipeline exists, iteration in flight** (`state.md` present, foundation ✓, `current_phase` is an iteration phase):

> `Iteration is in progress: epic **<current_epic>** at phase **<current_phase>**. Choose: 1. Pause iteration, run change standalone. 2. Absorb change into current iteration (recommended if in scope). 3. Cancel.`

- **Pause:** record `paused_iteration: <epic> @ <phase>` at top of `state.md`. Proceed to Step 3 (standalone).
- **Absorb:** stop. Say `Resume the iteration with /agile-dev:iterate and fold the change into the current phase.`
- **Cancel:** stop.

**Case C — No pipeline** (`state.md` absent or foundation incomplete):

Proceed directly to Step 3 (standalone).

---

## Pipeline path — add epic and run as iteration

1. **Determine the next iteration number** from `state.md` (increment the `iteration` counter by 1 for display; do not write yet — Step 4 of iterate does that).

2. **Add the epic to the backlog:**
   - Choose a slug from the change description (lowercase, hyphens).
   - Append to `f3-backlog.md` as a new epic detail block. Use the change description as the epic description. Size: `M` (default; user can adjust). Priority: `P1`. Status: `TODO`.
   - Add a corresponding row to the Backlog table in `state.md`.

3. **Set the iteration state:**
   - Set `current_epic` in `state.md` to the new epic name.
   - Set `current_phase: Refinement`.
   - Create the iteration directory: `iterations/<NNN>-<slug>/`.

4. **Load and follow `${CLAUDE_PLUGIN_ROOT}/commands/iterate.md` from Step 3** (phases only — Step 1, 2, and the bundle algorithm are already done; the epic is picked). Run all phases (Refinement → Decomposition+Plan → Development → Verification → Integration) exactly as the iterate command would. Artifacts go to `iterations/<NNN>-<slug>/` as normal iteration files (`i1-spec.md`, `i2-plan.md`, `i3-outcome.md`). Step 4 (close the iteration) runs at the end and updates `state.md` and CHANGELOG as for any iteration.

---

## Step 3 — Standalone: check for in-flight change

Check `.project-artifacts/changes/*/change-state.md` for `status: IN_PROGRESS`.

- Found: ask `Change **<title>** is in progress at phase **<phase>**. Continue or start new? (continue/new)`. Resume or start fresh.
- Not found: proceed.

---

## Step 4 — Standalone: policy

Read `.project-artifacts/policy.md`. If missing, ask the user to configure five knobs (same as `/agile-dev:start` Step 0). Idempotent — no-ops if the file exists.

---

## Step 5 — Standalone: git check + focused analysis

### 5a — Git check

Run `git rev-parse --git-dir 2>/dev/null`.

- **Git present:** proceed.
- **No git:** ask:

  > `This directory is not a git repository. Options: 1. Initialise git here (commit current state as a baseline). 2. Stop.`

  - **1:** `git init`, stage all, commit `chore: baseline before agile-dev change`. Continue.
  - **2:** stop.

### 5b — Focused analysis

Read only what is relevant to this change. Do not run a full Analysis.

1. Identify affected modules / packages / files.
2. Read them for: existing structure & conventions; current test coverage; TODO/FIXME; dependencies on other modules.
3. Ask the user only for what can't be determined from code.

Produce a brief summary: affected files; conventions to follow; existing coverage; gotchas / constraints for Refinement.

---

## Step 6 — Standalone: run phases continuously

**Load policy** from `state.md` or defaults. Apply same overrides as `/agile-dev:iterate`.

Slug = lowercase, hyphens. All outputs to `.project-artifacts/changes/<slug>/`.

Create `change-state.md`:
```markdown
# Change State

title: <change title>
status: IN_PROGRESS
current_phase: Refinement
slug: <slug>
```

Run phases forward in one session. After each phase completes, advance `current_phase` in `change-state.md` and run the next. Do not ask the user to re-invoke `/agile-dev:change`.

### Refinement

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/refinement.md`.

**Do:** Tight scope: one change, not a roadmap. Interactive Q&A on what changes (before vs after), out-of-scope, edge cases, backwards compatibility. Delegate spec drafting to a subagent.

**Save:** `.project-artifacts/changes/<slug>/spec.md`

**⛳ CHECKPOINT:** Present spec; wait for APPROVE.

---

### Decomposition + Plan

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/decomposition.md`; `spec.md`.

**Do:** Generate proportionate task list — a small refactor should not produce 15 tasks. Immediately run Test Plan (load `${CLAUDE_PLUGIN_ROOT}/pipeline/test-plan.md`). Skip Test Plan when `test_coverage = none`.

**Save:** `.project-artifacts/changes/<slug>/plan.md` (Tasks section + Test Scenarios section)

**Checkpoint — conditional:**
- Auto-continue if tasks map cleanly to spec, roles unambiguous, no scope added, and every AC has a scenario.
- Otherwise ⛳ CHECKPOINT: present `plan.md`; wait for APPROVE.

---

### Development

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/development.md`; `spec.md`, `plan.md`.

1. Baseline in-process suite. Pre-existing failures = separate tasks.
2. TDD: failing tests first, implement, refactor.
3. In-process levels only. Wire external interfaces for Verification.
4. Commit small and often. No hardcoded credentials.
5. Self-review checklist.

**No checkpoint.** Write Development section to `.project-artifacts/changes/<slug>/outcome.md`.

---

### Verification

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/verification.md`; `spec.md`, `plan.md`.

Stand up test environment. Stub external third parties. Implement and run all System-integration + E2E + out-of-process Contract scenarios as test files. No chat-driven `curl`.

**Append** Verification section to `outcome.md`. No checkpoint.

---

### Integration

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/integration.md`; `spec.md`, `outcome.md`.

Build, prepare `.env`, start app, brief smoke, confirm Verification results. Append Integration section to `outcome.md`.

**Checkpoint — conditional:**
- Auto-continue when build green + Verification green + every AC covered.
- Otherwise ⛳ CHECKPOINT: present `outcome.md`; wait for APPROVE.

---

## Step 7 — Close the standalone change

After Integration approved:

1. `change-state.md`: `status: DONE`, `current_phase: DONE`.
2. Report: `Change **<title>** is complete.` List files changed and tests added.
3. If `.project-artifacts/state.md` exists, offer: `Add this to the project backlog as a completed epic for the record? (yes/no)`.

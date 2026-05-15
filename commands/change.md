---
description: Run a single bounded change (feature, refactor, bug fix) through the pipeline without the foundation phases
---

Single-change runner. Same rigour as a full iteration, no foundation phases. Runs forward through every phase in one session, stopping only at ⛳ checkpoints.

---

## Step 0 — Plugin self-permissions (one-time per user)

Before reading any pipeline files, ensure the user has authorised reads of this plugin's directory in their user settings. Two rules together: narrow + broad. Both are needed because Claude Code's permission matcher inconsistently honours broad `**` rules for the plugin dir. Idempotent — silently no-ops once both rules are present.

1. Check whether both rules exist:
   ```
   grep -qF 'plugins/cache/agile-dev/**' ~/.claude/settings.json 2>/dev/null && \
     grep -qF 'plugins/**' ~/.claude/settings.json 2>/dev/null
   ```
   Exit 0 → both rules present, skip the rest of Step 0.

2. Otherwise resolve `$HOME` and ask:

   > `Without permission rules, every read of this plugin's pipeline files will prompt for approval. Add these two rules to ~/.claude/settings.json?`
   > - `Read(<HOME>/.claude/plugins/cache/agile-dev/**)` — narrow
   > - `Read(<HOME>/.claude/plugins/**)` — broad
   >
   > `One-time setup. (yes / no)`

3. **yes** → Edit `~/.claude/settings.json` to ensure both rules are in `permissions.allow` (create file / keys / rules as needed; idempotent on existing rules). Confirm: `Permission rules added.`
4. **no** → Continue. Say: `Proceeding without the rules. You will be prompted per pipeline file.`
5. **Malformed JSON** → do not edit. Say: `~/.claude/settings.json is malformed; please fix manually. Skipping.`

---

## Step 1 — Understand the change

`$ARGUMENTS` is the change description. If empty, ask: `What change do you want to make? One or two sentences.`

---

## Step 2 — Check for in-flight work

### 2a — Iteration in progress?

If `.project-artifacts/state.md` exists and `current_epic` is set with `current_phase` not `Idle` / empty / legacy `Backlog`, an iteration is in flight. Ask:

> `Iteration is in progress: epic **<current_epic>** at phase **<current_phase>**. Choose: 1. Pause iteration, run change. 2. Absorb change into current iteration (recommended if in scope). 3. Cancel.`

- **Pause:** record `paused_iteration: <epic> @ <phase>` at top of `state.md` (or in `state-paused.md`). Proceed.
- **Absorb:** stop. Say `Resume the iteration with /agile-dev:iterate and fold the change into the current phase.`
- **Cancel:** stop.

### 2b — Change in progress?

Check `.project-artifacts/changes/*/change-state.md` for `status: IN_PROGRESS`.

- Found: ask `Change **<title>** is in progress at phase **<phase>**. Continue or start new? (continue/new)`. Resume or start fresh.
- Not found: proceed.

---

## Step 2.5 — Pipeline policy (one-time per project)

Configure three policy knobs for this project: autonomy, detail, test_coverage. Stored at `.project-artifacts/policy.md`. Idempotent — silently no-ops once the file exists.

1. Check `.project-artifacts/policy.md`:
   - **Exists:** print `Policy: <autonomy> / <detail> / <test_coverage>. Edit .project-artifacts/policy.md to change.` Skip the rest of Step 2.5.
   - **Missing:** continue to step 2.

2. Show the three knobs with recommended defaults; ask the user to pick:

   > **Autonomy** — how often the pipeline pauses for your approval:
   > - `user-driven` — every ⛳ checkpoint pauses.
   > - `semi-automatic` (recommended default) — conditional checkpoints auto-skip when straightforward.
   > - `ai-driven` — only Vision pauses. Prototypes / exploratory work.
   >
   > **Detail** — how verbose artifacts are:
   > - `full` (recommended default), `sparse`, `minimal`.
   >
   > **Test coverage** — how much testing:
   > - `thorough` (recommended default), `minimal`, `none` (skips Test Plan + Verification).
   >
   > Reply with three values (e.g. `semi-automatic full thorough`) or press Enter for the recommended defaults.

3. Parse + validate.

4. **Risky-combination confirmation:** if `autonomy = ai-driven` AND `test_coverage = none`, ask:
   > `ai-driven + no tests = no human approvals (except Vision) AND no test gate. Throwaway prototypes only. Confirm? (yes / no)`
   On no, return to step 2.

5. Create `.project-artifacts/` if missing. Write `.project-artifacts/policy.md`:

   ```markdown
   # Pipeline Policy

   autonomy: <chosen>
   detail: <chosen>
   test_coverage: <chosen>

   ## Notes
   <empty>
   ```

6. Confirm: `Policy set: <autonomy> / <detail> / <test_coverage>.`

---

## Step 3 — Git check, then focused codebase analysis

### 3a — Git check

Run `git rev-parse --git-dir 2>/dev/null`. The pipeline assumes git for commits, blame, history, and recovery flows.

- **Git present:** proceed to 3b.
- **No git:** existing-codebase change without git is surprising. Ask:

  > `This directory is not a git repository, which is unusual for a change against an existing codebase. Options: 1. Initialise git here (commit current state as a baseline). 2. Stop — I'm in the wrong directory or need to clone the repo first.`

  - **1 — init:** `git init`, stage all, commit with `chore: baseline before agile-dev change`. Continue.
  - **2 — stop:** halt. Say `Stopped. Cd to the right repo (or clone it), then re-run /agile-dev:change.`

### 3b — Focused analysis

Read only what is relevant to this change. Do not run a full Analysis.

1. Identify affected modules / packages / files.
2. Read them for: existing structure & conventions; current test coverage; TODO/FIXME in the area; dependencies on other modules.
3. Ask the user only for what can't be determined from code: design decisions, business rules, constraints.

Produce a brief summary (not a full Analysis doc): affected files; conventions to follow; existing coverage; gotchas / constraints for Refinement.

---

## Step 4 — Environment check

- `.devcontainer/devcontainer.json` exists: ask `Already inside the dev container? (yes/no)`. If no, instruct user to reopen in container.
- No `.devcontainer/`: load `${CLAUDE_PLUGIN_ROOT}/pipeline/environment.md`, detect stack from dependency manifests, generate `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, project `.claude/settings.json`. Wait for user to reopen in container.

⛳ CHECKPOINT Environment: user confirms inside the dev container.

---

## Step 5 — Run the change phases continuously

**Load policy.** Read `.project-artifacts/policy.md` once at session start. Same overrides as `/agile-dev:iterate`:
- `autonomy = user-driven` → every ⛳ pauses; conditional auto-skip / auto-continue disabled.
- `autonomy = semi-automatic` → phase-specific rules apply.
- `autonomy = ai-driven` → all checkpoints auto-continue except Vision (not part of a change anyway). Retrospective auto-completes.
- `test_coverage = none` → **skip Test Plan and Verification phases**. Change sequence becomes Refinement → Decomposition → Development → Integration → Retrospective. Don't write `test-plan.md` or `verify.md` in the change directory.
- `detail` → passed through to each phase per its Policy effects section.

If `policy.md` is missing, default to `semi-automatic / full / thorough` and print a one-line note.

Load each phase file as you reach that phase. Run phases forward in one session. After each phase ends (checkpoint APPROVE, auto-continue, or no-checkpoint completion): advance `current_phase` in `change-state.md` and run the next phase (apply test_coverage override when choosing next). Do not ask the user to re-invoke `/agile-dev:change`. The loop pauses only at a ⛳ CHECKPOINT or when the change closes at Retrospective.

**Context efficiency:** skip Read calls for files already in this session's context (earlier phase wrote or read them).

### Slug and directory

Slug = lowercase, hyphens, no spaces. All outputs to `.project-artifacts/changes/<slug>/`.

Create `change-state.md`:

```markdown
# Change State

title: <change title>
status: IN_PROGRESS
current_phase: Refinement
slug: <slug>
```

---

### Refinement [INTERACTIVE]

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/refinement.md`.

**Do:** Tight scope: one change, not a roadmap. Interactive Q&A focused on what changes (before vs after), out-of-scope, edge cases, backwards compatibility. Delegate spec drafting to a subagent.

**Save:** `.project-artifacts/changes/<slug>/spec.md`

**⛳ CHECKPOINT:** Present spec; wait for APPROVE.

---

### Decomposition

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/decomposition.md`; `spec.md`.

**Do:** Generate proportionate task list — a small refactor should not produce 15 tasks. For UI changes: ≥1 DESIGN task + ≥1 E2E scenario of type UI. For backend / protocol-only: the equivalent E2E task is API / Protocol / CLI / File-batch typed.

**Save:** `.project-artifacts/changes/<slug>/tasks.md`

**Checkpoint — conditional:**
- Auto-continue if tasks map cleanly to spec, roles unambiguous, no scope added.
- Otherwise ⛳ CHECKPOINT: present, wait for APPROVE.

---

### Test Plan

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/test-plan.md`; `spec.md`.

**Do:** BDD scenarios in plain language. Tag level + type per scenario. Regression scenarios for behaviour this change touches. E2E type follows architecture — not implicitly UI.

**Save:** `.project-artifacts/changes/<slug>/test-plan.md`

**⛳ CHECKPOINT:** Present test plan; wait for APPROVE.

---

### Development

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/development.md`; `spec.md`, `tasks.md`, `test-plan.md`.

**Do:**
1. Baseline: run existing in-process suite. Pre-existing failures = separate tasks; do not silently proceed.
2. TDD: failing in-process tests first, then implementation, then refactor.
3. In-process levels only (Unit / Component / in-process Contract). Out-of-process belongs to Verification.
4. Wire up external interfaces for Verification.
5. Commit small and often.
6. Env vars only — no hardcoded credentials.
7. Self-review checklist.
8. Subagents for independent parallel tasks.

**No checkpoint.** Save a brief summary (files changed, in-process tests, decisions) into `change-state.md` or a `dev.md` in the change directory.

---

### Verification

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/verification.md`; `spec.md`, `test-plan.md`.

**Do:** Stand up test environment. Stub external third parties via real mock-server processes. Implement and run every System-integration + E2E + out-of-process Contract scenario **as test files** in the project's framework — do not chat-drive `curl`/etc. Stabilise flakes by root-causing.

**Save:** `verify.md` — environment & reproduction; stubs; scenarios by level/type with AC; run results; quarantined items; AC coverage table.

**No checkpoint.**

---

### Integration

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/integration.md`; `spec.md`, `verify.md`.

**Do:**
1. Build (production command).
2. Prepare `.env`.
3. Start app; verify service connections.
4. Brief manual smoke of the affected journey.
5. Confirm `verify.md`: all non-quarantined passed; every AC traces to a passing scenario.

**Checkpoint — conditional:**
- Auto-continue when build green + Verification all green + every AC covered. Announce `Integration green — continuing with Retrospective.`
- Otherwise ⛳ CHECKPOINT: present build / smoke / AC table + `verify.md`; wait for APPROVE.

---

### Retrospective [INTERACTIVE]

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/retrospective.md`.

**Do:** Brief and proportionate to the change. Only items that drive a concrete change.

**Save:** `.project-artifacts/changes/<slug>/retro.md`

**⛳ CHECKPOINT — change boundary.** Always stops here. Present action items (or `No follow-up needed`); wait for APPROVE.

---

## Step 6 — Close the change

After Retrospective is approved:

1. `change-state.md`: `status: DONE`, `current_phase: DONE`.
2. Report: `Change **<title>** is complete.` List files changed and tests added.
3. If `.project-artifacts/state.md` (full pipeline) exists, offer: `Record this change as a completed epic in the backlog? (yes/no)`.

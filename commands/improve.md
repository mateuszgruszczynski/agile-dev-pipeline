---
description: Start the agile-dev pipeline for an existing codebase (Analysis → Vision → Architecture → Backlog → Environment in delta mode)
---

You are the pipeline orchestrator for an **existing codebase improvement**. Your job is to drive the user through the Foundation phases of the App Development Pipeline, starting from the Analysis phase rather than Vision.

Each phase definition lives in its own file under `${CLAUDE_PLUGIN_ROOT}/pipeline/`. Load each file only when entering that phase — do not load all phase files upfront.

| Phase | File |
|---|---|
| Analysis | `${CLAUDE_PLUGIN_ROOT}/pipeline/analysis.md` |
| Vision | `${CLAUDE_PLUGIN_ROOT}/pipeline/vision.md` |
| Architecture | `${CLAUDE_PLUGIN_ROOT}/pipeline/architecture.md` |
| Backlog | `${CLAUDE_PLUGIN_ROOT}/pipeline/backlog.md` |
| Environment | `${CLAUDE_PLUGIN_ROOT}/pipeline/environment.md` |

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

## Step 0.5 — Pipeline policy (one-time per project)

Configure three policy knobs for this project: autonomy, detail, test_coverage. Stored at `.project-artifacts/policy.md`. Idempotent — silently no-ops once the file exists.

1. Check `.project-artifacts/policy.md`:
   - **Exists:** print `Policy: <autonomy> / <detail> / <test_coverage>. Edit .project-artifacts/policy.md to change.` Skip the rest of Step 0.5.
   - **Missing:** continue to step 2.

2. Show the three knobs with recommended defaults; ask the user to pick:

   > **Autonomy** — how often the pipeline pauses for your approval:
   > - `user-driven` — every ⛳ checkpoint pauses.
   > - `semi-automatic` (recommended default) — conditional checkpoints auto-skip when straightforward; mandatory still pause.
   > - `ai-driven` — only Vision pauses. Prototypes / exploratory work.
   >
   > **Detail** — how verbose artifacts are:
   > - `full` (recommended default) — specs with rationale, ACs with out-of-scope, tasks with dependencies.
   > - `sparse` — specs without lengthy rationale.
   > - `minimal` — one-line outputs; just enough to drive the next phase.
   >
   > **Test coverage** — how much testing the pipeline produces:
   > - `thorough` (recommended default) — BDD per AC, regression for touched code.
   > - `minimal` — one happy-path scenario per AC; skip edge cases.
   > - `none` — skip Test Plan + Verification entirely. Manual smoke only.
   >
   > Reply with three values (e.g. `semi-automatic full thorough`) or press Enter for the recommended defaults.

3. Parse + validate. Repeat with error on invalid values.

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

## Step 1 — Understand the goal

The user wants to improve, extend, or refactor an existing codebase.

Arguments provided: $ARGUMENTS

If arguments were given, use them as the description of what the system should do or become. If no arguments were given, ask:
> "What should this system do or become? Describe the desired end state in a few sentences."

Wait for the answer before proceeding.

---

## Step 2 — Determine where we are

### 2a — Git check

Run `git rev-parse --git-dir 2>/dev/null`. The pipeline assumes git throughout.

- **Git present:** proceed.
- **No git:** existing-codebase mode without git is surprising — usually means the user is working in a tarball, an unzipped archive, or the wrong directory. Ask:

  > `This directory is not a git repository, which is unusual for an existing codebase. Options: 1. Initialise git here (will commit current state as a baseline). 2. Stop — I'm in the wrong directory or need to clone the repo first.`

  - **1 — init:** run `git init`, stage everything, commit with message `chore: baseline before agile-dev pipeline`. Then continue.
  - **2 — stop:** halt. Say `Stopped. Cd to the right repo (or clone it), then re-run /agile-dev:improve.`

### 2b — Pipeline state

Check whether `.project-artifacts/state.md` exists:

- **Does not exist** → fresh analysis. Begin at **Analysis**.
- **Exists** → read it and resume from the phase marked as current. Greet the user with a one-line summary of where we are and what comes next.

---

## Step 3 — Analysis: Codebase Analysis

Load `${CLAUDE_PLUGIN_ROOT}/pipeline/analysis.md` and follow it precisely.

**Do not ask the user to explain things you can read directly.** Use available tools to:
- Explore the directory structure
- Read dependency/manifest files (package.json, go.mod, requirements.txt, Cargo.toml, pom.xml, etc.)
- Read key source files to understand components and responsibilities
- Identify existing test files and assess coverage
- Find TODO/FIXME comments and obvious tech debt
- Identify CI/CD configuration files

Ask the user only for:
- Business context behind existing design decisions
- Undocumented architectural choices
- Known pain points not visible in code
- Anything that cannot be determined from the codebase itself

Produce the Analysis output as defined in `analysis.md` and save to `.project-artifacts/ana-analysis.md`.

**⛳ CHECKPOINT Analysis:** Present the full analysis. Ask:
> "Please review the above. Does this accurately describe what exists? Reply **APPROVE** to continue, or describe what is wrong or missing."

---

## Step 4 — Foundation phases in delta mode

After Analysis is approved, run Vision → Architecture → Backlog. For each phase: load its file from the table above, follow the phase definition, and apply these delta-mode rules throughout:

- **Vision** (`vision.md`) — describe the desired end state. Use Analysis output to frame what is missing or needs to change. Do not re-describe what already works correctly.
- **Architecture** (`architecture.md`) — start from the C4 diagrams in Analysis. Describe only the changes: what to add, remove, or restructure. Flag any breaking changes to existing interfaces.
- **Backlog** (`backlog.md`) — seed epics from the gap between Analysis and Vision. Include REFACTOR, FIX, and MIGRATION epic types alongside FEATURE. Tech debt from Analysis becomes explicit epics with priority, not hidden scope.

Save outputs to:
- `.project-artifacts/f1-vision.md`
- `.project-artifacts/f2-architecture.md`
- `.project-artifacts/f3-backlog.md`

Apply the standard checkpoint protocol at each phase.

---

## Step 5 — Environment Readiness Check

After Backlog is approved, load `${CLAUDE_PLUGIN_ROOT}/pipeline/environment.md` and follow it:
- Read `.project-artifacts/f2-architecture.md` to determine the stack.
- Generate `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, and `.claude/settings.json`.
- Present the three files to the user and instruct them to reopen the project in the container.
- ⛳ CHECKPOINT Environment: user confirms they are inside the container. Mark `Environment ✓` in `state.md`.

**Stop here.** Say: "Foundation complete. Reopen the project in the dev container, then run `/agile-dev:iterate` to begin the first iteration (Refinement)."

Do **not** run iteration phases in this session. Each phase runs in its own session via `/agile-dev:iterate` to keep sessions small and token-efficient.

---

## File layout

```
.project-artifacts/
  state.md                            ← pipeline position, backlog, and per-iteration history
  policy.md                           ← pipeline policy: autonomy / detail / test_coverage (set once at Step 0.5)
  pipeline-feedback.md                ← append-only meta-feedback about the agile-dev pipeline itself (created on first entry)
  ana-analysis.md                     ← Analysis output (improve mode only)
  f1-vision.md
  f2-architecture.md
  f3-backlog.md
  iterations/
    001-<epic-slug>/                  ← split iterations use 001-A-<slug> / 001-B-<slug>
      i1-spec.md                      ← Refinement
      i2-tasks.md                     ← Decomposition
      i3-test-plan.md                 ← Test Plan
      i4-dev.md                       ← Development summary
      i5-verify.md                    ← Verification result (out-of-process tests)
      i6-int.md                       ← Integration result
      i7-retro.md                     ← Retrospective
  releases/
    v1.0.0.md                         ← release notes (created by /agile-dev:release)
CHANGELOG.md                          ← root of project; appended at iteration close, version-grouped at release
```

## State file

Use the same state file format as `/agile-dev:start` documents, with these differences for improve mode:
- `mode: improve`
- `current_phase: Analysis` as the starting value
- The Foundation phases enum line becomes: `Foundation phases: Analysis | Vision | Architecture | Backlog | Environment`
- Add `Analysis ✓ → .project-artifacts/ana-analysis.md` to the completed phases list once Analysis is approved.

---

## Checkpoint protocol

At every ⛳ CHECKPOINT — full stop. Present the output, then ask:
> "Please review the above. Reply **APPROVE** to continue, or describe what needs to change."

Never proceed past a checkpoint without explicit approval.

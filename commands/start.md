---
description: Start the agile-dev pipeline for a new project (Vision → Architecture → Backlog → Environment)
---

You are the pipeline orchestrator. Your job is to drive the user through the Foundation phases of the App Development Pipeline, then hand off to `/agile-dev:iterate` for the iteration loop.

Each phase definition lives in its own file under `${CLAUDE_PLUGIN_ROOT}/pipeline/`. Load each file only when entering that phase — do not load all phase files upfront.

| Phase | File |
|---|---|
| Vision | `${CLAUDE_PLUGIN_ROOT}/pipeline/vision.md` |
| Architecture | `${CLAUDE_PLUGIN_ROOT}/pipeline/architecture.md` |
| Backlog | `${CLAUDE_PLUGIN_ROOT}/pipeline/backlog.md` |
| Environment | `${CLAUDE_PLUGIN_ROOT}/pipeline/environment.md` |

---

## Step 0 — Plugin self-permissions (one-time per user)

Before reading any pipeline files, ensure the user has authorised reads of this plugin's directory in their user settings. Two rules are added together: a narrow scoped rule and a broader plugins-tree rule. Both are needed because Claude Code's permission matcher inconsistently honours broad `**` rules for the plugin install dir — the explicit narrow rule is a safety net. Idempotent — silently no-ops once both rules are present.

1. Check whether both rules already exist:
   ```
   grep -qF 'plugins/cache/agile-dev/**' ~/.claude/settings.json 2>/dev/null && \
     grep -qF 'plugins/**' ~/.claude/settings.json 2>/dev/null
   ```
   Exit 0 → both rules present, skip the rest of Step 0.

2. Otherwise resolve `$HOME` (`bash -c 'echo $HOME'`) and ask the user:

   > `Without permission rules, every read of this plugin's pipeline files will prompt for approval. Add the following two rules to ~/.claude/settings.json?`
   > - `Read(<HOME>/.claude/plugins/cache/agile-dev/**)` — narrow, scoped to this plugin
   > - `Read(<HOME>/.claude/plugins/**)` — broad, defense-in-depth for harness misses
   >
   > `One-time setup. (yes / no)`

3. **yes** → Edit `~/.claude/settings.json` to ensure both rules are in `permissions.allow`:
   - File missing → create it with `{"permissions": {"allow": ["Read(<HOME>/.claude/plugins/cache/agile-dev/**)", "Read(<HOME>/.claude/plugins/**)"]}}`.
   - `permissions` or `permissions.allow` missing → add the keys.
   - `permissions.allow` exists → append each missing rule (skip rules already present, idempotent).
   Confirm: `Permission rules added to ~/.claude/settings.json.`
4. **no** → Continue. Say: `Proceeding without the rules. You will be prompted per pipeline file.`
5. **Malformed JSON** in `~/.claude/settings.json` → do not edit. Say: `~/.claude/settings.json is malformed; please fix manually. Skipping plugin permission setup.`

---

## Step 0.5 — Pipeline policy (one-time per project)

Configure three policy knobs for this project: autonomy (how often we pause for approval), detail (how verbose artifacts are), and test_coverage (how much testing to produce). Stored at `.project-artifacts/policy.md`. Idempotent — silently no-ops once the file exists.

1. Check `.project-artifacts/policy.md`:
   - **Exists:** print one-line summary `Policy: <autonomy> / <detail> / <test_coverage>. Edit .project-artifacts/policy.md to change.` Skip the rest of Step 0.5.
   - **Missing:** continue to step 2.

2. Show the three knobs with recommended defaults; ask the user to pick:

   > **Autonomy** — how often does the pipeline pause for your approval?
   > - `user-driven` — every ⛳ checkpoint pauses; explicit approval for everything.
   > - `semi-automatic` (recommended default) — conditional checkpoints auto-skip when work is straightforward; mandatory checkpoints still pause.
   > - `ai-driven` — only Vision pauses; the rest runs without asking. For prototypes / exploratory work.
   >
   > **Detail** — how verbose are produced artifacts?
   > - `full` (recommended default) — specs with rationale, ACs with out-of-scope, tasks with dependencies.
   > - `sparse` — specs without lengthy rationale; just the facts.
   > - `minimal` — one-line phase outputs; just enough to drive the next phase.
   >
   > **Test coverage** — how much testing does the pipeline produce?
   > - `thorough` (recommended default) — BDD scenarios per AC, regression for touched code, full pyramid.
   > - `minimal` — one happy-path scenario per AC; skip edge cases unless an AC names one.
   > - `none` — skip Test Plan + Verification entirely. Manual smoke only. Prototypes / spikes only.
   >
   > **Packaging** — when does the pipeline produce a runnable artifact (binary / jar / docker image / etc.) that you can copy to another machine and run?
   > - `each` (recommended default) — every Integration produces a packaged artifact in `dist/<NNN>-<slug>/`. Best when you want to ship or demo each iteration.
   > - `milestone` — package only when you run `/agile-dev:release` for a versioned release. Useful before MVP / during heavy churn when intermediate packages would just be noise.
   > - `final` — package only on explicit user request (`/agile-dev:release` with a flag, or manual). Quietest option; appropriate for early prototypes.
   >
   > **Iteration size** — how much work goes into one iteration? T-shirt sizes have point values (XS=1, S=1.7, M=3, L=5.2, XL=9, XXL=15.6); the bundler picks a set of epics summing close to this target.
   > - `xs` (1 pt), `s` (1.7), `m` (3), `l` (5.2), `xl` (9, recommended default), `xxl` (15.6).
   > - Larger = fewer checkpoints, more work per pause. Smaller = tighter feedback loops, more interruptions.
   >
   > Reply with five values (e.g. `semi-automatic full thorough each xl`) or press Enter for the recommended defaults.

3. Parse the response. Validate each value against its allowed set. If invalid, repeat the prompt with the error.

4. **Risky-combination confirmation:** if `autonomy = ai-driven` AND `test_coverage = none`, ask:

   > `Selected ai-driven + no tests. This means no human approvals (except Vision) AND no automated test gate. Code is produced with no test coverage and no checkpoint review. Suitable only for throwaway prototypes. Confirm? (yes / no)`

   On no, return to step 2.

5. Create `.project-artifacts/` if missing. Write `.project-artifacts/policy.md`:

   ```markdown
   # Pipeline Policy

   autonomy: <chosen>
   detail: <chosen>
   test_coverage: <chosen>
   packaging: <chosen>
   iteration_size: <chosen>

   ## Notes
   <empty — add reasons or context here, or change values directly above>
   ```

6. Confirm: `Policy set: <autonomy> / <detail> / <test_coverage> / <packaging> / iteration ~<iteration_size>. Stored in .project-artifacts/policy.md (edit by hand to change later).`

---

## Step 1 — Determine where we are

### 1a — Git check

Run `git rev-parse --git-dir 2>/dev/null` in the working directory. The pipeline assumes git throughout (commit-small rule, CHANGELOG, mid-iteration recovery, Verification committing test files), so resolve this before writing any artifacts.

- **Git present:** proceed.
- **No git:** offer to initialise. Greenfield default is yes — say:

  > `This directory is not a git repository. The pipeline requires git for commits, CHANGELOG, and recovery flows. Initialise it now? (yes / no)`

  - **yes:** run `git init`, then create a minimal `.gitignore` with:
    ```
    .env
    .env.local
    node_modules/
    dist/
    build/
    target/
    out/
    .DS_Store
    ```
    Stage and commit with message `chore: initialise repository`. Continue.
  - **no:** stop. Say `Git is required. Initialise a repo (or open the project from one), then re-run /agile-dev:start.`

### 1b — Pipeline state and artifact handling

Read `.project-artifacts/state.md` (if present) and check for foundation artifacts (`f1-vision.md`, `f2-architecture.md`, `f3-backlog.md`). Determine which of the five cases applies and act:

**Case 1 — Truly fresh** (no `state.md`, no foundation artifacts): initialise state (see State file format below) and begin at Vision.
- If the user provided an initial idea via `$ARGUMENTS`, use it as the seed for Vision.
- If no arguments, ask the user to describe what they want to build in one or two sentences.

**Case 2 — Orphaned artifacts** (no `state.md` but foundation artifacts exist): ambiguous origin. Stop and ask:

> `Found foundation artifacts (<list which ones>) but no state.md. Choose: 1. Reconstruct state.md from existing artifacts and resume. 2. Archive existing artifacts and start fresh. 3. Cancel.`

- **1 — Reconstruct:** write `state.md` marking every present artifact as ✓ in `Completed foundation phases`. `current_phase` becomes the first foundation phase whose artifact is missing. Greet and resume.
- **2 — Archive:** perform the archive action from Case 5 below, then begin at Vision.
- **3 — Cancel:** stop.

**Case 3 — Foundation in progress** (`state.md` present, at least one foundation phase not ✓): resume from `current_phase`. Existing ✓ artifacts are the base — do not regenerate them. Greet with a one-line summary.

**Case 4 — Foundation complete, iteration in flight** (`state.md` present, all foundation ✓, `current_phase` is an iteration phase): start is not the right tool. Stop and say:

> `Foundation is complete and iteration <NNN> (<epic>) is in flight at phase <current_phase>. Use /agile-dev:iterate to continue, /agile-dev:revise <phase> to refine a foundation phase, or finish / abandon the current iteration then re-run /agile-dev:start for a major rework.`

**Case 5 — Foundation complete, project at rest** (`state.md` present, all foundation ✓, `current_phase: Idle`): user is starting a major pivot. Existing project artifacts are project history.

> `Foundation is already complete. /agile-dev:start will treat this as a major pivot: existing project artifacts (state.md, f1-vision.md, f2-architecture.md, f3-backlog.md, iterations/, releases/, changes/) will be MOVED to .project-artifacts/archive/<YYYY-MM-DD-HHMMSS>/ as project history, then a fresh Foundation will begin. policy.md and pipeline-feedback.md stay in place. Continue? (yes / no)`

- **yes:**
  1. Create `.project-artifacts/archive/<YYYY-MM-DD-HHMMSS>/`.
  2. `mv` each of the listed files / directories into the archive, preserving structure.
  3. Write `archive-reason.md` in the archive dir: `Archived on <date> when user re-ran /agile-dev:start. Reason: major pivot — fresh foundation requested.`
  4. Proceed to Vision (Step 2 below).
- **no:** stop and say `Stopped. Use /agile-dev:revise <phase> for targeted foundation changes, or /agile-dev:iterate to start the next iteration.`

---

## Step 2 — Execute phases in order

Work through Vision → Architecture → Backlog → Environment. For each phase:

1. Announce which phase you are entering (e.g. "**Starting Architecture**").
2. **Load the phase file** for the current phase from the table above using the Read tool.
3. Follow the phase definition precisely.
4. For **[INTERACTIVE]** phases: ask the questions listed in the phase one topic at a time — do not dump all questions at once. Wait for the user's answer before asking the next.
5. Produce the output defined for that phase.
6. Save the output to the appropriate file (see File layout below).
7. Reach the **⛳ CHECKPOINT**: present the full output and ask:
   > "Please review the above. Reply **APPROVE** to continue, or describe what needs to change."
8. Revise and re-present until the user approves.
9. Update `.project-artifacts/state.md` to mark the phase complete and set the next phase as current.
10. Move to the next phase.

For **complex generation tasks** (writing a full architecture doc, a long backlog with detailed epic blocks) — use a subagent via the Agent tool to do the heavy lifting, then review and present the result yourself.

---

## File layout

All outputs are persisted as markdown files so the pipeline survives session restarts:

```
.project-artifacts/
  state.md                            ← pipeline position, backlog, and per-iteration history
  policy.md                           ← pipeline policy: autonomy / detail / test_coverage (set once at Step 0.5)
  pipeline-feedback.md                ← append-only meta-feedback about the agile-dev pipeline itself (created on first entry)
  f1-vision.md                        ← Vision output
  f2-architecture.md                  ← Architecture output
  f3-backlog.md                       ← Backlog output
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

Epic slug = lowercase, hyphens, no spaces (e.g. `user-authentication`, `csv-import`).
Iteration number is zero-padded to three digits, incrementing per completed epic.

---

## State file format

`.project-artifacts/state.md` must follow this exact format so `/agile-dev:status` and `/agile-dev:iterate` can parse it:

```markdown
# Pipeline State

status: IN_PROGRESS
mode: greenfield
version: unreleased
current_phase: <phase name>
current_epic: <epic name or "none">
iteration: <N>

## Phase enums

- Foundation phases: Vision | Architecture | Backlog | Environment
- Iteration phases: Idle | Refinement | Decomposition | Test Plan | Development | Verification | Integration | Retrospective

`Idle` means no iteration is in progress; `/agile-dev:iterate` sets this between iterations.

## Completed foundation phases
- Vision ✓ → .project-artifacts/f1-vision.md
- Architecture ✓ → .project-artifacts/f2-architecture.md
- Backlog ✓ → .project-artifacts/f3-backlog.md
- Environment ✓

## Backlog (copy from f3-backlog.md, keep in sync)
| Priority | Epic | Size | Status |
|---|---|---|---|
| P1 | User Authentication | M | DONE |
| P1 | CSV Import | S | IN_PROGRESS |
| P2 | Dashboard | L | TODO |

## Completed iterations
| # | Epics | Status | Closed | Notes | Retro |
|---|---|---|---|---|---|
| 001 | EP-1 User Authentication (XL) | DONE | YYYY-MM-DD | <one-line retro highlight, or "No plan changes", or abandonment reason> | iterations/001-user-authentication/i7-retro.md |
| 002 | EP-3 Search index (L) + EP-7 Filter UI (M) + EP-9 Pagination (M) | DONE | YYYY-MM-DD | Bundle, 11.2 pts | iterations/002-search-index/i7-retro.md |

## Releases
| Version | Date | Iterations | Notes |
|---|---|---|---|

## Foundation revisions
| Date | Phase | Reason | Triggered by |
|---|---|---|---|
```

Notes:
- `mode` is `greenfield` for projects started with `/agile-dev:start`, `improve` for `/agile-dev:improve`.
- `version` is `unreleased` until the first `/agile-dev:release`; thereafter it tracks the latest released version.
- The `Completed iterations` table is empty until the first iteration closes; `/agile-dev:iterate` appends rows at iteration close. Split iterations (mid-iteration recovery Tier 2) appear as `<NNN>-A` and `<NNN>-B` rows. The `Status` column is `DONE` for completed iterations and `ABANDONED` for Tier 3 closures. The `Notes` column carries a one-line retro highlight (or the abandonment reason). The `Epics` column lists every epic bundled into the iteration with its t-shirt size in parens; a bundle joins them with ` + `.
- The `Releases` and `Foundation revisions` tables stay empty until their respective commands run; keep the headings as placeholders so the format stays consistent.
- Update `status` to `COMPLETE` when all epics are `DONE`.

---

## Environment phase and handoff

After Vision + Architecture + Backlog are all approved, run the Environment phase:

1. Load `${CLAUDE_PLUGIN_ROOT}/pipeline/environment.md` and follow it.
   - Read `.project-artifacts/f2-architecture.md` to determine the stack.
   - Generate `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, and `.claude/settings.json`.
   - Present the three files to the user and instruct them to reopen the project in the container.
   - ⛳ CHECKPOINT Environment: user confirms they are inside the container. Mark `Environment ✓` in `state.md`.
2. **Stop here.** Say: "Foundation complete. Reopen the project in the dev container, then run `/agile-dev:iterate` to begin the first iteration (Refinement)."

Do **not** run iteration phases (Refinement, Decomposition, Test Plan, Development, Verification, Integration, Retrospective) in this session. Each of those runs in its own session via `/agile-dev:iterate` to keep sessions small and token-efficient.

---

## Checkpoint protocol

At every ⛳ CHECKPOINT — full stop. Never auto-approve. Never proceed speculatively.

Present the phase output, then ask exactly:
> "Please review the above. Reply **APPROVE** to continue, or describe what needs to change."

If the user requests changes: apply them, re-present the updated output, and ask again. Repeat until approved.

---

## Arguments

$ARGUMENTS

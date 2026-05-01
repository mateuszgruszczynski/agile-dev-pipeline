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

## Step 1 — Determine where we are

Check whether `.project-artifacts/state.md` exists:

- **Does not exist** → fresh project. Initialise state (see State file format below) and begin at **Vision**.
  - If the user provided an initial idea: `$ARGUMENTS` — use it as the seed for Vision. Skip re-asking for things already answered.
  - If no arguments: ask the user to describe what they want to build in one or two sentences, then begin Vision.
- **Exists** → read `.project-artifacts/state.md`, identify the current phase, and resume from there. Greet the user with a one-line summary of where we are and what comes next.

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
  state.md                            ← pipeline position and phase index
  timeline.md                         ← per-iteration log (created at first iteration close)
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
| # | Epic | Closed | Retro |
|---|---|---|---|
| 001 | User Authentication | YYYY-MM-DD | iterations/001-user-authentication/i7-retro.md |

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
- The `Completed iterations` table is empty until the first iteration closes; `/agile-dev:iterate` appends rows at iteration close. Split iterations (mid-iteration recovery Tier 2) appear as `<NNN>-A` and `<NNN>-B` rows.
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

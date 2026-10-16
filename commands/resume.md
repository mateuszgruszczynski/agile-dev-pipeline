---
description: Detect where this project's pipeline left off and continue from there — Foundation, iteration, or a standalone change — without having to know which command to run.
---

Resume runner. This command takes no arguments and makes no state-machine decisions of its own: it reads what's on disk, decides which existing command already owns that state, then loads and follows that command's own logic precisely from the right point. All the actual Case-detection lives in `start.md` / `improve.md` / `iterate.md` / `change.md` — this file only routes to it, so there is exactly one place each of those rules is defined.

If the user typed an idea or goal after `/agile-dev:resume`, ignore it — this command never starts anything new. If there's nothing to resume, say so and point at `/agile-dev:start` or `/agile-dev:improve` instead of guessing what the text meant.

**Communication style.** Enumerate, don't narrate — bullets and short declarative lines over flowing prose. Lead with the decision or the fact, not a preamble.

---

## Step 1 — Check for an in-flight standalone change first

Check `.project-artifacts/changes/*/change-state.md` for any file with `status: IN_PROGRESS`.

- **Found:** say `Found an in-progress standalone change: <title>, at phase <phase>. Resuming via /agile-dev:change.` Then **load `${CLAUDE_PLUGIN_ROOT}/commands/change.md` and follow it precisely from Step 3** (its own in-flight check) — it will find the same file and continue or ask to start new, exactly as if the user had typed `/agile-dev:change` themselves.
- **Not found:** proceed to Step 2.

This runs first because a standalone change tracks its own state independently of the main pipeline — a project can have a paused standalone change *and* a main pipeline at rest at the same time, and the change is almost always the more recent thing to pick back up.

---

## Step 2 — Check the main pipeline

Read `.project-artifacts/state.md`.

### 2a — No `state.md`

Check for orphaned foundation artifacts: `f1-vision.md`, `f2-architecture.md`, `f3-backlog.md`, `ana-analysis.md`.

- **None exist:** say `No pipeline found. Nothing to resume. Run /agile-dev:start <your idea> or /agile-dev:improve <your goal> to begin.` Stop.
- **Some exist:** this is the one case `/agile-dev:resume` can't fully resolve on its own — both `/agile-dev:start` and `/agile-dev:improve` handle orphaned artifacts identically (reconstruct / archive / cancel), but telling them apart matters for which one's Analysis-phase assumptions are correct. Check for `ana-analysis.md`:
  - **Present:** say `Found orphaned foundation artifacts from an improve-mode run. Resuming via /agile-dev:improve.` Load `${CLAUDE_PLUGIN_ROOT}/commands/improve.md` and follow it precisely from Step 1 (treat the orphaned-artifact recovery as `$ARGUMENTS`-equivalent — it will ask its own Case 2 question).
  - **Absent:** say `Found orphaned foundation artifacts with no Analysis file, so this looks like a greenfield /agile-dev:start run — resuming via /agile-dev:start. If this project actually began with /agile-dev:improve, cancel at the next prompt and run /agile-dev:improve instead; its recovery works the same way.` Load `${CLAUDE_PLUGIN_ROOT}/commands/start.md` and follow it precisely from Step 1.

### 2b — `state.md` present

Read `mode`, `current_phase`, the Foundation checkmarks, and the Backlog table's Status column.

- **Foundation incomplete** (any of Vision / Architecture / Backlog / Environment not ✓): say `Foundation in progress at <current_phase>. Resuming via /agile-dev:<start|improve>.` (pick the command from `mode: greenfield` → `start`, `mode: improve` → `improve`). Load that command's file and **follow it precisely from Step 1** — its own Case 3 (`state.md` present, a foundation phase not ✓) does the actual resume; do not re-derive which sub-case applies here.
- **Foundation complete, backlog fully `DONE`** (`status: COMPLETE`, or every backlog row `DONE`): say `Pipeline complete — nothing to resume. Run /agile-dev:status for the full picture, or /agile-dev:release if you haven't yet.` Stop.
- **Foundation complete, anything else** (an iteration phase in flight, or `Idle` with `TODO` epics remaining): say `Resuming via /agile-dev:iterate.` Load `${CLAUDE_PLUGIN_ROOT}/commands/iterate.md` and **follow it precisely from Step 1** — it already handles both "mid-iteration" and "pick the next epic bundle" correctly on its own.

---

## What this command deliberately does not do

- It does not duplicate any Case-detection logic from `start.md`, `improve.md`, `iterate.md`, or `change.md` — only enough file-existence checks to pick which one of those to hand off to. If one of those files' own logic ever changes, this file does not need to change with it, except where the checks above (which files exist, what counts as "complete") would also need updating.
- It does not accept or act on a seed idea, goal, or change description. That's what `/agile-dev:start`, `/agile-dev:improve`, and `/agile-dev:change` are for.
- It does not resolve the orphaned-artifacts ambiguity by asking the user up front — it makes the best guess available (via `ana-analysis.md`) and says so, because both commands' Case 2 behave the same way regardless, and the user can cancel and switch commands cheaply if the guess was wrong.

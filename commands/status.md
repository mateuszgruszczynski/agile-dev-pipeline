---
description: Report current agile-dev pipeline status (current phase, epic, backlog, completed iterations, next step)
---

Read `.project-artifacts/state.md`, then report the current pipeline state in a concise summary. Do not read any pipeline phase files — all information needed is in `state.md`.

If `.project-artifacts/state.md` does not exist, report: "No pipeline started yet. Run `/agile-dev:start <your idea>` (greenfield) or `/agile-dev:improve <goal>` (existing codebase) to begin." and stop.

---

Format the output as follows:

---

**Pipeline Status**

- **Overall status:** IN_PROGRESS / COMPLETE / NOT_STARTED
- **Mode:** greenfield / improve
- **Version:** <semver or "unreleased">
- **Current phase:** <phase name>
- **Current epic:** <name or "—">
- **Iteration:** <N>

**Foundation**

Render only the rows that apply to the project's mode. `improve` mode includes Analysis; `greenfield` does not.

- Analysis: ✓ done / ⏳ in progress / ○ not started   *(improve mode only)*
- Vision: ✓ done / ⏳ in progress / ○ not started
- Architecture: ✓ done / ⏳ in progress / ○ not started
- Backlog: ✓ done / ⏳ in progress / ○ not started
- Environment: ✓ done / ⏳ in progress / ○ not started

**Backlog**

Render the backlog table from `state.md`, including the Status column.

**Completed iterations**

If `state.md` has rows in the `Completed iterations` table, render that table. If not, report "No iterations completed yet."

**Releases**

If `state.md` has rows in the `Releases` table, render that table. If not, report "No releases yet."

**Foundation revisions**

If `state.md` has rows in the `Foundation revisions` table, render that table. If not, omit this section.

**Last completed phase:** <phase name> — <one-sentence summary of what was produced, drawn from state.md only>
**Next step:** <what happens next and what is needed from the user — e.g. "Run `/agile-dev:iterate` to continue with Decomposition" or "Foundation complete — reopen project in dev container and run `/agile-dev:iterate`">

---

## Consistency check

If anything in `state.md` looks inconsistent — flag it clearly so the user knows to investigate before continuing. Examples to check:
- A foundation phase marked `✓` but its expected output file (e.g. `f2-architecture.md`) is not listed.
- `current_phase` set to an iteration phase but `current_epic` is empty.
- `current_phase: Idle` but `current_epic` is non-empty.
- An epic listed as `IN_PROGRESS` in the backlog table that does not match `current_epic`.
- The legacy value `current_phase: Backlog` (from older state files) — treat as `Idle` and tell the user to update it.

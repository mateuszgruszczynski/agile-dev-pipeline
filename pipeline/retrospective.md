# Retrospective Phase

**Purpose:** Identify changes the iteration needs to drive into the plan / process / backlog. Output is an action list, not a narrative.

**Rule:** only document findings that lead to a concrete action. Nothing to change → output `No plan changes. Proceed to next iteration.`

**Review** — raise an item only if it requires a change:
- Backlog epics to add / remove / split / re-prioritise / re-scope.
- ACs that were unclear, wrong, or missing → update and note the fix.
- Architectural decisions that need revisiting → trigger a new Architecture checkpoint before the next iteration.
- New risks, dependencies, or blockers affecting the backlog.
- Project-specific process adjustments that should change how this team applies the pipeline.

**Output:**
- A list of concrete actions: `Add epic X`, `Split Y into Y1 and Y2`, `Revise AC-3 on Z`, `Revisit Architecture decision on schema`.
- Nothing to change: one line — `No plan changes. Proceed to next iteration.`

Do not include: what went well, what was hard, effort commentary, feelings — unless it produces an action recorded above.

**⛳ CHECKPOINT Retrospective:** user reviews the action list and backlog state before the next iteration begins. See [iterate.md](../commands/iterate.md) Step 4 for the iteration-boundary behaviour.

**Early-trigger paths:** Retrospective can be entered before Integration via mid-iteration recovery. See *Mid-iteration recovery* in [iterate.md](../commands/iterate.md). Tier 2 splits the iteration (N-A closes here, N-B replans). Tier 3 abandons. Keep retros tight in both cases.

---

## Pipeline feedback capture (meta — the agile-dev pipeline itself)

Separate from the project retro above. Captures meta-feedback about the pipeline tool: orchestration friction, ambiguous prompts, generated files that needed manual fixup, wrong checkpoint firings, surprising behaviour.

**Test:** would this observation matter to a different team using the same pipeline on a different project? Yes → pipeline feedback. No → project retro.

**Process:**

1. Self-observe during this Retrospective. Anything awkward → draft an entry.
2. Ask the user once: `Any pipeline-level friction this iteration? Reply with the issue or "none".`
3. User replies "none" and no self-observed entries → write nothing.
4. Otherwise: append to `.project-artifacts/pipeline-feedback.md` (create if missing — first line: `# Pipeline Feedback` + a one-line description). Each entry:

   ```markdown
   ## <YYYY-MM-DD> · Iteration <NNN> · <short title>
   **Phase / area:** <phase, command, or "general">
   **What happened:** <1–2 sentences>
   **Impact:** <why it was friction>
   **Suggested change:** <if known>
   ```

5. Inform user as a one-liner: `Pipeline feedback: <N> entry(ies) appended to pipeline-feedback.md.` Informational only — no approval needed.

---

## Iteration transition

```
Idle → Refinement → Decomposition → Test Plan → Development → Verification → Integration → Retrospective → Idle
```

Code Review folds into Development as a self-applied checklist (see [development.md](development.md)). Verification owns out-of-process tests (see [verification.md](verification.md)).

**Release boundary:** if this iteration is a release boundary (MVP done, milestone), run `/agile-dev:release` **before** Retrospective. See [release.md](../commands/release.md).

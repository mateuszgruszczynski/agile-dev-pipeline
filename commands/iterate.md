---
description: Run iteration phases continuously through Refinement / Decomposition / Test Plan / Development / Verification / Integration / Retrospective. Stops only at ⛳ approval checkpoints.
---

Iteration phase runner. Runs the iteration loop forward through every phase until it hits a ⛳ CHECKPOINT, the iteration boundary, or backlog exhaustion. State is saved to `state.md` after each approval; closing the session at any point is a safe pause.

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

## Step 1 — Validate state

Read `.project-artifacts/state.md`.

- Not present: stop. Say `No pipeline found. Run /agile-dev:start or /agile-dev:improve first.`
- Vision / Architecture / Backlog not complete: stop. Say `Foundation incomplete. Run /agile-dev:start or /agile-dev:improve first.`
- Environment not marked complete: run Environment now.
  - Load `${CLAUDE_PLUGIN_ROOT}/pipeline/environment.md` and `.project-artifacts/f2-architecture.md`.
  - Generate `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, project `.claude/settings.json`.
  - ⛳ CHECKPOINT Environment: user confirms they are inside the container. Mark `Environment ✓` in `state.md`.

**Container check** — if `Environment ✓` is marked in `state.md`, iteration phases must run inside the dev container. Run `test -f /.dockerenv && echo INSIDE || echo OUTSIDE`. If the result is `OUTSIDE`, refuse:

> `You're on the host, but iteration phases must run inside the dev container. Reopen the project in the container (VS Code / Cursor: Cmd+Shift+P → "Dev Containers: Reopen in Container"; JetBrains: right-click .devcontainer/devcontainer.json → Dev Containers → Create Dev Container and Mount Sources), then re-run /agile-dev:iterate.`

Then stop. Do not proceed to Step 2.

If `$ARGUMENTS` is provided, treat it as an epic-name override. See *Argument behaviour* at the bottom.

---

## Step 2 — Pick next iteration's epic bundle (only when no iteration is in progress)

`current_phase` is `Idle` / empty / legacy `Backlog`:

**Point values** (from `pipeline/backlog.md`):

| Size | XS | S | M | L | XL | XXL |
|---|---|---|---|---|---|---|
| Points | 1.0 | 1.7 | 3.0 | 5.2 | 9.0 | 15.6 |

**Budget:** read `iteration_size` from `.project-artifacts/policy.md` and look up its point value above. Default `xl` = 9 points.

### Bundle selection algorithm

1. **Load candidates.** Read `f3-backlog.md`. Take all epics with status `TODO`. Discard `DONE`, `IN_PROGRESS`, `BLOCKED`.
2. **Filter unblocked.** Drop epics whose declared dependencies (from the epic detail block) include any epic not yet `DONE`. If a candidate's dependency is in the same TODO pool, it stays blocked until its blocker is scheduled and completed.
3. **Order candidates.** Sort by priority (P1 first, then P2, then P3). Within the same priority, sort by size descending (larger first — fills budget faster). Stable tiebreak by submission order.
4. **Build bundle (greedy, closer-to-budget):**
   - If `$ARGUMENTS` is provided: parse it as one or more epic names (comma- or plus-separated). Use those as the bundle directly. Skip steps 5–7. Validate every named epic is in the unblocked TODO pool; if not, refuse.
   - Otherwise: walk the ordered candidate list, accumulating points.
     - If the bundle is empty (first candidate): add it unconditionally (rule: a single oversized epic is always allowed).
     - For each subsequent candidate `c`: compute `stop_dev = |budget - sum|` and `add_dev = |budget - (sum + c.points)|`. If `add_dev < stop_dev`, add `c` and continue. If `add_dev ≥ stop_dev`, stop — current bundle is closer to budget.
   - Add to the bundle any **dependent epics of bundled epics** that are themselves in the unblocked pool — only if they fit the same closer-to-budget rule. This avoids leaving a dependent stranded right after its blocker just shipped.
5. **Show the bundle to the user:**

   > `Next iteration <N> bundle (budget = <budget> pts / <size>; total = <sum> pts):`
   > `  • EP-3 — Search index (L, 5.2 pts) P1`
   > `  • EP-7 — Filter UI (M, 3.0 pts) P1`
   > `Proceed? (yes / edit <add EP-x | remove EP-y> / no)`

6. **edit** branch: parse the user's add/remove instructions, re-validate (dependencies unblocked, epic in TODO pool), recompute total, re-present. Loop until user replies yes or no.
7. **yes** branch: set `current_epic` in `state.md` to a comma-separated list of epic names from the bundle. Mark each bundled epic as `IN_PROGRESS` in the Backlog table. Set `current_phase: Refinement`. Iteration directory slug derives from the first (highest-priority) epic: `iterations/<NNN>-<first-epic-slug>/`. Proceed to Step 3.

8. **no / empty backlog:**
   - Empty: report `Backlog is empty — pipeline complete.` Stop.
   - User said no: stop. Say `Iteration not started.`

`current_phase` is an iteration phase (bundle in flight):
- `$ARGUMENTS` provided: refuse the override (see *Argument behaviour*). Stop.
- Otherwise: proceed to Step 3 at the saved phase. The bundle is whatever's listed in `current_epic`.

---

## Step 3 — Run phases continuously

**Load policy first.** Read `.project-artifacts/policy.md` once at session start. The three values control orchestrator behaviour for every phase below:

- **autonomy override** — applied globally to all checkpoints in this session:
  - `user-driven` → every ⛳ checkpoint (mandatory and conditional) pauses for explicit APPROVE. Auto-skip / auto-continue rules are disabled.
  - `semi-automatic` → phase-specific rules apply as written. Mandatory checkpoints pause; conditional ones auto-skip / auto-continue per their phase rule.
  - `ai-driven` → all checkpoints auto-continue except Vision (covered in Foundation). Retrospective produces its artifact and auto-loops to the next iteration. User can interrupt only by closing the session.
- **test_coverage override** — applied to the phase sequence:
  - `thorough` / `minimal` → run all seven iteration phases. Test Plan and Verification scope adjusts internally (see those phase files).
  - `none` → **skip Test Plan and Verification entirely**. The phase sequence becomes Refinement → Decomposition → Development → Integration → Retrospective. When advancing past Decomposition, set `current_phase: Development` (not Test Plan). When advancing past Development, set `current_phase: Integration` (not Verification). Do not write `i3-test-plan.md` or `i5-verify.md`.
- **detail override** — passed through to each phase (each phase file has a Policy effects section explaining its variants).
- **packaging override** — applied at Integration's step 7:
  - `each` → Integration packages a deliverable artifact in `dist/<NNN>-<slug>/` every iteration and smoke-tests it (per `test_coverage`).
  - `milestone` → Integration skips packaging by default; the `/agile-dev:release` command produces the artifact at the release boundary.
  - `final` → Integration skips packaging in normal iterations. The user explicitly requests a build via `/agile-dev:release` (or by editing `policy.md` to `each` for one iteration).

If `policy.md` is missing (older project predating this feature, or a Foundation that never set policy), default to `semi-automatic / full / thorough` (matches the previous behaviour). Print a one-line note: `No policy.md found; defaulting to semi-automatic / full / thorough.`

Read the phase file for `current_phase`. Load artifacts listed in the phase's `Load:` line — but **skip Read calls for files already in this session's context**. The `Load:` list is a requirement, not a sequence of Read calls.

**After each phase finishes** (checkpoint APPROVE, auto-continue, or no-checkpoint completion): advance `current_phase` in `state.md` and run the next phase in the same session. Apply the test_coverage override above when deciding which next phase to run. Do not ask the user to re-invoke `/agile-dev:iterate`. The loop pauses only at: a ⛳ CHECKPOINT awaiting APPROVE (per the autonomy override), the user closing the session, or the Retrospective iteration-boundary choice (skipped for `ai-driven`).

---

### Phase: Refinement

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/refinement.md`; epic detail block from `state.md` or `f3-backlog.md`.

**Do:** Interactive Q&A. Delegate spec drafting to a subagent (see refinement.md). Review the result.

**Save:** `.project-artifacts/iterations/<NNN>-<slug>/i1-spec.md`

**⛳ CHECKPOINT:** Present spec; wait for APPROVE.

---

### Phase: Decomposition

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/decomposition.md`; `i1-spec.md`.

**Do:** Generate task list per decomposition.md. Delegate drafting to a subagent unless trivial.

**Save:** `.project-artifacts/iterations/<NNN>-<slug>/i2-tasks.md`

**Checkpoint — conditional:**
- Auto-continue if every task maps to an AC or a standard cross-cutting category, roles are unambiguous, and no scope was added beyond the spec.
- Otherwise ⛳ CHECKPOINT: present the list; wait for APPROVE.

---

### Phase: Test Plan

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/test-plan.md`; `i1-spec.md`.

**Do:** Write BDD scenarios from ACs. Delegate scenario drafting to a subagent. Assign **level** (Unit / Component / Contract / System-integration / E2E) and **type** (UI / API / Protocol / CLI / File-batch) yourself — these decide which phase owns each scenario. For existing codebases: also write regression scenarios for behaviour this epic touches; scope to what the epic actually changes.

**Save:** `.project-artifacts/iterations/<NNN>-<slug>/i3-test-plan.md`

**⛳ CHECKPOINT:** Present the test plan; wait for APPROVE.

---

### Phase: Development

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/development.md`; `i1-spec.md`, `i2-tasks.md`, `i3-test-plan.md`.

**Do:**
1. Baseline (existing codebases): run the in-process suite. Pre-existing failures become separate FIX epics.
2. Implement DEV tasks TDD-style. In-process tests only here (Unit / Component / in-process Contract). Out-of-process levels belong to Verification.
3. Update `i2-tasks.md` in place: `[x]` done / `[~]` deferred / `[ ]` pending.
4. Wire up external interfaces so Verification can drive them out-of-process.
5. Commit small and often — do not bundle the iteration into a single commit.
6. Security rules: env vars only, `.env.example`, `.gitignore`.
7. Apply self-review checklist (development.md).
8. Use subagents for independent parallel tasks.

**No checkpoint.**

**Save:** `i4-dev.md` — files changed; in-process tests by level + AC each covers; external interfaces wired; key decisions; deviations; self-review result.

---

### Phase: Verification

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/verification.md`; `i1-spec.md`, `i3-test-plan.md`, `i4-dev.md`. From `f2-architecture.md` load only the **Integration Strategy** table and **Project Type Adaptations** section.

**Do:**
1. Stand up test environment (Testcontainers / docker-compose / ephemeral). Record reproduction steps.
2. Stub external third parties via real mock-server processes. No in-process mocks at this level.
3. Implement and run every System-integration + E2E + out-of-process Contract scenario **as test files in the project's test framework**. Do not chat-drive `curl`/`grpcurl`/etc. (see verification.md anti-pattern).
4. Stabilise flakes by fixing root causes. Quarantine with written reason + follow-up task as a last resort.
5. Confirm AC coverage. Each AC has ≥1 Verification scenario unless it has no out-of-process observable.
6. Subagents in parallel for independent scenarios.

**No checkpoint.** Quality is enforced by the tests.

**Save:** `i5-verify.md` — environment + reproduction; stubs; tests by level/type with AC each covers; run results; quarantined items; AC coverage table.

---

### Phase: Integration

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/integration.md`; `i1-spec.md`, `i4-dev.md`, `i5-verify.md`. From `f1-vision.md` load only the **Key user journeys** section.

**Do:**
1. Build (production command).
2. Prepare `.env` (classify variables, pre-fill safe defaults, request real credentials).
3. Start the app; verify it connects to all required services.
4. Manual smoke of the core user journey. Keep brief — Verification already covered the scenarios.
5. Confirm `i5-verify.md`: all non-quarantined passed; every AC traces to a passing scenario.
6. Demo script if the epic produces something demonstrable. Note explicitly if not.
7. Fix Integration-only issues. Defects from earlier phases should already be closed.

**Save:** `i6-int.md` — build status; env prep; start result; smoke outcome; Verification roll-up; AC pass/fail table; Integration-phase issues; demo outcome.

**Checkpoint — conditional:**
- Auto-continue when all of: build green, every non-quarantined Verification scenario passed, every AC covered. Announce `Integration green — continuing with Retrospective.`
- Otherwise ⛳ CHECKPOINT: present `i6-int.md` + `i5-verify.md`. User chooses APPROVE (accept as-is), REJECT (loop back — see *Mid-iteration recovery*), or release boundary.

**Release boundary:** if APPROVE *and* this iteration is a release boundary (MVP done, milestone), stop and say `Integration approved. Release boundary — run /agile-dev:release before continuing.`

---

### Phase: Retrospective

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/retrospective.md`; `i1-spec.md`, `i3-test-plan.md`, `i4-dev.md`, `i5-verify.md`, `i6-int.md`.

**Do:** Interactive. Only surface findings that drive a concrete change. Update `f3-backlog.md` and the backlog table in `state.md` if epics added / removed / re-prioritised.

**Save:** `i7-retro.md`

**⛳ CHECKPOINT — iteration boundary.** Always stops here. Present:
- Retro action items (or `No plan changes`)
- Updated backlog snapshot
- Proposed next epic (apply Step 2 selection rule: name when unambiguous, list candidates when ambiguous, none if empty)

User chooses:
- **APPROVE** — close this iteration (Step 4) and continue immediately into the next.
- **APPROVE + STOP** — close this iteration but pause; next `/agile-dev:iterate` starts fresh.
- **REJECT / edit** — revise and re-present.

---

## Step 4 — Close the iteration

After Retrospective is approved:

1. **state.md:**
   - Mark **every bundled epic** `DONE` in Backlog table.
   - Append to Completed iterations: `| <NNN> | <epic-list-with-sizes> | DONE | <YYYY-MM-DD> | <retro highlight or "No plan changes"> | iterations/<NNN>-<first-epic-slug>/i7-retro.md |`
     - Single epic: `EP-1 User auth (XL)`. Bundle: `EP-3 Search index (L) + EP-7 Filter UI (M) + EP-9 Pagination (M)`.
   - Clear `current_epic`; set `current_phase: Idle`; increment `iteration`.
   - All backlog epics `DONE` → also set `status: COMPLETE`.

2. **CHANGELOG.md** at project root (Keep-a-Changelog format if file is new):
   ```markdown
   ## [Iteration <NNN>] — <epic-list> — <YYYY-MM-DD>

   ### Added / Changed / Fixed
   - **EP-<id> <name>:** <line drawn from i4-dev.md, i5-verify.md, i6-int.md for this epic>
   - **EP-<id> <name>:** <line for the next bundled epic>

   Retro: iterations/<NNN>-<first-epic-slug>/i7-retro.md
   ```
   For a single-epic iteration the bullet list collapses to one bullet without the `EP-x` prefix.

3. Report: `Iteration <NNN> complete. <N> epic(s) done: <epic-list>.` Show remaining backlog.

4. **Branch based on user's Retrospective choice + state:**
   - Retro flagged Vision / Architecture / Backlog action items → stop. Say `Retro flagged a foundation change — run /agile-dev:revise <phase> before the next iteration.`
   - User chose **APPROVE + STOP** → stop. Say `Iteration closed. Run /agile-dev:iterate when ready.`
   - Backlog empty → stop. Say `Backlog is empty — pipeline complete.`
   - Next epic selection is **ambiguous** (≥2 tied at top priority) → ask the disambiguation question from Step 2.3 in this same session, then start the next iteration's Refinement. This is one question, not a new approval gate.
   - Otherwise (APPROVE + unambiguous next epic + no foundation flag): loop back to Step 2 in the same session. Do not wait for the user.

---

## Mid-iteration recovery

If a defect surfaces that "continuing" can't fix — wrong AC, scope can't ship, architectural assumption broken — pick the lowest tier that fits. Do not hand-edit `state.md` to skip past the problem.

### Tier 1 — Loop back (minor defect)

One phase produced wrong output; the rest is sound.

1. Set `current_phase` back to the affected phase.
2. Re-run that phase and re-checkpoint.
3. Continue forward. Iteration counter unchanged.

### Tier 2 — Split into N-A and N-B (major issue, partial work keepable)

Half the spec is out of scope, architecture needs to change before the rest can proceed, or — for bundles — one epic in the bundle is broken and the rest is sound.

**For a single-epic iteration:**

1. Rename `iterations/<NNN>-<slug>/` → `iterations/<NNN>-A-<slug>/`. Fix internal cross-references.
2. Set `current_phase: Retrospective`. Run Retrospective for N-A: write `i7-retro.md` covering what shipped, what was deferred, why the split.
3. Append to Completed iterations: `| <NNN>-A | <epic> | DONE | <date> | <summary + split reason> | iterations/<NNN>-A-<slug>/i7-retro.md |`. CHANGELOG entry for what N-A delivered.
4. Open N-B: create `iterations/<NNN>-B-<slug>/`, set `current_phase: Refinement`. Keep `current_epic`. Iteration counter unchanged until N-B closes.
5. N-B runs the full phase loop. Closes as `<NNN>-B` in Completed iterations.

**For a multi-epic bundle:**

1. Identify the broken epic(s) — the ones that can't be completed in this iteration.
2. Compute the **dependent set**: every other epic in the bundle that lists a broken epic as a dependency, transitively.
3. Split:
   - **N-A epics** = bundled epics minus broken minus their dependents. These can still ship.
   - **N-B epics** = broken epics + their dependents. These move to a fresh iteration with replanned scope.
4. **Edge case — N-A is empty** (broken epic blocks everything else, or every epic is broken): this isn't a split; it's a Tier 3 abandon. Switch to Tier 3 below.
5. **Edge case — N-B is just one epic and it's truly abandoned** (not deferred, removed from backlog entirely): close N-A as a normal iteration (no split); record the abandoned epic in the Retrospective with reason. Skip the rest of Tier 2.
6. Otherwise execute the split:
   a. Rename `iterations/<NNN>-<slug>/` → `iterations/<NNN>-A-<slug>/`. Fix internal cross-references.
   b. Update artifacts inside N-A's directory to drop the broken/deferred epics from their per-epic sections (so `i1-spec.md`, `i2-tasks.md`, etc. only describe what N-A ships). Move the dropped sections to `iterations/<NNN>-A-<slug>/deferred-to-N-B.md` for the record.
   c. Set `current_phase: Retrospective`. Run Retrospective for N-A: `i7-retro.md` covers what shipped, what was deferred, why the split.
   d. Append to Completed iterations: `| <NNN>-A | <N-A epic-list> | DONE | <date> | Split — moved <N-B epic-list> to N-B because <reason> | iterations/<NNN>-A-<slug>/i7-retro.md |`.
   e. CHANGELOG entry for what N-A delivered.
   f. Mark N-A epics `DONE` in Backlog table; deferred N-B epics revert to `TODO` (they'll be picked up by the next Step 2 bundle selection — or by N-B directly, see g).
   g. Open N-B: create `iterations/<NNN>-B-<first-N-B-epic-slug>/`. Set `current_epic` to the N-B epic-list. Set `current_phase: Refinement` (N-B usually needs replanning). Iteration counter unchanged until N-B closes.
   h. N-B runs the full phase loop. Closes as `<NNN>-B` in Completed iterations.

It's fine to stop iteration N-A earlier than originally planned if the broken epic forces scope/plan changes. The split exists to preserve work, not to enforce a full iteration on partial scope.

### Tier 3 — Abandon (cannot keep partial work)

Foundational assumption was wrong / epic no longer needed / external dependency gone.

1. Set `current_phase: Retrospective`. Short retro on why it failed and what to do with the epic.
2. Write `i7-retro.md` with the abandonment reason.
3. Append to Completed iterations: `| <NNN> | <epic> | ABANDONED | <date> | <reason> | iterations/<NNN>-<slug>/i7-retro.md |`.
4. No CHANGELOG entry.
5. Reset `current_epic`, `current_phase: Idle`, increment `iteration`. Apply any backlog changes from the retro.

### Choosing a tier

Lowest that fits. Uncertain between 1 and 2 → ask the user. Tier 3 only when there is nothing to keep.

---

## State file — fields used by this command

```
mode: greenfield | improve
current_epic: <epic name or empty>
current_phase: <Idle | Refinement | Decomposition | Test Plan | Development | Verification | Integration | Retrospective>
iteration: <number>
```

Split iterations (Tier 2) use `<NNN>-A-<slug>` / `<NNN>-B-<slug>` directories and record each part separately in Completed iterations. The `iteration` counter advances by 1 per split iteration — bumps to `<NNN+1>` only after N-B closes.

Full state file format: [start.md](start.md).

## Artifact directory naming

`<NNN>` = zero-padded iteration number (`001`, `002`). `<slug>` = epic name lowercased with spaces → hyphens (`user-authentication`).

## Argument behaviour

`$ARGUMENTS` selects which epic to refine next when no iteration is in progress.

- **No epic in progress:** match against backlog epic names; pick the match instead of highest-priority TODO. No match → fall back to highest-priority TODO, warn.
- **Epic already in progress:** refuse. Say:

  > `Epic **<current_epic>** is already in progress at phase **<current_phase>**. Cannot switch to '<argument>' mid-iteration. Finish the current epic, run mid-iteration recovery to abandon it, or use /agile-dev:change for a one-off. Once the in-progress iteration is closed, re-run /agile-dev:iterate <argument>.`

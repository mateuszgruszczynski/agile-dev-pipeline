---
description: Run iteration phases continuously through Refinement / Decomposition+Plan / Development / Verification / Integration. Stops only at ⛳ approval checkpoints. Also used by /agile-dev:change when the project has an existing pipeline.
---

Iteration phase runner. Runs the iteration loop forward through every phase until it hits a ⛳ CHECKPOINT or backlog exhaustion. State is saved to `state.md` after each approval; closing the session at any point is a safe pause.

---

## Step 1 — Validate state

Read `.project-artifacts/state.md`.

- Not present: stop. Say `No pipeline found. Run /agile-dev:start or /agile-dev:improve first.`
- Vision / Architecture / Backlog not complete: stop. Say `Foundation incomplete. Run /agile-dev:start or /agile-dev:improve first.`
- Environment not marked complete: run Environment now.
  - Load `${CLAUDE_PLUGIN_ROOT}/pipeline/environment.md` and `.project-artifacts/f2-architecture.md`.
  - Generate the production build recipe and optionally dev container files.
  - ⛳ CHECKPOINT Environment: user approves the environment setup. Mark `Environment ✓` in `state.md`.

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
5. **Present the bundle, and decide whether to pause** (per the `autonomy` policy):

   Build the summary first:
   > `Next iteration <N> bundle (budget = <budget> pts / <size>; total = <sum> pts):`
   > `  • EP-3 — Search index (L, 5.2 pts) P1`
   > `  • EP-7 — Filter UI (M, 3.0 pts) P1`

   Then:
   - `ai-driven` → print the summary as a notification and proceed to step 7. Never ask.
   - `semi-automatic` (default) → **auto-proceed when the pick is unambiguous.** The pick is unambiguous when it is the plain greedy result with no judgment call: no other TODO epic ties at the same priority and would fit the budget equally well at the margin, and the bundle was not formed by force-adding a single oversized epic past budget. When unambiguous, print the summary and proceed to step 7 without asking. Only when the pick required judgment (an arbitrary tie-break, or a lone oversized epic) append `Proceed? (yes / edit <add EP-x | remove EP-y> / no)` and wait.
   - `user-driven` → always append `Proceed? (yes / edit <add EP-x | remove EP-y> / no)` and wait.

6. **edit** branch (only reachable when the question was asked): parse the user's add/remove instructions, re-validate (dependencies unblocked, epic in TODO pool), recompute total, re-present. Loop until user replies yes or no.
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
  - `ai-driven` → all checkpoints auto-continue. User can interrupt only by closing the session.
- **test_coverage override** — applied to the phase sequence:
  - `thorough` / `minimal` → run all phases. Test Plan (inside Planning) and Verification scope adjusts internally.
  - `none` → **skip Test Plan and Verification entirely**. The phase sequence becomes Refinement → Decomposition → Development → Integration. When advancing past Decomposition, set `current_phase: Development`. Do not write the Test Scenarios section of `i2-plan.md` or the Verification section of `i3-outcome.md`.
- **detail override** — passed through to each phase (each phase file has a Policy effects section explaining its variants).
- **packaging override** — applied at Integration's step 7:
  - `each` → Integration packages a deliverable artifact in `dist/<NNN>-<slug>/` every iteration and smoke-tests it (per `test_coverage`).
  - `milestone` → Integration skips packaging by default; the `/agile-dev:release` command produces the artifact at the release boundary.
  - `final` → Integration skips packaging in normal iterations.

If `policy.md` is missing, default to `semi-automatic / full / thorough`. Print a one-line note: `No policy.md found; defaulting to semi-automatic / full / thorough.`

Read the phase file for `current_phase`. Load artifacts listed in the phase's `Load:` line — but **skip Read calls for files already in this session's context**. The `Load:` list is a requirement, not a sequence of Read calls.

**Permissions are handled by the plugin's PreToolUse hooks** (`hooks/permission-gate.sh`, `hooks/write-guard.sh`) — do not stop to ask the user for tool approvals. Recognised dev tools (build / test / lint / format runners, local git, in-project writes) are auto-approved with no prompt; dangerous commands are blocked. A genuinely unrecognised command falls through to the normal permission flow and prompts once — that is expected, not an error to route around. If a project repeatedly uses a dev tool the hook doesn't recognise, the fix is to add it to the plugin's `hooks/guards.json` allow list (a plugin change), not to special-case it here.

**After each phase finishes** (checkpoint APPROVE, auto-continue, or no-checkpoint completion): advance `current_phase` in `state.md` and run the next phase in the same session. Apply the test_coverage override above when deciding which next phase to run. Do not ask the user to re-invoke `/agile-dev:iterate`. The loop pauses only at: a ⛳ CHECKPOINT awaiting APPROVE (per the autonomy override), or the user closing the session.

---

### Phase: Refinement

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/refinement.md`; epic detail block from `state.md` or `f3-backlog.md`.

**Do:** Interactive Q&A on behaviour, then surface and confirm the **design decisions** (how it will be built, including which external services are mockable vs. need real keys) — see refinement.md. This is the iteration's single engagement point. Delegate spec drafting to a subagent. Review the result.

**Save:** `.project-artifacts/iterations/<NNN>-<slug>/i1-spec.md` (spec + ACs + Design Decisions section)

**⛳ CHECKPOINT:** Present spec, ACs, and Design Decisions; wait for APPROVE. Approving locks both what and how.

---

### Phase: Decomposition + Plan

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/decomposition.md`; `i1-spec.md`.

**Do:**
1. Read the **Design Decisions** already locked in `i1-spec.md` — do not re-ask them. Generate the task list per decomposition.md. Delegate drafting to a subagent unless trivial. If decomposition surfaces a genuinely new decision, record a reasonable default (semi-automatic/ai-driven) rather than pausing — see decomposition.md Step 1.
2. Immediately run the Test Plan phase (load `${CLAUDE_PLUGIN_ROOT}/pipeline/test-plan.md`). Write BDD scenarios from ACs. Delegate scenario drafting to a subagent. Assign **level** (Unit / Component / Contract / System-integration / E2E) and **type** (UI / API / Protocol / CLI / File-batch) yourself. For existing codebases: also write regression scenarios.
   - Skip Test Plan (step 2) when `test_coverage = none`.

**Save:** `.project-artifacts/iterations/<NNN>-<slug>/i2-plan.md`
- Tasks section (from Decomposition)
- Test Scenarios section (from Test Plan, unless `test_coverage = none`)

**Checkpoint — conditional (after both tasks and scenarios are ready):**
- Auto-continue if: every task maps to an AC or a standard cross-cutting category, roles are unambiguous, no scope added beyond the spec, and every AC has a scenario at its lowest meaningful level (or `test_coverage = none`).
- Otherwise ⛳ CHECKPOINT: present `i2-plan.md`; wait for APPROVE.

---

### Phase: Development

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/development.md`; `i1-spec.md`, `i2-plan.md`.

**Do:**
1. Baseline (existing codebases): run the in-process suite. Pre-existing failures become separate FIX epics.
2. Implement DEV tasks TDD-style. In-process tests only here (Unit / Component / in-process Contract). Out-of-process levels belong to Verification.
3. Update the Tasks section of `i2-plan.md` in place: `[x]` done / `[~]` deferred / `[ ]` pending.
4. Wire up external interfaces so Verification can drive them out-of-process.
5. Commit small and often — do not bundle the iteration into a single commit.
6. Security rules: env vars only, `.env.example`, `.gitignore`.
7. Apply self-review checklist (development.md).
8. Use subagents for independent parallel tasks.

**No checkpoint.**

**Save:** Development section of `.project-artifacts/iterations/<NNN>-<slug>/i3-outcome.md` (create file with `# Iteration NNN Outcome` heading).

---

### Phase: Verification

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/verification.md`; `i1-spec.md`, `i2-plan.md` (Scenarios section), `i3-outcome.md` (Development section). From `f2-architecture.md` load only the **Integration Strategy** table and **Project Type Adaptations** section.

**Do:**
1. Stand up test environment (Testcontainers / docker-compose / ephemeral). Record reproduction steps.
2. Stub external third parties via real mock-server processes. No in-process mocks at this level.
3. Implement and run every System-integration + E2E + out-of-process Contract scenario **as test files in the project's test framework**. Do not chat-drive `curl`/`grpcurl`/etc.
4. Stabilise flakes by fixing root causes. Quarantine with written reason + follow-up task as a last resort.
5. Confirm AC coverage. Each AC has ≥1 Verification scenario unless it has no out-of-process observable.
6. Subagents in parallel for independent scenarios.

**No checkpoint.** Quality is enforced by the tests.

**Save:** Verification section appended to `i3-outcome.md`.

---

### Phase: Integration

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/integration.md`; `i1-spec.md`, `i3-outcome.md`. From `f1-vision.md` load only the **Key user journeys** section.

**Do:**
1. Build (production command).
2. Prepare `.env` (classify variables, pre-fill safe defaults, request real credentials).
3. Start the app; verify it connects to all required services.
4. Manual smoke of the core user journey. Keep brief — Verification already covered the scenarios.
5. Confirm Verification section of `i3-outcome.md`: all non-quarantined passed; every AC traces to a passing scenario.
6. Package deliverable artifact per `packaging` policy (step 7 of integration.md).
7. Demo script if the epic produces something demonstrable. Note explicitly if not.

**Save:** Integration section appended to `i3-outcome.md`.

**Checkpoint — conditional:**
- Auto-continue when all of: build green, every non-quarantined Verification scenario passed, every AC covered.
- Otherwise ⛳ CHECKPOINT: present `i3-outcome.md`. User chooses APPROVE (accept), REJECT (loop back — see *Mid-iteration recovery*), or release boundary.

**Release boundary:** if APPROVE *and* this iteration is a release boundary (MVP done, milestone), stop and say `Integration approved. Release boundary — run /agile-dev:release before continuing.`

**Iteration boundary (after APPROVE or auto-continue)** — per `autonomy` policy:

- `user-driven` → ask once:
  > `Iteration <N> complete. Any backlog changes before the next iteration? (list changes or press enter to continue)`
  - Changes listed → apply to `f3-backlog.md` and the Backlog table in `state.md`, then close (Step 4).
  - Enter / no changes → close immediately (Step 4).
- `semi-automatic` (default) / `ai-driven` → **do not ask.** Close immediately and roll into the next iteration. The backlog is editable directly at any time (`f3-backlog.md`), and `/agile-dev:change` adds an epic mid-stream — a per-iteration prompt with an empty default isn't worth the interruption.

---

## Step 4 — Close the iteration

After Integration APPROVE (and iteration-boundary question):

1. **state.md:**
   - Mark **every bundled epic** `DONE` in Backlog table.
   - Append to Completed iterations: `| <NNN> | <epic-list-with-sizes> | DONE | <YYYY-MM-DD> | <one-line summary or "No changes"> | iterations/<NNN>-<first-epic-slug>/i3-outcome.md |`
     - Single epic: `EP-1 User auth (XL)`. Bundle: `EP-3 Search index (L) + EP-7 Filter UI (M) + EP-9 Pagination (M)`.
   - Clear `current_epic`; set `current_phase: Idle`; increment `iteration`.
   - All backlog epics `DONE` → also set `status: COMPLETE`.

2. **CHANGELOG.md** at project root (Keep-a-Changelog format if file is new):
   ```markdown
   ## [Iteration <NNN>] — <epic-list> — <YYYY-MM-DD>

   ### Added / Changed / Fixed
   - **EP-<id> <name>:** <line drawn from i3-outcome.md for this epic>

   Outcome: iterations/<NNN>-<first-epic-slug>/i3-outcome.md
   ```
   For a single-epic iteration the bullet list collapses to one bullet without the `EP-x` prefix.

3. Report: `Iteration <NNN> complete. <N> epic(s) done: <epic-list>.` Show remaining backlog.

4. **Branch based on state:**
   - Iteration-boundary changes flagged a Vision / Architecture / Backlog action that requires foundation work → stop. Say `Foundation change needed — run /agile-dev:revise <phase> before the next iteration.`
   - Backlog empty → stop. Say `Backlog is empty — pipeline complete.`
   - Next epic selection is **ambiguous** (≥2 tied at top priority) → ask the disambiguation question from Step 2 in this same session, then start the next iteration's Refinement. This is one question, not a new approval gate.
   - Otherwise (no foundation flag, backlog not empty, unambiguous next epic): loop back to Step 2 in the same session. Do not wait for the user.

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
2. Set `current_phase: Integration`. Run Integration for N-A with what shipped; complete the iteration boundary close for N-A.
3. Append to Completed iterations: `| <NNN>-A | <epic> | DONE | <date> | Split — deferred remainder to N-B | iterations/<NNN>-A-<slug>/i3-outcome.md |`. CHANGELOG entry for what N-A delivered.
4. Open N-B: create `iterations/<NNN>-B-<slug>/`, set `current_phase: Refinement`. Keep `current_epic`. Iteration counter unchanged until N-B closes.
5. N-B runs the full phase loop. Closes as `<NNN>-B` in Completed iterations.

**For a multi-epic bundle:**

1. Identify the broken epic(s) — the ones that can't be completed in this iteration.
2. Compute the **dependent set**: every other epic in the bundle that lists a broken epic as a dependency, transitively.
3. Split:
   - **N-A epics** = bundled epics minus broken minus their dependents. These can still ship.
   - **N-B epics** = broken epics + their dependents. These move to a fresh iteration with replanned scope.
4. **Edge case — N-A is empty**: this is a Tier 3 abandon. Switch to Tier 3 below.
5. **Edge case — N-B is just one epic and it's truly abandoned** (removed from backlog): close N-A as a normal iteration; record the abandoned epic with reason. Skip the rest of Tier 2.
6. Otherwise execute the split:
   a. Rename `iterations/<NNN>-<slug>/` → `iterations/<NNN>-A-<slug>/`. Fix internal cross-references.
   b. Update artifacts inside N-A's directory to drop the broken/deferred epics from their per-epic sections. Move the dropped sections to `iterations/<NNN>-A-<slug>/deferred-to-N-B.md` for the record.
   c. Run Integration for N-A; complete the iteration-boundary close for N-A.
   d. Append to Completed iterations: `| <NNN>-A | <N-A epic-list> | DONE | <date> | Split — moved <N-B epic-list> to N-B | iterations/<NNN>-A-<slug>/i3-outcome.md |`.
   e. CHANGELOG entry for what N-A delivered.
   f. Mark N-A epics `DONE`; deferred N-B epics revert to `TODO`.
   g. Open N-B: create `iterations/<NNN>-B-<first-N-B-epic-slug>/`. Set `current_epic` to the N-B epic-list. Set `current_phase: Refinement`. Iteration counter unchanged until N-B closes.
   h. N-B runs the full phase loop. Closes as `<NNN>-B` in Completed iterations.

### Tier 3 — Abandon (cannot keep partial work)

Foundational assumption was wrong / epic no longer needed / external dependency gone.

1. Set `current_phase: Integration`. Brief Integration run: build status only; skip smoke if nothing was built.
2. Append to Completed iterations: `| <NNN> | <epic> | ABANDONED | <date> | <abandonment reason> | — |`.
3. No CHANGELOG entry.
4. Reset `current_epic`, `current_phase: Idle`, increment `iteration`. Apply any backlog changes from the decision.

### Choosing a tier

Lowest that fits. Uncertain between 1 and 2 → ask the user. Tier 3 only when there is nothing to keep.

---

## State file — fields used by this command

```
mode: greenfield | improve
current_epic: <epic name or empty>
current_phase: <Idle | Refinement | Decomposition | Development | Verification | Integration>
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

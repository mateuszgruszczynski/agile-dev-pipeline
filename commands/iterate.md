---
description: Run the next iteration phase (Refinement / Decomposition / Test Plan / Development / Verification / Integration / Retrospective). One phase per invocation.
---

You are the pipeline phase runner. Each invocation of this command runs **exactly one phase** of the iteration loop, then stops. This keeps each session small and token-efficient.

---

## Step 1 — Validate state

Read `.project-artifacts/state.md`.

- If it does not exist: stop and say "No pipeline found. Run `/agile-dev:start` or `/agile-dev:improve` first."
- If Vision, Architecture, or Backlog are not complete: stop and say "Foundation is not complete. Run `/agile-dev:start` or `/agile-dev:improve` first."
- If Environment is not marked complete: run the Environment phase now.
  - Read `${CLAUDE_PLUGIN_ROOT}/pipeline/environment.md` for the full Environment phase definition.
  - Read `.project-artifacts/f2-architecture.md` to determine the stack.
  - Generate `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, and `.claude/settings.json`.
  - Present the three files and instruct the user to reopen the project in the container, then resume.
  - ⛳ CHECKPOINT Environment: user confirms they are inside the container. Mark `Environment ✓` in `state.md`.

If an argument was provided, treat it as an epic name override: `$ARGUMENTS`. See *Argument behaviour* at the bottom of this file.

---

## Step 2 — Determine what to do next

Read `state.md` and identify `current_phase` and `current_epic`.

**If no epic is in progress (`current_phase` is empty, `Idle`, or the legacy `Backlog`):**
1. Find the highest-priority epic with status `TODO` in the backlog. If `$ARGUMENTS` was provided, prefer the epic whose name matches it.
2. If none: report "Backlog is empty — all epics are done. Pipeline complete." and stop.
3. Ask: "Next up: **<epic name>** (Priority: <priority>, Size: <size>). Shall I start Refinement? (yes/no)"
4. On yes: set `current_epic` and `current_phase: Refinement` in `state.md`. Proceed to Step 3.

**If an epic is in progress:**
- If `$ARGUMENTS` is non-empty: refuse the override (see *Argument behaviour* at the bottom of this file). Stop and prompt the user. Do not proceed to Step 3 silently.
- Otherwise: proceed to Step 3 using the saved `current_phase`.

---

## Step 3 — Run the current phase

Read the phase file for the current phase. Load only the prior artifacts listed below. Execute the phase, then advance `current_phase` and stop.

### Phase: Refinement

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/refinement.md` + the epic's entry (description, scenarios, HLACs, out-of-scope, risks) from `.project-artifacts/state.md` or `.project-artifacts/f3-backlog.md`.

**Do:** Run the Refinement phase interactively. Ask clarifying questions one at a time. After Q&A, you may delegate the spec drafting to a subagent and review the result yourself.

**Save:** `.project-artifacts/iterations/<NNN>-<slug>/i1-spec.md`

**⛳ CHECKPOINT:** Present spec and wait for APPROVE.

**On approve:** set `current_phase: Decomposition` in `state.md`. Say: "Refinement complete. Run `/agile-dev:iterate` to continue with Decomposition."

---

### Phase: Decomposition

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/decomposition.md` + `.project-artifacts/iterations/<NNN>-<slug>/i1-spec.md`

**Do:** Run the Decomposition phase. For long task lists, delegate generation to a subagent and review the result yourself.

**Save:** `.project-artifacts/iterations/<NNN>-<slug>/i2-tasks.md`

**⛳ CHECKPOINT:** Present task list and wait for APPROVE.

**On approve:** set `current_phase: Test Plan` in `state.md`. Say: "Decomposition complete. Run `/agile-dev:iterate` to continue with Test Plan."

---

### Phase: Test Plan

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/test-plan.md` + `.project-artifacts/iterations/<NNN>-<slug>/i1-spec.md`

**Do:** Run the Test Plan phase. Write BDD scenarios from the ACs in the spec. Assign each scenario a **level** (Unit / Component / Contract / System-integration / E2E) and a **type** (UI / API / Protocol / CLI / File-batch / etc.) — see `test-plan.md` for the full decision rule. The level determines which phase owns the scenario: in-process levels (Unit, Component) → Development; out-of-process levels (System-integration, E2E) → Verification; Contract → split by form. For existing codebase work: also write regression scenarios for any existing behaviour this epic touches — scoped to behaviour the epic actually changes; do not expand into general coverage gaps. For long scenario lists, delegate generation to a subagent and review the result yourself.

**Save:** `.project-artifacts/iterations/<NNN>-<slug>/i3-test-plan.md`

**⛳ CHECKPOINT:** Present the test plan and wait for APPROVE.

**On approve:** set `current_phase: Development` in `state.md`. Say: "Test Plan complete. Run `/agile-dev:iterate` to continue with Development."

---

### Phase: Development

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/development.md` + `i1-spec.md` + `i2-tasks.md` + `i3-test-plan.md` from `.project-artifacts/iterations/<NNN>-<slug>/`

**Do:**
1. **Baseline first (existing codebases):** run the existing in-process test suite before writing any new code. Note any pre-existing failures as separate FIX epics — do not proceed past them silently.
2. Implement all DEV tasks from Decomposition using TDD: failing in-process tests first, then implementation, then refactor under green.
3. As tasks complete, update `i2-tasks.md` in place — mark each task as `[x]` (done), `[~]` (deferred to a follow-up epic), or `[ ]` (still pending).
4. Apply the self-review checklist from `development.md` to your own output.
5. Cover all **in-process** test levels assigned in the Test Plan (Unit, Component, in-process Contract). Out-of-process levels (System-integration, E2E, out-of-process Contract) are owned by the Verification phase — do not write or run them here.
6. Wire up the application's external interfaces (HTTP routes, message handlers, CLI commands) so Verification can drive them out-of-process. No test-only shortcuts.
7. Apply all security rules (no hardcoded credentials, `.env.example`, `.gitignore`).
8. Use subagents for independent parallel implementation tasks where appropriate.

**No checkpoint pause here** — proceed directly to saving the summary and setting the next phase.

**Save:** Write `i4-dev.md` to the iteration directory containing:
- Files changed (added / modified / removed)
- In-process tests written, broken down by level (Unit / Component / Contract-in-process), with the AC each covers
- External interfaces wired up and ready for Verification (HTTP routes, message handlers, CLI commands)
- Key implementation decisions and their rationale
- Any deviations from the spec or task list, with reason
- Self-review checklist result (one line per item)

**On completion:** set `current_phase: Verification` in `state.md`. Show the user a one-paragraph summary of `i4-dev.md`. Say: "Development complete. Run `/agile-dev:iterate` to continue with Verification."

---

### Phase: Verification

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/verification.md` + `i1-spec.md` + `i3-test-plan.md` + `i4-dev.md` + `f2-architecture.md` from `.project-artifacts/iterations/<NNN>-<slug>/` and `.project-artifacts/`

**Do:** Run the Verification phase:
1. Stand up the test environment (Testcontainers, local docker-compose, or ephemeral deployed env). Record the choice and how to reproduce it.
2. Stub external third parties via real contract-driven mock-server processes (WireMock, Pact, hoverfly, Mockoon, hand-rolled HTTP stubs) — never via in-process mocks at this level.
3. Implement and run every System-integration scenario from `i3-test-plan.md`, driving the application through its real interface (HTTP / gRPC / message / socket / CLI / file drop) and asserting on what the BDD `Then` clause names.
4. Implement and run every E2E scenario. Type follows architecture: UI (Playwright / Cypress / WebDriver / Appium), API-only driver scripts, protocol-driven tests, or multi-channel chains. E2E does **not** mean UI by default.
5. Implement and run any out-of-process Contract scenarios assigned to this phase.
6. Stabilise flakes by fixing root causes — not by adding sleeps or retries. If a test cannot be stabilised this iteration, quarantine it with a written reason and a follow-up FIX task.
7. Confirm AC coverage: each AC has at least one Verification-level scenario, **unless** the AC has no out-of-process observable (in which case in-process coverage from Development is sufficient and explicitly noted).
8. Use subagents for independent parallel test authoring where appropriate.

**No checkpoint pause here** — Verification produces an artifact and proceeds. Quality is enforced by the tests themselves: a non-quarantined failure must be fixed before the phase can complete.

**Save:** Write `i5-verify.md` to the iteration directory containing:
- Test environment (how stood up, how to reproduce)
- External-service stubs (which third parties, which contract / mock server)
- System-integration tests by type (count + AC each covers)
- E2E tests by type (count + AC each covers)
- Run results (totals, pass/fail, any failures and their fix)
- Flaky / quarantined tests with reason and follow-up task
- AC coverage table (one row per AC: which Verification scenarios prove it, or marked "in-process only" with justification)

**On completion:** set `current_phase: Integration` in `state.md`. Show the user a one-paragraph summary of `i5-verify.md`. Say: "Verification complete. Run `/agile-dev:iterate` to continue with Integration."

---

### Phase: Integration

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/integration.md` + `i1-spec.md` + `i4-dev.md` + `i5-verify.md` from `.project-artifacts/iterations/<NNN>-<slug>/` + `f1-vision.md` from `.project-artifacts/`

**Do:** Run the Integration & Demo phase:
1. Build the application (production build).
2. Prepare `.env` (classify variables, pre-fill safe defaults, ask for any real credentials).
3. Start the application and verify it connects to all required services.
4. Perform a manual smoke test of the core user journey from Vision (catches what automated tests don't — visual breakage, console errors, broken nav).
5. Confirm Verification results in `i5-verify.md`: all non-quarantined scenarios pass; every AC traces to a passing scenario (Verification level when out-of-process observable; in-process otherwise).
6. Prepare a demo script if the epic produces a demonstrable user-visible state. Note explicitly when an epic doesn't (e.g. CI setup, base data model).
7. Fix any Integration-only issues found — do not defer. Test failures from earlier phases should already be closed before reaching this step.

**Save:** Write `i6-int.md` to the iteration directory containing:
- Build status (command run, success/failure, any warnings worth surfacing)
- `.env` preparation notes (variables classified, real credentials required)
- Application start result and health check
- Manual smoke test outcome
- Verification roll-up (pointer to `i5-verify.md` + confirmation all non-quarantined scenarios pass)
- AC pass/fail table (one row per AC, citing the scenario(s) that prove it)
- Issues found at this phase and how they were resolved
- Demo script outcome (or note that no demo was applicable)

**⛳ CHECKPOINT:** Present `i6-int.md` summary (build status, smoke test result, AC table) alongside `i5-verify.md`. Wait for APPROVE.

**On approve:** set `current_phase: Retrospective` in `state.md`. Say: "Integration complete. If this iteration is a release boundary (MVP done, milestone reached), run `/agile-dev:release` first to bundle iterations into a versioned release. Otherwise run `/agile-dev:iterate` to continue with Retrospective."

---

### Phase: Retrospective

**Load:** `${CLAUDE_PLUGIN_ROOT}/pipeline/retrospective.md` + `i1-spec.md` + `i3-test-plan.md` + `i4-dev.md` + `i5-verify.md` + `i6-int.md` from `.project-artifacts/iterations/<NNN>-<slug>/`

**Do:** Run the Retrospective phase interactively. Only surface findings that require a concrete change. Update `.project-artifacts/f3-backlog.md` and the backlog table in `state.md` if epics were added, removed, or re-prioritised.

**Save:** `.project-artifacts/iterations/<NNN>-<slug>/i7-retro.md`

**⛳ CHECKPOINT:** Present action items (or "No plan changes") and updated backlog. Wait for APPROVE.

**On approve:** close the iteration (Step 4 below).

---

## Step 4 — Close the iteration

After Retrospective is approved, do all of the following before reporting completion:

1. **Update state.md:**
   - Mark the current epic as `DONE` in the Backlog table.
   - Append a row to the `Completed iterations` table: `| <NNN> | <epic name> | <today's date YYYY-MM-DD> | iterations/<NNN>-<slug>/i7-retro.md |`
   - Clear `current_epic`.
   - Set `current_phase: Idle`.
   - Increment the `iteration` counter.
   - If all backlog epics are now `DONE`, also set `status: COMPLETE`.

2. **Append to CHANGELOG.md** at the project root (create the file if missing using Keep-a-Changelog format):
   ```markdown
   ## [Iteration <NNN>] — <epic name> — <YYYY-MM-DD>

   ### Added / Changed / Fixed (group as applicable)
   - <one-line summary lines drawn from i4-dev.md, i5-verify.md, and i6-int.md>

   Retro: iterations/<NNN>-<slug>/i7-retro.md
   ```

3. **Update `.project-artifacts/timeline.md`** (create on first iteration close):
   ```markdown
   # Project Timeline

   | # | Epic | Status | Closed | Notes |
   |---|---|---|---|---|
   | 001 | <epic name> | DONE | <YYYY-MM-DD> | <one-line retro highlight or "No plan changes"> |
   ```

4. Report: "Iteration <NNN> complete. Epic **<name>** is done." Show the remaining backlog with statuses. If the retro produced action items targeting Vision, Architecture, or Backlog, also say: "Retro flagged a foundation change — run `/agile-dev:revise <phase>` before the next iteration." Otherwise say: "Run `/agile-dev:iterate` to start the next iteration."

---

## Mid-iteration recovery

If a defect surfaces during an iteration that cannot be fixed by just continuing — wrong AC, scope can't ship, architectural assumption broken — pick the lowest tier that fits. Do not silently hand-edit `state.md` to "skip" past the problem.

### Tier 1 — Loop back (minor defect)

Use when one phase produced wrong output but the rest is sound. Examples: an AC needs rewording; a task missed a dependency; a test scenario has a typo.

1. Set `current_phase` back to the affected phase in `state.md`.
2. Re-run that phase and re-checkpoint.
3. Continue forward. Do not bump the iteration counter.

### Tier 2 — Split into N-A and N-B (major issue, partial work is keepable)

Use when enough is wrong that the remainder needs replanning, but the work already done deserves to be closed out. Examples: half the spec turns out to be out of scope; architecture needs to change before the rest can proceed.

1. Rename the in-flight directory: `iterations/<NNN>-<slug>/` → `iterations/<NNN>-A-<slug>/`. Fix any internal cross-references.
2. In `state.md` set `current_phase: Retrospective`. Run Retrospective for N-A — write `i7-retro.md` covering what shipped, what was deferred, and why the split happened.
3. Close N-A: append to the Completed iterations table with `| <NNN>-A | <epic name> | <date> | iterations/<NNN>-A-<slug>/i7-retro.md |`. Append a CHANGELOG entry for what N-A actually delivered. Update `timeline.md`.
4. Open N-B: create `iterations/<NNN>-B-<slug>/`, set `current_phase: Refinement` (the replanned remainder almost always needs a fresh spec). Keep `current_epic` as is. Do NOT increment the `iteration` counter — it stays at `<NNN>` until N-B closes, then advances to `<NNN+1>`.
5. N-B runs through the full phase loop. At its close it is recorded as `<NNN>-B` in the Completed iterations table.

### Tier 3 — Abandon (cannot keep partial work)

Use when the iteration cannot produce shippable work. Examples: foundational assumption was wrong; epic is no longer needed; external dependency disappeared.

1. Set `current_phase: Retrospective`. Run a short Retrospective focused on why this failed, what to do with the epic (return to TODO, split, drop), and any backlog changes.
2. Write `i7-retro.md` with the abandonment reason.
3. Append to the Completed iterations table with `| <NNN> | <epic name> | <date> | ABANDONED — iterations/<NNN>-<slug>/i7-retro.md |`.
4. Do NOT append a CHANGELOG entry (no shipped work). Update `timeline.md` with the abandonment.
5. Reset `current_epic`, set `current_phase: Idle`, increment the `iteration` counter. Apply any backlog changes from the retro.

### Choosing a tier

Default to the lowest tier that fits. When uncertain between Tier 1 and Tier 2, ask the user. Tier 3 is rare — only use it when there is genuinely nothing to keep.

---

## State file — fields used by this command

```
mode: greenfield | improve
current_epic: <epic name or empty>
current_phase: <Idle | Refinement | Decomposition | Test Plan | Development | Verification | Integration | Retrospective>
iteration: <number>
```

When an iteration is split (Tier 2 above), iteration directories use `<NNN>-A-<slug>` and `<NNN>-B-<slug>`, and the Completed iterations table records each part separately (e.g. `003-A` and `003-B`). The `iteration` counter still advances by 1 per split iteration — it bumps to `<NNN+1>` only after N-B closes.

The full state file format is documented in [start.md](start.md).

## Artifact directory naming

`<NNN>` is the zero-padded iteration number (e.g. `001`, `002`). `<slug>` is the epic name lowercased with spaces replaced by hyphens (e.g. `001-user-authentication`).

## Argument behaviour

`$ARGUMENTS` is treated as an epic-name override: it selects which epic to refine next when no iteration is in progress.

- **No epic in progress** (`current_phase` is `Idle` / empty / legacy `Backlog`): match the argument against backlog epic names; pick the matching epic instead of the highest-priority TODO. If no match, fall back to the highest-priority TODO and warn the user.
- **An epic is already in progress** (`current_phase` is any iteration phase): refuse the override. Stop and tell the user:

  > "Epic **<current_epic>** is already in progress at phase **<current_phase>**. Cannot switch to '<argument>' mid-iteration. Finish the current epic, run mid-iteration recovery (see *Mid-iteration recovery* above) to abandon it, or use `/agile-dev:change` for a one-off change."

  Do not proceed with the current phase silently — wait for the user to choose how to resolve. Once the in-progress iteration is closed, abandoned, or recovered, re-run `/agile-dev:iterate <argument>`.

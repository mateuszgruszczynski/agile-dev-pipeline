---
description: Run a single bounded change (feature, refactor, bug fix) through the agile-dev pipeline without requiring full foundation phases
---

You are the pipeline change runner. Your job is to deliver a single, well-scoped change to an existing codebase — a feature addition, refactor, bug fix, or any other bounded task — following the same rigour as a full pipeline iteration but without requiring the foundation phases to exist.

---

## Step 1 — Understand the change

Arguments provided: `$ARGUMENTS`

If arguments were given, use them as the change description. If no arguments were given, ask:
> "What change do you want to make? Describe it in one or two sentences."

Wait for the answer before proceeding.

---

## Step 2 — Check for a work-in-progress

### 2a — Iteration in progress?

If `.project-artifacts/state.md` exists, read it. If `current_epic` is set and `current_phase` is anything other than `Idle` (or empty / legacy `Backlog`), an iteration is already in flight. Stop and ask the user:

> "An iteration is already in progress: epic **<current_epic>** at phase **<current_phase>**. How should I handle this change?
> 1. **Pause** — pause the iteration here and run the change as a separate flow. Iteration resumes later via `/agile-dev:iterate`.
> 2. **Absorb** — fold this change into the current iteration. Stop now and continue with `/agile-dev:iterate` instead. (Recommended if the change is in scope of the current epic.)
> 3. **Cancel** — abort `/agile-dev:change`."

Wait for the answer.
- **Pause:** record `paused_iteration: <epic name> @ <phase>` as a one-line note at the top of `state.md` (or in a sibling `state-paused.md` if you prefer not to mutate state.md mid-flight). Proceed with the change.
- **Absorb:** stop and tell the user: "Resume the iteration with `/agile-dev:iterate`. Capture the change scope inside Refinement (or the current phase) of the in-flight epic."
- **Cancel:** stop.

### 2b — Change in progress?

Check whether `.project-artifacts/changes/` contains a directory whose `change-state.md` has `status: IN_PROGRESS`.

- **Found one:** ask the user — "There is a change already in progress: **<title>** at phase **<phase>**. Continue from there, or start a new change? (continue/new)"
  - If continue: resume from the saved phase.
  - If new: proceed normally.
- **Not found:** proceed normally.

---

## Step 3 — Focused codebase analysis

Do not run a full Analysis of the entire codebase. Instead, read only what is relevant to this specific change:

1. Identify the area of the codebase affected: which modules, packages, files, or layers the change will touch.
2. Read those files using available tools. Look for:
   - Existing structure and conventions in the affected area
   - Current test coverage for the code being changed
   - Any TODO/FIXME comments or known issues in the affected area
   - Dependencies the changed code has on other modules
3. Ask the user only for things that cannot be determined from the code: undocumented design decisions, business rules, known constraints.

Produce a brief focused summary (not a full Analysis document — just enough to inform Refinement):
- Affected files and components
- Relevant conventions and patterns to follow
- Existing test coverage in the affected area
- Any gotchas or constraints to carry into Refinement

---

## Step 4 — Environment check

Check whether a dev container already exists for this project:

- **`.devcontainer/devcontainer.json` exists:** ask the user — "Are you already running inside the dev container for this project? (yes/no)". If yes, proceed. If no, instruct them to reopen in the container first.
- **No `.devcontainer/` exists:** read `${CLAUDE_PLUGIN_ROOT}/pipeline/environment.md` for the full Environment phase definition, then:
  1. Determine the tech stack from the affected files and dependency manifests (package.json, go.mod, pom.xml, requirements.txt, Cargo.toml, etc.).
  2. Generate `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, and `.claude/settings.json` tailored to the detected stack.
  3. Present the three files and instruct the user to reopen the project in the container.
  4. Wait for the user to confirm they are inside the container before proceeding.

⛳ CHECKPOINT Environment: user confirms they are inside the dev container.

---

## Step 5 — Run the change phases

Load each phase file as you reach that phase — do not load all files upfront. Work through these phases in order:

### Slug and directory

Derive a slug from the change title: lowercase, hyphens, no spaces (e.g. `add-csv-export`, `refactor-auth-middleware`).
All output files go to: `.project-artifacts/changes/<slug>/`

Create `change-state.md` there:

```markdown
# Change State

title: <change title>
status: IN_PROGRESS
current_phase: Refinement
slug: <slug>
```

---

### Refinement [INTERACTIVE]

- Keep scope tight: one change, not a roadmap.
- Read `${CLAUDE_PLUGIN_ROOT}/pipeline/refinement.md` for the phase definition.
- Ask clarifying questions one at a time. Focus on:
  - What exactly changes (behaviour before vs after)
  - What is explicitly out of scope for this change
  - Edge cases and failure modes
  - Backwards compatibility requirements
- Produce the Change Spec with Acceptance Criteria (ACs).
- Save to `.project-artifacts/changes/<slug>/spec.md`.
- Update `change-state.md`: `current_phase: Refinement`.
- ⛳ CHECKPOINT: present and wait for APPROVE.

---

### Decomposition

- Use the approved spec.
- Read `${CLAUDE_PLUGIN_ROOT}/pipeline/decomposition.md` for the phase definition.
- Assign roles (DEV, QA, DEVOPS, etc.); include any necessary DOCS tasks.
- Keep the list proportionate — a small refactor should not produce 15 tasks.
- For changes with a UI: always include at least one DESIGN task and at least one E2E scenario of type UI. For backend or protocol-only changes, the equivalent E2E scenario is API / Protocol / CLI / File-batch typed — pick the type that matches how the change is actually used.
- Save to `.project-artifacts/changes/<slug>/tasks.md`.
- Update `change-state.md`: `current_phase: Decomposition`.
- ⛳ CHECKPOINT: present and wait for APPROVE.

---

### Test Plan

- Use the approved ACs from Refinement.
- Read `${CLAUDE_PLUGIN_ROOT}/pipeline/test-plan.md` for the phase definition.
- Write BDD scenarios (Given/When/Then) in plain business language — no technical jargon, no implementation details.
- Tag each scenario with **level** (Unit / Component / Contract / System-integration / E2E) and **type** (UI / API / Protocol / CLI / File-batch / etc.). The level decides which phase owns the scenario: in-process levels → Development; out-of-process levels → Verification; Contract → split by form. Type is independent of level — E2E does not mean UI.
- Also write regression scenarios for any existing behaviour this change touches.
- Save to `.project-artifacts/changes/<slug>/test-plan.md`.
- Update `change-state.md`: `current_phase: Test Plan`.
- ⛳ CHECKPOINT: present the test plan and wait for APPROVE.

---

### Development

- Read `${CLAUDE_PLUGIN_ROOT}/pipeline/development.md` for the phase definition (in-process tests + self-review checklist).
- **Baseline first:** run the existing in-process test suite before writing any new code. Any pre-existing failure must be noted and treated as a separate task — do not proceed past it silently.
- Write failing in-process tests first (TDD), then implementation, then refactor under green tests.
- Cover only the **in-process** test levels assigned in the Test Plan (Unit, Component, in-process Contract). Out-of-process levels are owned by the Verification step.
- Wire up external interfaces (HTTP routes, message handlers, CLI commands) so Verification can drive them out-of-process. No test-only shortcuts.
- Never hardcode credentials — use environment variables from the first commit.
- Apply the self-review checklist to your own output before finishing.
- Use subagents for independent parallel tasks where appropriate.
- Present a brief implementation summary (files changed, in-process tests written, decisions made).
- Update `change-state.md`: `current_phase: Development`.
- No checkpoint pause here — proceed directly to Verification.

---

### Verification

- Read `${CLAUDE_PLUGIN_ROOT}/pipeline/verification.md` for the phase definition.
- Stand up the test environment (Testcontainers, local docker-compose, or ephemeral deployed env). Record the choice and how to reproduce it.
- Stub external third parties via real contract-driven mock-server processes — never via in-process mocks at this level.
- Implement and run every System-integration and E2E scenario from `test-plan.md`, plus any out-of-process Contract scenarios. Drive the application through its real interface (HTTP / gRPC / message / socket / CLI / file drop) and assert on the BDD `Then` clause.
- Stabilise flakes by fixing root causes — quarantine with a written reason and follow-up only as a last resort.
- Save a Verification summary to `.project-artifacts/changes/<slug>/verify.md` covering: test environment, external-service stubs, scenarios run by level/type, run results, flaky/quarantined items, and AC coverage table.
- Update `change-state.md`: `current_phase: Verification`.
- No checkpoint pause here — quality is enforced by the tests; proceed directly to Integration.

---

### Integration

- Read `${CLAUDE_PLUGIN_ROOT}/pipeline/integration.md` for the phase definition.
- Build the application (run the production build command).
- Prepare `.env` (classify variables, pre-fill safe defaults, request real credentials).
- Start the application and verify it connects to all required services.
- Perform a manual smoke test of the affected user journey.
- Confirm Verification results in `verify.md`: all non-quarantined scenarios pass; every AC traces to a passing scenario.
- Update `change-state.md`: `current_phase: Integration`.
- ⛳ CHECKPOINT: present the build status, smoke test result, and AC pass/fail table alongside `verify.md`. Wait for APPROVE.

---

### Retrospective [INTERACTIVE]

- Keep this brief — proportionate to the size of the change.
- Read `${CLAUDE_PLUGIN_ROOT}/pipeline/retrospective.md` for the phase definition.
- Only surface findings that require a concrete change: were the ACs clear, did anything unexpected surface, any follow-up work needed?
- Save to `.project-artifacts/changes/<slug>/retro.md`.
- Update `change-state.md`: `current_phase: Retrospective`.
- ⛳ CHECKPOINT: present action items (or "No follow-up needed"). Wait for APPROVE.

---

## Step 6 — Close the change

After Retrospective is approved:

1. Update `change-state.md`: `status: DONE`, `current_phase: DONE`.
2. Report: "Change **<title>** is complete."
3. List the files changed and tests added.
4. If a full pipeline (`state.md`) exists in `.project-artifacts/`, offer: "This change is not tracked in the pipeline backlog. Do you want to record it as a completed epic there? (yes/no)"

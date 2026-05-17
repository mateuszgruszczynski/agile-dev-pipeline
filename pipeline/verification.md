# Verification Phase

**Purpose:** Author and run out-of-process tests against the assembled, running application. In-process tests (Unit, Component) cannot prove a deployed app works; Verification closes that gap before Integration.

**Owns:** System-integration, E2E, and out-of-process Contract scenarios from the Test Plan. Levels and types are defined in [test-plan.md](test-plan.md) — do not duplicate that material here.

> **Skipped entirely when `test_coverage = none`** in `.project-artifacts/policy.md`. The orchestrator goes Development → Integration, does not write `i5-verify.md`, and Integration's AC table changes to a manual-smoke check (see [integration.md](integration.md)).

---

## Inputs

- `i1-spec.md` — spec and ACs
- `i3-test-plan.md` — scenarios tagged by level and type; this phase owns the out-of-process ones
- `i4-dev.md` — Development summary
- `f2-architecture.md` — Integration Strategy table + Project Type Adaptations (load these sections only)

---

## Steps

1. **Stand up the test environment.** Pick one based on architecture:
   - **Testcontainers** for real infra per test run (DB, Redis, Kafka, etc.)
   - **Local docker-compose / devcontainer stack** when the test env is the dev container
   - **Ephemeral or shared deployed env** when production-like infra is required

   Record reproduction steps. Non-reproducible tests are not tests.

2. **Stub external third parties via real mock-server processes** (WireMock, Pact, hoverfly, Mockoon, hand-rolled HTTP stubs). Never in-process mocks at this level. Pin contracts to the production schema/version.

3. **Implement System-integration scenarios as test files** in the project's test framework (pytest, jest, junit, go test, rspec, vitest). The test file is the artifact — committed, re-runs in CI.
   - Drive the application via the language's real client (HTTP via `requests`/`supertest`/`RestAssured`, gRPC via generated client, broker client, socket, subprocess, filesystem).
   - Use real internal infra (DB / queue / cache).
   - Assert what the BDD `Then` clause names. Do not assert internal state unless the AC names it.

4. **Implement E2E scenarios as test files.** Type follows architecture: UI (Playwright / Cypress / WebDriver / Appium), API-only chained, protocol-driven (Kafka producer+consumer, MQTT, socket), or multi-channel. E2E does not imply UI.

5. **Run the suite** via the project's runner (`pytest`, `npm test`, `mvn verify`, `go test ./...`). Every System-integration and E2E scenario from the Test Plan must execute. A scenario waiting on external dependency or missing infra is flagged explicitly — fix now or move to a follow-up FIX epic. Do not mark uncovered scenarios as covered.

6. **Stabilise flakes by root cause.** No sleeps, no retries. If unfixable this iteration: quarantine with written reason + follow-up task.

7. **Confirm AC coverage.** Each AC has ≥1 Verification scenario unless it has no out-of-process observable (then in-process coverage from Development is sufficient and explicitly noted).

---

## ⛔ Anti-pattern — do not chat-drive HTTP/protocol calls

Invoking `curl http://localhost:8080/...` (or `grpcurl`, `kafkacat`, ad-hoc socket scripts) one request at a time from the chat is **not Verification**. Costs:

- Each request + response lands in conversation context (~500–2000 tokens per call). A 5-roundtrip scenario can burn 10k+ tokens that a single test-file run compresses into a one-line pass/fail.
- Nothing is committed. The "passing" result vanishes with the session. No regression coverage.
- Test Plan scenarios become orphaned: tagged but with no test file in the repo.

`curl` is fine for one-off debugging or Integration's brief manual smoke. Not for Verification.

---

## Use subagents — default for independent test authoring

Delegate test authoring to subagents by default. Scenarios are usually independent and parallelizable. The orchestrator owns environment setup, mock-server configuration, and AC coverage confirmation.

- **Pass:** the scenario(s), test environment description, interface contract, BDD `Then` clause to assert. Tell it to produce a runnable test file in the project's framework.
- **Expect:** the test file content. Orchestrator integrates, runs, aggregates results.

Parallelize when scenarios are independent. Sequential when they share fixtures.

Skip for <3 scenarios or one-line additions to existing files.

---

## Output

Write `i5-verify.md`:

- **Test environment** — setup + reproduction steps
- **External-service stubs** — which third parties, which mock server / contract
- **System-integration tests** — count by type + AC each covers
- **E2E tests** — count by type + AC each covers
- **Run results** — totals, pass/fail, failures with fix
- **Quarantined tests** — reason + follow-up task
- **AC coverage table** — one row per AC: Verification scenarios that prove it, or "in-process only" with justification

---

## Bundle handling

When the iteration covers multiple epics, `i5-verify.md`'s AC coverage table groups rows per epic. Same DoD applies across all bundled epics — every AC of every epic in the bundle traces to a passing scenario (unless `test_coverage = none`).

---

## Definition of Done

- Test environment reproducible and recorded in `i5-verify.md`
- Every System-integration and E2E scenario from the Test Plan implemented and run
- All non-quarantined tests pass
- Every quarantined test has reason + follow-up FIX task
- Each AC covered by ≥1 Verification scenario, or in-process coverage with explicit note
- `i5-verify.md` written and accurate

Fix any failure before Integration. No deferral.

## Policy effects

`test_coverage` axis:
- `thorough` (default) — full behaviour above: implement every scenario, full AC coverage, mock-server stubs, real internal infra.
- `minimal` — implement only the System-integration / E2E scenarios that exist in `i3-test-plan.md`. Under `test_coverage = minimal`, the Test Plan itself contains only happy-path scenarios — so this phase implements those happy paths only. No additional scenarios.
- `none` — phase **skipped entirely**. Orchestrator goes Development → Integration. No `i5-verify.md`. Quality gate in Integration becomes manual smoke + the build passing.

`detail` axis (applies to `i5-verify.md` content when phase runs):
- `full` — full output as above.
- `sparse` — drop the per-scenario "AC each covers" breakdown; keep counts and run results.
- `minimal` — environment + run results table only (pass/fail counts).

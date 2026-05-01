# Verification Phase

**Purpose:** Author and run **out-of-process tests against the assembled, running application**. This is where system-integration tests and end-to-end tests are written and executed — black-box, against real interfaces, on a runtime that resembles production.

This phase exists because in-process tests (unit, component) — however thorough — cannot prove that the deployed application works. Code that passes in-process tests can still fail when it hits the real wire, real infra, real auth, and real third parties. Verification closes that gap before Integration.

---

## Test levels and types — orthogonal axes

The pipeline separates **level** (scope and isolation) from **type** (medium / interface). A test of any level can be of any type; an E2E test is not a UI test by definition.

**Level — owned by phase:**

| Level | Scope | Boundary | Owned by |
|---|---|---|---|
| Unit | Single function/class | In-process | Development |
| Component | Multiple internal classes interacting | In-process; mocks for external collaborators | Development |
| Contract | Boundary between this system and an external service (API shape, message format) | Either | Whichever phase the form fits — usually Development if mock-server-based, Verification if it requires the running service |
| System-integration | Assembled application behind its real interface | Out-of-process; real internal infra (DB, queue, cache, file system); external third parties stubbed via contract-driven mock servers | **Verification** |
| E2E | Full operator/user journey across the system | Out-of-process; real or production-like environment | **Verification** |

**Type — independent of level:**

- **UI** — drive a browser, desktop window, or mobile screen
- **API** — HTTP / REST / GraphQL / gRPC
- **Protocol** — TCP / UDP / raw sockets / pub-sub / MQTT / AMQP / Kafka / WebSocket
- **CLI** — subprocess invocation, stdin/stdout/exit-code assertions
- **File / batch** — drop a file, observe outputs

A backend service may have E2E tests that are entirely API-typed (no UI). An IoT system may have E2E tests over MQTT. A distributed system's E2E test may chain API + queue + protocol.

When the Test Plan tags a scenario, it carries both axes: e.g. *"Level: System-integration, Type: HTTP API"* or *"Level: E2E, Type: Pub-Sub (Kafka) + REST"*.

---

## Inputs

- `i1-spec.md` — the spec and ACs.
- `i3-test-plan.md` — the Test Plan, with each scenario tagged by level and type. Scenarios at System-integration and E2E levels are owned by this phase.
- `i4-dev.md` — Development summary, including which in-process tests already exist.
- `f2-architecture.md` — to confirm which interfaces and third-party services are in scope.

---

## Steps

1. **Stand up the test environment.** Decide based on the architecture:
   - **Testcontainers** (or equivalent) for real infra brought up per test run — DB, Redis, Kafka, etc.
   - **Local docker-compose / devcontainer stack** — when the test environment is the developer's running container.
   - **Ephemeral or shared deployed environment** — when the test depends on production-like infra (cloud-only services, managed identity, real DNS).

   Record the choice and how to reproduce it. Tests that cannot be reproduced are not tests.

2. **Stub external third parties via contract-driven mock servers** (WireMock, Pact, hoverfly, Mockoon, or hand-rolled HTTP stubs) — never via in-process mocks at this level. The mock server runs as a real process and the application talks to it over the real wire. Pin contracts to the same schema/version used in production.

3. **Implement the system-integration scenarios** from the Test Plan. For each:
   - Drive the application through its real interface (HTTP request, gRPC call, message publish, socket connect, CLI invocation, file drop).
   - Use real internal infra (DB, queue, cache).
   - Assert the observable outcome that the BDD `Then` clause names — what a user sees, what the system makes available, or what an external observer can detect.
   - Do not assert against internal state (table rows, in-memory variables) unless the AC explicitly names that observable output.

4. **Implement the E2E scenarios** from the Test Plan. Type depends on the architecture: UI (Playwright / Cypress / WebDriver / Appium), API-only (driver script that chains HTTP / gRPC calls), protocol-driven (Kafka producer + consumer assertions, MQTT client roundtrip, socket client). For multi-channel E2E, drive each channel in the order the user/system would, and assert on the channel where the outcome appears.

5. **Run the tests against the running application.** Every system-integration and E2E scenario in the Test Plan must execute. A scenario that is not yet implementable (waiting on external dependency, missing test infra) must be flagged explicitly — either fix it now or move it to a follow-up FIX epic in Retrospective; do not mark it as covered.

6. **Stabilise flakes.** A flaky out-of-process test is worse than no test — it teaches the team to ignore the suite. For any test that fails intermittently:
   - Fix the root cause (race, timing, fixture leak) — not the symptom (retry, sleep).
   - If the root cause is in the application, return to Development; record it in `i4-dev.md` as a follow-up.
   - If genuinely cannot be stabilised this iteration, quarantine with a written reason and a follow-up task.

7. **Confirm coverage against ACs.** For each AC in the spec, list which Verification-level scenarios cover it. Gaps must be either filled or escalated.

---

## Output

Write `i5-verify.md` to the iteration directory, containing:

- **Test environment** — how it was stood up and how to reproduce
- **External-service stubs** — which third parties were stubbed, with which contract / mock server
- **System-integration tests** — count by type (API / protocol / CLI / file), with the AC each covers
- **E2E tests** — count by type (UI / API / protocol / multi-channel), with the AC each covers
- **Run results** — totals, pass/fail, and any failures with their fix
- **Flaky tests** — quarantined items with reason and follow-up task
- **AC coverage table** — one row per AC, showing the Verification-level scenarios that prove it (and which ACs are still gated only by in-process tests, which is acceptable when the AC has no out-of-process observable)

---

## No checkpoint pause

Like Development, Verification produces an artifact and proceeds directly. Quality is enforced by the tests themselves: if a Verification scenario fails, the phase cannot complete until it is fixed (or escalated and quarantined with reason). The user reviews `i5-verify.md` at the Integration checkpoint, where it is read alongside the build and demo result.

---

## Definition of Done — Verification

The Verification phase is done when:

- The test environment is reproducible and recorded in `i5-verify.md`
- Every System-integration and E2E scenario from the Test Plan is implemented and runs against the real application
- All non-quarantined Verification tests pass
- Every quarantined test has a written reason and a follow-up FIX task
- Each AC has at least one Verification-level scenario covering it, **unless** the AC has no out-of-process observable (in which case the in-process coverage from Development is sufficient and explicitly noted)
- `i5-verify.md` is written and accurate

If any item fails, fix before advancing to Integration. Do not defer.

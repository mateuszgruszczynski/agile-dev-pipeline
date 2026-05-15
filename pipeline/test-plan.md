# Test Plan Phase

**Purpose:** Translate the approved ACs into a concrete, human-readable test plan — a set of acceptance test scenarios written in BDD format **before any code is written** (shift-left). The output is a plan, not executed tests: it specifies expected behaviour and tags each scenario with a **level** (scope/isolation) and a **type** (interface/medium). Implementation is split between Development (in-process levels) and Verification (out-of-process levels).

**Format per test scenario:**

- **ID** — short identifier (e.g. T-01)
- **Feature** — the epic or feature being tested
- **Scenario** — one-line description of what is being verified (e.g. "User logs in with valid credentials")
- **Covers AC** — reference to the AC from Refinement this scenario validates
- **Level** — assigned using the decision rule below: Unit / Component / Contract / System-integration / E2E
- **Type** — UI / API (HTTP/gRPC/GraphQL) / Protocol (TCP/UDP/sockets/pub-sub/MQTT/Kafka/WebSocket) / CLI / File-batch / etc. A scenario may carry more than one type (e.g. *API + Pub-Sub* for a request that triggers a downstream message)
- **Owned by** — derived from level: in-process levels (Unit, Component) → Development; out-of-process levels (System-integration, E2E) → Verification; Contract → either, depending on form (see below)
- **BDD scenario:**
  ```
  Given [the context or preconditions — system state, user role, data setup]
  When  [the action the user or system takes]
  Then  [the observable outcome — what the user sees or what the system makes available]
  And   [additional outcome assertions, if needed]
  ```
- **Notes** — edge cases, variants, or explicit exclusions

**Writing guidelines:**
- Write in plain language that a non-technical stakeholder can read, follow, and verify during a live demo
- Use domain language from the spec — no class names, HTTP status codes, SQL, or database table names in the scenario text
- "Then" describes what the user observes or what the system makes available — not what function was called or what record was inserted
- Happy path scenarios first, then alternative paths and failure cases
- If a scenario cannot be written without technical jargon, the AC is probably too implementation-specific — go back and rewrite the AC in Refinement
- Each scenario should be independently executable: a reader with no prior context should be able to follow it

**Levels and types — orthogonal axes:**

- **Level** describes scope and isolation (what is real vs. faked, in-process vs. out-of-process). It is independent of the medium.
- **Type** describes the interface or medium the test exercises. UI is one type; an HTTP API is another; a Kafka topic, a TCP socket, a CLI invocation are others. A backend service can have E2E tests entirely at the API or protocol type — there is no rule that E2E means UI.

Assign **both** axes per scenario. The level decides which phase owns the test; the type decides what tooling is used to drive it.

**Level decision rule (assign the lowest level that meaningfully verifies the scenario):**

```
1. UNIT — in-process, owned by Development
   Can this be verified by calling a function/method/class in isolation,
   with all dependencies replaced by fakes or test inputs?
   → Yes: Unit test. Stop.

2. COMPONENT — in-process, owned by Development
   (Also called module-integration or in-process integration.)
   Does this require two or more real internal classes working together
   (e.g. service + repository, handler + use-case), with external
   dependencies (DB, queue, third-party API) replaced by mocks or fakes?
   Does it run inside the same process as the application code
   (e.g. Spring's @SpringBootTest, FastAPI TestClient, ASP.NET WebApplicationFactory)?
   → Yes: Component test. Stop.

3. CONTRACT — owned by either phase
   Does this verify the schema/shape/protocol at a boundary with an external service?
   - If the test runs against a static contract or mock server in-process: Development.
   - If the test requires the running service or a deployed mock: Verification.
   → Yes: Contract test. Stop, and tag which phase owns it.

4. SYSTEM-INTEGRATION — out-of-process, owned by Verification
   Does this require the assembled application running behind its real interface
   (HTTP / gRPC / message queue / socket / CLI), with real internal infra
   (real DB, real Redis, real broker — typically via Testcontainers or a deployed
   stack), and external third parties stubbed via a real mock server?
   → Yes: System-integration test. Stop.

5. E2E — out-of-process, owned by Verification
   Does this require a full operator/user journey across the system, possibly
   chaining multiple interfaces (e.g. HTTP request triggers a Kafka message that
   updates a DB read by another HTTP endpoint)?
   The journey may or may not involve a UI — type is independent of level.
   → Yes: E2E test. Tag the type(s) it spans.
```

**Anti-conflation reminder:** Do not write "E2E (UI)" or "E2E (non-UI)" as if they were levels. Write *Level: E2E, Type: UI* or *Level: E2E, Type: HTTP API*.

**Definition of Testability:** Every AC must satisfy the DoT in [definitions.md](definitions.md). If you cannot write a scenario for an AC without technical jargon, the AC fails DoT — return to Refinement and rewrite it before continuing.

**Anti-duplication rule:** If a scenario is assigned to Unit, do not also write a Component or System-integration test for the same behaviour. Higher-level tests verify integration paths and user flows — not logic already covered below. When in doubt, ask: "what would break here that a lower-level test would not catch?"

**Coverage requirement:** Each AC needs at least one scenario at its lowest meaningful level — but every AC with an out-of-process observable (anything visible at the application's real interface) **must also have a System-integration or E2E scenario** owned by Verification. In-process coverage alone is not sufficient when the AC describes behaviour the user or another system observes through the wire.

**Guidelines:**
- Write at least one scenario per AC; write additional scenarios for edge cases and failure paths
- Scenarios should be readable by someone who did not write the spec
- If a scenario cannot be written clearly, the AC is probably too vague — go back and tighten Refinement
- After assigning levels, verify the set covers all ACs without obvious gaps or redundancy
- *When working on an existing codebase:* also write regression scenarios for existing behaviour that this epic touches. If existing behaviour has no tests, write them now before changing anything.

**Subagent — default for BDD scenario drafting.** Skip only for very small epics (<3 ACs). Level/type tagging stays with the orchestrator — the pyramid rule needs judgment.

- **Pass:** approved spec (`i1-spec.md`) with ACs, writing guidelines from this file, BDD format spec. Tell it to produce ≥1 scenario per AC plus regression scenarios for behaviour this epic touches.
- **Expect:** draft scenarios in BDD format, no level/type tags. Orchestrator assigns level (decision rule) and type (matching architecture interfaces), writes `i3-test-plan.md`.

**Output:**
- Acceptance test scenarios list (document or table)

**Policy effects:**

`test_coverage` axis:
- `thorough` (default) — full behaviour above: ≥1 scenario per AC plus edge / failure / regression scenarios.
- `minimal` — one happy-path scenario per AC; skip edge-case and failure-path scenarios unless an AC explicitly names one. No regression scenarios unless the touched code has no existing tests at all.
- `none` — this phase is **skipped entirely** by the orchestrator; `i3-test-plan.md` is not produced. Iteration goes Decomposition → Development (no Test Plan, no Verification). DoD adapts accordingly (see definitions.md).

`detail` axis (applies when `test_coverage` is `thorough` or `minimal`):
- `full` — full BDD scenarios with Given / When / Then / And + Notes per scenario.
- `sparse` — Given / When / Then only, no Notes block.
- `minimal` — scenario ID + one-line scenario name + level/type tag + AC reference. No Given/When/Then. The orchestrator can fill the BDD later if needed.

**⛳ CHECKPOINT Test Plan:** User reviews the plan and confirms it correctly captures expected behaviour. No implementation begins until the plan is approved. (Skipped entirely when `test_coverage = none`.)

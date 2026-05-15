# Decomposition Phase

**Purpose:** Break the approved epic spec into concrete tasks, assigned by role. Tasks should be small enough to be independently completable and reviewable.

**What to define per task:**
- Short title
- Role responsible: DEV / QA / DEVOPS / SRE / SECURITY / DESIGN / DATA
- Description (what exactly needs to be done)
- Dependencies on other tasks in this iteration
- Testability notes (how will we know this task is done?)

**Roles reference:**

Use the role set chosen during Architecture. Small projects may use only DEV + QA; large distributed systems may use all. Apply only the roles relevant to this project.

| Role | Responsibility | Typical app types |
|---|---|---|
| DEV | Implementation, in-process tests (Unit / Component / in-process Contract), code review | All |
| QA | Test strategy and out-of-process tests (System-integration / E2E / out-of-process Contract) — owned by Verification phase. Type follows architecture: UI, API, protocol, CLI, file-batch | All |
| DEVOPS | CI/CD, containers, infrastructure, deployments | Web, backend, distributed |
| SRE | Reliability, observability, alerting, runbooks | Backend, distributed |
| SECURITY | Threat modeling, dependency audits, secrets, input review | All (scaled to risk) |
| DESIGN | UX/UI design, accessibility, design system, visual styling | Web, desktop, mobile |
| DATA | Analytics, event tracking, data pipelines, dashboards | Web, mobile, data products |

**Task types to consider (only include relevant ones):**
- DEV: implementation tasks plus in-process tests (Unit, Component, in-process Contract), broken down by component or layer
- QA: out-of-process test tasks owned by Verification — System-integration, E2E, out-of-process Contract — with the **type** specified per task (UI, API/HTTP/gRPC/GraphQL, Protocol/TCP/UDP/sockets/pub-sub/MQTT/Kafka/WebSocket, CLI, File-batch). E2E does not imply UI; pick the type the user or system actually uses.
- DEVOPS: pipeline, containerization, environment config, deployment scripts, **local run verification** (ensuring `npm start` / `docker compose up` / equivalent works end-to-end on a developer machine)
- SRE: monitoring, alerting, runbooks, dashboards
- SECURITY: dependency audit, secrets management, input validation review, threat model update
- DESIGN: component design, accessibility review, design tokens, styling, UX review
- DOCS: any documentation that must be produced or updated as part of this epic (see Documentation Policy below)

**Documentation Policy:**
Generate documentation as part of the iteration that produces the thing being documented — not as a separate later effort. For each epic, determine at decomposition time which docs are needed:

- **API docs** (e.g. OpenAPI spec, man page, CLI --help) — DEV task, done when the API is done
- **README / getting started** — DEV or DOCS task; update on any public-facing change
- **Architecture Decision Records (ADRs)** — written in Architecture for foundation decisions; one ADR per significant decision made during an iteration
- **Changelog entry** — added to CHANGELOG.md as part of every merged feature or fix
- **Runbook / ops guide** — SRE task, done alongside the observability work in Development
- **Onboarding / user guide** — DOCS task; only for user-facing features, written when the feature is stable

Documentation tasks appear in the task list like any other task, with a role owner and a done condition.

**Guidelines:**
- Order tasks to enable parallel work where possible
- Flag tasks that block others clearly
- Each DEV task should have corresponding in-process test coverage (DEV) plus, where the behaviour is observable out-of-process, a Verification-owned scenario (QA)
- Infrastructure and security tasks should not be deferred to the end
- For epics with a UI: always include at least one DESIGN task and at least one E2E scenario of type UI. For backend / protocol-only epics, the equivalent E2E task is API / Protocol / CLI / File-batch typed — pick the type that matches how the epic is actually used

**Subagent — default for task list drafting.** Skip only for very small epics (<5 tasks). Role assignments and dependencies stay with the orchestrator — they need conversation context.

- **Pass:** approved spec (`i1-spec.md`), active role set (from `f2-architecture.md`), Task types + Documentation Policy below.
- **Expect:** ordered draft list with proposed role + description + done condition per task. Orchestrator reviews roles, adjusts dependencies, writes `i2-tasks.md`.

**Output:**
- Ordered task list with role assignments and dependencies

**Policy effects** (`detail` axis):
- `full` — task title + role + description + dependencies + testability/done condition.
- `sparse` — task title + role + one-line description. Drop dependencies unless critical, drop testability note.
- `minimal` — task title + role only (one line per task). No description, no deps.

**⛳ CHECKPOINT Decomposition:** User reviews task breakdown and confirms nothing is missing or misassigned.

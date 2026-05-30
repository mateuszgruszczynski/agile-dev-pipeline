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

**Step 1 — Implementation decisions review (before task generation)**

Read `i1-spec.md` and identify every non-trivial implementation decision the spec implies but does not specify. These are choices Claude would otherwise make silently and embed invisibly in tasks. Common categories:

- Data model: schema structure, how entities are identified or deduplicated, indexing strategy
- Algorithm or strategy: matching logic, ranking, caching, retry/backoff approach
- Integration style: sync vs async, polling vs webhook, batch vs streaming
- State management: where and how state is stored, consistency guarantees, handling of concurrent updates
- Error and edge-case handling: what happens on partial failure, what the user sees

For each decision, present it as one of two forms:

> **Decision needed — [topic]**
> - Option A: [description] — [tradeoff]
> - Option B: [description] — [tradeoff]
> *(Option C if genuinely distinct)*
> Which do you prefer?

> **Intended approach — [topic]**
> I'll [approach] because [reason]. Let me know if you'd like to do it differently.

Use "Decision needed" when multiple approaches are genuinely reasonable and the choice has meaningful consequences. Use "Intended approach" when one path is clearly right for this stack and spec, but the choice is non-obvious enough that the user should know about it.

Present all decisions together in one message. Wait for the user to respond. Record every confirmed choice as a **Design Decisions** section at the top of `i2-plan.md` before the Tasks section. Do not generate tasks until all decisions are confirmed.

---

**Step 2 — Task list**

**Subagent — default for task list drafting.** Skip only for very small epics (<5 tasks). Role assignments and dependencies stay with the orchestrator — they need conversation context.

- **Pass:** approved spec (`i1-spec.md`), confirmed design decisions, active role set (from `f2-architecture.md`), Task types + Documentation Policy below.
- **Expect:** ordered draft list with proposed role + description + done condition per task. Orchestrator reviews roles, adjusts dependencies, writes tasks into `i2-plan.md`.

**Output:**
- Write `i2-plan.md` (create the file with a `# Iteration NNN Plan` heading):

  ```markdown
  # Iteration NNN Plan

  ## Design Decisions

  [one line per confirmed decision: topic → chosen approach]

  ## Tasks

  [ordered task list]
  ```

After writing Tasks, **immediately run the Test Plan phase** (load `${CLAUDE_PLUGIN_ROOT}/pipeline/test-plan.md`) without pausing for user input. Test Plan appends the **Test Scenarios** section to the same `i2-plan.md`. The combined checkpoint at the end of Test Plan presents the full `i2-plan.md`.

**Policy effects** (`detail` axis):
- `full` — task title + role + description + dependencies + testability/done condition.
- `sparse` — task title + role + one-line description. Drop dependencies unless critical, drop testability note.
- `minimal` — task title + role only (one line per task). No description, no deps.

**Bundle handling**: when the iteration has multiple epics, `i2-plan.md` Tasks section has one sub-section per epic. Tasks within each sub-section are tagged with the parent epic (e.g. `EP-3 DEV-1 — Index schema`). The straightforward / judgment-needed checkpoint rule applies to the bundle as a whole, not per epic.

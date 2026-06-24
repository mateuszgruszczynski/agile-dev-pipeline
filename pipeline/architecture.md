# Architecture & Tech Stack Phase  [INTERACTIVE]

**Purpose:** Decide the high-level system shape and technology choices. Produce just enough architecture to make informed epic planning — not a full design doc.

*When entering from Analysis (existing codebase): start from the C4 diagrams produced in Analysis. Architecture describes **what changes** — components to add, remove, or restructure. Propose tech stack changes only when justified; prefer consistency with what already exists unless there is a clear reason to diverge. Flag any breaking changes to existing interfaces explicitly.*

**What to define:**
- App type confirms which roles/concerns apply (e.g. no DEVOPS for a local CLI tool; no DESIGN for a headless server)
- High-level components (e.g. frontend, backend API, database, worker, CLI, daemon, mobile client)
- Technology stack: language(s), frameworks, key libraries, runtime environments
- Data storage approach (if any): local files, embedded DB, remote DB, event store, etc.
- Integration points: external APIs, services, protocols (see Integration Strategy below)
- Deployment target: local machine, cloud, container, app store, package manager
- **Orchestration & containerization decision:** Does this project need containers (Docker)? Container orchestration (Compose, Kubernetes, ECS)? Serverless functions? A monolith on a VM? Decide here and record the rationale. Small projects default to the simplest option.
- Key quality attributes to prioritize: performance, reliability, security, maintainability, portability
- Roles that apply to this project (subset of: DEV, QA, DEVOPS, SRE, SECURITY, DESIGN, DATA)
- **UI and design level:** if the project has a user interface, decide the level of UI polish expected:
  - *Functional* — no dedicated styling effort; the app works but looks basic
  - *Clean* — a simple design system or component library; readable and professional
  - *Polished* — full visual design with branding, animations, and accessibility focus
- **Security posture:** authentication mechanism (if any), secrets and credentials management strategy (environment variables, secrets manager, vault), data sensitivity classification. Every project must decide how credentials are handled before the first line of code is written.
- **Deliverable artifact:** what end users actually get to run. Decide here so Environment can generate the right production build recipe and Integration knows what to produce. Capture:
  - **Type:** one of — `native-binary` (e.g. Go / Rust statically-linked), `jar` / `war` (JVM), `npm-bundle` (Node.js distributable), `docker-image` (containerised app), `tarball` (archive of a directory), `platform-installer` (.dmg / .msi / .deb / .rpm / .exe), `script` (a bash/python script with its dependencies).
  - **Target platforms:** the OS+arch pairs the artifact must run on, e.g. `linux-x86_64`, `linux-arm64`, `darwin-arm64`, `windows-x86_64`. If multiple are required and the language doesn't cross-compile cleanly, plan accordingly (Architecture flags it; Environment generates platform-specific build commands; Integration may build per-platform).
  - **Run instructions:** the one-line invocation a user runs after copying the artifact to a machine, e.g. `./myapp --port 8080`, `java -jar myapp.jar`, `docker load < image.tar.gz && docker run myapp:latest`. This is what gets embedded in `i3-outcome.md` and `releases/v<version>.md`.
  - **External runtime requirements:** anything the user must have installed on the target machine besides the artifact, e.g. "JVM 21+", "Docker", "none — statically linked".

**Example questions to draw from — adapt to the conversation, do not run as a script:**

The list below is a non-exhaustive starter set. Pick the ones that close real gaps for *this* project, ask follow-ups based on the answers, and skip any that earlier answers (or the Vision output) have already covered. **Stop asking when you have enough information to produce every item in the Output section below** — running through every example question is not the goal; getting to a confident Output is.

- "Will this need to run offline or always requires network access?"
- "Is multi-user or concurrent access required?"
- "Do you already have infrastructure preferences (Docker, serverless, bare metal)?"
- "What are your expectations around observability and logging?"
- "Does this need to scale horizontally, or is a single instance sufficient?"
- "What level of UI polish do you expect — functional, clean, or polished?"
- "How will the application manage credentials and secrets? (env vars, secrets manager — never hardcoded)"
- "What data does this system store, and how sensitive is it?"

**Integration Strategy (define once here, referenced throughout iterations):**

For each external service identified:
- Name and purpose (e.g. "Stripe — payment processing")
- Integration style: REST / GraphQL / gRPC / SDK / webhook / message queue
- Auth method: API key, OAuth, mTLS, etc.
- Contract ownership: do we own the contract, or does the external provider?
- Mock/stub policy: use a mock in local dev and CI; hit the real service only in staging/production
- Error handling expectations: retries, circuit breaker, fallback behavior
- Which iteration this integration is first needed (maps to epic in Backlog)

**Project Type Adaptations:**

Use the app type to scope roles, test types, and demo expectations. Apply only the rows that match this project; if it spans multiple types, take the union.

| App type | Roles | Skip | Tests | Demo |
|---|---|---|---|---|
| CLI tool (small) | DEV, QA, SECURITY (lightweight) | DEVOPS unless publishing to a package manager; SRE; DESIGN; DATA | unit + CLI smoke tests | run the command, show output |
| Desktop app — web renderer (Electron, Tauri) | DEV, QA, DESIGN, SECURITY | SRE unless it phones home; DEVOPS unless auto-update is needed | unit + integration + UI/snapshot + E2E | launch and use the app — runs inside the container |
| Native desktop app (egui, Qt, GTK, Swift/AppKit, wxWidgets) | DEV, QA, DESIGN, SECURITY | SRE; DEVOPS unless publishing installer builds | unit + integration, headless (no display required) so they pass in CI and inside the container | **hybrid mode** — build inside the container, run the binary on the host. Do not attempt to open a GUI window inside the container. |
| Web app (frontend + backend) | DEV, QA, DEVOPS, SRE, SECURITY, DESIGN; DATA optional | — | unit + integration + E2E + contract (if external APIs) + **E2E UI (Playwright/Cypress) — mandatory, not optional** | live URL or local server with a manual smoke test of the core user flow |
| Mobile app | DEV, QA, DESIGN, SECURITY; DEVOPS optional (CI publishes builds); DATA optional | — | unit + integration + UI + E2E (device/emulator) | running on device or simulator |
| Backend service / API | DEV, QA, DEVOPS, SRE, SECURITY | DESIGN | unit + integration + contract + performance (if latency-sensitive) | API calls showing expected behaviour |
| Distributed system | All roles | — | all test types including contract and chaos/resilience testing | end-to-end flow across services |

Record the chosen role set and applicable test types in the Architecture output so Decomposition and Test Plan phases inherit them without re-deciding.

**Diagrams — format standard:**

All architecture diagrams are produced as code, stored in the repository. No binary diagram files.

- **C4 Model** is the standard. Produce the levels that add value:
  - *Level 1 — System Context:* always produce this.
  - *Level 2 — Container:* produce for multi-component systems.
  - *Level 3 — Component:* only when a container is complex enough to need it.
  - *Level 4 — Code:* rarely worth it; skip unless the domain model is the core complexity.
- **Mermaid** is the default rendering format. Use it for C4 diagrams and sequence diagrams.
- **PlantUML** is acceptable as an alternative if the team already uses it.

**Subagent — default for document drafting.** Skip only for very small projects (single CLI tool, one-file script). The C4 diagrams and integration strategy table are particularly worth offloading. High-stakes decisions (tech stack, role set, orchestration approach, security posture) stay with the orchestrator and the user.

- **Pass:** approved Vision (`f1-vision.md`), user's answers, Output requirements + diagram standard + Project Type Adaptations table from this file.
- **Expect:** full architecture document with Mermaid diagrams. Orchestrator reviews, fixes decisions, writes `f2-architecture.md`.

For complex projects, pin a heavier model on the subagent call (e.g. `model: opus`) for architecture reasoning; orchestrator's default model is fine for the rest of Foundation.

**Output:**
- C4 Context diagram (Mermaid)
- C4 Container diagram (Mermaid) — if multi-component
- Tech stack decision (with brief rationale for non-obvious choices)
- Orchestration and containerization decision
- Integration strategy table (one row per external service)
- Deployment target description
- Active roles for this project
- Key quality attributes in priority order
- UI and design level decision (functional / clean / polished)
- Security posture: auth mechanism, secrets management strategy, data sensitivity classification
- Deliverable artifact: type + target platforms + run instructions + external runtime requirements

**⛳ CHECKPOINT Architecture:** User reviews and approves architecture, stack, UI level, and security posture before proceeding.

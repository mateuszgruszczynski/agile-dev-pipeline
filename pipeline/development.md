# Development Phase

**Purpose:** Implement the epic — write the code and the **in-process tests** (Unit and Component levels). Code Review is folded into this phase as a self-applied checklist; there is no separate Review checkpoint.

**Out-of-process tests are not written here.** System-integration and E2E scenarios from the Test Plan are owned by the [Verification phase](verification.md) and run against the assembled, running application. Contract tests sit in either phase depending on form (in-process mock-server tests live here; tests requiring the deployed service live in Verification).

All implementation follows TDD at the in-process levels — tests are written before or alongside the code, never after.

- Write failing in-process tests first (Unit, then Component as needed) for each piece of logic
- Implement code to make tests pass
- Refactor under green tests
- Follow the agreed stack and architecture — no unilateral tech changes
- Keep commits small and focused; each commit must pass all in-process tests
- No commented-out code, no untracked TODOs

*When working on an existing codebase:* run the existing in-process test suite before making any changes to establish a green baseline. Any pre-existing failure must be noted and treated as a FIX epic, not silently inherited. Match the existing code style and conventions unless the epic explicitly calls for a style change.

**Use subagents** for independent parallel implementation work where appropriate (e.g. multiple DEV tasks on different modules with no shared state). Apply the self-review checklist to subagent output the same as your own.

**Security rules — apply from the first commit:**
- Never hardcode credentials, API keys, database passwords, or tokens in source code
- All environment-specific configuration (URLs, connection strings, feature flags) must be externalized via environment variables or a configuration file that is not committed to version control
- Add a `.env.example` file listing all required environment variables with placeholder values; the real `.env` is always in `.gitignore`
- Verify no secrets are committed before every push (use a pre-commit hook or secret scanner if available)

---

## Self-review checklist

Apply this checklist to your own output before declaring Development complete. There is no separate Review checkpoint — this is a self-applied gate.

- [ ] Does this match the ACs from Refinement and the in-process scenarios from the Test Plan?
- [ ] Are edge cases handled in the code (separately from whether out-of-process tests will catch them)?
- [ ] Are there no hardcoded secrets or credentials?
- [ ] Is error handling appropriate?
- [ ] Are all in-process scenarios from the Test Plan implemented (Unit, Component, and Contract-in-process)?
- [ ] Does this introduce any new dependencies? Are they justified?
- [ ] Does this follow the agreed architecture from Architecture? No unilateral structural changes.
- [ ] Are all new public interfaces documented (API, CLI flags, config options)?
- [ ] Are the application's external interfaces (HTTP routes, message handlers, CLI commands) wired up such that Verification can drive them out-of-process? (Routes registered, handlers exposed, no test-only shortcuts.)

**Note on AI-generated code:** Apply the same checklist with extra attention to:
- Hallucinated or subtly wrong library usage — verify against actual docs
- Logic that looks plausible but is incorrect at edge cases
- License compatibility of any suggested dependencies
- Over-engineered patterns that don't fit the project's simplicity level

If any item fails, fix it before moving on. Do not produce a Development summary until all items pass.

---

## Test policies — in-process tests only

This phase covers the in-process levels from the Test Plan. The table below defines what each level is and how it runs. Out-of-process levels (System-integration, E2E) are listed for reference but are owned by [Verification](verification.md).

| Level | Owned by | What is real | What is faked | When to run |
|---|---|---|---|---|
| **Unit** | Development | Single function/class | All collaborators (fakes, stubs, test inputs) | Every commit, in CI |
| **Component** | Development | Multiple internal classes interacting in-process (e.g. service + repository) | External dependencies (DB, queue, third-party API) — typically via mocks | Every commit, in CI |
| **Contract (in-process)** | Development | Application's serialization / parsing of a contract | Counterparty (mock server / static contract spec) | Every commit, in CI |
| **Contract (out-of-process)** | Verification | Application calling or providing the real contract | Counterparty (real mock server process or test instance of partner) | Per iteration |
| **System-integration** | Verification | Assembled app + real internal infra (DB, queue, cache) | External third parties via real mock-server processes | Per iteration |
| **E2E** | Verification | Full operator/user journey through real interfaces (UI / API / protocol — type is independent of level) | Production-like environment; external third parties may be real or mock-server stubbed | Per iteration |

**In-process test infrastructure rules:**

- **Unit tests** — no external infrastructure; use in-process fakes, stubs, or test doubles. Never spin up a container for a unit test.
- **Component tests** — run inside the same process as the application code (e.g. Spring's `@SpringBootTest`, FastAPI `TestClient`, ASP.NET `WebApplicationFactory`, Rails request specs). External dependencies are mocked at the dependency boundary.
- **Contract tests (in-process form)** — verify serialization/parsing against a contract spec or in-memory mock server. The application's wire boundary is *not* exercised for real here — that happens in Verification.

**Build and config parity rules — critical:**

These rules exist because in-process tests that pass against a simplified configuration do not validate the real application. The configuration the in-process tests run under must be as close to production as practical.

- Component tests must use the same middleware chain, routing, authentication setup, and database schema as the real running application — not a simplified test profile that bypasses real setup.
- The composition root (the wiring of dependencies) must be the same one the real application uses; do not build an alternate "test wiring" that diverges.
- In-process tests are *not* a substitute for out-of-process Verification — they are the cheap, fast layer of the pyramid. Anything observable at the application's real interface must also be covered by Verification.

**Regression policy:**

- Full in-process suite (Unit + Component) runs on every push — this is the cheap regression gate
- Out-of-process suite (System-integration + E2E + out-of-process Contract) is owned by Verification and runs at least once per iteration
- No fix merged without a regression test at the appropriate level

---

## Cross-cutting tasks

Apply these alongside DEV work when the epic calls for them. They were defined in Decomposition; this phase is where they're implemented.

### Infrastructure & Deployment (DEVOPS) — if applicable

- Update CI/CD pipeline for new functionality
- Containerization or packaging changes
- Environment variable and secret management
- Deployment scripts or manifests updated

### Observability (SRE) — if applicable

- Add structured logging for new code paths
- Add or update metrics and dashboards
- Define or update alerts for new failure modes
- Update runbooks if operational behaviour changed

### Security (SECURITY) — always

- Scan dependencies for new vulnerabilities introduced in this epic
- Verify no secrets are committed (run secret scanner)
- Review new input validation and output encoding
- Verify all credentials and config values come from environment variables, not source code
- For significant new features: update threat model

---

## Development output

Produce a Development summary at the end of the phase covering:
- Files changed (added / modified / removed)
- In-process tests written (count by level — Unit / Component / Contract-in-process — with the AC each covers)
- Key implementation decisions made (and why)
- External interfaces wired up and ready for Verification (HTTP routes, message handlers, CLI commands)
- Any deviations from the spec or task list (with reason)
- Self-review checklist result

The orchestrator persists this summary as `i4-dev.md` for the iteration record. The next phase, Verification, will use it as input.

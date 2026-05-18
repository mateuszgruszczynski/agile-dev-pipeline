# Development Phase

**Purpose:** Implement the epic — code + in-process tests (Unit, Component, in-process Contract). Code Review is a self-applied checklist; no separate Review checkpoint. Out-of-process tests (System-integration, E2E, out-of-process Contract) belong to [Verification](verification.md).

TDD at in-process levels: tests written before or alongside code, never after.

- Failing in-process tests first (Unit, then Component as needed)
- Implement to pass
- Refactor under green
- Follow the agreed stack / architecture — no unilateral tech changes
- Commit small and often. Each commit passes all in-process tests. Do not bundle the iteration into one commit.
- No commented-out code, no untracked TODOs

*Existing codebases:* run the existing in-process suite first to establish a green baseline. Pre-existing failures become FIX epics, not silent inheritance. Match existing style unless the epic calls for a change.

**Subagents** for independent parallel implementation work (different modules, no shared state). Apply the self-review checklist to subagent output the same as your own.

**Security rules — from the first commit:**
- No hardcoded credentials, API keys, DB passwords, tokens
- Environment-specific config (URLs, connection strings, feature flags) externalised via env vars or untracked config file
- `.env.example` with placeholders committed; real `.env` in `.gitignore`
- Verify no secrets committed before every push (pre-commit hook or scanner)

---

## Self-review checklist

Apply before declaring Development complete. Self-applied gate — no separate Review.

- [ ] Matches ACs from Refinement and in-process scenarios from the Test Plan
- [ ] Edge cases handled in code (separate from out-of-process coverage)
- [ ] No hardcoded secrets / credentials
- [ ] Error handling is appropriate
- [ ] All in-process scenarios implemented (Unit / Component / Contract-in-process)
- [ ] New dependencies are justified
- [ ] Follows agreed architecture — no unilateral structural changes
- [ ] New public interfaces documented (API, CLI flags, config)
- [ ] External interfaces (HTTP routes, message handlers, CLI commands) wired up so Verification can drive them out-of-process

**AI-generated code — extra attention to:**
- Hallucinated or subtly wrong library usage — verify against actual docs
- Logic that looks plausible but fails at edge cases
- License compatibility of suggested dependencies
- Over-engineering that doesn't fit the project's simplicity level

Any item fails → fix before producing the summary.

---

## Test policies — in-process only

| Level | Owned by | Real | Faked | When |
|---|---|---|---|---|
| Unit | Development | Single function/class | All collaborators | Every commit, CI |
| Component | Development | Multiple internal classes in-process (e.g. service + repo) | External deps (DB / queue / 3rd-party API) via mocks | Every commit, CI |
| Contract (in-process) | Development | App's serialization / parsing | Counterparty (mock server / static spec) | Every commit, CI |
| Contract (out-of-process) | Verification | App calling/providing the real contract | Counterparty (real mock-server process) | Per iteration |
| System-integration | Verification | Assembled app + real internal infra | External 3rd parties via mock-server processes | Per iteration |
| E2E | Verification | Full operator/user journey through real interfaces | Production-like env; 3rd parties real or mock-stubbed | Per iteration |

**In-process rules:**
- Unit: no external infra. In-process fakes / stubs / test doubles. Never spin a container.
- Component: same process as application code (`@SpringBootTest`, FastAPI `TestClient`, ASP.NET `WebApplicationFactory`, Rails request specs). Mock at the dependency boundary.
- Contract (in-process): verify serialization/parsing against contract spec or in-memory mock server. The wire boundary is exercised in Verification, not here.

**Build / config parity:** Component tests must use the same middleware chain, routing, auth setup, and DB schema as the running application. Same composition root, no alternate "test wiring". In-process tests are the cheap fast layer, not a substitute for Verification.

**Regression:** full in-process suite (Unit + Component) on every push. No fix merged without a regression test at the right level. Out-of-process suite owned by Verification, runs per iteration.

---

## Cross-cutting tasks

Apply alongside DEV work when Decomposition assigned them.

**Infrastructure & Deployment (DEVOPS):** CI/CD updates; containerization/packaging; env var and secret management; deployment scripts/manifests.

**Observability (SRE):** structured logging on new paths; metrics + dashboards; alerts on new failure modes; runbook updates.

**Security (SECURITY) — always:** dependency vuln scan; secret-scanner pass before push; input validation / output encoding review; verify env-var usage; threat-model update for significant new features.

---

## Output

Write the **Development** section of `i3-outcome.md` (create the file with a `# Iteration NNN Outcome` heading):

```markdown
# Iteration NNN Outcome

## Development

- Files changed (added / modified / removed)
- In-process tests written, by level (Unit / Component / Contract-in-process), with the AC each covers
- External interfaces wired up and ready for Verification (HTTP routes, message handlers, CLI commands)
- Key implementation decisions (and why)
- Deviations from spec / task list (with reason)
- Self-review checklist result
```

Persisted in `i3-outcome.md` for Verification to append to.

## Bundle handling

When the iteration has multiple epics, the Development section of `i3-outcome.md` groups Files-changed, In-process tests, and Key decisions per epic (with `EP-x` headings). Commit messages reference the epic with a conventional-commit footer or prefix: `feat(EP-3): add search index schema`. This keeps history navigable per epic even when many were implemented in one iteration.

No per-epic checkpoint within Development — the bundle flows as one continuous implementation pass. The whole iteration's worth of in-process tests must be green before the phase completes.

## Policy effects

`test_coverage` axis:
- `thorough` (default) — write in-process tests for every Test Plan scenario tagged Unit / Component / in-process Contract. Aim for the standard test pyramid.
- `minimal` — write in-process tests only for the happy-path Test Plan scenarios. Skip edge / failure / regression unless the AC explicitly names one.
- `none` — write **no in-process tests**. Implementation only. The self-review checklist's "tests cover ACs" item becomes "self-review confirms behaviour matches ACs (no tests, per policy)". Skip the TDD red-green-refactor loop.

`detail` axis (applies to `i4-dev.md` summary):
- `full` — every section from Output above with rationale per decision and full deviation explanations.
- `sparse` — files-changed list, tests-by-level totals (not per-AC), decisions as one-liners, deviations as one-liners.
- `minimal` — files-changed list and tests-by-level totals only. No decisions section, no deviations section.

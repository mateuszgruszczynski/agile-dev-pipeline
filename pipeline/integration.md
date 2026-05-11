# Integration & Demo Phase

**Purpose:** Prove the verified code builds, starts, and behaves like a real application end-to-end. Tests are already written and run (in-process in [Development](development.md), out-of-process in [Verification](verification.md)). Integration does not re-run the suite — `i5-verify.md` is the test-outcome source of truth. This phase handles production-style build, env wiring, manual smoke, and demo readiness.

---

## Inputs

- `i1-spec.md` — ACs to walk
- `i4-dev.md` — Development summary
- `i5-verify.md` — Verification summary. Any failure or quarantine here must be resolved or explicitly accepted before this phase completes.
- `f1-vision.md` — **Key user journeys** section only

---

## Steps

1. **Merge all iteration tasks; resolve conflicts.**

2. **Build the application.** Production build command (`npm run build`, `mvn package`, `go build`, `docker compose build`). Build must succeed before continuing.

3. **Prepare `.env`** before starting the app:
   - Exists: verify it covers all variables in `.env.example`. Add missing.
   - Does not exist: read `.env.example` and classify each variable:
     - *Safe test defaults* — ports, log levels, `NODE_ENV=development`, local service URLs (`DATABASE_URL=postgresql://localhost:5432/appdb_dev`, `REDIS_URL=redis://localhost:6379`), feature flags. Pre-fill.
     - *Requires real value* — external API keys, OAuth secrets, payment tokens, third-party creds. Cannot be guessed.
   - Generate `.env` with safe defaults. List variables needing real values; ask user. Do not start the app until every required var has a value.
   - Remind the user: local-testing only, never commit.

4. **Start the application; verify service connections.**
   - Web / backend / CLI / containerised: start inside the container as normal.
   - **Native GUI (hybrid mode):** binary built in container, runs on host. Execute the compiled binary on the host (`cargo run --release` or the built artifact directly). Do not open a GUI window inside the container.

5. **Manual smoke test** — walk the core user journey from Vision. Catches what automated tests don't: visual breakage, broken navigation, layout regressions, console noise.
   - Key screens and navigation work (no broken links, 404s, routing errors)
   - Core UI interactions present and functional (buttons / forms / inputs respond)
   - No missing UI elements or unstyled layouts
   - Happy path behaves per spec
   - No console errors or crashes

   *Non-UI apps:* invoke the primary interface (HTTP endpoint, CLI command, message publish) end-to-end and observe output as an operator.

   **Keep the smoke brief.** Verification already proved the scenarios. One or two touchpoints to confirm "assembled app runs, front door works". Long `curl` / click-through sequences here usually mean Verification missed a scenario — record it in the Test Plan for next iteration; do not silently retest in chat.

6. **Confirm Verification results** from `i5-verify.md`:
   - All System-integration and E2E scenarios passed (or quarantined with reason + follow-up task).
   - Each AC covered by a Verification scenario, or by in-process tests in `i4-dev.md` when there's no out-of-process observable.
   - Unresolved failure → do not proceed. Loop back per *Mid-iteration recovery* in [iterate.md](../commands/iterate.md).

7. **Demo preparation.** If the epic produces a demonstrable user-visible state, prepare a short script covering the happy path. Early epics (project setup, CI, base schema) may not — note explicitly and confirm build/start still works.

---

## Demo readiness checklist

- [ ] Production build green
- [ ] `.env` complete
- [ ] App starts; required services connect
- [ ] Manual smoke passes
- [ ] All non-quarantined Verification scenarios in `i5-verify.md` pass
- [ ] Each AC traces to a passing scenario (Verification when out-of-process observable; in-process otherwise)
- [ ] No known blocking bugs
- [ ] Core user flow demonstrable without errors

DoD: Integration cannot be APPROVED until every condition in [definitions.md](definitions.md) DoD holds. The list above is the operational view — keep in sync.

---

## Output

`i6-int.md`:
- **Build status** — command, success/failure, warnings
- **Environment preparation** — variables classified, real credentials required
- **Application start** — health check, services connected
- **Manual smoke** — what was walked, what passed, observations
- **Verification roll-up** — pointer to `i5-verify.md` + one-line confirmation
- **AC pass/fail table** — one row per AC, citing the scenario(s) that prove it
- **Integration-phase issues** — defects from earlier phases should already be closed
- **Demo outcome** — or "no demo applicable"

---

**⛳ CHECKPOINT Integration:** user reviews `i6-int.md` + `i5-verify.md`, watches the demo or signs off the checklist. Epic accepted or returned with specific feedback. (Conditional auto-continue rules live in [iterate.md](../commands/iterate.md).)

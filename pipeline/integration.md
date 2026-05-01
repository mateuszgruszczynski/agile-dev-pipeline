# Integration & Demo Phase

**Purpose:** Take the now-verified code and prove it builds, starts, and behaves like a real application end-to-end. Tests have already been written and run — in-process tests in [Development](development.md), out-of-process tests in [Verification](verification.md). Integration is where the human-shaped checks happen: production-style build, environment wiring, manual smoke, and demo readiness.

This phase does **not** re-run the test pyramid as its job. The Verification artifact (`i5-verify.md`) is the source of truth for test outcomes. Integration confirms the assembled application works in the way a user or operator would experience it, fills in `.env` for a real run, and produces the demo/checkpoint state that the user reviews.

---

## Inputs

- `i1-spec.md` — ACs to walk through during the smoke test.
- `i4-dev.md` — Development summary (in-process test results, files changed).
- `i5-verify.md` — Verification summary (out-of-process tests, AC coverage table). If any Verification scenario failed or was quarantined, that must be resolved or explicitly accepted before this phase can complete.
- `f1-vision.md` — for the core user journey to walk through.

---

## Steps

1. **Merge all tasks** from this iteration; resolve conflicts.

2. **Build the application:** run the production build command (e.g. `npm run build`, `mvn package`, `go build`, `docker compose build`). The build must succeed with no errors before proceeding.

3. **Prepare the local environment file** before starting the application — ensure a `.env` (or equivalent config file) is present with all required variables set.
   - If a `.env` already exists: verify it covers all variables listed in `.env.example`. If any are missing, add them now.
   - If no `.env` exists: read `.env.example` and classify each variable into two groups:
     - *Safe test defaults* — variables that can take standard local values without real credentials: ports, log levels, `NODE_ENV=development`, local service URLs (e.g. `DATABASE_URL=postgresql://localhost:5432/appdb_dev`, `REDIS_URL=redis://localhost:6379`), feature flags. Pre-fill these with sensible defaults automatically.
     - *Requires real value* — external API keys, OAuth client secrets, payment provider tokens, third-party service credentials. These cannot be guessed or faked for a local run.
   - Generate a `.env` file with all safe defaults pre-filled.
   - For any variable that requires a real value: list them explicitly and ask the user to provide them before continuing. Do not start the application until every required variable has a value.
   - Remind the user: this `.env` is for local testing only and must not be committed to version control.

4. **Start the application:** run the built application and verify it starts without errors and connects to its required services.
   - *Web / backend / CLI / containerised apps:* start inside the container as normal.
   - *Native GUI apps (hybrid mode):* the binary was built inside the container but the window system is on the host. Run the compiled binary on the host machine (e.g. `cargo run --release` or execute the built artifact directly). Do not attempt to open a GUI window inside the container.

5. **Manual smoke test** — walk through the core user journey defined in Vision as a real user would. The job here is to catch the things automated tests don't: visual breakage, broken navigation, layout regressions, console noise.
   - All key screens and navigation paths work (no broken links, 404s, or routing errors)
   - Core UI interactions are present and functional (buttons, forms, links, inputs respond correctly)
   - No missing UI elements, unstyled layouts, or broken visual structure
   - The application behaves as specified for the happy path
   - No console errors or application crashes during normal use

   *For non-UI applications:* the smoke equivalent is invoking the primary interface (HTTP endpoint, CLI command, message publish) end-to-end and observing the output as an operator would. The point is the same: confirm the assembled artifact works the way a human would use it.

6. **Confirm Verification results.** Read `i5-verify.md`:
   - All System-integration and E2E scenarios passed (or are quarantined with a written reason and follow-up task).
   - Each AC is covered either by a Verification scenario or — for ACs with no out-of-process observable — by in-process tests recorded in `i4-dev.md`.
   - If anything failed and was not resolved in Verification, do not proceed; loop back per *Mid-iteration recovery* in [iterate.md](../commands/iterate.md).

7. **Demo preparation** — if the project is at a stage where a working demo is meaningful, prepare a short demo script covering the happy path and verify it runs cleanly. Very early epics (initial project setup, CI pipeline, base data model) may not produce a user-visible demo; note that explicitly and confirm the build/start steps still work.

---

## Demo readiness checklist

- [ ] Production build succeeds without errors
- [ ] `.env` (or equivalent) is present with all required variables set
- [ ] Application starts and all required services connect
- [ ] Manual smoke test passes: core user journey works, no broken UI, no crashes
- [ ] All Verification scenarios from `i5-verify.md` pass (or are quarantined with reason + follow-up)
- [ ] Each AC traces to a passing scenario (Verification level when out-of-process observable; in-process otherwise)
- [ ] No known blocking bugs
- [ ] Core user flow can be demonstrated without errors

**Definition of Done:** Integration cannot be APPROVED until every condition in the DoD in [definitions.md](definitions.md) holds. The checklist above is the operational view of DoD for this phase — keep both lists in sync.

---

## Output

Write `i6-int.md` to the iteration directory containing:

- **Build status** — command run, success/failure, any warnings worth surfacing
- **Environment preparation** — variables classified, real credentials required
- **Application start result** — health check, services connected
- **Manual smoke test outcome** — what was walked through, what passed, anything observed
- **Verification roll-up** — pointer to `i5-verify.md` plus a one-line confirmation that all non-quarantined scenarios pass
- **AC pass/fail table** — one row per AC, citing the scenario(s) (Verification or in-process) that prove it
- **Issues found at this phase and how they were resolved** (Integration-only — defects from earlier phases should already be closed)
- **Demo script outcome** (or note that no demo was applicable for this epic)

---

**⛳ CHECKPOINT Integration:** User reviews `i6-int.md` together with `i5-verify.md` and either watches the demo or signs off the checklist. Epic is accepted or returned with specific feedback.

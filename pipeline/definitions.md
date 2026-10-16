# Definitions: Ready / Testability / Done / Scope Fidelity

Single source of truth for the four gates the pipeline applies. Each definition lists conditions that must hold before a phase can advance. Update the conditions here, not in the phases that reference them.

These are quality gates, not phases. They are checked from inside the phases listed under "Where this is enforced".

---

## Definition of Ready (DoR)

**Purpose:** Gate before an epic enters Refinement. Confirms the backlog detail block is complete enough to start spec work.

**Conditions:**
- Epic has a name, type (FEATURE / INFRA / FIX / etc.), priority, and rough size
- Description states what the epic delivers and why it matters
- 2–3 key scenarios are written (`As a [user], I can [action]`)
- 3–5 high-level acceptance criteria are listed
- Out-of-scope statement is present (1–2 sentences)
- Risks and unknowns are listed, or explicitly noted as none
- Dependencies on other epics are identified, and any blocking ones are resolved or scheduled
- The HLACs look testable in principle — a tester reading them can imagine writing scenarios for each

**Where this is enforced:**
- [backlog.md](backlog.md) — when producing the epic detail block
- [iterate.md](../commands/iterate.md), Refinement phase — refuse to start Refinement if the picked epic fails DoR; either fix the backlog block first, or pick a different epic

If DoR fails, fix the backlog block before continuing — do not paper over it inside Refinement.

---

## Definition of Testability (DoT)

**Purpose:** Gate inside Refinement and Test Plan. Each AC must be observable and verifiable in plain language; if it isn't, the AC is too implementation-specific or too vague.

**Conditions per AC:**
- Stated as an observable outcome — what the user sees or what the system makes available, not what function ran or what record was inserted
- Specific and unambiguous — two readers would agree whether it passed or failed on a given run
- Written in domain language — no class names, HTTP status codes, SQL, or table names
- Has at least one BDD scenario that can be written for it without technical jargon
- Edge cases and failure modes for the AC are either covered by additional scenarios or explicitly listed as out of scope

**Where this is enforced:**
- [refinement.md](refinement.md) — when finalising the AC list. Each AC is checked against the DoT before the spec checkpoint.
- [test-plan.md](test-plan.md) — when writing scenarios. If a scenario cannot be written for an AC without technical jargon, the AC fails DoT — return to Refinement and rewrite it.

If DoT fails, the cheapest fix is almost always rewriting the AC, not adding more test scaffolding.

---

## Definition of Done (DoD)

**Purpose:** Gate at Integration close. The epic is not done until every condition holds.

**Conditions:**
- Production build succeeds with no errors
- Application starts and connects to all required services
- Manual smoke test of the core user journey passes
- Full **in-process** test suite passes (Unit + Component + in-process Contract) — no regressions
- Full **out-of-process** test suite passes (System-integration + E2E + out-of-process Contract) — no regressions; any quarantined test has a written reason and a follow-up FIX task
- Every AC traces to at least one passing scenario: a Verification-level scenario when the AC has any out-of-process observable, in-process otherwise (explicitly noted)
- Self-review checklist from [development.md](development.md) is satisfied
- No hardcoded credentials anywhere; `.env.example` and `.gitignore` are up to date
- Regression coverage exists for behaviour this epic touched (within the epic's scope)
- Documentation tasks listed in Decomposition are complete (README, API docs, runbook, ADRs as applicable)
- CHANGELOG.md has an entry for this iteration
- `i2-plan.md` and `i3-outcome.md` are written and accurate

**Where this is enforced:**
- [verification.md](verification.md) — Verification cannot complete until every non-quarantined out-of-process scenario passes and AC coverage is confirmed.
- [integration.md](integration.md) — Integration cannot be APPROVED until every DoD condition holds.
- [iterate.md](../commands/iterate.md), iteration close — closing the iteration is gated on a passing Integration checkpoint, which is gated on DoD.

**Policy effects on DoD** (driven by `.project-artifacts/policy.md`):

| Policy | DoD adaptation |
|---|---|
| `test_coverage = thorough` (default) | All conditions above apply unchanged. |
| `test_coverage = minimal` | Out-of-process scenarios are limited to happy paths; "no regressions" still applies but is measured against the reduced scenario set. AC trace still required (one happy-path scenario per AC is enough). |
| `test_coverage = none` | Drop "Full in-process suite passes", "Full out-of-process suite passes", and "Every AC traces to ≥1 passing scenario" from the DoD. Replace with: "Production build succeeds. Application starts and connects. Manual smoke test passes. Each AC marked pass/fail in the manual-smoke walkthrough with a one-line note in the Integration section of `i3-outcome.md`." The Verification section of `i3-outcome.md` is not produced and is not part of DoD. |
| `detail` and `autonomy` axes | Do not change DoD conditions; they only change verbosity / approval behaviour, not what counts as "done". |
| `packaging = each` | Adds to DoD: **a runnable deliverable artifact exists in `dist/<NNN>-<slug>/`** matching the type declared in `f2-architecture.md`, smoke-tested per `test_coverage`. Run instructions and external runtime requirements are recorded in `i3-outcome.md`. |
| `packaging = milestone` or `final` | DoD unchanged at iteration close (no `dist/` produced). At `/agile-dev:release` boundary, the release-time DoD adds: `releases/v<version>/` contains the deliverable artifact, `RUN.md`, runtime requirements, and `MANIFEST.txt` with sha256 hashes. |
| `iteration_size` (any value) | DoD conditions apply to **every epic in the bundle** when the iteration covers multiple. Every bundled epic's ACs must trace to passing scenarios (or in-process coverage with note, or manual smoke when `test_coverage = none`); `i3-outcome.md` covers every bundled epic; CHANGELOG entry lists every bundled epic. |

If DoD fails, fix it before approving Integration. Do not defer DoD failures to the next iteration without an explicit decision at the Integration checkpoint and a follow-up FIX epic in the backlog.

---

## Definition of Scope Fidelity (DoSF)

**Purpose:** Gate on any subagent-drafted content (Vision, Architecture, Backlog, Refinement). DoR and DoT catch a requirement that's *incomplete or ambiguous relative to what the user asked for*. Neither one catches a requirement that's complete, unambiguous, and correctly implemented — but that nobody asked for in the first place. A draft can pass DoR and DoT perfectly while still containing fabricated scope (e.g. a stated requirement for "a selector" silently expanded into "automatic detection logic," or example documents shown for context turned into a requirement to migrate them). This is a different failure mode and needs its own gate.

**Conditions:**
- Every subagent drafting Vision/Architecture/Backlog/Refinement content also produces an explicit **"Added beyond what was stated"** list: every capability, feature, or behaviour in the draft that the user did not explicitly request, named individually, with a one-line reason it seemed reasonable to add. If the subagent added nothing, the list says so explicitly ("None — every item traces to something the user said") — it is never just omitted.
- The orchestrator reviews this list against the actual conversation before presenting anything — don't trust the subagent's self-report blindly; this is exactly the kind of check a subagent can under-report on its own work.
- At the checkpoint, the list is presented **separately and first**, before the main artifact — short, bolded, one line per item. It is never folded into the body of the spec/vision/architecture doc, where it's easy to miss in a long document.
- Each item needs an explicit confirm or strike from the user — not a blanket APPROVE of the whole checkpoint. An item the user strikes is removed from the artifact before it's saved. An item they confirm becomes a stated requirement going forward; it does not need to be re-flagged on a later pass.

**Where this is enforced:**
- [vision.md](vision.md) — Vision Statement, MVP definition, user journeys
- [architecture.md](architecture.md) — architecture decisions
- [backlog.md](backlog.md) — epic generation
- [refinement.md](refinement.md) — spec and AC drafting

If DoSF surfaces an added item the user wants to keep, that's a legitimate requirement now — update the artifact and move on. The gate exists to make that an explicit decision, not a silent one.

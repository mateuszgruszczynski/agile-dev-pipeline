# Epic Backlog Phase  [INTERACTIVE]

**Purpose:** Decompose the product vision into a prioritized list of epics. Each epic is a meaningful chunk of user-facing or system-level value. This is the master backlog — it will evolve across iterations.

*When entering from Analysis (existing codebase): seed the backlog from the gap between Analysis (current state) and Vision (desired state). Epic types expand to include REFACTOR, FIX, and MIGRATION alongside FEATURE. Tech debt identified in Analysis should appear as explicit epics with a priority, not as hidden work inside feature epics.*

**If Vision built an Impact Map** (Goal → Actors → Impacts → Deliverables — see [vision.md](vision.md)): start epic generation from its Deliverables layer rather than re-deriving the epic list from the Vision Statement alone, and make sure every epic traces back to at least one Impact. An epic that doesn't trace to any Impact is either missing from the map (go add it) or isn't actually serving the stated goal (question whether it belongs in this backlog at all).

**What to define per epic:**
- **Epic ID:** `EP-<n>`, assigned sequentially, stable for the life of the backlog. Every reference to this epic elsewhere (dependencies, iteration bundles, `state.md`) uses this ID, not the name — the bundler script matches on it exactly.
- Short name (e.g. "User Authentication", "CSV Import", "CLI Subcommand: report")
- One-paragraph description — what it delivers and why it matters
- Type: FEATURE / INFRA / QA / SECURITY / DESIGN / DATA / TECH_DEBT / REFACTOR / FIX / MIGRATION / SPIKE
- Priority: P1 (must have for MVP) / P2 (important) / P3 (nice to have)
- **Journey step:** which step of Vision's key user journey this epic serves (or "cross-cutting" for infra/security epics that don't map to one step)
- **Slice:** `MVP` (part of the thinnest walking skeleton across the whole journey) or `Deferred` (depth added after the MVP release) — see Story Map below
- Rough size: XS / S / M / L / XL / XXL — t-shirt sizing with point values used by the iteration bundler (see table below). Required, not optional.
- **Depends on:** other epics' IDs this one needs `DONE` first, comma-separated; `—` if none. A dependency that blocks *design* (not just execution) — see SPIKE epics below — is written `needs-findings-from:<id>` instead of a plain ID. This is both a detail-block field and a `state.md` table column (see [iterate.md](../commands/iterate.md) Step 2) — the iteration bundler script reads the column, not the prose.
- Applicable roles (which disciplines this epic touches)
- **Key scenarios (2–3):** brief "As a [user], I can [action]" statements that make the epic concrete.
- **High-level acceptance criteria (3–5 items):** what must be true for this epic to be considered complete.
- **Out of scope:** 1–2 sentences on what this epic deliberately does NOT include.
- **Key risks or unknowns:** anything that could make this epic harder or require a decision before starting.

**T-shirt sizes and point values** (used by the iteration bundler):

| Size | Points | Rough effort |
|---|---|---|
| XS | 1.0 | Quick fix / one-file tweak |
| S | 1.7 | Small focused change |
| M | 3.0 | Standard feature / refactor |
| L | 5.2 | Substantial work, multiple files |
| XL | 9.0 | Large feature, default iteration target |
| XXL | 15.6 | Should usually be split before scheduling |

Points scale as `sqrt(3)^n` so each step is ~1.73× the previous — closer than doubling, allowing finer iteration packing. The iteration bundler ([iterate.md](../commands/iterate.md) Step 2) sums epic points and picks a combination as close as possible to the iteration budget (default = XL = 9 points), respecting priority order and dependencies.

**SPIKE epics — a time-boxed investigation, not working code.** Use type `SPIKE` for an epic whose product is evidence and a decision, not a shippable feature: an unknown external system, an unclear data format, a feasibility question `/agile-dev:research` didn't cover upfront. A SPIKE epic differs from the others in several ways, carried through the rest of the pipeline:
- **Time-boxed scope** — state the box explicitly in the description (e.g. "half a day"), not just a size estimate.
- **ACs phrased as questions answered with evidence**, not behaviour: "Does the API expose historical data, and under what tier?" rather than "the API returns historical data."
- **Result vocabulary beyond pass/fail**: `works`, `works with limits`, `does not work`, `unverified`, `unresolved` are all legitimate outcomes — see the Definition of Done adaptation in [definitions.md](definitions.md).
- **Deliverable is a findings document**, not code, with a mandatory **foundation impact** section: does this spike's result require revising Vision, Architecture, or the Backlog itself? State explicitly, even if the answer is "no impact." Integration surfaces this section automatically — see [integration.md](integration.md).
- If another epic's own design depends on what a SPIKE will find, declare that explicitly with **`needs-findings-from: <spike-epic>`** in the dependent epic's dependency list — stronger than an ordinary dependency, because it means the dependent epic cannot even be *designed* yet, not just that it must wait to start. The iteration bundler ([iterate.md](../commands/iterate.md) Step 2) treats this as a hard barrier regardless of point budget: never bundle a `needs-findings-from` epic into the same iteration as the spike it depends on, even if there's room.

**Arrange epics as a Story Map, not just a flat list.** Lay the backlog along Vision's key user journey (the steps, in order) as a horizontal backbone — most epics map to one journey step; cross-cutting ones (infra, security) sit alongside the step(s) they support. Then slice horizontally into two rows: **MVP** — the thinnest walking skeleton that touches every step of the journey, even shallowly — and **Deferred** — depth added after the MVP release. An epic's slice is its MVP-vs-deferred status, visible at a glance in the backlog table, not something to infer from a priority letter. Priority (P1/P2/P3) still governs fine-grained ordering *within* a slice; the slice itself is the structural MVP boundary. This uses the epics the pipeline already produces as the map's units — not generic "As a user, I want" cards. The existing Key scenarios field above is a separate, smaller thing, untouched by this.

**Guidelines:**
- Aim for 5–15 epics initially; more will be added in retrospectives
- P1 epics should be the minimum to have a working, demonstrable product
- Infrastructure and security epics belong in the backlog alongside features
- If the Architecture phase decided a UI design level of "clean" or "polished", include a DESIGN epic
- Avoid mixing unrelated concerns in one epic
- Each epic detail block must satisfy the **Definition of Ready** in [definitions.md](definitions.md) before it can enter Refinement

**Risk-first sequencing.** Check whether this project ran in deep-requirements mode: `f1-vision.md` has a "Concrete interpretation" / "Confirmed assumptions" section, or `.project-artifacts/research/findings.md` exists with an `[assumption]`/`[claimed]` item accepted as an open risk rather than fully resolved. If so, check whether any backlog epic's job is specifically to prove or disprove that risk — often a small epic such as "confirm candidate data source has the required fields" or "prototype the riskiest integration." If such an epic exists, assign it **P1** regardless of its stand-alone user-facing value, and say why in its description (e.g. "P1 — the rest of the backlog assumes this works; proving it in iteration 1 is cheaper than discovering it's wrong after several iterations of investment"). This is not a special case of P1 — an unresolved foundational risk is itself an MVP blocker, even before it has any user-facing value of its own. The iteration bundler ([iterate.md](../commands/iterate.md) Step 2) already sorts P1 first, so no change is needed there — this only changes which epic earns the P1. Skip this entirely when deep-requirements mode never triggered for this project; ordinary value-based priority is already risk-appropriate there.

**Use subagents:** for long backlogs (10+ epics), delegate per-epic detail-block generation to a subagent and review the set yourself before presenting. Keep the priority/sizing decisions with you — those need user judgment.

**Definition of Scope Fidelity (see [definitions.md](definitions.md)):** after the drafting subagent(s) return their epic detail blocks, delegate to a **second, independent subagent** — the spec critic — with the drafts plus Vision/Architecture and the user's answers (not the drafters' own opinion of their work). Its only job: find gaps, ambiguity, inconsistency, and interpretation-space, and produce the "Added beyond what was stated" list itself — epics, scenarios, or ACs that go beyond what the conversation actually asked for. Present that list separately and first at the checkpoint, before the backlog table itself.

**Output:**
- Prioritized epic backlog table (id, name, type, priority, size, status, journey step, slice, depends on)
- Epic detail block for each epic: scenarios, high-level ACs, out of scope, risks

**Before the checkpoint — dependency cross-check.** Two passes, different in kind:

1. **Structural (scriptable) — run it, don't re-derive it.** `${CLAUDE_PLUGIN_ROOT}/scripts/backlog_integrity_check.py --state .project-artifacts/state.md` checks every `Depends on` / `needs-findings-from` token against the actual ID list and detects dependency cycles. It only works once `state.md`'s Backlog table exists — at this phase, run it against a scratch table built from the draft epics instead (same columns), or defer it to the first run of `/agile-dev:iterate`, which runs it automatically. This catches broken references and cycles for free; it does **not** catch the check below.
2. **Semantic (still needs a reader).** For every epic, check each of its ACs against the epic's *declared* dependencies: if an AC's observable actually needs output from another epic (e.g. "a running UI" when no UI epic is listed), that epic is an undeclared dependency — add it to the dependency list rather than letting it surface later at Refinement. This requires reading and understanding the AC text; no script does this.

**⛳ CHECKPOINT Backlog:** User reviews, reorders, adds, or removes epics. Backlog is approved before first iteration begins.

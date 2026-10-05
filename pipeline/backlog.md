# Epic Backlog Phase  [INTERACTIVE]

**Purpose:** Decompose the product vision into a prioritized list of epics. Each epic is a meaningful chunk of user-facing or system-level value. This is the master backlog — it will evolve across iterations.

*When entering from Analysis (existing codebase): seed the backlog from the gap between Analysis (current state) and Vision (desired state). Epic types expand to include REFACTOR, FIX, and MIGRATION alongside FEATURE. Tech debt identified in Analysis should appear as explicit epics with a priority, not as hidden work inside feature epics.*

**What to define per epic:**
- Short name (e.g. "User Authentication", "CSV Import", "CLI Subcommand: report")
- One-paragraph description — what it delivers and why it matters
- Type: FEATURE / INFRA / QA / SECURITY / DESIGN / DATA / TECH_DEBT / REFACTOR / FIX / MIGRATION
- Priority: P1 (must have for MVP) / P2 (important) / P3 (nice to have)
- Rough size: XS / S / M / L / XL / XXL — t-shirt sizing with point values used by the iteration bundler (see table below). Required, not optional.
- Known dependencies on other epics — list epic names or IDs; empty if none. The iteration bundler honours these: a dependent epic cannot be scheduled until its blockers are DONE.
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

**Guidelines:**
- Aim for 5–15 epics initially; more will be added in retrospectives
- P1 epics should be the minimum to have a working, demonstrable product
- Infrastructure and security epics belong in the backlog alongside features
- If the Architecture phase decided a UI design level of "clean" or "polished", include a DESIGN epic
- Avoid mixing unrelated concerns in one epic
- Each epic detail block must satisfy the **Definition of Ready** in [definitions.md](definitions.md) before it can enter Refinement

**Risk-first sequencing.** Check whether this project ran in deep-requirements mode: `f1-vision.md` has a "Concrete interpretation" / "Confirmed assumptions" section, or `.project-artifacts/research/findings.md` exists with an `[assumption]`/`[claimed]` item accepted as an open risk rather than fully resolved. If so, check whether any backlog epic's job is specifically to prove or disprove that risk — often a small epic such as "confirm candidate data source has the required fields" or "prototype the riskiest integration." If such an epic exists, assign it **P1** regardless of its stand-alone user-facing value, and say why in its description (e.g. "P1 — the rest of the backlog assumes this works; proving it in iteration 1 is cheaper than discovering it's wrong after several iterations of investment"). This is not a special case of P1 — an unresolved foundational risk is itself an MVP blocker, even before it has any user-facing value of its own. The iteration bundler ([iterate.md](../commands/iterate.md) Step 2) already sorts P1 first, so no change is needed there — this only changes which epic earns the P1. Skip this entirely when deep-requirements mode never triggered for this project; ordinary value-based priority is already risk-appropriate there.

**Use subagents:** for long backlogs (10+ epics), delegate per-epic detail-block generation to a subagent and review the set yourself before presenting. Keep the priority/sizing decisions with you — those need user judgment.

**Output:**
- Prioritized epic backlog table (name, type, priority, size, status)
- Epic detail block for each epic: scenarios, high-level ACs, out of scope, risks

**⛳ CHECKPOINT Backlog:** User reviews, reorders, adds, or removes epics. Backlog is approved before first iteration begins.

# Epic Backlog Phase  [INTERACTIVE]

**Purpose:** Decompose the product vision into a prioritized list of epics. Each epic is a meaningful chunk of user-facing or system-level value. This is the master backlog — it will evolve across iterations.

*When entering from Analysis (existing codebase): seed the backlog from the gap between Analysis (current state) and Vision (desired state). Epic types expand to include REFACTOR, FIX, and MIGRATION alongside FEATURE. Tech debt identified in Analysis should appear as explicit epics with a priority, not as hidden work inside feature epics.*

**What to define per epic:**
- Short name (e.g. "User Authentication", "CSV Import", "CLI Subcommand: report")
- One-paragraph description — what it delivers and why it matters
- Type: FEATURE / INFRA / QA / SECURITY / DESIGN / DATA / TECH_DEBT / REFACTOR / FIX / MIGRATION
- Priority: P1 (must have for MVP) / P2 (important) / P3 (nice to have)
- Rough size: S / M / L / XL (intuitive, not story points)
- Known dependencies on other epics
- Applicable roles (which disciplines this epic touches)
- **Key scenarios (2–3):** brief "As a [user], I can [action]" statements that make the epic concrete.
- **High-level acceptance criteria (3–5 items):** what must be true for this epic to be considered complete.
- **Out of scope:** 1–2 sentences on what this epic deliberately does NOT include.
- **Key risks or unknowns:** anything that could make this epic harder or require a decision before starting.

**Guidelines:**
- Aim for 5–15 epics initially; more will be added in retrospectives
- P1 epics should be the minimum to have a working, demonstrable product
- Infrastructure and security epics belong in the backlog alongside features
- If the Architecture phase decided a UI design level of "clean" or "polished", include a DESIGN epic
- Avoid mixing unrelated concerns in one epic
- Each epic detail block must satisfy the **Definition of Ready** in [definitions.md](definitions.md) before it can enter Refinement

**Use subagents:** for long backlogs (10+ epics), delegate per-epic detail-block generation to a subagent and review the set yourself before presenting. Keep the priority/sizing decisions with you — those need user judgment.

**Output:**
- Prioritized epic backlog table (name, type, priority, size, status)
- Epic detail block for each epic: scenarios, high-level ACs, out of scope, risks

**⛳ CHECKPOINT Backlog:** User reviews, reorders, adds, or removes epics. Backlog is approved before first iteration begins.

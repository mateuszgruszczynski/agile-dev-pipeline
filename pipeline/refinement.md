# Refinement Phase

**Purpose:** Elaborate the backlog detail block (description, key scenarios, HLACs, out-of-scope, risks) into a full implementable spec with detailed Acceptance Criteria. Output: `i1-spec.md` — the source of truth for this iteration; replaces the backlog block.

**What to produce:**
- Detailed description of the epic's scope
- User stories or scenarios (format: "Given / When / Then" or "As a [user], I want [action] so that [outcome]")
- Acceptance Criteria (ACs) — specific, testable, unambiguous conditions for done
- What is explicitly out of scope for this epic
- Edge cases and failure modes to handle
- UI/UX notes if applicable (rough wireframes, flow descriptions, behavior on error states, design level requirement from Architecture)
- Performance or reliability requirements specific to this epic
- Security considerations specific to this epic

**Example questions to draw from — adapt to the conversation, do not run as a script:**

The list below is a non-exhaustive starter set. Pick the ones that close real gaps for *this* epic, ask follow-ups based on the answers, and skip any that the backlog detail block or earlier answers have already covered. **Stop asking when you have enough information to produce every item in the Output section below and every AC satisfies the Definition of Testability** — running through every example question is not the goal; getting to a confident, testable spec is.

- "What should happen if [edge case]?"
- "Is there a specific UI pattern you have in mind?"
- "Should this be backwards compatible with anything?"
- "What's the acceptable failure behavior?"

**Gates:**
- Before starting Refinement, confirm the picked epic satisfies the **Definition of Ready** in [definitions.md](definitions.md). If it doesn't, fix the backlog block first.
- Before the Refinement checkpoint, confirm every AC satisfies the **Definition of Testability** in [definitions.md](definitions.md). If any AC fails DoT, rewrite it.

**Subagent — default for spec drafting.** Q&A stays with the orchestrator (interactive). After Q&A, delegate drafting to a subagent.

- **Pass:** backlog detail block, user's answers, the Output requirements below. Tell it to apply DoT to every AC.
- **Expect:** full spec content as a single result. Orchestrator reviews, fixes, writes `i1-spec.md`.

Skip only for trivial-scope epics (one-line FIX, single-AC tweak).

**Output:**
- Epic Spec document with ACs
- Mermaid sequence or flow diagram for any non-trivial multi-step interaction (optional but recommended when the flow is hard to describe in prose)

**Policy effects** (`detail` axis only — autonomy is handled in iterate.md / change.md):
- `full` — full output above with rationale for each AC, out-of-scope section, edge cases narrative, optional Mermaid.
- `sparse` — drop the per-AC rationale and the edge-case narrative. Keep ACs, out-of-scope, security/perf bullets, optional Mermaid.
- `minimal` — ACs only (numbered list), one-line per AC. Out-of-scope as a single line if it's non-empty. No diagrams, no narrative.

**Bundle handling** (when the iteration has more than one epic): produce a single `i1-spec.md` with one section per bundled epic. Each section has the same internal structure (description, scenarios, ACs, out-of-scope, edge cases, etc.). ACs are numbered with the parent epic ID for traceability — e.g. `EP-3.AC-1`, `EP-3.AC-2`, `EP-7.AC-1`. Delegate per-epic section drafting to subagents in parallel; the orchestrator assembles. For a single-epic iteration the spec is one flat document with no section headers (same as before).

**⛳ CHECKPOINT Refinement:** User reviews and approves the spec and ACs. No implementation begins until approved.

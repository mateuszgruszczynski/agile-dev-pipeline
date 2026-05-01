# Refinement Phase

**Purpose:** Elaborate the **backlog detail block** for this epic — the description, key scenarios, HLACs, out-of-scope, and risks captured during the Backlog phase — into a full, implementable spec with detailed Acceptance Criteria. The output is `i1-spec.md`. This is the most important phase — unclear specs cause rework.

The backlog block is the seed; the spec is its full elaboration. Refer back to it but do not duplicate it — the spec replaces it as the source of truth for this iteration.

**What to produce:**
- Detailed description of the epic's scope
- User stories or scenarios (format: "Given / When / Then" or "As a [user], I want [action] so that [outcome]")
- Acceptance Criteria (ACs) — specific, testable, unambiguous conditions for done
- What is explicitly out of scope for this epic
- Edge cases and failure modes to handle
- UI/UX notes if applicable (rough wireframes, flow descriptions, behavior on error states, design level requirement from Architecture)
- Performance or reliability requirements specific to this epic
- Security considerations specific to this epic

**Questions to ask the user if unclear:**
- "What should happen if [edge case]?"
- "Is there a specific UI pattern you have in mind?"
- "Should this be backwards compatible with anything?"
- "What's the acceptable failure behavior?"

**Gates:**
- Before starting Refinement, confirm the picked epic satisfies the **Definition of Ready** in [definitions.md](definitions.md). If it doesn't, fix the backlog block first.
- Before the Refinement checkpoint, confirm every AC satisfies the **Definition of Testability** in [definitions.md](definitions.md). If any AC fails DoT, rewrite it.

**Use subagents:** after clarifying questions are answered, delegate spec drafting (including the AC list and any Mermaid diagrams) to a subagent and review the result yourself before the checkpoint.

**Output:**
- Epic Spec document with ACs
- Mermaid sequence or flow diagram for any non-trivial multi-step interaction (optional but recommended when the flow is hard to describe in prose)

**⛳ CHECKPOINT Refinement:** User reviews and approves the spec and ACs. No implementation begins until approved.

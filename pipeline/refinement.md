# Refinement Phase

**Purpose:** Elaborate the backlog detail block (description, key scenarios, HLACs, out-of-scope, risks) into a full implementable spec with detailed Acceptance Criteria **and the key design decisions for how it will be built**. Output: `i1-spec.md` — the source of truth for this iteration; replaces the backlog block.

Refinement is **the** engagement point for an iteration: behaviour (what) and design (how) are settled together here, so everything downstream (Decomposition, Development, Verification, Integration) can run without further approvals. Spend the user's attention here.

If Vision built an Impact Map, don't re-derive "why does this epic matter" from scratch — reference the Impact/Deliverable link this epic already traces to (see [vision.md](vision.md), [backlog.md](backlog.md)). The answer already exists; this phase just needs to stay consistent with it, not re-ask it.

**SPIKE epics — a read-only pre-survey is allowed before sizing, and ACs are questions.** A `SPIKE` epic (see [backlog.md](backlog.md)) can't be sized responsibly without knowing roughly what's there — explicitly permitted: a brief, read-only look at the external system or data before confirming the time-box and ACs, disclosed to the user as part of what Refinement produced, not hidden. Phrase ACs as questions answered with evidence ("Does the API expose historical data, and under what tier?"), not behaviour. The result vocabulary is `works` / `works with limits` / `does not work` / `unverified` / `unresolved` — not pass/fail (see the Definition of Done adaptation in [definitions.md](definitions.md)). The deliverable is a findings document with a mandatory foundation-impact section — see [backlog.md](backlog.md) and [integration.md](integration.md) for what happens with it.

**Discovery/format epics — outcome-phrased ACs, evidence may revise the spec.** For an epic whose job is to *discover* a format or structure from real data (not build against an already-known one), phrase ACs as outcomes ("every status the module needs is defined and justified") rather than locking in literal values before the evidence exists — a literal AC written before real data is seen is a common source of the build later contradicting an approved AC. Add a standing clause to the spec: "evidence from the real data may change the lists in this spec; changes are recorded in a revision section and reported at Integration." Record any such deviation in the spec's revision section as it happens, not as a silent exception discovered later.

**What to produce:**
- Detailed description of the epic's scope
- User stories or scenarios (format: "Given / When / Then" or "As a [user], I want [action] so that [outcome]")
- Acceptance Criteria (ACs) — specific, testable, unambiguous conditions for done
- What is explicitly out of scope for this epic
- Edge cases and failure modes to handle
- UI/UX notes if applicable (rough wireframes, flow descriptions, behavior on error states, design level requirement from Architecture)
- Performance or reliability requirements specific to this epic
- Security considerations specific to this epic
- **Design Decisions** — the non-trivial implementation choices this epic implies (see below)

**Design decisions — surface them here, before the checkpoint:**

After the behavioral Q&A, identify every non-trivial implementation decision the spec implies but does not specify. These are choices Claude would otherwise make silently and bury in code. Common categories:

- Data model: schema structure, how entities are identified or deduplicated over time, indexing strategy
- Algorithm or strategy: matching logic, ranking, caching, retry/backoff approach
- Integration style: sync vs async, polling vs webhook, batch vs streaming
- State management: where/how state is stored, consistency guarantees, handling of concurrent updates
- Error and partial-failure handling: what happens when a multi-step or external operation fails halfway, what the user sees
- **External services & credentials:** which third parties this epic calls; for each, whether it can be **mocked/stubbed** for testing and demo, or genuinely needs a real account/key. (This drives Integration: anything mockable must not block the run later — see [integration.md](integration.md).)
- **Confidential inputs:** if this epic reads anything confidential (internal docs, customer data, proprietary content) to inform the spec or as fixture data, decide now how it's isolated — see the pattern in [development.md](development.md)'s Confidential inputs section.

Present each decision as one of two forms, all together in one message:

> **Decision needed — [topic]**
> - Option A: [description] — [tradeoff]
> - Option B: [description] — [tradeoff]
> *(Option C if genuinely distinct)*
> Which do you prefer?

> **Intended approach — [topic]**
> I'll [approach] because [reason]. Tell me if you'd rather do it differently.

Use **Decision needed** when multiple approaches are genuinely reasonable with meaningful consequences; the user (product owner *and* engineer) chooses. Use **Intended approach** when one path is clearly right for this stack but non-obvious enough that the user should know — a notification with an override window, not a question. Also always extend an open invitation: *"Anything else about how this should work that you want captured rather than left to me?"*

**Parking a decision for deeper discussion.** Design decisions are presented together, by design — splitting them one-at-a-time here would be worse, since they're often related. But if the user wants to dig into *one* of them rather than just answering it, don't let that stall the rest or lose track of it: say "Parking [topic] for discussion — continuing with the others," resolve the rest, then return explicitly ("Back to [topic] — [one-line recap of what's being decided]") and settle it before writing `i1-spec.md`.

Record every confirmed choice in the **Design Decisions** section of `i1-spec.md`. Treat them as constraints, not suggestions. Decomposition reads them; it does not re-ask.

**Example behavioral questions — adapt to the conversation, do not run as a script. One topic at a time — no exceptions:** ask a single question, wait for the user's actual answer, then ask the next. Never dump two or more questions in one message, even ones that seem related or quick.

The list below is a non-exhaustive starter set. Pick the ones that close real gaps for *this* epic, ask follow-ups based on the answers, and skip any that the backlog detail block or earlier answers have already covered. **Stop asking when you have enough information to produce every item in the Output section below and every AC satisfies the Definition of Testability** — running through every example question is not the goal; getting to a confident, testable spec is.

- "What should happen if [edge case]?"
- "Is there a specific UI pattern you have in mind?"
- "Should this be backwards compatible with anything?"
- "What's the acceptable failure behavior?"

**Gates:**
- Before starting Refinement, confirm the picked epic satisfies the **Definition of Ready** in [definitions.md](definitions.md). If it doesn't, fix the backlog block first.
- Before the Refinement checkpoint, confirm every AC satisfies the **Definition of Testability** in [definitions.md](definitions.md). If any AC fails DoT, rewrite it.

**Worked examples for behavior-critical ACs.** For any AC where the *interpretation* of the behaviour could plausibly be misread (matching/identity logic, ranking, transformations, anything where "obvious" hides a choice), attach at least one concrete worked example — specific input → expected output. This is the cheapest defence against a subagent or implementer building the wrong thing from a correct-sounding but ambiguous AC. In deep-requirements mode, reuse the worked examples confirmed in Vision as the anchor and extend them per AC.

**Subagent — default for spec drafting.** Q&A and design-decision Q&A stay with the orchestrator (interactive). After both, delegate drafting to a subagent.

- **Pass:** backlog detail block, user's answers, the confirmed design decisions, **the confirmed worked examples and non-goals from Vision (`f1-vision.md`) when present**, the Output requirements below. Tell it to apply DoT to every AC and to make every behavior-critical AC consistent with the worked examples — never to invent behaviour the examples or design decisions don't support.
- **Expect:** full spec content as the result. Orchestrator **reviews the draft against the worked examples and non-goals** — reject any AC that contradicts them or silently resolves an ambiguity the user didn't decide — then fixes and writes `i1-spec.md`.
- **Definition of Scope Fidelity (see [definitions.md](definitions.md)):** do not ask the drafting subagent to self-report its own added scope. Delegate to a **second, independent subagent** — the spec critic — with the draft plus the epic's backlog block, the user's answers, and the design decisions. Its only job: find gaps, ambiguity, inconsistency, and interpretation-space, and produce the "Added beyond what was stated" list itself — every AC or scenario that goes beyond what was actually asked for. Present that list separately and first at the checkpoint, before the spec itself.

Skip only for trivial-scope epics (one-line FIX, single-AC tweak).

**Output:**
- Epic Spec document with ACs
- **Design Decisions** section: one line per confirmed decision (`topic → chosen approach`), including the external-services/credentials list with each marked *mockable* or *needs real key*
- Mermaid sequence or flow diagram for any non-trivial multi-step interaction (optional but recommended when the flow is hard to describe in prose)

**Policy effects** (`detail` axis only — autonomy is handled in iterate.md / change.md):
- `full` — full output above with rationale for each AC, out-of-scope section, edge cases narrative, optional Mermaid.
- `sparse` — drop the per-AC rationale and the edge-case narrative. Keep ACs, out-of-scope, security/perf bullets, optional Mermaid.
- `minimal` — ACs only (numbered list), one-line per AC. Out-of-scope as a single line if it's non-empty. No diagrams, no narrative.

**Bundle handling** (when the iteration has more than one epic): produce a single `i1-spec.md` with one section per bundled epic. Each section has the same internal structure (description, scenarios, ACs, out-of-scope, edge cases, etc.). ACs are numbered with the parent epic ID for traceability — e.g. `EP-3.AC-1`, `EP-3.AC-2`, `EP-7.AC-1`. Delegate per-epic section drafting to subagents in parallel; the orchestrator assembles. For a single-epic iteration the spec is one flat document with no section headers (same as before).

**⛳ CHECKPOINT Refinement:** User reviews and approves the spec, ACs, **and Design Decisions** together. This is the consolidated per-iteration engagement point — approving here locks both what and how, and the remaining phases run without further approval (subject to the `autonomy` policy). No implementation begins until approved.

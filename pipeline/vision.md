# Vision Phase  [INTERACTIVE]

**Purpose:** Understand what we're building and why — at the highest level. This phase is about business goals and user value, not technology.

*When entering from Analysis (existing codebase): Vision describes the **desired end state** of the system, not the current one. Frame it as "what should this system do / become" and use the Analysis output to highlight the delta — what is missing, what needs to change, what should be removed.*

**What to explore:**
- What problem does this app solve? For whom?
- What is the expected user experience in one sentence?
- Is this a CLI tool, desktop app, web app, mobile app, backend service, distributed system, or a combination?
- Who are the primary users or operators?
- What does success look like? (qualitative or quantitative)
- Are there hard constraints? (platform, language, existing systems to integrate with, compliance)
- What is explicitly out of scope?
- What are the key user journeys? Walk through step-by-step how a user accomplishes their primary goal from start to finish.
- What is the smallest version of this product that would be genuinely useful to a real user?
- Are there existing tools, processes, or systems this replaces? What do users currently do instead, and why is that not good enough?
- What are users' biggest frustrations or pain points today?

**Example questions to draw from — adapt to the conversation, do not run as a script:**

The list below is a non-exhaustive starter set. Pick the ones that close real gaps for *this* project, ask follow-ups based on the answers, and skip any that earlier answers have already covered. **Stop asking when you have enough information to produce every item in the Output section below** — running through every example question is not the goal; getting to a confident Output is.

- "Is this intended for end users or developers/operators?"
- "Do you have a preferred language, framework, or runtime?"
- "Are there any existing systems this must integrate with?"
- "What is the expected scale — personal tool, team tool, or public product?"
- "Walk me through how a typical user would use this from start to finish."
- "What's the one thing users absolutely must be able to do on day one?"
- "What does a successful interaction look like from the user's perspective?"

**Concrete interpretation playback — required in deep-requirements mode** (see [start.md](../commands/start.md); on when research findings exist, the app is external-data/API dependent, or the idea is still abstract after the opening exchange):

A high-level idea is the single biggest source of silent misinterpretation — you (and the subagents you delegate to) fill the gaps, and the mismatch only surfaces in the finished, wrong app. Close that gap *here*, before any drafting:

1. **Play the purpose back concretely.** Restate, in your own words, what the app actually does end-to-end — not the slogan. "As I understand it: the user does X, the system does Y, and the value is Z."
2. **Give 2–3 worked examples.** Pick real, specific inputs and state the expected output: *"If the user feeds in <concrete input>, the app produces <concrete output> because <reason>."* Use the user's real domain data, not placeholders. Worked examples expose misread intent faster than any abstract question.
3. **State explicit non-goals.** "This is NOT a ___ / it does NOT do ___." Wrong interpretations usually hide in the unstated boundary.
4. **Confirm the assumptions register.** If research produced a Key assumptions register, walk its intent-related items here and correct them. Otherwise, list the interpretation choices you'd otherwise make silently and have the user confirm or correct each.

Ask the user to confirm or correct the playback before you draft anything. Treat a correction as a hard requirement. **Do not delegate drafting until the interpretation is confirmed** — otherwise the subagent inherits the misread.

For a small, clearly-specified, self-contained app (deep-requirements mode off), skip this — a one-line restatement is enough.

**Use subagents:** the Q&A and the interpretation playback are interactive and stay with you. Only after the user has confirmed the concrete interpretation may you delegate Vision Statement drafting (and the user-journey narratives) to a subagent — and pass it the confirmed worked examples and non-goals, not just the abstract idea. Review the result against those examples before the checkpoint.

**Output:**
- Product Vision Statement (2–4 sentences)
- Target user(s)
- App type and platform(s)
- Hard constraints and out-of-scope items
- Rough success criteria
- Key user journeys (1–3 step-by-step narratives of primary use cases, written from the user's perspective)
- MVP definition: the minimum feature set for a first usable, demonstrable version
- **(deep-requirements mode)** Concrete interpretation: the confirmed worked examples (input → expected output) and the explicit non-goals. These become the reference subagents and later phases check their work against.
- **(deep-requirements mode)** Confirmed assumptions: the intent and external-world assumptions the user verified or corrected, with any still-open items flagged.

**⛳ CHECKPOINT Vision:** User reviews and approves the Vision Statement, user journeys, and MVP definition before proceeding. In deep-requirements mode, the worked examples, non-goals, and confirmed assumptions are part of what's approved — they are the contract against which the build's correctness is later judged.

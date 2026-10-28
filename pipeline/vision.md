# Vision Phase  [INTERACTIVE]

**Purpose:** Understand what we're building and why — at the highest level. This phase is about business goals and user value, not technology.

*When entering from Analysis (existing codebase): Vision describes the **desired end state** of the system, not the current one. Frame it as "what should this system do / become" and use the Analysis output to highlight the delta — what is missing, what needs to change, what should be removed.*

**If the user points at external reference files** (example documents, existing specs, sample data) living outside the project directory: once it's clear you'll need to read more than one or two of them, offer to add a permission rule scoped to just that directory — `Read(<that directory>/**)` in `~/.claude/settings.json` — instead of leaving the user to hit Claude Code's own all-or-nothing "allow reads outside the working directory" prompt (which only offers "allow everything outside the project" or "ask every time," no middle ground). Ask first; if the user agrees, read `~/.claude/settings.json` (create it if missing), add the rule to `permissions.allow`, write it back, and confirm. If they decline, continue — reads proceed through Claude Code's normal prompt flow as usual.

**Opening question — frame it as a job, not a feature request.** Before anything else, anchor on the underlying situation and motivation rather than whatever solution shape the user walked in with: *"When does this come up? What are you actually trying to accomplish at that moment? What would 'done' feel like?"* (Jobs-to-be-Done framing: when [situation], I want to [motivation], so I can [expected outcome].) A user who arrives with a specific feature idea has usually already half-designed a solution — this question surfaces the need underneath it before that shape gets locked in as fact.

**What to explore:**
- What problem does this app solve? For whom? (the job from the opening question, now in scope)
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

**Grounded options first, as the default question style.** A user who doesn't know the possibility space can't give a good answer to a blank question — and most of the questions above have well-understood common shapes. Default to presenting 2–4 realistic options grounded in real knowledge of the domain instead of an open prompt: *"Most apps like this handle [X] by doing A, B, or C — which fits, or tell me if none do"* rather than *"how do you want to handle X?"* This reuses the Option A/B/C/D pattern already used for decisions in `refinement.md` and `architecture.md`, just applied earlier — to exploration, not only to decisions. Fall back to a genuinely open question only when the domain is novel enough that there isn't a small set of realistic shapes to offer.

**Example questions to draw from — adapt to the conversation, do not run as a script:**

The list below is a non-exhaustive starter set. Pick the ones that close real gaps for *this* project, ask follow-ups based on the answers, and skip any that earlier answers have already covered. **Stop asking when you have enough information to produce every item in the Output section below** — running through every example question is not the goal; getting to a confident Output is.

- "Is this intended for end users or developers/operators?"
- "Do you have a preferred language, framework, or runtime?"
- "Are there any existing systems this must integrate with?"
- "What is the expected scale — personal tool, team tool, or public product?"
- "Walk me through how a typical user would use this from start to finish."
- "What's the one thing users absolutely must be able to do on day one?"
- "What does a successful interaction look like from the user's perspective?"

**Build the Impact Map before drafting.** Once the opening Q&A gives enough material, structure it explicitly instead of leaving it as scattered answers:

1. **Goal** — the business/product outcome this app exists to produce. Usually falls straight out of the JTBD opening question's "expected outcome."
2. **Actors** — who can affect that goal. Not just end users — anyone whose behaviour matters: operators, admins, a support team, an existing system.
3. **Impacts** — how each actor needs to behave differently to move the goal. One or two per actor, stated as a behaviour change, not a feature.
4. **Deliverables** — what you'd build to cause each impact. This layer seeds Backlog's epic list directly — see [backlog.md](backlog.md). Each epic should trace back to at least one Impact.

Agent-drivable as a plain four-step conversational chain — no diagrams or multiple participants required. A sentence or two per layer is enough for most projects; expand only where the domain genuinely needs it.

**Concrete interpretation playback — required in deep-requirements mode** (whether deep-requirements mode is on is decided in [start.md](../commands/start.md) Step 1, from the `requirement_rigor` policy knob: `always` forces it on, `never` forces it off, and `auto` — the default — turns it on when research findings exist, the app is external-data/API dependent, or the idea is still abstract after the opening exchange):

A high-level idea is the single biggest source of silent misinterpretation — you (and the subagents you delegate to) fill the gaps, and the mismatch only surfaces in the finished, wrong app. Close that gap *here*, before any drafting:

1. **Play the purpose back concretely.** Restate, in your own words, what the app actually does end-to-end — not the slogan. "As I understand it: the user does X, the system does Y, and the value is Z." If an Impact Map was built, this is a natural restatement of its Goal — reuse it rather than re-deriving the purpose from scratch.
2. **Give 2–3 worked examples.** Pick real, specific inputs and state the expected output: *"If the user feeds in <concrete input>, the app produces <concrete output> because <reason>."* Use the user's real domain data, not placeholders. Worked examples expose misread intent faster than any abstract question.
3. **State explicit non-goals.** "This is NOT a ___ / it does NOT do ___." Wrong interpretations usually hide in the unstated boundary.
4. **Confirm the assumptions register.** If research produced a Key assumptions register, walk its intent-related items here and correct them. Otherwise, list the interpretation choices you'd otherwise make silently and have the user confirm or correct each.

This register is a grouped set, walked together — not asked one item per message. But if the user wants to dig into *one* item rather than just confirming it, don't let that stall the rest or lose track of it: say "Parking [item] for discussion — continuing with the rest," walk the remaining items, then return explicitly ("Back to [item] — [one-line recap]") and resolve it before moving on.

Ask the user to confirm or correct the playback before you draft anything. Treat a correction as a hard requirement. **Do not delegate drafting until the interpretation is confirmed** — otherwise the subagent inherits the misread.

For a small, clearly-specified, self-contained app (deep-requirements mode off), skip this — a one-line restatement is enough.

**Use subagents:** the Q&A and the interpretation playback are interactive and stay with you. Only after the user has confirmed the concrete interpretation may you delegate Vision Statement drafting (and the user-journey narratives) to a subagent — and pass it the confirmed worked examples and non-goals, not just the abstract idea. Review the result against those examples before the checkpoint.

**Definition of Scope Fidelity (see [definitions.md](definitions.md)):** after the drafting subagent returns the Vision Statement, delegate to a **second, independent subagent** — the spec critic — with the draft plus the confirmed worked examples and non-goals (not the drafter's own opinion of its work). Its only job: find gaps, ambiguity, inconsistency, and interpretation-space, and produce the "Added beyond what was stated" list itself. Present that list separately and first at the checkpoint, before the Vision Statement itself.

**Output:**
- Product Vision Statement (2–4 sentences)
- Impact Map: Goal → Actors → Impacts → Deliverables
- Target user(s)
- App type and platform(s)
- Hard constraints and out-of-scope items
- Rough success criteria
- Key user journeys (1–3 step-by-step narratives of primary use cases, written from the user's perspective)
- MVP definition: the minimum feature set for a first usable, demonstrable version
- **(deep-requirements mode)** Concrete interpretation: the confirmed worked examples (input → expected output) and the explicit non-goals. These become the reference subagents and later phases check their work against.
- **(deep-requirements mode)** Confirmed assumptions: the intent and external-world assumptions the user verified or corrected, with any still-open items flagged.

**⛳ CHECKPOINT Vision:** User reviews and approves the Vision Statement, Impact Map, user journeys, and MVP definition before proceeding. In deep-requirements mode, the worked examples, non-goals, and confirmed assumptions are part of what's approved — they are the contract against which the build's correctness is later judged.

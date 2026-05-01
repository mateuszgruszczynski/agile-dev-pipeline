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

**Questions to ask the user if unclear:**
- "Is this intended for end users or developers/operators?"
- "Do you have a preferred language, framework, or runtime?"
- "Are there any existing systems this must integrate with?"
- "What is the expected scale — personal tool, team tool, or public product?"
- "Walk me through how a typical user would use this from start to finish."
- "What's the one thing users absolutely must be able to do on day one?"
- "What does a successful interaction look like from the user's perspective?"

**Use subagents:** the Q&A is interactive and stays with you, but after the user has answered the questions you may delegate Vision Statement drafting (and the user-journey narratives) to a subagent and review the result yourself before the checkpoint.

**Output:**
- Product Vision Statement (2–4 sentences)
- Target user(s)
- App type and platform(s)
- Hard constraints and out-of-scope items
- Rough success criteria
- Key user journeys (1–3 step-by-step narratives of primary use cases, written from the user's perspective)
- MVP definition: the minimum feature set for a first usable, demonstrable version

**⛳ CHECKPOINT Vision:** User reviews and approves the Vision Statement, user journeys, and MVP definition before proceeding.

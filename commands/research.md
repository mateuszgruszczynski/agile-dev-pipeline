---
description: Research feasibility and implementation approach for a novel app idea. Runs before the pipeline — produces findings that feed directly into /agile-dev:start Vision and Architecture phases.
---

Research runner. Takes a rough idea, identifies what's unknown, searches the web, writes and runs probe scripts to collect structured data without token waste, and produces a findings artifact that tells you whether and how to build the thing before committing to a full pipeline.

---

## Step 1 — Capture the idea

`$ARGUMENTS` is the idea description. If empty or too vague to act on, ask:

> *"Describe the app you want to research. What problem does it solve? What are you most uncertain about — technical feasibility, data availability, existing solutions, cost, legal?"*

Keep asking follow-up questions until you have:
- What the app does (user-facing goal)
- What external data, APIs, or services it likely depends on
- Any known constraints (platform, budget, must-use technology)
- What the user is most uncertain about

Do not start researching until you understand what the unknowns actually are.

---

## Step 2 — Build the research plan

Identify 3–8 research questions that must be answered before planning can begin. Group them:

- **Feasibility** — can this be built? Are there blockers (legal, data access, API availability, technical limits)?
- **Data and APIs** — what external sources does this need? Are they accessible, at what cost, under what terms?
- **Existing solutions** — what's already built? What can be learned or reused? What gaps exist?
- **Technical approach** — what libraries, frameworks, or patterns fit? What are the tradeoffs between approaches?
- **Risks and unknowns** — what could kill the project before it starts? What needs a spike?

Present the research plan to the user (one sentence per question). Ask:
> *"Anything missing or not worth researching?"*

Adjust based on feedback, then proceed.

---

## Step 3 — Research

For each research question, choose sources based on what type of answer you need. Do not default to a single web search for everything — many of the most useful sources are not well-indexed by general search engines.

**Source selection by question type:**

| Question type | Primary sources | Secondary |
|---|---|---|
| What libraries or packages exist? | Package registries directly: `npmjs.com/search`, `pypi.org/search`, `crates.io/search`, `search.maven.org`, `pkg.go.dev` | GitHub topic pages, awesome-* lists (search GitHub for `awesome-<domain>`), WebSearch |
| What APIs or data sources exist? | `rapidapi.com`, `programmableweb.com`, government open data portals (`data.gov`, `data.europa.eu`), domain-specific registries | WebSearch `"<domain> API"`, HackerNews `"<domain> API"` |
| What datasets are available? | `kaggle.com/datasets`, `huggingface.co/datasets`, `datasetsearch.research.google.com`, domain-specific repos (financial, geospatial, health) | WebSearch, academic search |
| Does an existing implementation exist? | GitHub search (`github.com/search?q=<topic>&type=repositories`), GitLab search | WebSearch, Product Hunt |
| What do practitioners say about this approach? | HackerNews (`hn.algolia.com`), Reddit (`reddit.com/search`), Stack Overflow (`stackoverflow.com/search`) | WebSearch |
| Is this technically feasible / what are the limits? | Official docs and changelogs, GitHub issues on relevant libs, arXiv (`arxiv.org/search`) for algorithmic questions | Google Scholar, WebSearch |
| What AI models or embeddings are available? | `huggingface.co/models`, `openai.com/docs`, provider-specific model pages | WebSearch |
| What does this API actually return? | **Write a probe script (Step 4)** — do not rely on documentation alone | Official API reference |

**How to search:**

Use `WebSearch` for general queries and for sources without a structured search API. Use `WebFetch` to read specific pages directly — a package registry search page, a GitHub README, an API pricing page, an arXiv abstract. Fetch when the search snippet doesn't give enough detail.

Use multiple queries per question if the first results are thin. Vary the phrasing: a question about "scraping car listings" may surface more useful results as "used car data API", "automotive listings API", or "car price dataset".

For GitHub specifically: search for repositories by topic (`github.com/topics/<topic>`), by keyword in README, and look at starred forks of relevant repos to find maintained alternatives.

Skip sources that clearly duplicate something already found. Stop when you have enough evidence to write a confident finding — exhaustive coverage is not the goal.

---

## Step 4 — Probe scripts

When web research alone cannot answer a question — because you need to see what data actually looks like, not just what documentation says — write a minimal script and run it immediately.

**When to use a probe script:**
- Verifying what an API endpoint actually returns (fields, pagination, rate limit headers)
- Checking whether a website is accessible and what its HTML structure looks like
- Testing authentication or discovering rate limit behaviour
- Sampling a dataset to understand its shape and completeness
- Checking robots.txt and crawl delays programmatically across multiple targets

**⚠️ Connectivity is not capability.** A probe that gets `200 OK` from a list endpoint proves you can *reach* the API — it does **not** prove the specific capability your app depends on is available on the tier you tested. Docs routinely omit that the function you actually need is behind a paid plan, a partner agreement, KYC/approval, or a higher rate tier. So:
- Probe the **exact capability the app relies on**, not a generic health/list call. If the app needs historical price data, fetch historical price data — not the docs' "getting started" endpoint.
- When you hit auth or a paywall (`401`, `402`, `403`, "upgrade your plan"), that is a **finding**, not a failure to route around. Record exactly what was gated and what tier/approval it demanded.
- If a capability cannot be exercised without paying or signing up, you **cannot** mark it verified. Mark it `MUST-VERIFY` (see Step 5) — never infer it works from adjacent endpoints that did.

**How to write probe scripts:**
- Use Python by default (available everywhere); switch to the project's language if it's already decided
- One script per question — keep them short and focused
- No error suppression — let failures surface clearly; a 403, 402, or empty result is itself an answer
- Print structured output: dump JSON, print field names, show sample records, report counts, **print HTTP status and any error/quota body verbatim**
- Do not write production-quality code — these are throwaway probes; just make them work

Run each script immediately after writing it. Use the output as evidence in Step 5.

Save all scripts to `.project-artifacts/research/scripts/<question-slug>.py`. They are kept for reference — the user may want to extend or repurpose them later.

---

## Step 5 — Synthesise findings

**Golden rule: nothing is a fact unless you verified it.** Docs and search results are *claims*. A probe run is *evidence* — but only for exactly what it exercised. Everything else is an *assumption*. The report must keep these three apart on every line; do not launder a claim or an assumption into a recommendation.

Tag every finding with its provenance and confidence:
- `[verified]` — a probe script exercised the exact capability and it worked. Cite the script.
- `[claimed]` — stated by docs / a search result / a repo README, not independently confirmed.
- `[assumption]` — inferred or filled in by you; nobody confirmed it.

Compile the report with these sections:

### Access & Cost reality check (mandatory)
The most common silent killer: the API exists, but the function the app needs is gated behind money, approval, or KYC that the docs don't lead with. For **every** external dependency, answer explicitly — and tag each answer `[verified]` / `[claimed]` / `[assumption]`:

| Dependency | Capability the app needs | Available on free/used tier? | Paywall / approval / KYC for *that* capability? | How confirmed |
|---|---|---|---|---|
| example.com API | historical price series | ? | ? | probe got 402 on /history → MUST-VERIFY |

Any cell that is `?`, `[claimed]`, or `[assumption]` for a capability the app **depends on** becomes a **MUST-VERIFY** item, and:
- **caps the Feasibility verdict at Yellow** (cannot be Green), and
- becomes a hard pre-condition listed below (the pipeline will not start until it's resolved — see Step 6 and `start.md`).

### Feasibility verdict
One of:
- **Green** — every capability the app depends on is `[verified]`; no open MUST-VERIFY access/cost item; no fundamental blocker.
- **Yellow** — viable, but these must be resolved first: [list every MUST-VERIFY item + other pre-conditions]. A research run with *any* unverified access/cost dependency is Yellow at best, by rule.
- **Red** — fundamental blocker: [explain why and what would need to change].

### Findings
One section per research question. For each: what was found (with provenance tags), what it means for the project, and concrete evidence — API response fields, status codes seen, data-source URLs, library names/versions, cost figures, TOS constraints. Where a probe ran, cite the script and the actual output, not the doc.

### Recommended approach
The preferred technical direction in 3–5 sentences: language, key libraries or external services, architecture sketch, main integration points. State plainly which parts rest on `[verified]` evidence and which rest on `[claimed]`/`[assumption]` — the user is choosing a direction, and they need to know which load-bearing pieces are still unconfirmed. If a meaningful alternative exists, name it and why it was not recommended.

### Key assumptions (register)
A flat list of every `[assumption]` and load-bearing `[claimed]` item the recommendation depends on — about the world (API behaviour, cost, data quality, legal) **and** about intent (what "the app" is supposed to do where the brief was vague). Each line: the assumption, why it matters if wrong, and how to confirm it. This register is carried into `start.md` and surfaced for confirmation — it is the antidote to "decisions made automatically on research that turned out wrong."

### Open questions
Anything research could not answer. For each: what would resolve it (a quick spike, a legal review, a test account, direct contact with the provider).

### Pre-conditions before starting the pipeline
Specific things that must be true before `/agile-dev:start` proceeds. Includes **every MUST-VERIFY access/cost item** plus the rest (API key obtained, paid tier confirmed, legal review done, spike validated, dataset confirmed to have required fields). Mark each as resolved/unresolved.

---

## Step 6 — Write artifacts and checkpoint

1. Create `.project-artifacts/research/` if it doesn't exist.
2. Write `.project-artifacts/research/findings.md` with the full synthesis from Step 5.
3. If scripts were written, confirm they are saved under `.project-artifacts/research/scripts/`.
4. If the directory has no git repository yet, offer:
   > *"No git repository found. Initialise one and commit the research findings? (yes / no)"*
   - yes: `git init`, create a minimal `.gitignore` (`.env`, `dist/`, `node_modules/`, `.DS_Store`), stage and commit with `chore: research findings`.
   - no: continue.

**⛳ CHECKPOINT Research:** Present `findings.md`, but do not just dump it — **walk the user through the risky parts and get a decision on each**:
1. Read out the **MUST-VERIFY access/cost items** one by one. For each, ask the user to either confirm from their own knowledge ("yes, I have the paid tier" / "no, that function is enterprise-only") or accept it as an open pre-condition to verify before building. Update each item's status from their answer.
2. Read out the **Key assumptions register**, especially any `[assumption]` about *what the app is meant to do*. Correct the user's intent here, now — this is where a vague brief gets misread.
3. Restate the **Feasibility verdict** after their answers (it may move from Yellow toward Green as items resolve, or to Red if something they know rules it out).

Then wait for approval.

After approval, say:

> *"Research complete. Run `/agile-dev:start`. The findings load into Vision and Architecture, and any unresolved MUST-VERIFY pre-condition will block the build until you resolve it — that's deliberate."*

---

## Arguments

$ARGUMENTS

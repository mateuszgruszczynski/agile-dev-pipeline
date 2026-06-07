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

**How to write probe scripts:**
- Use Python by default (available everywhere); switch to the project's language if it's already decided
- One script per question — keep them short and focused
- No error suppression — let failures surface clearly; a 403 or empty result is itself an answer
- Print structured output: dump JSON, print field names, show sample records, report counts
- Do not write production-quality code — these are throwaway probes; just make them work

Run each script immediately after writing it. Use the output as evidence in Step 5.

Save all scripts to `.project-artifacts/research/scripts/<question-slug>.py`. They are kept for reference — the user may want to extend or repurpose them later.

---

## Step 5 — Synthesise findings

Compile everything into a research report with these sections:

### Feasibility verdict
One of:
- **Green** — no fundamental blockers found; recommend starting the pipeline
- **Yellow** — viable, but address the following before starting: [list pre-conditions]
- **Red** — fundamental blocker: [explain why and what would need to change]

### Findings
One section per research question. For each: what was found, what it means for the project. Include concrete evidence: API response fields, data source URLs, library names and versions, cost figures, TOS constraints.

### Recommended approach
The preferred technical direction in 3–5 sentences: language, key libraries or external services, architecture sketch, main integration points. If a meaningful alternative exists, name it and explain why it was not recommended.

### Data and API sources
Table of every external source, service, or dataset relevant to the project:

| Source | What it provides | Access | Cost | Notes |
|---|---|---|---|---|
| example.com API | Used car listings with price history | API key required | Free tier: 1000 req/day | TOS allows price aggregation; HTML scraping prohibited |

### Open questions
Anything research could not answer. For each: what would resolve it (a quick spike, a legal review, a test account, direct contact with the service provider).

### Pre-conditions before starting the pipeline
Specific things that must be true before `/agile-dev:start` is run. Examples: API key obtained, legal review completed, spike prototype validated, dataset confirmed to have required fields.

---

## Step 6 — Write artifacts and checkpoint

1. Create `.project-artifacts/research/` if it doesn't exist.
2. Write `.project-artifacts/research/findings.md` with the full synthesis from Step 5.
3. If scripts were written, confirm they are saved under `.project-artifacts/research/scripts/`.
4. If the directory has no git repository yet, offer:
   > *"No git repository found. Initialise one and commit the research findings? (yes / no)"*
   - yes: `git init`, create a minimal `.gitignore` (`.env`, `dist/`, `node_modules/`, `.DS_Store`), stage and commit with `chore: research findings`.
   - no: continue.

**⛳ CHECKPOINT Research:** Present `findings.md`. User reviews and approves the findings.

After approval, say:

> *"Research complete. Run `/agile-dev:start` — the findings in `.project-artifacts/research/findings.md` will be loaded automatically during Vision and Architecture."*

---

## Arguments

$ARGUMENTS

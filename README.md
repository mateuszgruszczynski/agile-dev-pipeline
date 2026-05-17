# Agile Dev Pipeline

A structured, agile-inspired development pipeline for Claude Code, packaged as a **Claude Code plugin**. Describe what you want to build, and the pipeline guides you — and Claude — through discovery, architecture, planning, and iterative implementation, with checkpoints at every key decision so you stay in control.

Inspired by Scrum, Kanban, the V-model, and lean practices. Works for any app type: CLI tools, web apps, desktop apps, mobile apps, backend services, distributed systems.

---

## How it works

The pipeline runs as a set of **slash commands** inside Claude Code. Once the plugin is installed, the commands are available in every Claude Code session under the `/agile-dev:` namespace.

When you run a pipeline command, Claude acts as an orchestrator: it interviews you, produces plans and specs, waits for your approval at every major step, and then implements the work — all within a single conversation (or split across short sessions, since each phase runs independently).

All outputs (vision, architecture, backlog, specs, test cases, retrospectives) are saved as markdown files in a `.project-artifacts/` folder inside your project, so the pipeline survives session restarts and you can review everything at any time.

### The three modes

| Command | When to use |
|---|---|
| `/agile-dev:start` | Building something new from scratch |
| `/agile-dev:improve` | Improving or extending an existing codebase |
| `/agile-dev:change` | A single bounded change (feature, refactor, bug fix) without full foundation phases |

Modes `start` and `improve` share the same iteration loop once the foundation is established. Mode `change` is a lightweight path for one-off work.

### What a session looks like

```
You:    /agile-dev:start a CLI tool that converts CSV files to JSON

Claude: Starting Vision
        What problem does this solve? Who is the primary user?

You:    developers who need to quickly transform data files in scripts

Claude: [asks 2–3 more focused questions]
        ...produces a Vision Statement...
        Please review the above. Reply APPROVE to continue, or describe what needs to change.

You:    APPROVE

Claude: Starting Architecture
        [proposes architecture, asks about preferences]
        ...APPROVE...

Claude: Starting Backlog → Environment
        [generates .devcontainer/ + .claude/settings.json]
        Foundation complete. Reopen the project in the dev container, then run /agile-dev:iterate.

You:    [Cmd+Shift+P → Dev Containers: Reopen in Container]
        /agile-dev:iterate

Claude: [inside the container, picks the first epic, runs Refinement → ... → Retrospective]
```

Every time Claude produces a plan, spec, or decision, it stops and asks for your approval before continuing. You can redirect, ask for changes, or add context. The shift to "inside the dev container" happens once, between Foundation and the first iteration.

### Pipeline policy — three knobs you set once per project

Before any phase runs, you choose three things that control how the pipeline behaves for this project. Stored in `.project-artifacts/policy.md` — editable by hand at any time.

| Knob | Options | What it controls |
|---|---|---|
| **autonomy** | `user-driven` / `semi-automatic` (default) / `ai-driven` | How often the pipeline pauses for your approval. `user-driven` = every checkpoint. `semi-automatic` = conditional checkpoints auto-skip when work is straightforward. `ai-driven` = only Vision pauses; everything else runs through. |
| **detail** | `full` (default) / `sparse` / `minimal` | How verbose the produced artifacts are. `full` = current behaviour with rationale and edge cases. `sparse` = facts only, no narrative. `minimal` = one-line outputs, just enough to drive the next phase. |
| **test_coverage** | `thorough` (default) / `minimal` / `none` | How much testing the pipeline produces. `thorough` = full pyramid. `minimal` = one happy-path scenario per AC. `none` = skips Test Plan + Verification entirely; manual smoke is the only gate. For prototypes. |
| **packaging** | `each` (default) / `milestone` / `final` | When a runnable artifact (binary / jar / docker image / etc.) gets produced. `each` = every iteration writes one to `dist/<NNN>-<slug>/`. `milestone` = only at `/agile-dev:release` boundaries. `final` = only on explicit user request. Architecture decides *what* the artifact is and which platforms it targets; Environment generates the build recipe; Integration runs it and smoke-tests the result. |
| **iteration_size** | `xs` / `s` / `m` / `l` / `xl` (default) / `xxl` | How much work goes into one iteration. T-shirt sizes have point values (XS=1, S=1.7, M=3, L=5.2, XL=9, XXL=15.6, scaling as √3). The iteration bundler picks a set of TODO epics from the backlog summing closest to this budget, respecting priority order and dependencies. Default `xl` = 9 points ≈ one XL epic, two L epics, three M epics, or any equivalent combination. Larger = fewer checkpoints per real-world unit of work. |

The defaults match the pipeline's original behaviour, so existing projects don't change. You're asked once during `/agile-dev:start` / `/agile-dev:improve` / `/agile-dev:change`. Combining `ai-driven` with `none` triggers an extra confirmation since it removes both human and automated gates — only appropriate for throwaway code.

### The two halves: Foundation and Iteration

```
Foundation (runs once per project)         Iteration loop (per epic, repeats)
──────────────────────────────────         ──────────────────────────────────
Vision → Architecture → Backlog            Refinement → Decomposition
   → Environment                              → Test Plan → Development
                                              → Verification → Integration
                                              → Retrospective ── next epic ──┐
                                                                              ↓
                                              (continue, stop, or release)
```

**Foundation** sets up the project once: what to build, how to build it, the list of epics, and a reproducible dev environment.

**Iteration** runs through every epic in the backlog. Each iteration produces a spec, a test plan, code, automated tests, and a verified, demoable result. The loop flows forward continuously and only stops at ⛳ approval checkpoints. Closing the Claude session at any approval is a safe pause — the next command picks up where you left.

### Foundation phases

| Phase | What it produces | Checkpoint? |
|---|---|---|
| **Analysis** *(improve mode only)* | Snapshot of the existing codebase | Yes |
| **Vision** | Statement of what we're building and why | Yes |
| **Architecture** | Tech stack, component layout, integration plan | Yes |
| **Backlog** | Prioritised list of epics | Yes |
| **Environment** | Dev container (Docker) tailored to the stack; after this, you reopen the project inside the container | Yes |

### Iteration phases

| Phase | What it produces | Checkpoint? |
|---|---|---|
| **Refinement** | Detailed spec + Acceptance Criteria for this epic | Yes |
| **Decomposition** | Task breakdown by role (DEV / QA / DEVOPS / SRE / SECURITY / DESIGN / DATA) | Auto-skip when straightforward |
| **Test Plan** | BDD scenarios for each Acceptance Criterion, each tagged with level + type | Yes |
| **Development** | Code + **in-process** tests (Unit, Component) | None |
| **Verification** | **Out-of-process** tests (System-integration, E2E) run against the running application | None |
| **Integration** | Production build, manual smoke test, demo readiness | Auto-continue on green |
| **Retrospective** | Action items for the backlog; iteration-boundary decision (continue / stop / fix foundation) | Yes |

> **A few terms worth a one-line gloss:**
> - **AC** (Acceptance Criteria): testable conditions stating "this epic is done when …"
> - **BDD** (Behaviour-Driven Development): scenarios in plain language — *Given X, When Y, Then Z* — that non-engineers can read and verify.
> - **In-process tests:** run inside your application's own process. Fast, cheap (Unit, Component).
> - **Out-of-process tests:** drive the real running application from outside — over HTTP, message queues, the UI, a CLI, etc. Slower, but prove the deployed app actually works (System-integration, E2E).
> - **Level** vs **type:** every test scenario carries both. Level = scope (Unit / Component / Contract / System-integration / E2E). Type = interface (UI / API / Protocol / CLI / File-batch). A backend service can have E2E tests entirely over HTTP — E2E does **not** imply UI.

---

## Prerequisites

1. **Claude Code** installed and set up. If you haven't done this yet, follow the official guide: https://docs.anthropic.com/claude-code
2. A Claude Code account with an active session.
3. **Git** installed and your project initialised as a git repo. The pipeline relies on git for commits, history, and recovery flows. If your directory isn't a repo yet, `/agile-dev:start` will offer to `git init` for you.
4. **Docker Desktop** (or another Docker runtime) and a container-aware editor — VS Code, Cursor, or any IDE with a "Reopen in Container" action. The pipeline generates a dev container for your project so all development work runs in a reproducible environment. If you don't have these, you'll be prompted to install them at the Environment phase.

> **Dev container?** A Docker container with your project's dependencies pre-installed. After Backlog approval, the pipeline writes the container config; you click "Reopen in Container" in your editor; Claude restarts inside the container with the right tools already wired up. You don't need to know Docker to use it — the pipeline handles the setup.

---

## Installation

The pipeline is distributed as a Claude Code plugin. Installation is two commands inside any Claude Code session.

### Step 1 — Add the marketplace

```
/plugin marketplace add mateuszgruszczynski/agile-dev-pipeline
```

This registers the GitHub repository as a plugin source.

### Step 2 — Install the plugin

```
/plugin install agile-dev@agile-dev
```

That's it. The seven commands are now available in every Claude Code session:

- `/agile-dev:start`
- `/agile-dev:improve`
- `/agile-dev:change`
- `/agile-dev:iterate`
- `/agile-dev:status`
- `/agile-dev:release` — bundle iterations into a versioned release (MVP-first)
- `/agile-dev:revise` — revise a foundation phase (Vision / Architecture / Backlog) when Retrospective flags it

### Updating

When a new version of the pipeline is released, update with:

```
/plugin update agile-dev
```

Updates handle file removals cleanly — orphaned files from older versions are pruned automatically.

### Uninstalling

```
/plugin uninstall agile-dev
```

### After install — a one-time permission rule

Claude Code does not currently let a plugin pre-authorise reads of its own files via the shipped `settings.json`. Without a rule, you would be prompted to approve every read of the pipeline's definition files (`pipeline/vision.md`, `pipeline/architecture.md`, …).

The pipeline handles this automatically: the first time you run `/agile-dev:start`, `/agile-dev:improve`, `/agile-dev:change`, or `/agile-dev:iterate`, Step 0 of the command checks your `~/.claude/settings.json` and, if no rule covers the plugin, asks you once: *"Add `Read(<your-home>/.claude/plugins/cache/agile-dev/**)` to your user settings?"*. Reply **yes**, and from your next Claude Code session onwards the rule will be in effect — Claude reads `~/.claude/settings.json` once at session start, so the running session that added the rule still sees the old in-memory permission set and may prompt for the first few files; subsequent sessions don't.

If you'd rather add the rule manually, drop this into the `permissions.allow` array in `~/.claude/settings.json` (replace `<HOME>` with your actual home directory):

```json
"Read(<HOME>/.claude/plugins/cache/agile-dev/**)"
```

**Heads-up: occasional prompts can still appear** even with the rule in place. Claude Code's permission matcher sometimes misses on transient reads even when an `allow` rule should match — a known harness behaviour, not a plugin or rule-syntax issue. Approving the prompt is harmless; if it gets noisy or repeats, file a `/feedback` report inside Claude Code with the specific path and rule. See the FAQ for details.

---

## Usage

### Starting a new project

Open a terminal in your project folder and start a Claude Code session, then run:

```
/agile-dev:start <brief description of what you want to build>
```

Example:
```
/agile-dev:start a web app that lets teams track their weekly goals and celebrate completions
```

Claude will begin the foundation phase, asking clarifying questions one at a time.

### Improving an existing project

Navigate to the existing project folder, start Claude Code, and run:

```
/agile-dev:improve <description of what the system should do or become>
```

Example:
```
/agile-dev:improve add user authentication and a REST API to the existing data processing tool
```

Claude will first read and analyse your codebase before asking any questions, then propose a delta plan based on what already exists.

### A single bounded change

For a one-off feature, refactor, or bug fix that doesn't warrant the full foundation flow:

```
/agile-dev:change <description of the change>
```

Example:
```
/agile-dev:change add CSV export to the reports page
```

Goes through Refinement → Decomposition → Test Plan → Development → Verification → Integration → Retrospective for that single change only.

### Running iterations

After Foundation is complete, drive the iteration loop with:

```
/agile-dev:iterate
```

Each invocation runs **forward through every iteration phase** until it hits an approval checkpoint, the iteration boundary, or the end of the backlog. After every approval, the loop continues in the same session — you don't have to re-invoke the command between phases. Closing the session at any approval saves your place; the next `/agile-dev:iterate` resumes from there.

To work on a specific epic out of priority order:

```
/agile-dev:iterate <epic name>
```

Only allowed when no other iteration is in progress.

### Checking status

At any point — including after restarting a session — you can check where you are:

```
/agile-dev:status
```

Claude will read `.project-artifacts/state.md` and report the current phase, current epic, remaining backlog, and what comes next.

### Resuming after a restart

Just open Claude Code in the same project folder and run `/agile-dev:iterate` (or `/agile-dev:start` / `/agile-dev:improve`) again. The pipeline reads `.project-artifacts/state.md` automatically and picks up from where it left off.

---

## Project files

After the pipeline has run for a while, your project will contain a `.project-artifacts/` folder:

```
.project-artifacts/
  state.md                        ← current position, backlog, and per-iteration history
  policy.md                       ← pipeline policy (autonomy / detail / test_coverage)
  pipeline-feedback.md            ← meta-feedback about the pipeline itself (created on first entry)
  ana-analysis.md                 ← codebase analysis (improve mode only)
  f1-vision.md                    ← approved vision and goals
  f2-architecture.md              ← approved architecture decisions
  f3-backlog.md                   ← epic backlog
  iterations/
    001-<epic-name>/              ← split iterations use 001-A / 001-B
      i1-spec.md                  ← detailed spec and acceptance criteria
      i2-tasks.md                 ← task breakdown by role
      i3-test-plan.md             ← acceptance test scenarios (test plan)
      i4-dev.md                   ← development summary (in-process tests)
      i5-verify.md                ← verification result (out-of-process tests)
      i6-int.md                   ← integration result (build, smoke, demo)
      i7-retro.md                 ← retrospective notes
  releases/
    v1.0.0.md                     ← release notes (created by /agile-dev:release)
releases/                         ← runnable release artifacts (binaries / images / jars) — usually .gitignored
  v1.0.0/
    <artifact-files>              ← the actual built artifact(s)
    RUN.md                        ← run instructions copied from architecture
    MANIFEST.txt                  ← sha256 of every file in this dir
dist/                             ← per-iteration runnable artifacts (created when policy.packaging=each) — .gitignored
  001-<epic-slug>/
    <artifact-files>              ← runnable build of iteration 001
  changes/
    <change-slug>/                ← /agile-dev:change outputs
      change-state.md
      spec.md
      tasks.md
      test-plan.md
      retro.md
CHANGELOG.md                      ← root of project; appended at iteration close
```

These files are yours — you can read, edit, and commit them alongside your code.

The pipeline also generates `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, and `.claude/settings.json` during the Environment phase, so all subsequent work runs inside a reproducible container.

### Feeding pipeline issues back

`pipeline-feedback.md` is the place to capture **meta-feedback about the pipeline tool itself** — things like ambiguous prompts, awkward orchestration, generated files that needed manual fixup, or surprising checkpoint behaviour. It is project-agnostic: anything project-specific stays in the per-iteration `i7-retro.md`. The Retrospective phase prompts for it once per iteration and appends entries automatically when there is something to record. To turn the file into pipeline improvements, open Claude Code in the `agile-dev-pipeline` repo, run `/agile-dev:improve` (or paste the file directly), and the entries become epics in the pipeline's own backlog. Larger architectural proposals that aren't ready for implementation live in `IDEAS.md` at this repo's root.

---

## FAQ

**What is `policy.md` and how do I change it?**
A markdown file at `.project-artifacts/policy.md` holding three project-wide settings: `autonomy`, `detail`, and `test_coverage`. Set once during the first foundation command (Step 0.5). To change later, open the file and edit the values directly — the orchestrator reads it at the start of every `/agile-dev:iterate` and `/agile-dev:change` session. There's no slash command for editing; hand-edit is intentional, since policy changes are rare and a deliberate decision.

**What happens if I run `/agile-dev:start` or `/agile-dev:improve` on a project that already has artifacts?**

Five cases, handled explicitly in Step 1b (start) / Step 2b (improve):

- **Truly fresh** (no `state.md`, no foundation artifacts) — runs from the first foundation phase.
- **Orphaned artifacts** (no `state.md` but foundation artifacts exist — manual setup, prior failed run, or migration) — the pipeline stops and asks: reconstruct `state.md` from what exists and resume; archive everything and start fresh; or cancel.
- **Foundation in progress** (some foundation phases ✓, others not) — resumes from the marked `current_phase`. Existing ✓ artifacts are the base; the pending phase is what runs. No silent overwrites.
- **Foundation complete, iteration in flight** — refuses. Points you at `/agile-dev:iterate` (continue), `/agile-dev:revise <phase>` (targeted foundation change), or abandon-and-restart.
- **Foundation complete, project at rest** (`current_phase: Idle`) — treats it as a major pivot. After explicit confirmation, MOVES (not copies) all existing project artifacts (`state.md`, `f1/f2/f3`, `iterations/`, `releases/`, `changes/`) into `.project-artifacts/archive/<YYYY-MM-DD-HHMMSS>/` as project history, writes an `archive-reason.md` note, then begins a fresh Foundation. `policy.md` and `pipeline-feedback.md` stay in place. Old work is never lost — it lives in `archive/` and you can browse or restore it.

So: existing artifacts are never silently overwritten. Either they're preserved in place (resume), reconstructed into state (orphans → reconstruct), or moved to `archive/` as history (major pivot or orphans → archive).

**How many epics per iteration? Why does the pipeline sometimes bundle several?**

The `iteration_size` policy sets a points budget for each iteration (default = XL = 9 points, scaling as √3 across t-shirt sizes). The bundler picks unblocked TODO epics from the backlog in priority order, accumulating until the sum is as close to the budget as possible. So a single XL epic is one iteration; two L epics together (10.4 pts) is also one iteration; three M epics (9 pts) is one iteration. Aim: less time spent on approvals, more work per pause. Dependencies are respected — a dependent epic won't bundle until its blocker is DONE. Smaller iterations (`m`, `l`) give tighter feedback loops; larger (`xxl`) give longer focused stretches. Edit `policy.md` to change anytime.

**What is a "slug"?**

A short, filename-friendly identifier derived from a longer name: lowercase, hyphens for spaces, no special characters. The pipeline uses slugs in directory paths: `iterations/001-user-authentication/`, `changes/add-csv-export/`. For a multi-epic iteration the slug is the first (highest-priority) epic's slug — so a bundle led by "Search Index" lives at `iterations/002-search-index/`.

**What if I want different policies for different iterations?**
Not supported in v1. Policy is project-wide. The workaround is to change `policy.md` between iterations and accept that you'll need to remember to switch it back. If per-iteration override becomes common, it's a future enhancement.

**Where does the runnable app end up?**
At Integration close, the pipeline writes the packaged deliverable to `dist/<NNN>-<slug>/` in your project root — accessible directly from the host through the dev-container bind mount. The directory contains the artifact itself (binary, jar, docker image tarball, etc.) plus run instructions copied from `f2-architecture.md`. Copy that directory to any machine that meets the runtime requirements (e.g. has a JVM if the deliverable is a jar) and you can run the app without checking out code or installing build tools. At `/agile-dev:release` boundaries, the same artifact is copied to `releases/v<version>/` with a `MANIFEST.txt` of sha256 hashes for verification.

**Why is the production Dockerfile separate from `.devcontainer/Dockerfile`?**
The dev container has Claude Code, build toolchains, language compilers, debuggers — everything you need to develop, but bloated for shipping. The project-root `Dockerfile` (generated by Environment when the deliverable type is `docker-image`) is multi-stage: a build stage that uses heavyweight tools, and a slim runtime stage (e.g. `distroless`, `alpine`) that contains only what the running app actually needs. The result is a small, secure image ready for production.

**Cross-platform builds — do they work?**
Depends on the stack. Architecture's "target platforms" list drives this. Go and Rust cross-compile cleanly from one host. JVM and Node bytecode/JS run anywhere the runtime is installed, so a single artifact covers all platforms. Native C/C++ is the hardest case — Environment may produce only the native-architecture artifact and write a `BUILDING-OTHER-PLATFORMS.md` note in `dist/` explaining how to build the others. Platform-installer types (`.dmg`, `.msi`, `.deb`) usually require building on the target platform.

**Can I disable tests entirely for a quick prototype?**
Yes — set `test_coverage: none` in `.project-artifacts/policy.md`. The pipeline skips Test Plan and Verification phases entirely. Manual smoke at Integration becomes the only quality gate, and the Definition of Done adapts (`definitions.md` describes the changes). Combining this with `autonomy: ai-driven` triggers a confirmation prompt because you're removing both human approval and automated test gates — appropriate only for throwaway code.

**Why am I being prompted for plugin files even though Step 0 added a permission rule?**
Two reasons depending on when the prompt fires.
First-session quirk — Step 0 writes the rule to `~/.claude/settings.json` mid-session, but Claude Code reads that file once at session start. So the running session still has the old in-memory permission set and may prompt for the first few plugin files. From the next session onwards the rule is loaded at startup and the path is silently allowed.
Intermittent harness misses — even with the rule loaded correctly, Claude Code's permission matcher occasionally fails to recognise a covered path on a transient read. This is a known harness behaviour, not a plugin or rule-syntax problem. Approving the prompt is harmless. If it gets noisy or repeats, file a `/feedback` report inside Claude Code with the specific path and the rule from your settings.

**Do I really need to be in a git repository?**
Yes. The pipeline relies on git for commits, history, CHANGELOG entries, and mid-iteration recovery. `/agile-dev:start` will offer to `git init` if your directory isn't a repo yet. `/agile-dev:improve` and `/agile-dev:change` will warn and ask, because a non-git existing codebase usually means you're in the wrong directory.

**The Environment phase wants me to "Reopen in Container" — what is that?**
After Backlog approval, the pipeline generates `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, and `.claude/settings.json`. In VS Code, press `Cmd+Shift+P` → **Dev Containers: Reopen in Container**; Cursor and other container-aware editors have the same action. Claude restarts inside the container with all the right tools and permissions already wired up. From here on, all iteration work happens inside the container.

**How do I pause in the middle of an iteration?**
Close the Claude session at any approval checkpoint. `state.md` records where you are; the next `/agile-dev:iterate` resumes from the exact same phase.

**What is `state.md`?**
A markdown file at `.project-artifacts/state.md` tracking the current phase, the current epic, the backlog (with statuses), completed iterations, and releases. The pipeline reads it on every command. Run `/agile-dev:status` to see a human-readable summary at any time.

**What is `pipeline-feedback.md`?**
A separate file at `.project-artifacts/pipeline-feedback.md` capturing **meta-feedback about the pipeline tool itself** (not your project). The Retrospective phase prompts for it once per iteration and appends an entry if there's anything to record. To turn the file into pipeline improvements, open Claude Code in the `agile-dev-pipeline` repo and run `/agile-dev:improve` against it.

**Something went wrong mid-iteration — how do I recover?**
The pipeline has three tiers:
1. **Loop back** — re-run a single phase that produced wrong output. Small fix, no work lost.
2. **Split** — close the partial work as iteration N-A and replan the rest as N-B. Use when half the spec was wrong but what shipped is keepable.
3. **Abandon** — record why and reset. Use when nothing is salvageable.
Claude offers the appropriate tier when defects surface; you confirm.

**A Retrospective said Architecture needs revising. Now what?**
Run `/agile-dev:revise <phase>` (where `<phase>` is `vision`, `architecture`, or `backlog`). It redoes that foundation phase and cascades changes downstream. Only allowed at `Idle` (between iterations) and only when the Retrospective explicitly flagged it.

**When do I run `/agile-dev:release`?**
At a milestone — MVP done, public release, end of a stable batch. It bundles all iterations closed since the last release into a versioned release note (`releases/v<version>.md`), tags the CHANGELOG, and bumps the `version` field in `state.md`. Releases are explicit, not automatic per iteration.

**Can I redo a phase I've already approved?**
Yes. Edit `state.md` to set `current_phase` back to the phase you want to redo, then run `/agile-dev:iterate`. For a clean approach, use the **Tier 1 — Loop back** recovery flow described above; the pipeline will re-run the phase and re-checkpoint.

**Can I run the pipeline without the dev container?**
Not recommended. Foundation phases (Vision / Architecture / Backlog) run on the host fine — they only write markdown. But everything from Refinement onwards expects the container's permissions and tools to be in place. Skipping the container means you'll be prompted to approve every shell command Claude runs, and the generated `.claude/settings.json` allowlists won't match the host's tooling.

**Where do I report bugs or request features in the pipeline itself?**
Capture them in your project's `pipeline-feedback.md` during normal use (the Retrospective phase will prompt). For deliberate reports, open an issue at https://github.com/mateuszgruszczynski/agile-dev-pipeline.

---

## What the pipeline does not do

- It does not push code, open pull requests, or deploy anything without your explicit instruction.
- It does not skip checkpoints — every plan and spec requires your approval before implementation begins.
- It does not make architectural decisions unilaterally — proposals always go through the Architecture phase with your review.

---

## Repository layout

For contributors or anyone curious about the plugin internals:

```
agile-dev-pipeline/
  .claude-plugin/
    plugin.json                   ← plugin manifest
    marketplace.json              ← marketplace listing (this repo serves as its own marketplace)
  commands/
    start.md
    improve.md
    change.md
    iterate.md
    status.md
    release.md
    revise.md
  pipeline/
    analysis.md
    vision.md
    architecture.md
    backlog.md
    environment.md
    refinement.md
    decomposition.md
    test-plan.md
    development.md
    verification.md
    integration.md
    retrospective.md
    definitions.md                ← Definition of Ready / Testability / Done
```

The commands reference phase definitions via `${CLAUDE_PLUGIN_ROOT}/pipeline/<phase>.md`.

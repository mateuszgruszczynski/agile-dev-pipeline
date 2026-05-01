# Analysis Phase

*Existing codebase entry point — loaded by `/agile-dev:improve`.*

**Purpose:** Before defining anything, understand what already exists. Produce an objective picture of the current system so that Vision, Architecture, and Backlog can describe *changes* rather than starting from zero.

**What to analyse:**
- **Structure** — directory layout, modules, packages, key entry points
- **Tech stack** — languages, frameworks, libraries, runtime versions (read from dependency files: package.json, go.mod, requirements.txt, pom.xml, etc.)
- **Architecture** — reverse-engineer a C4 Context + Container diagram from what exists; identify components, their responsibilities, and how they communicate
- **Test coverage** — what test types exist, rough coverage level, obvious gaps
- **Data model** — schemas, migrations, key entities (if applicable)
- **External integrations** — APIs called, services depended on, protocols used
- **Known issues** — TODO/FIXME comments in code, open issues if a tracker is accessible, obvious code smells
- **CI/CD** — what pipelines exist, how the project is built and deployed

**How to do it:**
- Read the codebase using available tools — do not ask the user to explain code that can be read directly
- Ask the user only for things that cannot be determined from the code: business context, undocumented design decisions, known pain points, what prompted the improvement request
- **Use subagents** for parallel exploration of unrelated parts of the codebase (e.g. one subagent per top-level module). Merge their findings into a single coherent analysis before the checkpoint.

**Output:**
- Current tech stack summary
- C4 Context diagram (Mermaid) — system and its external actors
- C4 Container diagram (Mermaid) — major components and their relationships
- Test coverage summary (types present, estimated coverage, gaps)
- Known issues and tech debt list
- External integrations list

**⛳ CHECKPOINT Analysis:** User reviews the analysis. Correct any misunderstandings before proceeding — errors here will propagate into Vision and Architecture.

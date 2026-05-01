# Environment Readiness Check Phase

**Purpose:** Generate a dev container configuration tailored to this project's tech stack. Foundation phases run on the host — they produce only markdown and need no dev tools. Everything from Refinement onwards runs inside this container, where Claude has the permissions needed to build, test, and run the application without prompting for every command.

**When to run:** Once, after Backlog is approved. Produces three files, then pauses for the user to reopen the project inside the container.

---

## Step 1 — Read the stack

Read `.project-artifacts/f2-architecture.md`. Extract:
- Primary language runtime(s) and required version(s)
- Build tools (npm, maven, gradle, pip, cargo, etc.)
- Whether Docker is needed (containerised app, Testcontainers, Docker Compose for local services)
- Any additional CLI tools needed for testing or deployment
- **App type** — specifically whether this is a **native GUI desktop app** (egui, Qt, GTK, wxWidgets, Swift/AppKit, Win32, etc.)

If the app type is native GUI: flag the project as **hybrid mode**. The dev container handles all build and test steps; running the application for demo and manual smoke testing happens on the host machine.

---

## Step 2 — Generate `.devcontainer/Dockerfile`

Use `mcr.microsoft.com/devcontainers/base:ubuntu-24.04` as the base. Add only the tools required by this project's stack. Always install Claude Code so the pipeline can continue inside the container.

Tool installation reference — include only what the stack needs:

| Stack | Dockerfile snippet |
|---|---|
| Node.js / npm | `RUN curl -fsSL https://deb.nodesource.com/setup_<version>.x \| bash - && apt-get install -y nodejs` |
| Java (OpenJDK) | `RUN apt-get install -y openjdk-<version>-jdk` |
| Maven | `RUN apt-get install -y maven` |
| Gradle | `RUN apt-get install -y gradle` |
| Python | `RUN apt-get install -y python3 python3-pip python3-venv` |
| Go | `RUN apt-get install -y golang-go` |
| Rust | `RUN curl https://sh.rustup.rs -sSf \| sh -s -- -y && echo 'source $HOME/.cargo/env' >> ~/.bashrc` |
| .NET / C# | `RUN apt-get install -y dotnet-sdk-<version>` (after adding Microsoft package feed) |
| Ruby | `RUN apt-get install -y ruby-full` |
| Docker CLI | `RUN apt-get install -y docker.io` |

Always append at the end:
```dockerfile
RUN npm install -g @anthropic-ai/claude-code
```

---

## Step 3 — Generate `.devcontainer/devcontainer.json`

```json
{
  "name": "<project-slug>-dev",
  "build": { "dockerfile": "Dockerfile" },
  "mounts": [
    "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
  ],
  "remoteEnv": {
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}"
  },
  "customizations": {
    "vscode": {
      "extensions": ["anthropic.claude-code"]
    }
  }
}
```

Include the Docker socket mount only if the stack uses Docker. The `ANTHROPIC_API_KEY` passthrough makes Claude Code work inside the container without baking the key into the image.

---

## Step 4 — Generate `.claude/settings.json`

Generate a project-level Claude Code settings file with an allowlist scoped to this project's stack.

Always include the base allowlist:

```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(ls *)", "Bash(find *)", "Bash(grep *)",
      "Bash(cat *)", "Bash(head *)", "Bash(tail *)",
      "Bash(mkdir *)", "Bash(cp *)", "Bash(mv *)", "Bash(rm *)",
      "Bash(chmod *)", "Bash(touch *)", "Bash(echo *)",
      "Bash(curl *)", "Bash(wget *)", "Bash(env)", "Bash(which *)",
      "Bash(apt-get *)", "Bash(apt *)"
    ],
    "deny": []
  }
}
```

Add stack-specific entries on top:

| Stack | Additional entries |
|---|---|
| Node.js / npm | `"Bash(npm *)"`, `"Bash(npx *)"`, `"Bash(node *)"` |
| TypeScript | `"Bash(tsc *)"` |
| Java | `"Bash(java *)"`, `"Bash(javac *)"` |
| Maven | `"Bash(mvn *)"`, `"Bash(./mvnw *)"` |
| Gradle | `"Bash(gradle *)"`, `"Bash(./gradlew *)"` |
| Python | `"Bash(python3 *)"`, `"Bash(pip3 *)"`, `"Bash(pytest *)"` |
| Go | `"Bash(go *)"` |
| Rust | `"Bash(cargo *)"`, `"Bash(rustc *)"` |
| .NET / C# | `"Bash(dotnet *)"` |
| Ruby | `"Bash(ruby *)"`, `"Bash(bundle *)"`, `"Bash(rake *)"` |
| Docker | `"Bash(docker *)"`, `"Bash(docker compose *)"` |

---

## Step 5 — Present and instruct

Show the three generated files to the user. Then say:

> The dev container is ready. To continue:
> - **VS Code:** press `Cmd+Shift+P` → **Dev Containers: Reopen in Container**
> - **Cursor / other editors:** use the equivalent "Reopen in Container" action
>
> Once inside the container, run `/agile-dev:iterate` to begin the first iteration phase.

**If hybrid mode (native GUI app):** also tell the user:

> This project uses a native GUI framework. The container handles all build, test, and lint steps. To run the application for the smoke test, use the host directly.
>
> On your host machine, allow the run command in Claude Code settings via `/update-config`, or add it manually to `~/.claude/settings.json`:
> ```json
> { "permissions": { "allow": ["Bash(cargo run *)"] } }
> ```

**⛳ CHECKPOINT Environment:** User confirms they are running inside the container. Record as `Environment ✓` in `state.md`.

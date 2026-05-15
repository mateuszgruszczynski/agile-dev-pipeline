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

# Container-only Claude Code settings — broader permissions that NEVER touch
# the host's ~/.claude/settings.json. The container is sandboxed, so allowing
# any Bash command and any directory is acceptable here even though it would
# not be on the host.
USER vscode
RUN mkdir -p /home/vscode/.claude && cat > /home/vscode/.claude/settings.json <<'JSON'
{
  "permissions": {
    "allow": [
      "Bash(*)",
      "Read(/**)", "Write(/**)", "Edit(/**)",
      "Read(/home/vscode/.claude/plugins/**)"
    ],
    "additionalDirectories": ["/"]
  },
  "extraKnownMarketplaces": {
    "agile-dev": {
      "source": { "source": "github", "repo": "mateuszgruszczynski/agile-dev-pipeline" }
    }
  },
  "enabledPlugins": {
    "agile-dev@agile-dev": true
  }
}
JSON
USER root
```

The explicit `Read(/home/vscode/.claude/plugins/**)` is required even though `Read(/**)` is also listed: Claude Code's permission matcher inconsistently honours the broad `/**` rule when the actual read target is the plugin install dir. Same behaviour observed on host (where a `Read(/Users/<user>/.claude/plugins/cache/agile-dev/**)` rule is needed despite any broader rules). Listing both keeps the broad rule for general filesystem access and the narrow rule for the specific path that gets misses.

The bake of `extraKnownMarketplaces` and `enabledPlugins` registers the marketplace and marks the plugin as enabled. Actual plugin code is installed at container creation time via `postCreateCommand` in `devcontainer.json` (Step 3). If the user wants additional plugins available inside the container, they edit this baked block AND add the install to `postCreateCommand`.

---

## Step 3 — Generate `.devcontainer/devcontainer.json`

```json
{
  "name": "<project-slug>-dev",
  "build": { "dockerfile": "Dockerfile" },
  "remoteUser": "vscode",
  "mounts": [
    "source=${localEnv:HOME}/.claude.json,target=/home/vscode/.claude.json,type=bind,consistency=cached",
    "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
  ],
  "remoteEnv": {
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}"
  },
  "postCreateCommand": "claude plugin marketplace add mateuszgruszczynski/agile-dev-pipeline 2>/dev/null; claude plugin install agile-dev@agile-dev",
  "customizations": {
    "vscode": {
      "extensions": ["anthropic.claude-code"]
    }
  }
}
```

Only the auth file is bind-mounted:
- `~/.claude.json` — OAuth tokens + MCP configs + per-project trust. Sharing this means no re-authentication after Reopen in Container.

**Do not bind-mount `~/.claude/plugins/`.** Claude Code's plugin registry files (`installed_plugins.json`, `known_marketplaces.json`) store absolute host paths — they break inside the container's Linux filesystem and the plugin fails to load. The container manages its own plugin install at container creation time via `postCreateCommand` (above), which runs once per container build and installs `agile-dev` directly from GitHub into the container's own `~/.claude/plugins/` with correct container-local paths. Step 2's baked `~/.claude/settings.json` (with `extraKnownMarketplaces` + `enabledPlugins`) is also still in place, so even if `postCreateCommand` runs second the marketplace is already registered.

The `2>/dev/null` on the first command swallows errors from re-adding an already-registered marketplace (which the bake in Step 2 may have done). The install command is idempotent.

Not shared: host `~/.claude/settings.json` (so the container's broad `Bash(*)` allowlist doesn't bleed onto the host), and conversation history (`projects/`, `sessions/`, `history.jsonl`).

Notes:
- Windows hosts (no WSL): use `${localEnv:USERPROFILE}` instead of `${localEnv:HOME}`.
- `remoteUser: vscode` must match the target path `/home/vscode/.claude/...`. Do not change one without the other.
- Linux host with non-1000 UID: may need `containerUser` / `updateRemoteUserUID` to make the auth bind mount writable.
- Include the Docker socket mount only if the stack uses Docker.
- `ANTHROPIC_API_KEY` passthrough is a fallback for API-key auth users; OAuth users get auth from the mounted `~/.claude.json`.

---

## Step 4 — Generate project `.claude/settings.json`

This is a separate file from the container's `/home/vscode/.claude/settings.json` baked in Step 2. The project-level file lives at the workspace root, applies whenever the project is opened (host **or** container), and carries the conservative per-stack allowlist. The container also gets the broader `Bash(*)` from Step 2; on the host, only this project-level file applies. Both exist on purpose.

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

Detect the user's editor before presenting instructions. Run:

```bash
echo "TERM_PROGRAM=$TERM_PROGRAM"
```

Map the value to a specific instruction:

| `TERM_PROGRAM` | Editor | Reopen action |
|---|---|---|
| `vscode` | VS Code or Cursor (Cursor is a VS Code fork; same env var) | macOS: `Cmd+Shift+P` → **Dev Containers: Reopen in Container**. Linux/Windows: `Ctrl+Shift+P` → same. |
| `JetBrains-JediTerm` | IntelliJ family (IDEA / PyCharm / WebStorm / GoLand / RustRover / …) | Right-click `.devcontainer/devcontainer.json` → **Dev Containers** → **Create Dev Container and Mount Sources**. Alternatively use the JetBrains Gateway plugin. |
| `WarpTerminal` / `Apple_Terminal` / `iTerm.app` / empty | Standalone terminal (not running inside a container-aware editor) | Open the project in VS Code or Cursor first, then use the VS Code / Cursor action above. |

Show the three generated files, then present the matching instruction.

After the user confirms they are inside the container, also tell them:

> The `postCreateCommand` in `devcontainer.json` should have already installed the `agile-dev` plugin during container creation. Verify with `/plugin list` — `agile-dev` should be listed. Then run `/agile-dev:iterate` to start the first iteration.
>
> **Recovery (only if `/plugin list` does not show `agile-dev`)** — the postCreate install failed (network issue at creation time, or Claude CLI not yet available). Run manually:
> ```
> /plugin marketplace add mateuszgruszczynski/agile-dev-pipeline
> /plugin install agile-dev@agile-dev
> ```

**If hybrid mode (native GUI app):** also tell the user:

> This project uses a native GUI framework. The container handles all build, test, and lint steps. To run the application for the smoke test, use the host directly.
>
> On your host machine, allow the run command in Claude Code settings via `/update-config`, or add it manually to `~/.claude/settings.json`:
> ```json
> { "permissions": { "allow": ["Bash(cargo run *)"] } }
> ```

**⛳ CHECKPOINT Environment:** User confirms they are running inside the container. Record as `Environment ✓` in `state.md`.

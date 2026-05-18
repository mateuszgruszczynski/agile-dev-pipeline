# Environment Readiness Check Phase

**Purpose:** Prepare the project's build, test, and run infrastructure. Produces a production build recipe (always) and optionally a dev container configuration when the stack requires it. Foundation phases run on the host; iteration phases also run on the host by default — a dev container is opt-in, not mandatory.

**When to run:** Once, after Backlog is approved.

---

## Step 1 — Read the stack

Read `.project-artifacts/f2-architecture.md`. Extract:
- Primary language runtime(s) and required version(s)
- Build tools (npm, maven, gradle, pip, cargo, etc.)
- Whether Docker is needed (containerised app, Testcontainers, Docker Compose for local services)
- Any additional CLI tools needed for testing or deployment
- **App type** — specifically whether this is a **native GUI desktop app** (egui, Qt, GTK, wxWidgets, Swift/AppKit, Win32, etc.)
- **Out-of-process test requirements** — whether Verification needs Docker for Testcontainers or docker-compose service stacks

If the app type is native GUI: flag the project as **hybrid mode** — build and test in any environment, run the app on the host for demo and manual smoke.

---

## Step 2 — Generate the production build recipe

Generate the recipe that Integration will use to produce the deployable artifact. Separate from any dev container — this recipe must produce a slim, runnable output for the target environment.

Choose the right template based on the **Deliverable artifact** decision in `f2-architecture.md`:

| Deliverable type | Recipe to generate | Output location |
|---|---|---|
| `docker-image` | Project-root `Dockerfile` (multi-stage: build stage has dev tools; final stage is slim runtime — `alpine`, `distroless`, or `slim` variant). Also `.dockerignore`. | `dist/<NNN>-<slug>/image.tar.gz` |
| `native-binary` | `build.sh` running the language's static-build command (`go build -ldflags="-s -w"`, `cargo build --release`, etc.). For multiple target platforms, loop over them. | `dist/<NNN>-<slug>/<binary>-<platform>` |
| `jar` / `war` | `build.sh` running `mvn package` / `gradle build` producing a runnable JAR. | `dist/<NNN>-<slug>/<app>.jar` |
| `npm-bundle` | `build.sh` running the bundler (Vite / esbuild / webpack) and tarring the output. | `dist/<NNN>-<slug>/<app>-bundle.tar.gz` |
| `tarball` | `build.sh` compiling (if needed) then tarring the runnable directory. | `dist/<NNN>-<slug>/<app>.tar.gz` |
| `platform-installer` | `build.sh` invoking the platform packager (`pkg`, `wix`, `dpkg-deb`, `electron-builder`, etc.) for each target. | `dist/<NNN>-<slug>/<app>-<version>.<ext>` |
| `script` | `build.sh` bundling script + dependencies into a runnable archive (PyInstaller, shc, zipapp). | `dist/<NNN>-<slug>/<app>` |

**For `docker-image` projects:**

```dockerfile
# syntax=docker/dockerfile:1
FROM <build-base> AS build
WORKDIR /app
COPY . .
RUN <build commands>

FROM <runtime-base>
WORKDIR /app
COPY --from=build /app/<artifact> /app/
EXPOSE <port if applicable>
CMD ["./<entrypoint>"]
```

Runtime base per stack: Java → `eclipse-temurin:21-jre-alpine`, Go → `gcr.io/distroless/static`, Node → `node:20-alpine`, Python → `python:3.12-slim`.

**Cross-platform builds** (when Architecture lists multiple target platforms):
- Go: `GOOS=<os> GOARCH=<arch> go build` loop in `build.sh`.
- Rust: `cargo build --target <triple>` (requires `rustup target add <triple>`).
- JVM / Node / Python: same JAR / bundle runs everywhere — runtime requirement covers it.
- Native (C, C++): cross-compile via Zig or produce native-arch artifact + `BUILDING-OTHER-PLATFORMS.md`.

**Always:**
- Add `dist/` to `.gitignore`.
- Commit the recipe (`Dockerfile`, `build.sh`, build config additions) so the build is reproducible.

---

## Step 3 — Testcontainers and local services (when applicable)

If Verification will need real infrastructure (DB, Redis, Kafka, etc.) for out-of-process tests, document the approach:

- **Testcontainers** (preferred for per-test isolation): note the library for the project's language (`testcontainers-java`, `testcontainers-go`, `testcontainers-python`, `@testcontainers/testcontainers`, etc.). Verification phase uses this to spin up infra automatically during test runs — no persistent local service required.
- **docker-compose** (for stateful services or when Testcontainers isn't available): generate a `docker-compose.test.yml` at project root with only the services needed for Verification (not the app itself).
- **No Docker** (when the stack can use in-memory fakes or external services directly): note this explicitly.

This step produces documentation / config, not a running environment. Verification will actually start and stop containers.

---

## Step 4 — Dev container (optional)

A dev container is useful when:
- The stack requires a specific runtime version not easily installed on the host (e.g. obscure JDK, old Python)
- Multiple conflicting runtimes would pollute the host
- The team wants strict environment reproducibility

For most projects on common stacks (modern Node, Go, Rust, Python, Java), the host toolchain is sufficient and a dev container adds friction without benefit.

**Ask the user:**

> `Does this project need a dev container? Reasons to say yes: unusual runtime, conflicting versions, or you want full isolation. For most projects on standard stacks, no is the right answer. (yes / no)`

**If no:** skip to Step 5.

**If yes:** generate the following:

### Dockerfile (`.devcontainer/Dockerfile`)

Use `mcr.microsoft.com/devcontainers/base:ubuntu-24.04` as the base. Add only the tools required by this project's stack.

Tool installation reference — include only what the stack needs:

| Stack | Dockerfile snippet |
|---|---|
| Node.js / npm | `RUN curl -fsSL https://deb.nodesource.com/setup_<version>.x \| bash - && apt-get install -y nodejs` |
| Java (OpenJDK) | `RUN apt-get install -y openjdk-<version>-jdk` |
| Maven | `RUN apt-get install -y maven` |
| Python | `RUN apt-get install -y python3 python3-pip python3-venv` |
| Go | `RUN apt-get install -y golang-go` |
| Rust | `RUN curl https://sh.rustup.rs -sSf \| sh -s -- -y && echo 'source $HOME/.cargo/env' >> ~/.bashrc` |
| .NET / C# | `RUN apt-get install -y dotnet-sdk-<version>` |
| Ruby | `RUN apt-get install -y ruby-full` |
| Docker CLI | `RUN apt-get install -y docker.io` |

Always append at the end:
```dockerfile
RUN npm install -g @anthropic-ai/claude-code

USER vscode
RUN mkdir -p /home/vscode/.claude && cat > /home/vscode/.claude/settings.json <<'JSON'
{
  "permissions": {
    "allow": ["Bash(*)", "Read(/**)", "Write(/**)", "Edit(/**)", "Read(/home/vscode/.claude/plugins/**)"],
    "additionalDirectories": ["/"]
  },
  "extraKnownMarketplaces": {
    "agile-dev": {
      "source": { "source": "github", "repo": "mateuszgruszczynski/agile-dev-pipeline" }
    }
  },
  "enabledPlugins": { "agile-dev@agile-dev": true }
}
JSON
USER root
```

### devcontainer.json (`.devcontainer/devcontainer.json`)

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

Notes:
- Only `~/.claude.json` is bind-mounted (auth tokens). Do not bind-mount `~/.claude/plugins/` — plugin registry files contain host-absolute paths that break in Linux containers.
- Include the Docker socket mount only if the stack uses Docker (Testcontainers, docker-compose, containerised app).
- Windows hosts: use `${localEnv:USERPROFILE}` instead of `${localEnv:HOME}`.

---

## Step 5 — Present and confirm

Present what was generated:
- Production build recipe (`Dockerfile` or `build.sh`) — always
- Testcontainers / docker-compose approach — if applicable
- Dev container files — if user chose yes in Step 4

**If dev container generated:**

Detect the user's editor:
```bash
echo "TERM_PROGRAM=$TERM_PROGRAM"
```

| `TERM_PROGRAM` | Reopen action |
|---|---|
| `vscode` / Cursor | `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Linux/Windows) → **Dev Containers: Reopen in Container** |
| `JetBrains-JediTerm` | Right-click `.devcontainer/devcontainer.json` → **Dev Containers → Create Dev Container and Mount Sources** |
| Other / empty | Open the project in VS Code / Cursor first, then use the VS Code action above |

After reopening, verify the plugin is installed: `/plugin list` should show `agile-dev`. If not, run:
```
/plugin marketplace add mateuszgruszczynski/agile-dev-pipeline
/plugin install agile-dev@agile-dev
```

**If hybrid mode (native GUI):** build and test inside the container; run the application on the host for demo and smoke testing.

**⛳ CHECKPOINT Environment:** User reviews build recipe and confirms the environment setup looks correct. Mark `Environment ✓` in `state.md`. Then say: "Environment ready. Run `/agile-dev:iterate` to start the first iteration."

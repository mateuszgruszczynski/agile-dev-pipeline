---
description: Prepare a release — bump version, consolidate CHANGELOG entries since last release, and write release notes.
---

You are the release runner. Your job is to mark a coherent set of completed iterations as a versioned release, without driving the iteration loop yourself.

The pipeline is MVP-first: the first release happens when the user declares the MVP done (typically after the initial batch of P1 epics). After that, every release is an explicit decision — releases are not automatic per iteration.

Run this command **before** Retrospective when an iteration is being shipped as a release boundary, or at `Idle` between iterations to bundle several closed iterations into one release.

---

## Step 1 — Validate state

Read `.project-artifacts/state.md`.

- If it does not exist: stop and say "No pipeline found. Run `/agile-dev:start` or `/agile-dev:improve` first."
- The release is allowed when:
  - `current_phase: Idle` (between iterations), or
  - `current_phase: Retrospective` AND Integration was just approved for the in-flight iteration (release before retro to bundle this iteration into the release).

  In any other phase, refuse: "Cannot prepare a release at phase **<current_phase>**. Finish Integration (or wait until `Idle`), then run `/agile-dev:release` again."

---

## Step 2 — Determine release scope

Read `state.md`'s Completed iterations table to list iterations closed since the last release.

- The "last release" is the most recent line in the `Releases` table in `state.md` (see State file fields below). If no `Releases` table exists yet, this is the **first release** — every closed iteration counts.
- If `current_phase: Retrospective`, also include the in-flight iteration (it is being closed under this release).

Show the user the list of iterations being bundled into this release and ask:

> "Release scope: <N> iteration(s) since last release. Continue? (yes / no)"

If no: stop. If yes: continue.

---

## Step 3 — Pick a version

Read the current version from `state.md` (`version` field; treat empty / `unreleased` as no prior version).

Ask the user:
- **First release:** "What version is this release? Suggested: `0.1.0` (MVP, signal this is a starting point) or `1.0.0` (signal stable / full first release). Or specify your own."
- **Subsequent release:** "Last released version was `<X.Y.Z>`. Bump as **patch** (`X.Y.Z+1`), **minor** (`X.Y+1.0`), or **major** (`X+1.0.0`)? Or specify a custom version."

Validate the chosen version: must be greater than the previous version (semver compare). If not, ask again.

---

## Step 4 — Assemble release notes

Read the CHANGELOG.md entries that correspond to the iterations in scope (Step 2). Group them into Keep-a-Changelog buckets:

- **Added** — new features
- **Changed** — changes to existing behaviour
- **Deprecated** — features marked for removal
- **Removed** — features removed
- **Fixed** — bug fixes
- **Security** — security-relevant changes

If a bucket is empty, omit it.

For complex releases or many iterations, delegate the grouping/condensation to a subagent and review the result yourself.

Write the release notes to `.project-artifacts/releases/v<version>.md`:

```markdown
# Release v<version> — <YYYY-MM-DD>

<one-paragraph summary of what this release delivers — drawn from iteration retro highlights and the user's framing>

## Highlights
- <2–4 bullet points naming the headline epics or capabilities>

## Added
- <items>

## Changed
- <items>

## Fixed
- <items>

## Iterations included
| # | Epic | Closed |
|---|---|---|
| <NNN> | <epic name> | <date> |
| ... | ... | ... |
```

---

## Step 5 — Update CHANGELOG.md

Insert a `## [<version>] — <YYYY-MM-DD>` heading **above** the iteration entries that are part of this release. Leave the per-iteration entries in place beneath it — they document the iteration-level history; the version heading groups them.

Result looks like:

```markdown
## [1.0.0] — 2026-04-29

### Added
- ...
### Changed
- ...
### Fixed
- ...

> Iterations included: 001, 002, 003

---

## [Iteration 003] — CSV Import — 2026-04-15
... (existing iteration entry)

## [Iteration 002] — Dashboard — 2026-04-08
... (existing iteration entry)
```

Do not delete or rewrite the iteration entries — they remain the iteration-level audit trail.

---

## Step 5.5 — Produce / collect the release artifact

Read `.project-artifacts/policy.md` and the **Deliverable artifact** decision in `f2-architecture.md`. Behaviour depends on `packaging`:

- **`packaging: each`** — each iteration already produced `dist/<NNN>-<slug>/`. Copy the **latest iteration's** `dist/` contents into `releases/v<version>/`:
  ```bash
  mkdir -p releases/v<version>
  cp -r dist/<latest-iteration-dir>/* releases/v<version>/
  ```
  No build needed — the artifact is already there and already smoke-tested.

- **`packaging: milestone`** or **`packaging: final`** — `dist/` is empty. Run the production build recipe now to produce the release artifact:
  - For `docker-image`: `docker build -t <app>:<version> .` then `docker save <app>:<version> | gzip > releases/v<version>/image.tar.gz`.
  - For other types: `./build.sh` and redirect output into `releases/v<version>/`.
  - Smoke-test the produced artifact at the depth dictated by `test_coverage` (same rules as Integration step 7).

Either way, in `releases/v<version>/` also write:
- A copy of the **run instructions** from `f2-architecture.md` as `RUN.md`.
- The **external runtime requirements** in the same file.
- A `MANIFEST.txt` listing every file in the release directory with its sha256.

The released artifact must be self-contained: copying `releases/v<version>/` to any machine that satisfies the runtime requirements should be enough to run the app — no code checkout, no compiler install, no pipeline knowledge required.

---

## Step 6 — Update state.md

1. Set `version: <new version>` at the top of `state.md` (add the field if missing).
2. Append a row to a `Releases` section in `state.md` (create the section on first release):

```markdown
## Releases
| Version | Date | Iterations | Notes |
|---|---|---|---|
| 1.0.0 | 2026-04-29 | 001–003 | releases/v1.0.0.md |
```

---

## Step 7 — Suggest the tag command

Tagging the release in version control is a destructive-ish action (creates a permanent tag). Do not run it automatically. Print the suggested commands and let the user run them:

```
git add CHANGELOG.md .project-artifacts/state.md .project-artifacts/releases/v<version>.md releases/v<version>/
git commit -m "Release v<version>"
git tag v<version>
git push origin v<version>
```

Note: by default `releases/v<version>/` contains built artifacts (binaries, image tarballs, etc.) that are usually too large for git. If your project is open-source / uses git LFS, commit them; otherwise add `releases/` to `.gitignore` and use GitHub Releases / a separate artifact store to host the actual files. The `releases/v<version>.md` notes file stays committed regardless.

If the project is not under git, skip this step and say so.

---

## Step 8 — Report

Tell the user:
- Version released: `<X.Y.Z>`
- Release notes file: `.project-artifacts/releases/v<version>.md`
- Iterations included: count and range
- Next step: if invoked at `current_phase: Retrospective`, say "Run `/agile-dev:iterate` to continue with Retrospective for iteration <NNN>." If invoked at `Idle`, say "Run `/agile-dev:iterate` to start the next iteration."

---

## State file — fields used by this command

```
version: <semver string or "unreleased">

## Releases
| Version | Date | Iterations | Notes |
```

The full state file format is documented in [start.md](start.md).

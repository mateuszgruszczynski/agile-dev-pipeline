#!/usr/bin/env bash
# PreToolUse hook (matcher: Bash). Three jobs:
#   1. Deny dangerous commands (sudo, rm -rf /, global installs, ...) — permissionDecision: deny.
#   2. Auto-allow recognised dev tools (build/test/lint/format/git) — permissionDecision: allow, no prompt.
#   3. Gate `git commit`: run a fast unit-test subset; block on failure (exit 2), allow on pass.
# Anything not matched is left to the normal permission flow (exit 0, no output).
#
# Reads a JSON object on stdin: { tool_name, tool_input: { command } }.
# Policy lists live in guards.json next to this script.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARDS="$SCRIPT_DIR/guards.json"

INPUT=$(cat)

emit() { # $1 = allow|deny  $2 = reason
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"%s","permissionDecisionReason":"%s"}}\n' "$1" "$2"
}

# Pure decision: prints DENY\t<reason> | ALLOW | COMMIT | DEFER. No side effects.
DECISION=$(printf '%s' "$INPUT" | GUARDS="$GUARDS" python3 -c '
import sys, json, os, re

try:
    d = json.load(sys.stdin)
except Exception:
    print("DEFER"); sys.exit(0)

if d.get("tool_name") != "Bash":
    print("DEFER"); sys.exit(0)

cmd = (d.get("tool_input") or {}).get("command", "") or ""
if not cmd.strip():
    print("DEFER"); sys.exit(0)

try:
    cfg = json.load(open(os.environ["GUARDS"]))
except Exception:
    cfg = {}

# 1. Deny dangerous patterns first.
for pat in cfg.get("bash_deny", []):
    try:
        if re.search(pat, cmd):
            print("DENY\t" + pat); sys.exit(0)
    except re.error:
        continue

# 2. git commit (without --no-verify) -> test gate.
if re.search(r"(^|[;&|]\s*)git\s+commit\b", cmd) and "--no-verify" not in cmd:
    print("COMMIT"); sys.exit(0)

# 3. Allow recognised dev tools. Inspect the first token of every
#    &&/||/;/| separated segment; allow only if EVERY segment leads with an allowed tool.
allow = set(cfg.get("bash_allow_tools", []))
segments = re.split(r"(?:&&|\|\||;|\|)", cmd)
ok = True
saw = False
for seg in segments:
    seg = seg.strip()
    if not seg:
        continue
    saw = True
    # strip leading env-assignments like FOO=bar
    toks = seg.split()
    i = 0
    while i < len(toks) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[i]):
        i += 1
    if i >= len(toks):
        ok = False; break
    tool = toks[i]
    base = tool.split("/")[-1]            # cargo, npm, mvnw ...
    sub = toks[i + 1] if i + 1 < len(toks) else ""
    # Outward / state-changing actions stay on the normal approval flow.
    if base == "git" and sub == "push":
        ok = False; break
    if tool in allow or base in allow:
        continue
    ok = False; break

if saw and ok:
    print("ALLOW")
else:
    print("DEFER")
')

KIND=${DECISION%%$'\t'*}
REASON=${DECISION#*$'\t'}

case "$KIND" in
  DENY)
    emit deny "Blocked by agile-dev guard (pattern: ${REASON})"
    exit 0
    ;;
  ALLOW)
    emit allow "Recognised dev tool — auto-approved by agile-dev"
    exit 0
    ;;
  COMMIT)
    # Fast unit-test gate. Only a cheap subset — the full suite is enforced at Verification/Integration.
    run_fast_tests() {
      if [ -f "Cargo.toml" ]; then
        echo "cargo test --lib --quiet"; return 0
      elif [ -f "go.mod" ]; then
        echo "go test -short ./..."; return 0
      elif [ -f "package.json" ] && python3 -c "import json,sys; sys.exit(0 if 'test:unit' in (json.load(open('package.json')).get('scripts') or {}) else 1)" 2>/dev/null; then
        if   [ -f "pnpm-lock.yaml" ]; then echo "pnpm run test:unit"
        elif [ -f "yarn.lock" ];      then echo "yarn run test:unit"
        else echo "npm run test:unit"; fi
        return 0
      elif [ -f "pom.xml" ]; then
        echo "mvn -q -o test"; return 0
      elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
        echo "./gradlew test --offline -q"; return 0
      fi
      return 1
    }

    if RUNNER=$(run_fast_tests); then
      echo "▶ agile-dev: fast unit tests before commit ($RUNNER)..." >&2
      if eval "$RUNNER" >&2 2>&1; then
        emit allow "Fast unit tests passed"
        exit 0
      else
        echo "✗ BLOCKED: unit tests failed. Fix them, or commit with --no-verify to bypass." >&2
        exit 2
      fi
    else
      # No reliable fast subset for this stack — don't run the full suite on every commit.
      emit allow "No fast unit subset detected; full suite enforced at Verification/Integration"
      exit 0
    fi
    ;;
  *)
    exit 0   # DEFER — normal permission flow
    ;;
esac

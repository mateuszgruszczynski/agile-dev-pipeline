#!/usr/bin/env bash
# PreToolUse hook (matcher: Write|Edit).
#   1. Deny writes to credential/secret files — permissionDecision: deny.
#   2. Auto-allow writes inside the project directory — permissionDecision: allow, no prompt.
#   3. Defer everything else (system config, paths outside the project) to the normal flow.
#
# Reads a JSON object on stdin: { tool_name, cwd, tool_input: { file_path } }.
# Pattern lists live in guards.json next to this script.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARDS="$SCRIPT_DIR/guards.json"

INPUT=$(cat)

DECISION=$(printf '%s' "$INPUT" | GUARDS="$GUARDS" PROJ="${CLAUDE_PROJECT_DIR:-}" python3 -c '
import sys, json, os, re

try:
    d = json.load(sys.stdin)
except Exception:
    print("DEFER"); sys.exit(0)

if d.get("tool_name") not in ("Write", "Edit"):
    print("DEFER"); sys.exit(0)

fp = (d.get("tool_input") or {}).get("file_path", "") or ""
if not fp:
    print("DEFER"); sys.exit(0)

try:
    cfg = json.load(open(os.environ["GUARDS"]))
except Exception:
    cfg = {}

base = os.path.basename(fp)
for pat in cfg.get("write_block", []):
    try:
        if re.search(pat, fp):
            print("DENY\t" + base); sys.exit(0)
    except re.error:
        continue

for pat in cfg.get("write_warn", []):
    try:
        if re.search(pat, fp):
            print("DEFER"); sys.exit(0)   # let the user approve system-config writes
    except re.error:
        continue

# Resolve project root and decide containment.
proj = os.environ.get("PROJ") or d.get("cwd") or os.getcwd()
try:
    proj = os.path.realpath(proj)
    target = fp if os.path.isabs(fp) else os.path.join(d.get("cwd") or proj, fp)
    target = os.path.realpath(target)
    if target == proj or target.startswith(proj + os.sep):
        print("ALLOW"); sys.exit(0)
except Exception:
    pass

print("DEFER")
')

KIND=${DECISION%%$'\t'*}
REASON=${DECISION#*$'\t'}

emit() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"%s","permissionDecisionReason":"%s"}}\n' "$1" "$2"
}

case "$KIND" in
  DENY)
    emit deny "Writing to '${REASON}' is blocked — manage credential/secret files manually"
    exit 0
    ;;
  ALLOW)
    emit allow "In-project write — auto-approved by agile-dev"
    exit 0
    ;;
  *)
    exit 0   # DEFER
    ;;
esac

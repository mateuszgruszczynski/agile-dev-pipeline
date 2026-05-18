#!/usr/bin/env bash
# PreToolUse hook: blocks writes to credential/secret files.
# Receives a JSON object on stdin with keys: tool_name, tool_input.

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_name', ''))
" 2>/dev/null)

# Only guard Write and Edit
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
  exit 0
fi

FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
inp = d.get('tool_input', {})
print(inp.get('file_path', ''))
" 2>/dev/null)

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Block: credential / secret files
BLOCK_PATTERNS=(
  '\.env$'
  '\.env\.'
  '\.pem$'
  '\.key$'
  '\.p12$'
  '\.pfx$'
  'credential'
  '\.token$'
  'secret\.json$'
  '\.secret$'
)

for pattern in "${BLOCK_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qE "$pattern"; then
    echo "BLOCKED: Writing to '$(basename "$FILE_PATH")' is not allowed — credential/secret files must be managed manually." >&2
    exit 2
  fi
done

# Warn: system config files (allow but notify)
WARN_PATTERNS=(
  '\.claude/settings\.json$'
  '\.gitconfig$'
  '\.bashrc$'
  '\.zshrc$'
  '\.ssh/'
)

for pattern in "${WARN_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qE "$pattern"; then
    echo "WARNING: Writing to system config '$(basename "$FILE_PATH")' — proceed only if intentional." >&2
    exit 0
  fi
done

exit 0

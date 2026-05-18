#!/usr/bin/env bash
# PreToolUse hook: runs the in-process test suite before git commit.
# Receives a JSON object on stdin with keys: tool_name, tool_input.
# Only acts when tool_input.command starts with "git commit".
# To bypass: use git commit --no-verify (or add --no-verify to the command).

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
inp = d.get('tool_input', {})
print(inp.get('command', ''))
" 2>/dev/null)

# Only intercept git commit commands
if ! echo "$COMMAND" | grep -qE '^git commit'; then
  exit 0
fi

# Honour --no-verify (user explicitly bypassing hooks)
if echo "$COMMAND" | grep -q '\-\-no-verify'; then
  exit 0
fi

# Detect test runner from project files in CWD
detect_runner() {
  if [ -f "package.json" ] && python3 -c "import json,sys; d=json.load(open('package.json')); sys.exit(0 if 'test' in d.get('scripts',{}) else 1)" 2>/dev/null; then
    echo "npm test"
  elif [ -f "go.mod" ]; then
    echo "go test ./..."
  elif [ -f "Cargo.toml" ]; then
    echo "cargo test"
  elif [ -f "pyproject.toml" ] || [ -f "pytest.ini" ] || [ -f "setup.cfg" ]; then
    echo "python -m pytest"
  elif [ -f "pom.xml" ]; then
    echo "mvn test -q"
  elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    echo "./gradlew test"
  elif [ -f "Gemfile" ]; then
    echo "bundle exec rspec"
  else
    echo ""
  fi
}

RUNNER=$(detect_runner)

if [ -z "$RUNNER" ]; then
  # No recognisable test runner — allow commit without checking
  exit 0
fi

echo "▶ Running tests before commit ($RUNNER)..." >&2

if eval "$RUNNER" 2>&1; then
  echo "✓ Tests passed — commit allowed." >&2
  exit 0
else
  echo "✗ BLOCKED: Tests failed. Fix failing tests or use 'git commit --no-verify' to bypass." >&2
  exit 2
fi

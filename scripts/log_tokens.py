#!/usr/bin/env python3
"""
Append one row to .project-artifacts/token-usage.md, computing the running
cumulative total. Used by start.md / improve.md / iterate.md / change.md's
"Token usage log" step so the orchestrator doesn't re-derive the running
tally and markdown formatting by hand at every phase boundary.

Usage:
  python3 log_tokens.py --file .project-artifacts/token-usage.md \
      --phase Refinement --context "Iteration 3 (CSV Import)" \
      --tokens 18200 --calls 4
"""
import argparse
import os
import re


HEADER = "| Phase | Context | Subagent tokens | Agent calls | Cumulative |\n"
SEP = "|---|---|---|---|---|\n"


def last_cumulative(path):
    if not os.path.exists(path):
        return 0
    rows = [l for l in open(path, encoding="utf-8") if l.strip().startswith("|")]
    data_rows = [r for r in rows if not re.match(r"^\|\s*-+\s*\|", r) and "Cumulative" not in r]
    if not data_rows:
        return 0
    last = data_rows[-1].strip().strip("|").split("|")
    try:
        return int(last[-1].strip().replace(",", ""))
    except ValueError:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--phase", required=True)
    ap.add_argument("--context", required=True)
    ap.add_argument("--tokens", required=True, type=int)
    ap.add_argument("--calls", required=True, type=int)
    args = ap.parse_args()

    prev = last_cumulative(args.file)
    cumulative = prev + args.tokens

    needs_header = not os.path.exists(args.file) or os.path.getsize(args.file) == 0
    with open(args.file, "a", encoding="utf-8") as f:
        if needs_header:
            f.write("# Token usage log\n\n")
            f.write(HEADER)
            f.write(SEP)
        f.write(f"| {args.phase} | {args.context} | {args.tokens} | {args.calls} | {cumulative} |\n")

    print(f"logged: {args.phase} · {args.context} · {args.tokens} tokens · cumulative {cumulative}")


if __name__ == "__main__":
    main()

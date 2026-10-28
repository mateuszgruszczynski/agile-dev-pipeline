#!/usr/bin/env python3
"""
Print the one-line checkpoint progress footer used throughout iterate.md:
  Progress: Iteration <N> · <current_epic> · <X>/<Y> epics done

Reads state.md directly so the orchestrator doesn't parse the Backlog table
and count DONE rows by hand at every checkpoint.

Usage:
  python3 checkpoint_footer.py --state .project-artifacts/state.md
"""
import argparse
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from bundle_select import parse_table  # reuse the same table parser


def field(text, name, default="?"):
    m = re.search(rf"^{name}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()

    text = open(args.state, encoding="utf-8").read()
    lines = text.splitlines()

    iteration = field(text, "iteration")
    current_epic = field(text, "current_epic", "none")

    rows = parse_table(lines, r"^##\s+Backlog\b")
    total = len(rows)
    done = sum(1 for r in rows if r.get("Status", "").strip().upper() == "DONE")

    print(f"Progress: Iteration {iteration} · {current_epic} · {done}/{total} epics done")


if __name__ == "__main__":
    main()

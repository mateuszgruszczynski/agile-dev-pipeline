#!/usr/bin/env python3
"""
Mechanical referential-integrity check over the Backlog table's dependency
graph: every "Depends on" / "needs-findings-from" token must name a real
epic ID, and the graph must be acyclic.

This is deliberately NARROWER than the "dependency cross-check" described in
pipeline/backlog.md — that check is semantic (does an AC's observable imply
an undeclared dependency, e.g. "a running UI" with no UI epic listed?) and
still needs a reader, not a parser. This script only catches the purely
structural subset: broken ID references and dependency cycles. Run it as a
cheap pre-pass before that semantic check, not as a replacement for it.

Usage:
  python3 backlog_integrity_check.py --state .project-artifacts/state.md
"""
import argparse
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from bundle_select import parse_table, parse_deps


def find_cycle(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    path = []

    def dfs(n):
        color[n] = GRAY
        path.append(n)
        for m in graph.get(n, []):
            if m not in color:
                continue  # unknown ref already reported separately
            if color[m] == GRAY:
                cyc_start = path.index(m)
                return path[cyc_start:] + [m]
            if color[m] == WHITE:
                result = dfs(m)
                if result:
                    return result
        path.pop()
        color[n] = BLACK
        return None

    for n in list(graph):
        if color[n] == WHITE:
            result = dfs(n)
            if result:
                return result
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()

    text = open(args.state, encoding="utf-8").read()
    rows = parse_table(text.splitlines(), r"^##\s+Backlog\b")

    ids = set()
    graph = {}
    broken_refs = []

    for r in rows:
        eid = r.get("ID", "").strip()
        if not eid:
            continue
        ids.add(eid)

    for r in rows:
        eid = r.get("ID", "").strip()
        if not eid:
            continue
        deps, needs_findings = parse_deps(r.get("Depends on", ""))
        graph[eid] = deps + needs_findings
        for d in deps + needs_findings:
            if d not in ids:
                broken_refs.append({"epic": eid, "missing_ref": d})

    cycle = find_cycle(graph)

    ok = not broken_refs and not cycle
    print(json.dumps({
        "ok": ok,
        "broken_refs": broken_refs,
        "cycle": cycle,
        "note": "structural check only — does not verify semantic AC-implied dependencies, see pipeline/backlog.md",
    }))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

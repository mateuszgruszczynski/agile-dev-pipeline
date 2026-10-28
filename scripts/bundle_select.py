#!/usr/bin/env python3
"""
Iteration bundle selection — implements the algorithm documented in
commands/iterate.md Step 2 ("Bundle selection algorithm"). That doc is the
spec; this script is the implementation. Keep them in sync if the algorithm
changes.

Reads the Backlog table and Releases table straight out of state.md so the
orchestrator doesn't have to re-derive the filter/order/greedy/re-check walk
by hand every iteration — it only needs to pass the budget and, optionally,
a forced epic list ($ARGUMENTS), then act on the JSON result.

Usage:
  python3 bundle_select.py --state .project-artifacts/state.md --budget 9.0
  python3 bundle_select.py --state .project-artifacts/state.md --budget 9.0 --force EP-3,EP-7
"""
import argparse
import json
import re
import sys

SIZE_POINTS = {"XS": 1.0, "S": 1.7, "M": 3.0, "L": 5.2, "XL": 9.0, "XXL": 15.6}


def parse_table(lines, heading_pat):
    """Find a '## <heading>' section and parse its first markdown pipe table."""
    start = None
    for i, line in enumerate(lines):
        if re.match(heading_pat, line.strip()):
            start = i
            break
    if start is None:
        return []
    header_idx = None
    for i in range(start + 1, len(lines)):
        if lines[i].strip().startswith("|"):
            header_idx = i
            break
        if lines[i].strip().startswith("## "):
            return []
    if header_idx is None:
        return []
    header = [c.strip() for c in lines[header_idx].strip().strip("|").split("|")]
    rows = []
    for i in range(header_idx + 2, len(lines)):  # +2 skips the |---|---| separator
        row = lines[i].strip()
        if not row.startswith("|"):
            break
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def load_state(path):
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    backlog = parse_table(lines, r"^##\s+Backlog\b")
    releases = parse_table(lines, r"^##\s+Releases\b")
    return backlog, releases


def parse_deps(cell):
    """'EP-1, needs-findings-from:EP-9' -> (['EP-1'], ['EP-9'])"""
    if not cell or cell.strip() in ("", "—", "-", "none", "None"):
        return [], []
    plain, needs_findings = [], []
    for tok in cell.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if tok.lower().startswith("needs-findings-from:"):
            needs_findings.append(tok.split(":", 1)[1].strip())
        else:
            plain.append(tok)
    return plain, needs_findings


def epic_points(size):
    return SIZE_POINTS.get(size.strip().upper(), None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--budget", required=True, type=float)
    ap.add_argument("--force", default=None, help="comma/plus-separated epic IDs or names from $ARGUMENTS")
    args = ap.parse_args()

    rows, releases = load_state(args.state)
    errors = []

    epics = {}
    order = []
    for idx, r in enumerate(rows):
        eid = r.get("ID", "").strip()
        if not eid:
            errors.append(f"Backlog row {idx} has no ID — skipped: {r}")
            continue
        points = epic_points(r.get("Size", ""))
        if points is None:
            errors.append(f"{eid}: unrecognised Size '{r.get('Size')}' — skipped")
            continue
        deps, needs_findings = parse_deps(r.get("Depends on", ""))
        epics[eid] = {
            "id": eid,
            "name": r.get("Epic", "").strip(),
            "priority": r.get("Priority", "").strip(),
            "size": r.get("Size", "").strip(),
            "points": points,
            "status": r.get("Status", "").strip().upper(),
            "slice": r.get("Slice", "").strip(),
            "depends_on": deps,
            "needs_findings_from": needs_findings,
            "submission_order": idx,
        }
        order.append(eid)

    mvp_released = len(releases) > 0

    def is_done(eid):
        return eid in epics and epics[eid]["status"] == "DONE"

    def needs_findings_blocked(e):
        return any(not is_done(t) for t in e["needs_findings_from"])

    # --- forced path ($ARGUMENTS) ---
    if args.force:
        forced_tokens = [t.strip() for t in re.split(r"[,+]", args.force) if t.strip()]
        bundle, bad = [], []
        for tok in forced_tokens:
            match = None
            if tok in epics:
                match = epics[tok]
            else:
                for e in epics.values():
                    if e["name"].lower() == tok.lower():
                        match = e
                        break
            if match is None:
                bad.append(tok)
                continue
            if match["status"] != "TODO":
                bad.append(f"{tok} (status={match['status']}, not TODO)")
                continue
            if needs_findings_blocked(match):
                bad.append(f"{tok} (blocked by needs-findings-from: {match['needs_findings_from']})")
                continue
            # dependency satisfied if DONE, or also present in this same forced bundle
            forced_ids = [epics[f]["id"] for f in forced_tokens if f in epics]
            unmet = [d for d in match["depends_on"] if not is_done(d) and d not in forced_ids]
            if unmet:
                bad.append(f"{tok} (unmet dependencies: {unmet})")
                continue
            bundle.append(match)
        if bad:
            print(json.dumps({"ok": False, "forced": True, "errors": bad + errors}))
            sys.exit(1)
        total = sum(e["points"] for e in bundle)
        print(json.dumps({
            "ok": True,
            "forced": True,
            "bundle": [{"id": e["id"], "name": e["name"], "size": e["size"], "points": e["points"], "priority": e["priority"]} for e in bundle],
            "total_points": round(total, 2),
            "budget": args.budget,
            "unambiguous": True,  # forced path never needs the ambiguity question — $ARGUMENTS is the explicit confirmation
            "errors": errors,
        }))
        return

    # --- step 1: candidates = TODO only ---
    candidates = [e for e in epics.values() if e["status"] == "TODO"]

    # --- step 2: filter unblocked (initial pool) + deferred-pre-MVP + needs-findings-from ---
    excluded_deferred = []
    excluded_needs_findings = []

    def independently_unblocked(e):
        return all(is_done(d) for d in e["depends_on"])

    pool = []
    for e in candidates:
        if needs_findings_blocked(e):
            excluded_needs_findings.append(e["id"])
            continue
        if e["slice"] == "Deferred" and not mvp_released:
            excluded_deferred.append(e["id"])
            continue
        if independently_unblocked(e):
            pool.append(e)

    # --- step 3: order — priority asc (P1 first), size desc, stable by submission order ---
    pr_rank = {"P1": 0, "P2": 1, "P3": 2}
    pool.sort(key=lambda e: (pr_rank.get(e["priority"], 9), -e["points"], e["submission_order"]))

    # --- step 4: greedy build, single-pass stop-on-first-fail ---
    bundle = []
    total = 0.0
    lone_oversized = False
    stopped_boundary = None  # first candidate that failed the closer-to-budget test
    for i, c in enumerate(pool):
        if not bundle:
            bundle.append(c)
            total += c["points"]
            if c["points"] > args.budget:
                lone_oversized = True
            continue
        stop_dev = abs(args.budget - total)
        add_dev = abs(args.budget - (total + c["points"]))
        if add_dev < stop_dev:
            bundle.append(c)
            total += c["points"]
        else:
            stopped_boundary = c
            break

    bundled_ids = {e["id"] for e in bundle}

    # --- re-check pool after each addition: chained dependents + needs-findings-from barrier ---
    changed = True
    while changed:
        changed = False
        for e in candidates:
            if e["id"] in bundled_ids:
                continue
            if needs_findings_blocked(e):
                continue  # hard barrier — never relaxed by bundling, only an actual DONE spike clears it
            if e["slice"] == "Deferred" and not mvp_released:
                continue
            unmet = [d for d in e["depends_on"] if not is_done(d) and d not in bundled_ids]
            if unmet:
                continue
            stop_dev = abs(args.budget - total)
            add_dev = abs(args.budget - (total + e["points"]))
            if add_dev < stop_dev:
                bundle.append(e)
                bundled_ids.add(e["id"])
                total += e["points"]
                changed = True

    # --- ambiguity check (step 5) ---
    unambiguous = True
    reason = None
    if lone_oversized:
        unambiguous = False
        reason = f"single epic {bundle[0]['id']} ({bundle[0]['size']}, {bundle[0]['points']}pt) exceeds budget on its own"
    elif stopped_boundary is not None:
        # tie = same priority + same size (hence identical points) as the boundary candidate
        tied = [c["id"] for c in pool
                if c["id"] != stopped_boundary["id"]
                and c["id"] not in bundled_ids
                and c["priority"] == stopped_boundary["priority"]
                and c["size"] == stopped_boundary["size"]]
        if tied:
            unambiguous = False
            reason = f"{stopped_boundary['id']} ties with {tied} at the same priority/size — arbitrary which one the margin picked"

    print(json.dumps({
        "ok": True,
        "forced": False,
        "bundle": [{"id": e["id"], "name": e["name"], "size": e["size"], "points": e["points"], "priority": e["priority"]} for e in bundle],
        "total_points": round(total, 2),
        "budget": args.budget,
        "unambiguous": unambiguous,
        "reason": reason,
        "excluded_deferred_pre_mvp": excluded_deferred,
        "excluded_needs_findings_from": excluded_needs_findings,
        "mvp_released": mvp_released,
        "errors": errors,
    }))


if __name__ == "__main__":
    main()

# Retrospective Phase

**Purpose:** Identify anything that requires a concrete change to the plan, process, or backlog. Keep it short and action-oriented — do not produce a narrative of what happened during the iteration.

**Rule: only document findings that lead to a concrete action.** If nothing needs to change, the output is: *"No plan changes. Proceed to next iteration."*

**What to review — only raise an item if it requires a change:**
- Are there backlog epics that need to be added, removed, split, re-prioritised, or re-scoped based on what was learned?
- Were any acceptance criteria unclear, wrong, or missing? If so: update the criteria and note the fix.
- Did any architectural decisions need to be revisited? If so: trigger a new Architecture checkpoint before the next iteration.
- Did any new risks, dependencies, or blockers surface that affect the backlog?
- Is any pipeline phase consistently producing too much or too little value — should the process be adjusted?

**Output:**
- A list of concrete changes only. Each item is an action: "Add epic X", "Split epic Y into Y1 and Y2", "Revise AC-3 on epic Z", "Revisit Architecture decision on database schema before next iteration".
- If no changes: one line — *"No plan changes. Proceed to next iteration."*

Do **not** include: what went well, what was difficult, effort commentary, or team feelings — unless they directly produce a backlog or process change that is recorded as an action item.

**⛳ CHECKPOINT Retrospective:** User reviews the action list and confirms backlog state before next iteration begins.

**Early-trigger paths:** Retrospective can be entered before Integration via the mid-iteration recovery rule. See *Mid-iteration recovery* in [iterate.md](../commands/iterate.md). Tier 2 splits the iteration into N-A (closed here, write retro now) and N-B (replanned remainder). Tier 3 abandons the iteration with a short retro recording the failure reason. In both cases keep the retro tight: only items that drive a concrete change.

---

## Iteration Transition

After Retrospective, the loop restarts:

1. Pull the next highest-priority epic from the approved backlog.
2. If backlog is empty → project is complete or enter maintenance mode.
3. If retro produced action items targeting Vision, Architecture, or Backlog: run `/agile-dev:revise <phase>` before the next iteration. Optional — only when retro flagged it. See [revise.md](../commands/revise.md).

```
Idle → Refinement → Decomposition → Test Plan → Development → Verification → Integration → Retrospective → Idle
```

Code Review and Validation are not separate phases — they are folded into Development as a self-applied checklist and a defined set of test policies. See [development.md](development.md). Verification owns the out-of-process tests (System-integration, E2E, out-of-process Contract); see [verification.md](verification.md).

## Release boundary

If the in-flight iteration is a release boundary (MVP done, milestone reached, or explicit decision), run `/agile-dev:release` **before** Retrospective. The release command bundles iterations since the last release into a versioned set with notes; Retrospective then runs as normal. Releases are MVP-first and explicit — they are not produced automatically per iteration. See [release.md](../commands/release.md).

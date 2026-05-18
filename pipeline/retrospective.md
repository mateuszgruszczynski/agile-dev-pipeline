# Retrospective Phase — Retired

The Retrospective phase has been removed. The iteration boundary is now handled inside Integration.

**What replaced it:**

After Integration's conditional checkpoint, the orchestrator asks a single question before closing the iteration:

> `Integration complete. Any backlog changes before the next iteration? (list changes or press enter to continue)`

If the user lists changes, the orchestrator applies them to `f3-backlog.md` and the Backlog table in `state.md`, then closes the iteration and proceeds. If the user presses enter, the iteration closes immediately and the next begins.

---

## Pipeline feedback capture (still active)

If you notice friction in the pipeline tool itself (ambiguous prompts, wrong checkpoint firing, generated files that needed manual fixup), append an entry to `.project-artifacts/pipeline-feedback.md` at any time:

```markdown
## <YYYY-MM-DD> · Iteration <NNN> · <short title>
**Phase / area:** <phase, command, or "general">
**What happened:** <1–2 sentences>
**Impact:** <why it was friction>
**Suggested change:** <if known>
```

No approval needed — informational only.

---
name: spec-driven-dev
description: >
  Spec-driven development: plan.md and tasks.md BEFORE writing code. Use PROACTIVELY
  whenever the user asks to add, implement, build, or create a feature, channel,
  provider, integration, endpoint group, module, or service - anything likely to touch
  3+ files or introduce a new component. Trigger phrases: "add a new X", "implement X",
  "let's add/build X", "plan this", "spec this out". Do NOT write feature code without
  the plan stage. Not for one-line fixes, typos, config tweaks, or questions.
---

# Spec-Driven Development

Core rule: **no production code before an approved spec.** For any non-trivial task,
follow this sequence and do not skip stages.

## Stage 1 — plan.md (the WHAT and WHY)

Create or update `docs/specs/<feature-name>/plan.md`:

```markdown
# <Feature name>

## Problem
One paragraph: what hurts today, for whom.

## Goal / Non-goals
Bullet each. Non-goals prevent scope creep — always include at least one.

## Design
- Architecture decision(s) and the alternative(s) rejected, with one-line reasons
- New/changed components (classes, endpoints, tables, queues) by name
- Data model changes (new migrations listed by intended version)
- Failure modes: what happens on crash / duplicate / timeout

## Risks & open questions
Anything unresolved. Empty section = you haven't thought hard enough.
```

STOP after writing plan.md. Present it and get explicit approval before Stage 2.
If the user answers open questions, update plan.md — it is the source of truth.

## Stage 2 — tasks.md (the HOW, sliced)

Create `docs/specs/<feature-name>/tasks.md`:

```markdown
# Tasks: <feature-name>

- [ ] T1: <verb phrase> — files: <paths> — done when: <verifiable check>
- [ ] T2: ...
```

Task rules:
- Each task independently completable and testable; roughly one commit each.
- Order by dependency; tests are part of the task, not a separate "write tests" task
  at the end.
- Migrations, config changes, and doc updates are explicit tasks, never side effects.
- 5–15 tasks. Fewer → task too big, split. More → feature too big, split the spec.

## Stage 3 — Execute

- Work strictly top-down through tasks.md. Mark `[x]` as each completes.
- One task = one commit, message referencing the task
  (`feat(notifications): T3 add dedup key to schema`).
- If reality contradicts the plan mid-task: STOP, update plan.md, flag the change,
  then continue. Never silently diverge from the spec.
- Definition of done per task: its "done when" check passes AND project tests pass.

## Stage 4 — Close out

- Verify every checkbox is `[x]` or explicitly deferred (moved to a "Deferred"
  section with reason).
- Update the project README/CLAUDE.md if the architecture changed.
- Summarize: what shipped, what was deferred, follow-ups discovered.

## Judgment calls

- Trivial change (1–2 files, no schema/API impact): skip the ceremony, say so
  explicitly ("skipping spec: trivial"), and just do it.
- Emergency fix: fix first, then backfill a minimal plan.md entry documenting what
  changed and why.

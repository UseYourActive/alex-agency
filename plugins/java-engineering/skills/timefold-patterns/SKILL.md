---
name: timefold-patterns
description: >
  Design and implementation patterns for constraint optimization with Timefold Solver
  (planning problems: scheduling, timetabling, rostering, routing, resource assignment).
  Use when the project depends on ai.timefold.solver or the task involves planning
  entities, constraint streams, or solver configuration. Not for generic optimization
  math or ML.
---

# Timefold Solver Patterns

Standing instructions for any Timefold work in this session.

## Domain modeling rules

- `@PlanningEntity` classes contain ONLY planning variables plus identity/problem
  facts they need; keep them thin and mutable only where the solver requires it.
- Everything the solver doesn't change is a problem fact — model facts as immutable
  (records where they don't need to be entities).
- `@PlanningVariable` should point at small, stable value ranges. Prefer
  `@ValueRangeProvider` on the solution class.
- Solution class (`@PlanningSolution`) exposes entity/fact collections with
  `@PlanningEntityCollectionProperty` / `@ProblemFactCollectionProperty` and a
  `@PlanningScore` field (`HardSoftScore` unless the domain demands more levels).
- Give every entity a stable `@PlanningId`.

## Constraint design rules

- Constraint Streams ONLY (`ConstraintProvider`). No score DRL, no easy/incremental
  Java score calculators unless benchmarking proves a need.
- One constraint = one method, named after the business rule
  (`teacherConflict`, `roomCapacity`, `lecturerPreferredSlot`).
- Hard constraints = feasibility (physical impossibility, legal rules).
  Soft constraints = preference/quality. Never mix by "big soft weights".
- Make weights configurable: use `@ConstraintConfiguration` +
  `@ConstraintWeight` so users can tune without recompiling (matches the
  strategy/configurable-constraint approach).
- Prefer `forEachUniquePair(...)` with `Joiners` over filtering cross products:
  ```java
  Constraint roomConflict(ConstraintFactory f) {
      return f.forEachUniquePair(Lesson.class,
              Joiners.equal(Lesson::getTimeslot),
              Joiners.equal(Lesson::getRoom))
          .penalize(HardSoftScore.ONE_HARD)
          .asConstraint("Room conflict");
      }
  ```
- Push work into `Joiners`; `filter(...)` is the last resort (it's evaluated per pair).

## Testing rules

- Every constraint gets a `ConstraintVerifier` test: at least one penalizing case,
  one non-penalizing case, and boundary cases.
  ```java
  constraintVerifier.verifyThat(TimetableConstraintProvider::roomConflict)
      .given(lessonA, lessonB)          // same room, same slot
      .penalizesBy(1);
  ```
- Solver integration test: tiny dataset, assert feasibility (`score.isFeasible()`)
  within a short `secondsSpentLimit`, not exact scores.

## Solver configuration

- Development: `solver.termination.spent-limit` short (5–30s) + environment mode
  `FULL_ASSERT` in tests to catch score corruption.
- Production: termination by unimproved-spent-limit rather than fixed time when
  quality matters.
- Log `Solver` best-score events via listener (observer pattern) for progress
  reporting; never poll.

## Performance checklist

1. No heavy computation inside constraint lambdas — precompute onto facts/entities.
2. Value ranges as small as the domain allows.
3. `equals`/`hashCode` on facts used in Joiners are correct and cheap.
4. Score corruption check passes in FULL_ASSERT before tuning anything.

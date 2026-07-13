---
name: qa-framework-architecture
description: >
  Architecture and conventions for the qa-commons test automation framework (and any
  test-framework code): module layout, JUnit 5 + AssertJ standards, thread-safety
  under parallel execution, seeded test data, configuration. Use when creating,
  extending, or reviewing test-framework/library code (not application code — for
  app tests inside a service, use test-architecture instead).
---

# QA Framework Architecture (qa-commons)

## Repository shape

ONE multi-module Maven repo, not one repo per concern:
- `core` — config loading, serialization (Jackson factory), seeded data factories,
  shared assertions, logging/reporting glue
- `api` — the typed Endpoint Object layer over RestAssured (see
  endpoint-object-pattern skill)
- `template` — living example project proving the framework against a real API;
  every framework feature gets demonstrated here or it doesn't exist
- Future, added ONLY when real need arrives: `ui` (Playwright), `perf` (Gatling),
  `mobile` (Appium)

## Stack decisions (settled — do not relitigate per task)

- JUnit 5, never TestNG. Parallelism via `junit-platform.properties`, not suite XML.
- AssertJ for all assertions; soft assertions via `SoftAssertions`/`assertSoftly` —
  NEVER hand-rolled verification wrapper hierarchies that override-and-delegate.
- datafaker (not javafaker), ALWAYS seeded: seed from a system property with a
  logged default, so any run is reproducible from its log line.
- No Lombok, no MapStruct. Records for models/DTOs; builders only where records
  don't fit.
- RestAssured stays an internal engine of the api module — test code never imports
  io.restassured directly.

## Thread-safety (the old framework's deadliest disease)

Tests WILL run in parallel. Therefore:
- NO singletons. No getInstance(), no static mutable state, no static
  lazy-init (`if (INSTANCE == null)` is a race). The old TestContext singleton +
  parallel methods = cross-test bleed; never recreate it.
- State lives per-test: constructor/method injection, JUnit extensions with
  ExtensionContext storage, or ThreadLocal ONLY inside framework internals with
  documented cleanup.
- No global mutation from class initializers (the old
  `static { RestAssured.filters(...) }` pattern is banned) — configuration happens
  in explicit, per-instance builders or extensions.
- Every framework class states its thread-safety in one Javadoc line.

## Configuration & credentials

- Typed config record loaded once per JVM from env vars with documented defaults;
  properties files carry NO real values — placeholders + .env.example only.
- Real credentials never in the repo (the old framework committed a client OAuth
  secret — that class of mistake is why the leak hooks exist).
- Base URLs always env-overridable so the same suite targets local/staging.

## Deferred-domain references (read only when that work happens)

- DB verification helpers (test oracles): read `references/db-test-oracles.md`
- Allure/report wiring: read `references/reporting-allure.md`
- Jira/AIO test-management sync: read `references/test-management-sync.md`

## Live-suite rules (tests against a running external service)

- Live tests are opt-in: tagged (@Tag("live")) and gated behind an explicit flag/
  profile, OFF by default - a fresh clone's `mvn clean verify` passes with the
  target service down.
- Never write a test that passes only while a KNOWN BUG exists in the target -
  a test that breaks when the target improves is a liability, not coverage.
  Controlled messiness (stub servers serving garbage on purpose) proves
  robustness; live bugs get reported, not enshrined.
- When adding the FIRST live test to a CONSUMER repo, the default-off gating
  (tag exclusion + opt-in flag) lands in the SAME commit - an ungated live test
  breaks that repo's CI the moment it merges.
- List/collection endpoints: assert the CONTRACT SHAPE (envelope fields, types,
  status), tolerate zero items - never depend on pre-existing data.

## Design rules

- Framework code is a LIBRARY: no test logic in it, no project-specific names,
  every public type documented with one usage example.
- Composition over inheritance towers: prefer small injected collaborators over
  Abstract*Base* chains three levels deep. One base class per module maximum.
- Reporting (Allure or plain logs) attaches via JUnit extensions/RestAssured
  filters configured explicitly in one place per module.

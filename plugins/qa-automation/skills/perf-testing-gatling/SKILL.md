---
name: perf-testing-gatling
description: >
  Performance testing patterns with Gatling (Java DSL): the protocol/steps/scenario/
  simulation layering, injection profiles, assertions, and safety rules. Use when
  writing or reviewing load tests, Gatling simulations, or the qa-commons perf
  module. Not for functional API tests.
---

# Gatling Performance Testing

## The four-layer split (keep from the old framework — it was right)

1. **Protocol** — one class configuring HttpProtocolBuilder: base URL (env-driven),
   shared headers, content type. Reused by every simulation.
2. **Steps** — smallest reusable unit: one HTTP call as a ChainBuilder with its
   checks. The perf equivalent of an endpoint method:
   ```java
   public ChainBuilder createVault(VaultModel vault) {
       return exec(http("CreateVault")
           .post(Urls.VAULT)
           .body(StringBody(json(vault)))
           .check(status().is(201), jmesPath("id").saveAs("vaultId")));
   }
   ```
3. **Scenario** — a user journey composed FROM steps (create → share → read),
   passing state via the Session (`saveAs`/`#{vaultId}` expressions).
4. **Simulation** — scenario + injection profile + assertions. Nothing else lives
   here; simulations stay ~20 lines.

## Session state rules

- Data flows between steps ONLY via Session variables (`saveAs`, `#{name}` EL) —
  never via Java fields on step/scenario classes (they're shared across virtual
  users; mutable fields there are a concurrency bug).
- Test data via feeders (csv/array/iterator) or per-user factories invoked inside
  the chain — one shared model instance across users invalidates the test.

## Injection profile vocabulary (when to use which)

- `atOnceUsers(n)` — spike at t=0; `rampUsers(n).during(d)` — gentle warm-up;
- `constantUsersPerSec(r).during(d)` — steady ARRIVAL RATE (open model: real-world
  traffic, users arrive regardless of system speed) — the default for services;
- `rampUsersPerSec(a).to(b).during(d)` — find the breaking point gradually;
- `stressPeakUsers(n).during(d)` — smooth surge to a peak.
- Open (arrival-rate) vs closed (concurrent-users) model matters: services facing
  the internet get OPEN model; closed model only for systems with a bounded user
  pool (call center app, worker pool).

## Assertions — a perf test without assertions is a demo

Every simulation asserts, minimum:
```java
.assertions(
    global().successfulRequests().percent().gte(99.0),
    global().responseTime().percentile(95).lt(500))
```
Prefer p95/p99 over max (max is one outlier) and over mean (means hide tails).

## Safety & hygiene

- Target env-configured, NEVER a default that could resolve to production; refuse
  to run if the target var is unset.
- Perf runs are separate from the functional suite (own module/profile, never in
  the PR pipeline); they run on demand or scheduled.
- Models/serialization shared with the functional framework via the core module —
  one source of truth for request shapes.
- Record the run context in the report: target, build/sha, profile, duration —
  numbers without context are noise.

---
name: twelve-factor
description: >
  Twelve-Factor App audit methodology for Java microservices (Quarkus/Spring Boot).
  Use when asked to audit, review, or harden a service's cloud-readiness, deployability,
  or 12-factor compliance, or when designing deployment/config/logging/scheduling for a
  containerized service. Not for frontend apps or generic code review.
---

# Twelve-Factor Audit (Java/Quarkus/Spring edition)

Assess each factor with EVIDENCE (file:line), never vibes. Grade: PASS / PARTIAL / FAIL / N-A.
For each factor below: what it means, then the concrete signals to check in a Java repo.

## I. Codebase — one repo, many deploys
Check: single service per repo; no copy-pasted sibling services; deploy variants via
config, not branches/forks.

## II. Dependencies — explicit, isolated
Check: mvnw/gradlew wrapper committed; versions pinned (no LATEST, no version ranges);
no reliance on system-installed tools in code (`Runtime.exec` of host binaries).

## III. Config — in the environment
Check: application.properties values use `${ENV_VAR}` (defaults OK for non-secrets);
`.env.example` exists and matches actual usage; NO secrets in code, properties defaults,
or committed .env; profiles (`%dev`, `%test`) only vary environment-shaped things.
Red flags: hardcoded URLs/credentials, secret defaults like `${DB_PASS:postgres}` for prod paths.

## IV. Backing services — attached resources
Check: DB/Redis/SMTP/queues reachable ONLY via config URLs; swapping provider = config
change, not code change (provider factories/strategies are a good sign).

## V. Build, release, run — strictly separated
Check: CI produces an immutable artifact/image; NOTHING mutates state at run start except
migrations owned by ONE tool. Red flags: `hibernate-orm.database.generation=update` or
`schema-management.strategy=update` coexisting with Flyway/Liquibase; builds performed on
the prod host; config baked into images.

Verify the migration tool actually EXECUTES: its location config matches the real
folder (Flyway default is db/migration, singular — a db/migrations folder is silently
ignored), and the schema history table is populated. Migration files existing proves
nothing; an ORM auto-DDL setting alongside inert migrations means the ORM owns the
schema in reality. Grade what runs, not what is configured.

## VI. Processes — stateless
Check: no session/queue/cache state in JVM memory that matters across requests.
Red flags: in-memory SmallRye channels for durable work (`@Channel` without a broker
connector binding in properties), static mutable maps, local file writes under the app dir,
sticky-session assumptions. In-memory is acceptable ONLY for loseable data — say so explicitly.

## VII. Port binding — self-contained
Check: app exports HTTP itself (Quarkus/Boot embedded server = pass by default); port from
env (`quarkus.http.port=${PORT:8080}`); no WAR-into-external-Tomcat.

## VIII. Concurrency — scale via processes
Check: can N replicas run safely? Red flags: `@Scheduled` jobs without a distributed
lock/leader election (every replica fires!); rate limiting or dedup in JVM memory instead
of Redis; file locks. Verify: schedulers use Redis SETNX/ShedLock/Quarkus-equivalent.

## IX. Disposability — fast start, graceful stop
Check: startup seconds not minutes (native/JVM tuning noted); SIGTERM handled — in-flight
work drains or is re-queued (`@PreDestroy`/shutdown hooks on consumers); K8s
`terminationGracePeriodSeconds` aligned; work is crash-safe (durable queue or outbox —
ties to VI).

## X. Dev/prod parity — same shape everywhere
Check: same DB engine in dev/test/prod (Testcontainers = pass; H2-in-test = fail);
same migration path; docker-compose mirrors prod services; minimal `%dev`/`%prod` divergence.

## XI. Logs — event streams to stdout
Check: console handler only; NO file handlers/rotation in app config; structured or at
least parseable format; correlation IDs via MDC. Red flags: `quarkus.log.file.enable=true`,
logback file appenders, writing audit logs to local disk.

## XII. Admin processes — one-off, same environment
Check: migrations/maintenance run as one-off commands/Jobs from the SAME image;
scripts are portable (not tied to one OS) or containerized; no "SSH in and run SQL by hand"
documented as process.

## Reporting rules
- Every finding: factor, file:line evidence, one-line impact, one-line fix.
- Rank the 3 highest-impact fixes first ("do these Monday").
- Distinguish violations from conscious trade-offs; ask before assuming intent.

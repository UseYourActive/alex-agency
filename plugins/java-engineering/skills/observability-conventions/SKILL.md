---
name: observability-conventions
description: >
  Observability standards: health checks, metrics naming, structured logging,
  correlation IDs, Prometheus/Grafana wiring. Use when adding or reviewing health
  endpoints, metrics, logging, dashboards, or alerting in a Java service. Not for
  business analytics or frontend monitoring.
---

# Observability Conventions

## Health checks — liveness vs readiness (never mix them)

- Liveness = "should the orchestrator restart me": process-internal only
  (deadlocks, out-of-memory sentinel). NEVER include backing services — a DB
  outage must not cause restart storms.
- Readiness = "should I receive traffic": DB ping, Redis ping, broker connection.
  Degraded optional dependencies (e.g. one notification channel down) →
  readiness UP with a `data` note, not DOWN.
- Startup info (version, build time) goes in a health `data` block or /info,
  never as a separate unauthenticated debug endpoint.

## Metrics (Micrometer)

- Naming: lowercase dot-separated, unit as suffix:
  `notifications.sent.total`, `notification.dispatch.duration.seconds`.
- Dimensions as TAGS, not names: `channel=email|sms|telegram`, `status=sent|failed`.
  Never encode unbounded values (user ids, recipients) as tags — cardinality explosion.
- Every external call (provider API, DB, Redis) gets a timer with an
  `outcome=success|error` tag. Business counters for domain events worth alerting on.

## Logging

- stdout only (12-factor XI). One line per event; no multi-line banners.
- Levels: ERROR = human should look; WARN = degraded but self-handling
  (retry scheduled, fallback used); INFO = domain lifecycle events; DEBUG = flow
  detail, off in prod.
- Correlation: request/notification id into MDC at the boundary, cleared after;
  include it in the pattern. Propagate across async hops (queue message headers →
  MDC on the consumer side).
- Never log secrets, tokens, full recipient lists, or message bodies; log ids
  and counts.

## Dashboards & alerts

- Provision Grafana dashboards/datasources as code in the repo (config/ dir),
  never hand-edited in the UI only.
- Alert on symptoms (error rate, p99 latency, queue depth/age), not causes
  (CPU). Every alert must have an obvious action; otherwise delete it.

# Database Helpers as Test Oracles

Purpose: verify system state directly in the DB when the API can't show it
(outbox rows, soft-deletes, audit columns). The old SQLDatabaseHelper had the
right idea and two diseases — fix both:

- NEVER swallow exceptions. The old helper caught, logged a warning, and rolled
  back — a broken oracle query silently passes the test. Oracle failures THROW
  and fail the test loudly.
- Parameterized queries (PreparedStatement) only — the old string-concat style is
  an injection habit and breaks on quotes in data.

Rules:
- Read-mostly. Writes only for seed/cleanup, wrapped in explicit transactions,
  never sprinkled mid-test.
- Builder-configured per instance from env config (host/db/creds) — no singleton
  connection, no static Properties; connections closed via try-with-resources.
- Return typed records or Optional, not Map<Integer, Map<String,String>> —
  callers should read like assertions: `db.notificationStatus(id)`.
- One helper per engine (Postgres, Mongo). Mongo needs the codec lesson from the
  old framework: register LocalDateTime/ObjectId codecs centrally in the client
  factory, or dates corrupt silently.
- Testcontainers for framework self-tests; real env access only via explicit env
  config in template/consumer projects.

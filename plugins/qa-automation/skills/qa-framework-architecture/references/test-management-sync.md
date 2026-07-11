# Test Management Sync (AIO / Jira pattern)

The old AIO_test_integration flow, generalized:
1. CI (or a local run) finishes -> results XML exists (surefire/junit).
2. A one-shot sync step creates a test CYCLE (from a test set or empty, titled
   with timestamp + build info) and imports the results file against it.
3. The cycle key is the join point between CI runs and Jira-visible reporting.

Rules for any rebuild:
- The sync is a POST-RUN step (CI job step or script), fully decoupled from test
  code — tests never know reporting exists. The old version's static mutable
  cycleKey on a @Getter/@Setter static class is the anti-pattern to avoid.
- All endpoints/tokens from env config; the auth header value is a secret.
- Idempotent-friendly: unique cycle titles (timestamp + sha) so reruns create
  distinguishable cycles instead of corrupting one.
- Failure to sync must FAIL VISIBLY in CI (non-zero exit) but must not fail the
  test job itself — separate step, separate status.
- JUnit 5 rebuild note: import the junit-platform XML or convert; the old flow
  assumed testng-results.xml.

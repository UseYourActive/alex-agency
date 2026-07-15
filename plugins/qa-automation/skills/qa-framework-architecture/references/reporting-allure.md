# Reporting Wiring (Allure)

What the old framework got right — keep all three ideas:
1. A custom RestAssured filter attaching each request/response pair to the report
   as prettified attachments (old CustomAllureRestAssuredFilter). Modern rule:
   register it PER endpoint instance in the base Endpoint class — never via a
   static RestAssured.filters() global.
2. Step lifecycle listener so business actions appear as named steps.
3. Log appender routing test logs into the report per-test, so a failure carries
   its own log slice.

Additions for the rebuild:
- Screenshot/trace attachments hook into assertion failure callbacks (see
  ui-automation-patterns) — attach at failure moment with the assertion message.
- Attach the datafaker seed and target base URL to every test = reproducibility
  from the report alone.
- Allure is optional per consumer project: reporting glue lives in core behind a
  small interface; plain SLF4J is the zero-dependency default.

## Failure philosophy (deliberate divergence from the oracle rule)

- The oracle IS the assertion: it fails LOUD. The reporter is a diagnostic
  side-channel: attachment/parameter failures log a WARN and the test
  continues - a broken report hook must never fail an otherwise-passing test.
- Keep reporting optional structurally: interface in core, SLF4J default,
  Allure via a tiny reflective bridge (no compile-time Allure dependency in
  core, ever); modules opt in with test-scope deps that never propagate.
- allure-maven's reportVersion pin to the 2.x line did NOT work in practice;
  the Allure 3 default engine reads 2.x-format results fine - verify the
  rendered report by OPENING it, never by the plugin exiting zero.

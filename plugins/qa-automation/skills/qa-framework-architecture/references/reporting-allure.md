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

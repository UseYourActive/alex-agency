---
name: ui-automation-patterns
description: >
  UI test automation patterns: Page Objects, locator strategy, waits, driver
  management, screenshot-on-failure. Use when building or reviewing UI test code or
  the qa-commons ui module (Playwright-first; Selenium rules included for legacy).
  Not for API tests (endpoint-object-pattern) or app-internal tests.
---

# UI Automation Patterns

## Page Object rules (engine-agnostic)

- One class per page/screen/major component. Locators private; tests NEVER see
  locators or the driver/page handle — only business-named methods:
  `loginAs(user)`, `submitOrder()`, `errorBanner()`.
- Action methods return the next page object (navigation) or a value (reads) —
  never void-and-hope. Assertions live in TESTS, not page objects; page objects
  expose state, tests judge it.
- Composition for shared fragments (header, dialogs) over inheritance towers.
  ONE base page class max, holding only cross-cutting helpers.
- Old framework's `BasePage.click(locator)` wrapper style (generic verb + locator
  passed by the test) is BANNED - it makes tests know locators, defeating the
  pattern entirely.

## Waits

- Playwright (default engine): built-in auto-waiting covers existence, visibility,
  stability, enablement — write NO manual waits for those. Explicit waits only for
  app-level conditions (data loaded, notification count changed) via
  `assertThat(locator).hasText(...)` style web-first assertions, which retry.
- Selenium (legacy only): all waits through one Waiter utility (explicit
  WebDriverWait with configurable timeout/poll); implicit waits BANNED (they
  poison every findElement and fight explicit waits). Never Thread.sleep.

## Driver / page lifecycle (the parallelism rules)

- One browser context (or driver) PER TEST, created and destroyed by a JUnit 5
  extension - never a shared singleton context (the old TestContext singleton
  under parallel methods = cross-test bleed).
- Playwright JAVA is NOT thread-safe across threads (unlike the JS/TS binding):
  one Playwright + Browser instance PER WORKER THREAD - a JVM-wide shared Browser
  corrupts the protocol under parallel execution (proven empirically). Within a
  thread: fresh BrowserContext + Page per test (cheap, isolated).
- Never assert via non-waiting accessors (locator.count(), isVisible()) - they
  read instantaneous state and pass by timing luck. Use waiting web-first
  assertions (assertThat(locator).hasCount/isVisible) which retry.
- Locator pattern semantics differ from JS: Java needs explicit
  java.util.regex.Pattern objects where JS auto-converts strings - a String
  where a Pattern is expected matches literally and fails silently.
- Provider interface + decorator (old IDriverProvider/DriverDecorator idea) stays
  a good seam for logging actions and choosing local vs remote - implement as
  injected collaborators, not static state.

## Failure diagnostics (keep the old framework's best UI idea)

- Screenshot on EVERY failure, including each SOFT assertion failure at the moment
  it happens (not just test end) - wire into the assertion callback / JUnit
  extension, attach to the report with the assertion message.
- Playwright: also enable tracing per test, retain-on-failure - the trace viewer
  (DOM snapshots + network + console) replaces most screenshot archaeology.

## Locator strategy

- Prefer user-facing locators: role, label, text, then data-testid; raw
  CSS/XPath structural paths are last resort and get a comment explaining why.
- Locator constants never duplicated across page objects; shared fragments own
  their locators.

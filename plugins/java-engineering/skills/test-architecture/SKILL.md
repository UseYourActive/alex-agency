---
name: test-architecture
description: >
  Enterprise test architecture: test taxonomy (unit/slice/integration/API), the AAA
  pattern, and the reusable test-kit (base classes, object mothers, custom assertions).
  Use when writing any test, designing test coverage for a feature, building or
  extending test infrastructure, or deciding which KIND of test a class needs.
  Complements quarkus/spring conventions. Not for production code design.
---

# Test Architecture

## The taxonomy — pick the CHEAPEST level that proves the behavior

1. UNIT — plain JUnit 5 + Mockito, no framework boot. For logic-bearing classes
   (services, mappers, validators, resolvers). Milliseconds each. Default choice.
2. SLICE — framework partially involved (@QuarkusTest with mocked externals,
   @WebMvcTest/@DataJpaTest in Spring). For code whose behavior IS framework wiring:
   endpoints, panache queries, exception mappers.
3. INTEGRATION — real backing services via Testcontainers (Postgres, Redis) or fakes
   (WireMock for HTTP providers, Mailpit/GreenMail for SMTP). For ADAPTERS: channel
   senders, repositories with nontrivial SQL, external clients. Mock-based unit tests
   on thin adapters are theater - they assert the mock was called. Test adapters
   against a fake server that verifies the real request shape.
4. API/CONTRACT — RestAssured against the running app (@QuarkusTest). For the public
   HTTP contract: status codes, error body shape (RFC 7807), pagination, validation
   messages, auth. One class per resource.

Placement mirrors production packages; suffix says the level:
`XxxTest` (unit/slice), `XxxIT`-style or `XxxIntegrationTest` (integration),
`XxxApiTest` (contract).

## AAA — mandatory shape of every test

```java
@Test
void claimBatch_skipsRowsLockedByOtherInstance() {
    // Arrange
    var locked = aNotification().queued().lockedBy("other-instance").build();
    repository.persist(locked);

    // Act
    var claimed = repository.claimBatch(10);

    // Assert
    assertThat(claimed).isEmpty();
}
```
- Blank line between the three blocks; comments optional once the shape is obvious.
- One behavior per test. Multiple asserts OK only if they describe ONE outcome.
- Name: methodUnderTest_condition_expectedOutcome or a business-readable @DisplayName.

## The test-kit — reusable infrastructure in `<root>.testkit`

Build these ONCE, reuse everywhere. When writing a test forces copy-paste of setup
that exists in another test, STOP and extract it into the kit instead.

- **Base classes**: `DatabaseTestBase` (Testcontainers Postgres + Flyway migrate +
  truncate-between-tests), `RedisTestBase`, `ApiTestBase` (RestAssured config, auth
  helpers, problem-json matchers), `WireMockTestBase` (per-test WireMock server +
  helpers to stub provider endpoints).
- **Object mothers / builders**: `aNotification()`, `anEmailRequest()` - fluent
  builders with SENSIBLE DEFAULTS so tests state only what matters:
  `aNotification().failed().withAttempts(3).build()`. One mother class per aggregate,
  in testkit, used by ALL levels. Never construct entities/DTOs inline in tests.
- **Custom assertions**: AssertJ extensions for domain objects
  (`assertThatNotification(n).isTerminal().hasAttempts(3)`) and for the RFC 7807
  error shape (`assertProblem(response).hasStatus(409).hasCode("NOTIF_081")`).
- **Time & async**: injectable/fake Clock helpers; awaitility for async assertions.
  Thread.sleep is BANNED.

## Coverage policy — what the numbers mean

- Target: BRANCH coverage on logic-bearing code (services, domain, validators,
  mappers). Global line % including DTOs/config is a vanity metric - never chase it.
- Thin adapters (senders, clients) are covered by INTEGRATION tests against fakes;
  their unit-mock coverage is worthless even at 100%.
- Trivial code (records, config holders, generated) needs no dedicated tests.
- The uncoverable (mandatory-JCA catch blocks etc.): document why, propose the seam,
  move on. 100% is not the goal; absence of UNTESTED RISK is.

## Credential isolation (non-negotiable)

- Tests must NEVER see real credentials or real provider endpoints. The test
  profile hard-overrides EVERY external credential, token, and base URL.
- Beware config-source ordering: a dotenv/.env config source can OUTRANK %test
  profile overrides (it did, in Quarkus) - when in doubt, use QuarkusTestProfile /
  @TestPropertySource per-test overrides, which win.
- Integration tests assert the fake is in effect (e.g. the client's base URL points
  at the WireMock server) before trusting any passing result - a test that silently
  talks to the real provider is worse than no test.

## Determinism rules

- No sleeps, no wall-clock time, no real network to the internet, no test order
  dependencies, no shared mutable state between tests.
- Randomness through a seeded/injectable source.
- A test that fails 1 run in 50 is a bug with the same priority as a production bug.

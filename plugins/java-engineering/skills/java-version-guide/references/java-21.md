# Java 21 Reference (covers 18–21; 21 is the LTS baseline — Alex's default)

Everything in java-17.md applies. Additions below.

## Virtual threads (the headline feature)

- Default choice for blocking I/O-heavy services (REST calls, JDBC, HTTP clients).
  - Spring Boot 3.2+: `spring.threads.virtual.enabled=true`
  - Quarkus: `@RunOnVirtualThread` on REST endpoints
  - Raw: `Executors.newVirtualThreadPerTaskExecutor()`
- Rules:
  - Never pool virtual threads — create per task; pooling defeats the purpose.
  - Avoid long `synchronized` blocks around blocking calls (pinning). Use
    `ReentrantLock` where a lock must wrap blocking I/O. (Pinning is fixed in 24+,
    but code targeting 21 must still care.)
  - `ThreadLocal` works but is costly at high thread counts; keep values small or
    refactor away.
  - CPU-bound work gains nothing — keep it on platform threads / ForkJoin.

## Pattern matching for switch + record patterns (final in 21)

```java
static String describe(PaymentResult r) {
    return switch (r) {
        case Approved(String txId)        -> "ok:" + txId;
        case Declined(String reason)      -> "declined: " + reason;
        case Errored(Throwable cause)     -> "error: " + cause.getMessage();
    };
}
```
- Deconstruct records directly in `case`; nest patterns for nested records.
- `when` guards: `case Declined d when d.reason().contains("fraud") -> ...`
- Prefer sealed hierarchy + exhaustive switch over visitor pattern.

## Sequenced collections (21)

- `SequencedCollection` / `SequencedMap`: `getFirst()`, `getLast()`, `reversed()`,
  `addFirst()`, `addLast()`. Use instead of `list.get(0)` / `list.get(size-1)`.

## Also available

- `Future.state()` for polling; structured concurrency and scoped values exist only
  as PREVIEW in 21 — do not use preview features in production code targeting 21.
- String templates were preview in 21 and later WITHDRAWN — never use them.

## Arriving from 17 — migration notes

- Mostly drop-in. Main wins: turn on virtual threads for I/O-bound services, replace
  visitor-style dispatch with record-pattern switches, adopt sequenced collections.
- Recheck any code using `synchronized` around I/O before enabling virtual threads.

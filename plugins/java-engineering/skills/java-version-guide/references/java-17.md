# Java 17 Reference (covers 11–17 range; 17 is the LTS baseline)

Ceiling: no virtual threads, no pattern matching for switch as stable pre-17 (final in
21), no record patterns, no sequenced collections, no scoped values.

## The idioms to use by default

- `record` for all DTOs and value objects:
  ```java
  public record CustomerDto(UUID id, String name, String email) {
      public CustomerDto {                      // compact ctor = validation
          Objects.requireNonNull(id);
          if (name == null || name.isBlank()) throw new IllegalArgumentException("name");
      }
  }
  ```
- `sealed` interfaces for closed hierarchies (results, domain events):
  ```java
  public sealed interface PaymentResult permits Approved, Declined, Errored {}
  public record Approved(String txId) implements PaymentResult {}
  public record Declined(String reason) implements PaymentResult {}
  public record Errored(Throwable cause) implements PaymentResult {}
  ```
- Switch expressions with arrow labels; exhaustive over sealed types and enums —
  prefer NO `default` branch on sealed/enum switches so the compiler flags new cases.
- `var` for obvious local types only; keep declarations readable.
- Text blocks (`"""`) for SQL, JSON fixtures, and multi-line strings.
- `instanceof` pattern matching: `if (o instanceof Money m) { use(m); }`
- Collection factories `List.of/Map.of/Set.of` (immutable, reject null).
- `Stream.toList()` (returns unmodifiable list — don't mutate it).
- `Optional.isEmpty()`, `String.isBlank()/strip()/lines()/formatted()`.
- `java.net.http.HttpClient` instead of legacy `HttpURLConnection`.

## Arriving from Java 8 — migration notes

- Replace hand-written value classes with records; delete equals/hashCode boilerplate.
- Replace `Collections.unmodifiable*(Arrays.asList(...))` with `List.of(...)`
  (beware: `List.of` rejects nulls; audit for null elements first).
- Illegal reflective access that "warned" on 9–16 fails on 17 (strong encapsulation).
  Check old libs (CGLIB-era, old Jackson/Hibernate) and upgrade them.
- Removed/deprecated: Nashorn is gone; `SecurityManager` deprecated; JAXB/JAX-WS no
  longer in the JDK — add explicit dependencies (`jakarta.xml.bind`).
- `javax.*` → `jakarta.*` if moving to Spring Boot 3.x / Quarkus 3.x at the same time.

## Pitfalls

- Records are shallowly immutable — a record holding a `List` still exposes a mutable
  list unless you defensively copy in the compact constructor:
  `list = List.copyOf(list);`
- Don't add mutable state or setters to records via arrays/collections.
- Switch expressions must be exhaustive; statement switches don't — prefer expressions.

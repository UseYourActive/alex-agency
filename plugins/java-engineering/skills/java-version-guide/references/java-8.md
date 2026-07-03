# Java 8 Reference

Hard ceiling: no `var`, no records, no sealed types, no switch expressions, no text
blocks, no `List.of()`/`Map.of()`, no `Optional.isEmpty()`, no modules, no HttpClient.

## Available and idiomatic

- Lambdas, method references, functional interfaces (`Function`, `Supplier`,
  `Predicate`, `BiFunction`)
- Streams API (but NOT `Stream.toList()` — use `collect(Collectors.toList())`)
- `Optional` (only `isPresent()`, `orElse`, `orElseGet`, `map`, `flatMap`, `filter`)
- `java.time` (LocalDate, Instant, Duration) — always prefer over `Date`/`Calendar`
- Default and static methods on interfaces
- `CompletableFuture` for async composition

## Substitutes for missing modern idioms

| Modern (17+) | Java 8 equivalent |
|---|---|
| `record Point(int x, int y)` | final class, final fields, ctor, getters, equals/hashCode/toString by hand |
| `List.of(a, b)` | `Collections.unmodifiableList(Arrays.asList(a, b))` |
| `Map.of(k, v)` | build HashMap, wrap in `Collections.unmodifiableMap` |
| `var x = ...` | explicit type |
| text blocks | concatenated strings or `String.join("\n", ...)` |
| `Stream.toList()` | `collect(Collectors.toList())` |
| switch expression | switch statement or if/else chain |
| `String.isBlank()` | `s.trim().isEmpty()` |

## Immutable value object template

```java
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        this.amount = Objects.requireNonNull(amount, "amount");
        this.currency = Objects.requireNonNull(currency, "currency");
    }

    public BigDecimal getAmount() { return amount; }
    public Currency getCurrency() { return currency; }

    @Override public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Money)) return false;
        Money other = (Money) o;
        return amount.equals(other.amount) && currency.equals(other.currency);
    }
    @Override public int hashCode() { return Objects.hash(amount, currency); }
    @Override public String toString() { return amount + " " + currency; }
}
```

## Common pitfalls in Java 8 codebases

- `Optional` as a field or method parameter — avoid; use it only as a return type.
- Parallel streams on small collections or inside web requests — almost always slower.
- Date/time: never `SimpleDateFormat` in shared state (not thread-safe); use
  `DateTimeFormatter`.
- Checked exceptions inside lambdas: wrap in a small helper that rethrows as unchecked.
- Interface default methods are for API evolution, not a place to hide business logic.

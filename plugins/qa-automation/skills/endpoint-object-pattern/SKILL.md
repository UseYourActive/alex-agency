---
name: endpoint-object-pattern
description: >
  The typed Endpoint Object pattern for API test automation: one class per API
  resource wrapping HTTP details, generic over request/response/error types, with a
  sealed typed result. Use when writing or reviewing API test clients, endpoint
  classes, API test suites, or the qa-commons api module. The API-side equivalent of
  the Page Object pattern.
---

# Endpoint Object Pattern

Tests never speak HTTP. Each API resource gets one Endpoint class that owns its
path, auth, and (de)serialization; tests call business-named methods and receive a
TYPED result. Compile-time safety on request, response, AND error bodies.

## The result type — sealed, not nullable fields

The old design returned one object with nullable body/errorBody/rawBody fields.
Modernize with a sealed hierarchy so illegal states don't exist:

```java
public sealed interface ApiResult<T, E> {
    int status();
    Headers headers();

    record Success<T, E>(int status, Headers headers, T body) implements ApiResult<T, E> {}
    record Failure<T, E>(int status, Headers headers, E error) implements ApiResult<T, E> {}
    record Unparsed<T, E>(int status, Headers headers, String raw) implements ApiResult<T, E> {}

    default T expectSuccess() { /* return body or throw with status+raw for diagnosis */ }
    default E expectFailure() { /* return error or throw */ }
}
```

- 2xx + parseable → Success; non-2xx + parseable error → Failure; anything else →
  Unparsed. Pattern-match in tests or use expectSuccess()/expectFailure() for the
  common cases.
- Negative tests get the SAME typing as positive ones: `expectFailure().code()`.

## The endpoint class

```java
public final class NotificationsEndpoint extends Endpoint<CreateNotificationRequest,
        NotificationResponse, ErrorResponse> {

    public NotificationsEndpoint(ApiConfig config, Auth auth) {
        super(config, "/api/v1/notifications",
              NotificationResponse.class, ErrorResponse.class, auth);
    }

    public ApiResult<NotificationResponse, ErrorResponse> create(CreateNotificationRequest req) {
        return post(req);                       // inherited typed verb
    }

    public ApiResult<NotificationResponse, ErrorResponse> getById(UUID id) {
        return get("/{id}", id);
    }
}
```

Rules:
- One endpoint class per resource; methods named after BUSINESS operations
  (create, cancel, listFailed), never after HTTP verbs alone.
- Config and auth injected via constructor — no singletons, no static base URLs;
  an endpoint instance is cheap and per-test.
- RestAssured (or any HTTP engine) is an implementation detail of the base
  Endpoint class only. Tests and endpoint subclasses never import it.
- Path params via typed method args; never string-concatenated URLs in tests.
- Reporting filter (Allure request/response attachment) configured per-instance in
  the base class, not via static global filters.

## Contract discovery (before writing any endpoint class)

- Never guess API paths. Fetch the machine-readable spec first: Quarkus serves
  /q/openapi (Swagger UI at /q/swagger-ui, health at /q/health/ready); Spring
  serves /v3/api-docs. Read paths, schemas, and error shapes from the spec, then
  verify the critical path with ONE real request before locking models to it.
- Query params NEVER by string concatenation ("?page=" + page) - not in tests,
  not in endpoint subclasses. The base Endpoint exposes a distinctly-named
  query-capable method (distinct name, not an overload, to avoid varargs
  ambiguity) that URL-encodes properly.

## Test data factories

- One factory per aggregate: `NotificationRequests.valid()`,
  `.withChannel(TELEGRAM)`, `.missingRecipient()` — fluent, defaults sensible,
  named after INTENT including invalid variants for negative tests.
- Backed by seeded datafaker (seed logged at run start; reproducible failures).
- Factories live beside models in the test project, extending core's seeded base.

## What tests look like (the goal)

```java
@Test
void duplicateNotification_returns409() {
    var request = NotificationRequests.valid();
    endpoint.create(request).expectSuccess();

    var second = endpoint.create(request);

    assertThat(second.status()).isEqualTo(409);
    assertThat(second.expectFailure().code()).isEqualTo("NOTIF_081");
}
```

AAA shape, no HTTP noise, typed all the way down, negative path as ergonomic as
the positive one. If a test needs a raw RestAssured escape hatch, the framework is
missing a feature — add it there instead.

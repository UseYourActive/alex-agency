---
name: rest-api-conventions
description: >
  HTTP/REST API design conventions: DTO naming, error responses, status codes,
  pagination, validation, OpenAPI, webhooks. Use when creating or modifying REST
  endpoints, request/response DTOs, exception mappers, or API contracts in any Java
  service. Framework-neutral; combine with quarkus-conventions or
  spring-boot-conventions. Not for messaging/gRPC/internal APIs.
---

# REST API Conventions

Apply to every endpoint and DTO you create or modify.

## Naming

- Request DTOs: `Create<X>Request`, `Update<X>Request`, `Get<X>sRequest` (records).
- Response DTOs: `<X>Response`, `Get<X>sResponse`. Never expose entities.
- Paths: plural nouns, kebab-case, no verbs: `POST /notifications`,
  `GET /templates/{id}`. Actions that aren't CRUD get a sub-resource:
  `POST /notifications/{id}/retries`.

## Status codes (use exactly these)

- 200 read/update OK · 201 created (with Location header) · 202 accepted for async
  processing (return an id to poll) · 204 delete OK
- 400 malformed/validation · 404 not found · 409 conflict/duplicate ·
  422 semantically invalid · 429 rate limited (with Retry-After header) ·
  500 unexpected only — never for expected domain failures

## Errors — one shape everywhere

RFC 7807 problem+json: `type`, `title`, `status`, `detail`, plus extensions
`code` (stable machine code, e.g. RATE_LIMIT_EXCEEDED) and `errors[]` for field
violations. One exception-mapper layer owns this; endpoints never build error
bodies. Localized `title`/`detail` via the message service when the project has i18n.

## Validation

- Validate at the boundary: Bean Validation annotations on request records,
  `@Valid` at the endpoint. Cross-field rules get a custom class-level annotation.
- Domain invariants re-checked in the domain, not trusted from DTOs.

## Pagination & filtering

- Query params: `page` (0-based), `size` (default 20, max 100), `sort=field,asc`.
- List responses wrap items: `{ items: [...], page, size, totalItems, totalPages }`.
- Never return unbounded lists from collection endpoints.

## Async operations

- Long work: 202 + body `{ id, status }`; expose `GET /<resource>/{id}` for status
  polling. Status enum, never free text.

## Webhooks (receiving)

- Verify signatures BEFORE parsing the body into objects; reject with 401 on
  failure, respond 2xx fast, and hand off processing async.
- Idempotency: dedupe by provider event id; webhooks WILL be delivered twice.

## OpenAPI

- Annotate endpoints with summary + response codes incl. error responses;
  examples for non-obvious request bodies. Swagger UI never enabled
  unconditionally in prod (config-gated).

---
name: quarkus-conventions
description: >
  Coding conventions and architecture rules for Quarkus projects. Use whenever writing,
  reviewing, or refactoring Java code in a project whose pom.xml or build.gradle contains
  quarkus-bom, io.quarkus, or quarkus-maven-plugin. Do NOT use for Spring Boot projects
  (use spring-boot-conventions instead) or non-Java projects.
---

# Quarkus Conventions

Apply these rules to ALL code you write or modify in this project. They are standing
instructions, not one-time steps.

## Hard rules (never violate)

- NO Lombok. Write constructors, getters, and equals/hashCode by hand or use records.
- NO MapStruct or any mapper code generation. Write explicit mapping methods.
- Constructor injection ONLY. Never use `@Inject` on fields. Prefer `final` fields.
- DTOs are Java `record` types. Never mutable classes with setters.
- JPA entities use a hand-written builder pattern (static inner `Builder` class),
  protected no-arg constructor for JPA, no public setters.
- One REST resource class per use case where practical (REPR: Request → Endpoint →
  Response). Endpoint methods stay thin; logic lives in application services.

## Extensibility (Open-Closed)

- Per-variant BEHAVIOR (per channel/provider/type): one strategy interface, one
  implementation per variant, discovered via CDI and dispatched from a map/registry.
  ONE exhaustive switch in a single factory is acceptable; two switches over the same
  enum in different places means extract a strategy or config map.
- Per-variant CONFIGURATION: model as a Map in @ConfigMapping
  (`limits.email.max=...` -> `Map<NotificationChannel, Limit> limits()`), so adding a
  variant is config + at most one new class, never editing existing methods.
- Validators: one ConstraintValidator per concern/variant composed via annotation
  groups, not a god-class with per-channel branches.

## Permitted exception to the records rule

- JAX-RS `@BeanParam` containers may be mutable classes with setters if the RESTEasy
  version requires it. They must be final, logic-free, and live in the api layer.
  If the project's RESTEasy Reactive supports record bean params, use records.

## Quarkus specifics

- Use `@ApplicationScoped` as the default bean scope; justify anything else.
- Configuration via `@ConfigMapping` interfaces, not `@ConfigProperty` field injection
  scattered across classes. Group config per feature.
- REST: use `quarkus-rest` (RESTEasy Reactive) annotations; return DTO records, never
  entities.
- Persistence: repository pattern with Panache **repository** style
  (`PanacheRepository<T>`), NOT active record style. Entities stay free of query logic.
- Query field names: never repeat raw string literals ("status") across queries; use
  the generated JPA static metamodel (hibernate-jpamodelgen -> `Entity_.FIELD`) or a
  per-entity constants holder.
- Errors: one `@ServerExceptionMapper` (or `ExceptionMapper`) layer translating domain
  exceptions to RFC 7807 problem responses. Never leak stack traces in responses.
- Prefer Mutiny (`Uni`/`Multi`) only when the endpoint genuinely benefits; otherwise
  plain imperative code on virtual threads (`@RunOnVirtualThread`) for Java 21+.

## Testing (part of EVERY change, not optional)

Any new endpoint, service method, or bean ships WITH its tests in the same task -
never deliver production code and defer tests unless the user explicitly says to skip.

- `@QuarkusTest` for slice/integration tests, RestAssured for endpoint tests.
- Unit tests for application services with plain JUnit 5 + Mockito, no Quarkus boot.
- Every bug fix gets a regression test first.

## Verification checklist (run mentally before finishing any task)

1. No `lombok` or `mapstruct` imports anywhere in the diff.
2. All new beans use constructor injection with final fields.
3. New DTOs are records; new entities have builders and protected constructors.
4. Endpoints return DTOs, and error paths map to problem responses.
5. Tests exist for the change.

For package/module placement questions, defer to the project's structure conventions
if a structure skill or CLAUDE.md rule exists; otherwise follow standard
feature-package layout (`<feature>/api`, `<feature>/domain`, `<feature>/infra`).

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

## Permitted exception to constructor injection (ArC proxyability)

- Normal-scoped beans that ArC must client-proxy sometimes REQUIRE a no-args
  constructor - notably JAX-RS resource families built on an inherited base class.
  If constructor injection breaks deployment with "unproxyable bean class", those
  specific classes may keep field injection or a package-private no-args constructor,
  with a comment stating the ArC reason. Scope the exception to the affected classes
  only, mirror it as a NAMED, commented exclusion in the ArchUnit rule, and never
  widen it to whole packages.

## Permitted exception to the records rule

- JAX-RS `@BeanParam` containers may be mutable classes with setters if the RESTEasy
  version requires it. They must be final, logic-free, and live in the api layer.
  If the project's RESTEasy Reactive supports record bean params, use records.

## Quarkus specifics

- Use `@ApplicationScoped` as the default bean scope; justify anything else.
- App configuration via `@ConfigMapping` interfaces, not `@ConfigProperty` field
  injection scattered across classes; group config per feature. Exception: framework
  properties (`quarkus.*`) cannot live in prefixed mappings - constructor-injecting
  those via `@ConfigProperty` is correct. Runtime-configurable schedules use the
  `@Scheduled(every = "{prop}")` expression form - that is idiomatic, not a smell.
- Build-affecting properties (`quarkus.container-image.build`, `quarkus.package.*`,
  deployment toggles) are NEVER unqualified in application.properties - they apply to
  every Maven invocation everywhere, including CI jobs that must not build images.
  Profile-qualify them (`%prod.`) or pass as -D flags in the invoking script.
- REST: use `quarkus-rest` (RESTEasy Reactive) annotations; return DTO records, never
  entities.
- Persistence: repository pattern with Panache **repository** style
  (`PanacheRepository<T>`), NOT active record style. Entities stay free of query logic.
- Query names are never inline literals. Panache/JPQL: generated JPA static metamodel
  (hibernate-jpamodelgen -> `Entity_.FIELD`). Native SQL: a per-entity `XxxSql` final
  constants class (table + column names). Never an interface of constants (constant
  interface antipattern).
- Errors: one `@ServerExceptionMapper` (or `ExceptionMapper`) layer translating domain
  exceptions to RFC 7807 problem responses. Never leak stack traces in responses.
- Prefer Mutiny (`Uni`/`Multi`) only when the endpoint genuinely benefits; otherwise
  plain imperative code on virtual threads (`@RunOnVirtualThread`) for Java 21+.

## Component hygiene

- Mapping between representations (entity <-> domain <-> DTO) lives in dedicated
  injectable @ApplicationScoped mapper components - NEVER private/static mapping
  methods inside services, pollers, or resources.
- Any type appearing in a component's public signatures (query results, projections,
  results like ClaimResult) gets its own file - nested types are for private
  implementation details only.
- When 3+ methods repeat the same guard/try-catch scaffolding (enabled checks,
  fail-open wrappers), extract one private functional helper; public methods stay thin.

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

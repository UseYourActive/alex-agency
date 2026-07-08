---
name: spring-boot-conventions
description: >
  Coding conventions and architecture rules for Spring Boot projects. Use whenever
  writing, reviewing, or refactoring Java code in a project whose pom.xml or
  build.gradle contains spring-boot-starter or org.springframework.boot. Do NOT use
  for Quarkus projects (use quarkus-conventions instead) or non-Java projects.
---

# Spring Boot Conventions

Apply these rules to ALL code you write or modify in this project. They are standing
instructions, not one-time steps.

## Hard rules (never violate)

- NO Lombok. Write constructors, getters, and equals/hashCode by hand or use records.
- NO MapStruct or any mapper code generation. Write explicit mapping methods.
- Constructor injection ONLY. Never `@Autowired` on fields. Single-constructor beans
  need no annotation. All injected fields are `final`.
- DTOs are Java `record` types. Never mutable classes with setters.
- JPA entities use a hand-written builder pattern (static inner `Builder` class),
  protected no-arg constructor for JPA, no public setters.
- REPR pattern for web layer: thin `@RestController` per use case, logic in
  application services.

## Extensibility (Open-Closed)

- Per-variant BEHAVIOR: one strategy interface, one bean per variant; inject
  `Map<String, Strategy>` (Spring builds it from bean names) or build an EnumMap in a
  factory. One exhaustive switch in one factory max; duplicated switches over the same
  enum mean extract.
- Per-variant CONFIGURATION: `@ConfigurationProperties` with a
  `Map<VariantKey, Settings>` field, so new variants are config-only.

## Spring specifics

- Prefer Spring Modulith-style module boundaries: one top-level package per business
  module; other modules may only depend on a module's `api`/exposed types.
- Configuration via `@ConfigurationProperties` records bound with
  `@EnableConfigurationProperties` or `@ConfigurationPropertiesScan`. No `@Value`
  scattered across classes.
- Persistence: Spring Data repositories are interfaces in the module's infra layer;
  controllers never touch repositories directly.
- Errors: one `@RestControllerAdvice` translating domain exceptions to
  `ProblemDetail` (RFC 7807). Never leak stack traces.
- Transactions: `@Transactional` on application-service methods, not controllers or
  repositories. Read-only where applicable.
- Enforce architecture with ArchUnit tests (layer dependencies, no field injection,
  naming). If an `arch` test package exists, add rules there when introducing new
  patterns.

## Testing (part of EVERY change, not optional)

Any new endpoint, service method, or bean ships WITH its tests in the same task -
never deliver production code and defer tests unless the user explicitly says to skip.

- Unit tests: plain JUnit 5 + Mockito for services, no Spring context.
- Slice tests: `@WebMvcTest` for controllers, `@DataJpaTest` for repositories.
- Full `@SpringBootTest` only for true end-to-end paths; keep them few.
- Every bug fix gets a regression test first.

## Verification checklist (run mentally before finishing any task)

1. No `lombok` or `mapstruct` imports anywhere in the diff.
2. All new beans use constructor injection with final fields.
3. New DTOs are records; new entities have builders and protected constructors.
4. Exceptions map to ProblemDetail; transactions sit on services.
5. ArchUnit rules still pass conceptually; tests exist for the change.

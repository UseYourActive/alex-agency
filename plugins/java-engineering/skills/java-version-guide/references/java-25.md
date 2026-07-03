# Java 25 Reference (covers 22–25; 25 is the LTS baseline)

Everything in java-21.md applies, with the pinning caveat lifted. Additions below.
If any detail matters for production, verify against current release notes — this
range is recent and tooling/library support may still be uneven.

## Finalized since 21 (usable in production on 25)

- **Unnamed variables & patterns (22):** `_` for ignored bindings.
  ```java
  case Approved(_) -> "ok";                 // ignore component
  try { ... } catch (NumberFormatException _) { return fallback; }
  ```
- **Foreign Function & Memory API (22):** replaces JNI for native interop
  (`java.lang.foreign`). Relevant if wrapping native libs (e.g. ONNX runtime).
- **Stream gatherers (24):** `Stream.gather(...)` — custom intermediate ops
  (windowing, scan, distinct-by). Use `Gatherers.windowFixed(n)`,
  `Gatherers.fold(...)`, `Gatherers.scan(...)` before writing manual loops.
- **Markdown doc comments (23):** `///` JavaDoc in Markdown.
- **Virtual thread pinning fix (24):** `synchronized` no longer pins carriers —
  the ReentrantLock workaround from the 21 guide is unnecessary on 24+.
- **Class-File API (24):** `java.lang.classfile` replaces ASM for bytecode tooling.
- **Scoped values (finalized in this range):** immutable per-thread context that is
  cheap with virtual threads — prefer over ThreadLocal for request context:
  ```java
  static final ScopedValue<RequestContext> CTX = ScopedValue.newInstance();
  ScopedValue.where(CTX, ctx).run(() -> handle(request));
  ```
- **Structured concurrency:** check current status before production use; API shape
  changed across previews (`StructuredTaskScope`). If finalized in your JDK build,
  prefer it for fan-out I/O over raw CompletableFuture composition.
- **Compact source files / instance main (25):** `void main()` without a class —
  fine for scripts and demos, not for services.

## Runtime & migration notes (from 21 → 25)

- 32-bit x86 port removed; check base images (use 64-bit, prefer modern
  `eclipse-temurin:25` style tags).
- `sun.misc.Unsafe` memory-access methods are deprecated for removal and warn on
  use — old libraries (some serializers, off-heap caches) may emit warnings; upgrade
  them.
- Ahead-of-time class loading/caching (Project Leyden increments) can cut startup —
  relevant for Quarkus-style fast-boot deployments; enable via `-XX:AOTCache` flags
  after measuring.
- Generational ZGC is the default ZGC mode; for low-latency services test
  `-XX:+UseZGC` against G1 with your workload.

## Pitfalls

- Don't use preview features in production; gate experiments behind `--enable-preview`
  in separate modules only.
- Library ecosystem (agents, bytecode manipulation, some Quarkus/Spring extensions)
  may trail a new LTS by months — verify before committing a service to 25.

---
name: java-version-guide
description: >
  Version-specific Java guidance and idioms for Java 8, 17, 21, and 25. Use when the
  project's Java version constrains what code is valid (e.g. maintaining a legacy
  Java 8 codebase, migrating between versions, or exploiting newest language features).
  Determines the version from pom.xml/build.gradle/toolchain, then loads only the
  matching reference file. Not needed for generic Java questions where version is
  irrelevant.
---

# Java Version Guide

This skill is a router. Do NOT rely on memory for version-specific details — read the
matching reference file, and only that file.

## Step 1 — Detect the project's Java version

Check, in order:
1. `pom.xml`: `<maven.compiler.release>`, `<java.version>`, or compiler plugin config
2. `build.gradle(.kts)`: `java.toolchain.languageVersion` or `sourceCompatibility`
3. `.sdkmanrc`, `.java-version`, Dockerfile base image
4. If nothing found, ask the user once.

## Step 2 — Read the matching reference

- Java 8  → read `references/java-8.md`
- Java 11–17 → read `references/java-17.md`
- Java 18–21 → read `references/java-21.md`
- Java 22–25 → read `references/java-25.md`

For migrations, read BOTH the source and target version files, and pay attention to
each file's "arriving from older versions" section.

## Step 3 — Apply

Write code using only features available in the detected version. When a newer idiom
exists but is unavailable, note it in one short comment or remark, then move on —
do not lecture about upgrade paths unless asked.

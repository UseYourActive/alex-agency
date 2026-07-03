# Alex Agency — Claude Code Marketplace

Personal, portable AI agency for Claude Code: skills, subagents, and hooks packaged
as installable plugins. One git repo, usable on any machine.

## Install (any machine)

```bash
# 1. Push this repo to GitHub as a PUBLIC repo (e.g. alexorozov/alex-agency)
# 2. In any Claude Code session:
/plugin marketplace add alexorozov/alex-agency
/plugin install java-engineering@alex-agency
```

Update everywhere later with `/plugin update java-engineering@alex-agency` after
pushing changes (bump the version in `plugins/java-engineering/.claude-plugin/plugin.json`
— the version is the cache key that makes updates propagate).

## Local development (no GitHub needed)

```bash
# Load the plugin for the current session only:
claude --plugin-dir ./plugins/java-engineering

# Validate structure before committing:
claude plugin validate ./plugins/java-engineering

# Inspect token cost (always-on vs on-invoke):
claude plugin details java-engineering
```

SKILL.md edits take effect immediately in the session; changes to `agents/` and
`hooks/` need `/reload-plugins` or a restart.

## What's inside

| Plugin | Component | What it does |
|---|---|---|
| java-engineering | skill: `quarkus-conventions` | Auto-applies Quarkus coding standards (no Lombok/MapStruct, constructor injection, records, Panache repositories, REPR) |
| java-engineering | skill: `spring-boot-conventions` | Same standards for Spring Boot (Modulith boundaries, ProblemDetail, ArchUnit) |
| java-engineering | skill: `java-version-guide` | Router skill: detects project Java version, loads only the matching reference (8 / 17 / 21 / 25) |
| java-engineering | skill: `timefold-patterns` | Timefold Solver modeling, constraint-stream, and ConstraintVerifier patterns |
| java-engineering | agent: `code-reviewer` | Read-only reviewer subagent, runs in its own context, returns prioritized findings |
| java-engineering | agent: `test-writer` | Test-writing subagent (JUnit 5, Mockito, slice tests, ConstraintVerifier) |
| java-engineering | hook: `block_banned_deps` | PreToolUse hook that hard-blocks any edit adding Lombok or MapStruct to .java files |

## Design principles

1. **Descriptions are targeting instructions.** Every skill description says exactly
   when to fire AND when not to. That's what makes auto-invocation reliable.
2. **Progressive disclosure.** SKILL.md bodies stay short; deep detail lives in
   `references/` files loaded only when needed. Keeps always-on token cost near zero.
3. **Skills teach, hooks enforce.** Conventions the model should follow are skills;
   non-negotiables (no Lombok) are deterministic hooks that block violations 100% of
   the time.
4. **Agents isolate noise.** Review and test runs happen in subagent context windows
   so the main session stays clean.
5. **Knowledge is model-agnostic.** SKILL.md files follow the open Agent Skills
   standard (plain markdown) and can be reused as context with other AI tools;
   agents/hooks are the Claude Code-specific wiring.

## Adding a new plugin

1. Copy the `plugins/java-engineering` layout to `plugins/<new-name>`.
2. Fill in `.claude-plugin/plugin.json` (name, version, description).
3. Add an entry to `.claude-plugin/marketplace.json` under `plugins`.
4. `claude plugin validate ./plugins/<new-name>`, bump versions, push.

Planned: `rag-delivery` (RAG/document-AI service patterns from BizLex),
`ai-services-business` (proposals, pricing, SME discovery), `marketing`.

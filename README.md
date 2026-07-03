# Alex Agency — Claude Code Marketplace

Personal, portable AI agency for Claude Code: skills, subagents, and hooks packaged
as installable plugins. One git repo, usable on any machine.

## Install (any machine)

```bash
# In any Claude Code session (one time per machine):
/plugin marketplace add UseYourActive/alex-agency
/plugin install java-engineering@alex-agency
```

Then restart Claude Code or run `/reload-plugins`.

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

---

# HOW TO ADD STUFF (read this before touching anything)

## The map — what goes where

```
alex-agency/                          ← the marketplace (this repo)
├── .claude-plugin/
│   └── marketplace.json              ← the CATALOG: lists every plugin below
└── plugins/
    └── java-engineering/             ← ONE plugin = one installable package
        ├── .claude-plugin/
        │   └── plugin.json           ← the plugin's ID card (name, version, description)
        ├── skills/
        │   └── my-skill/
        │       ├── SKILL.md          ← REQUIRED: the skill itself
        │       └── references/       ← optional: deep detail, loaded only when needed
        ├── agents/
        │   └── my-agent.md           ← one file = one subagent
        └── hooks/
            ├── hooks.json            ← which scripts run on which events
            └── scripts/              ← the actual scripts
```

Decision guide — which thing do I create?

| I want Claude to... | Create a... |
|---|---|
| Follow instructions/knowledge when relevant | **Skill** |
| Do a noisy job (review, research, tests) without polluting my chat | **Agent** |
| NEVER do something / ALWAYS do something, 100% guaranteed | **Hook** |
| Ship a new unrelated topic area (e.g. marketing) | **New plugin** |

Rule of thumb: skills teach, hooks enforce, agents isolate.

---

## Recipe 1 — Add a new SKILL (most common)

**Step 1.** Make the folder and file. Skill names: lowercase, hyphens, no spaces.

```
plugins/java-engineering/skills/qdrant-conventions/SKILL.md
```

**Step 2.** Fill it using this template:

```markdown
---
name: qdrant-conventions
description: >
  Conventions for Qdrant vector database work. Use when the project imports
  qdrant-client or the task involves collections, vector search, or hybrid
  BM25+dense retrieval. NOT for other vector DBs or generic SQL work.
---

# Qdrant Conventions

Apply these rules to all Qdrant work in this session.

## Hard rules
- (your rules here, imperative voice: "Use X", "Never Y")

## Snippets
- (code Claude should copy)
```

**Step 3.** The description is 90% of the skill. It decides WHEN the skill
auto-fires. It must contain:
- WHAT it covers, using the words you'd naturally type in a prompt
- WHEN to use it (detectable signals: dependency names, file types, task words)
- WHEN NOT to use it (stops false triggers)

**Step 4.** Keep SKILL.md under ~100 lines. Once invoked it sits in context for
the whole session, so every line costs tokens on every following message. If you
have deep detail (long snippet libraries, version matrices), put it in
`references/whatever.md` and write in SKILL.md: "For X, read references/whatever.md".
Claude will read it only when actually needed. See `java-version-guide` for the
canonical example of this pattern.

**Step 5.** Test locally, then publish (see Recipe 5).

```bash
claude --plugin-dir ./plugins/java-engineering
# in the session, force it once:  /java-engineering:qdrant-conventions
# then test auto-trigger: ask a Qdrant question WITHOUT naming the skill
```

---

## Recipe 2 — Add a new AGENT (subagent)

**Step 1.** One markdown file:

```
plugins/java-engineering/agents/migration-planner.md
```

**Step 2.** Template:

```markdown
---
name: migration-planner
description: >
  Plans Java version migrations. Use when the user asks to upgrade a project's
  Java/framework version. Analyzes the codebase read-only and returns a step plan.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a migration planner. (System prompt: who the agent is, its process
step by step, its rules, and EXACTLY what its final report must contain.)
```

**Step 3.** Know the three frontmatter dials:
- `tools:` — give the MINIMUM. Reviewer/analyst agents get `Read, Grep, Glob`
  only (they physically cannot edit files). Only builders get `Edit, Write`.
- `model:` — `haiku` for dumb grunt work, `sonnet` for normal work. Cheap models
  on agents = big token savings.
- `description:` — same rules as skills; it's how Claude decides to delegate.

**Step 4.** Always end the system prompt with the required output format
("Return: ..."). The agent's report is the ONLY thing that comes back to your
main chat — everything else stays in its own context window.

**Step 5.** Agents do NOT hot-reload. After changes: `/reload-plugins` or restart.

---

## Recipe 3 — Add a new HOOK

Hooks are scripts that run automatically on events. They are deterministic:
no AI judgment, no exceptions.

**Step 1.** Write a script in `plugins/java-engineering/hooks/scripts/`.
The contract:
- It receives the tool call as JSON on **stdin**
- Exit `0` = allow. Exit `2` = BLOCK, and whatever you print to **stderr** is
  shown to Claude so it can self-correct.
- Copy `block_banned_deps.py` as your starting point — it already parses the
  JSON correctly.

**Step 2.** Register it in `hooks/hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          { "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/my_check.py\"" }
        ]
      }
    ]
  }
}
```

- `PreToolUse` = runs BEFORE the tool (can block). `PostToolUse` = runs after
  (formatting, logging). There are more events — ask Claude Code itself
  ("what hook events exist?") for the current list.
- `matcher` = which tools trigger it (regex on tool names).
- ALWAYS use `${CLAUDE_PLUGIN_ROOT}` for paths — it resolves to wherever the
  plugin got installed on any machine.
- Windows note: if `python3` isn't found, change it to `python`.

**Step 3.** Test the script standalone before trusting it:

```bash
printf '%s' '{"tool_input":{"file_path":"A.java","content":"import lombok.Data;"}}' | python3 hooks/scripts/my_check.py
echo $?   # expect 2 for a violation, 0 for clean input
```

**Step 4.** Hooks do NOT hot-reload. `/reload-plugins` or restart.

⚠️ Hooks run real code on your machine automatically. Never copy a hook script
from the internet into this repo without reading every line.

---

## Recipe 4 — Add a whole NEW PLUGIN

Do this when the topic is genuinely separate (e.g. `marketing`), so people can
install it independently.

**Step 1.** Create the skeleton:

```
plugins/marketing/
├── .claude-plugin/plugin.json
└── skills/           (plus agents/, hooks/ only if needed)
```

**Step 2.** `plugin.json` minimum:

```json
{
  "name": "marketing",
  "version": "0.1.0",
  "description": "Marketing skills: positioning, copywriting, SME outreach.",
  "author": { "name": "Alex Orozov" },
  "license": "MIT"
}
```

**Step 3.** Register it in the catalog — add an entry to the `plugins` array in
`.claude-plugin/marketplace.json` at the REPO ROOT (copy the java-engineering
entry and edit name/source/description). Forgetting this step = plugin invisible.

**Step 4.** Validate: `claude plugin validate ./plugins/marketing`

**Step 5.** Publish (Recipe 5), then `/plugin install marketing@alex-agency`.

---

## Recipe 5 — PUBLISH any change (the loop you'll run every time)

1. Edit files.
2. **Bump the version** in that plugin's `.claude-plugin/plugin.json`
   (`0.1.0` → `0.1.1`). NO BUMP = NO UPDATE: the version is the cache key;
   without bumping, `/plugin update` thinks nothing changed.
3. ```bash
   git add .
   git commit -m "what you changed"
   git push
   ```
4. On every machine that uses it: `/plugin update java-engineering@alex-agency`
   (skills hot-reload in-session; agents/hooks need `/reload-plugins` or restart).

Version bumping convention: bug/typo fix → `0.1.0 → 0.1.1`; new skill/agent/hook
→ `0.1.0 → 0.2.0`; breaking rename or removal → `1.0.0`.

---

## Golden rules (why this repo stays fast and reliable)

1. **Fewer, sharper skills.** Every installed skill's description loads into
   EVERY session. 10 sharp skills > 100 micro-skills. Check the damage anytime:
   `claude plugin details java-engineering` (always-on vs on-invoke token cost).
2. **Don't teach Claude what it already knows.** A skill repeating textbook Java
   is pure token waste. Skills earn their place by encoding OUR conventions, OUR
   snippets, OUR processes.
3. **Extract, don't invent.** Create a skill only after you've explained the same
   thing to Claude twice in real sessions.
4. **Router + references for anything version/variant-shaped** (see
   java-version-guide) instead of one skill per variant.
5. **Non-negotiables become hooks,** not skill text. Skills are probabilistic;
   hooks are guaranteed.
6. **Evaluate before trusting.** Use the official skill-creator plugin
   (`/plugin marketplace add anthropics/claude-plugins-official`) to run evals
   on new/changed skills.

## Roadmap

- `rag-delivery` plugin: qdrant-conventions, langchain4j-patterns, semantic-caching,
  document-ingestion (extracted from BizLex work)
- `ai-services-business` plugin: proposal-writer, sme-discovery, pricing-calculator
- `marketing` plugin: positioning, content, outreach
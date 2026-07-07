#!/usr/bin/env python3
"""PreToolUse hook: block edits to EXISTING Flyway migration files.

Applied migrations are immutable — editing one breaks checksum validation in
every environment that already ran it. Creating NEW migration files is allowed.
Exit 0 = allow, exit 2 = block (stderr shown to Claude).
"""
import json
import os
import re
import sys

MIGRATION_PATH = re.compile(r"db/migrations?/", re.IGNORECASE)

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = payload.get("tool_name", "") or ""
    tool_input = payload.get("tool_input", {}) or {}
    file_path = (tool_input.get("file_path", "") or "").replace("\\", "/")

    if not file_path or not MIGRATION_PATH.search(file_path):
        return 0
    if not file_path.endswith(".sql"):
        return 0

    # Creating a brand-new migration file is fine.
    if tool_name == "Write" and not os.path.exists(file_path):
        return 0

    # Everything else (Edit/MultiEdit on any migration, Write over an existing one) is blocked.
    if os.path.exists(file_path) or tool_name in ("Edit", "MultiEdit"):
        print(
            f"BLOCKED: attempt to modify existing Flyway migration {file_path}. "
            "Applied migrations are immutable (checksum validation will fail everywhere). "
            "Create a NEW versioned migration (V<next>__description.sql) that alters the "
            "schema forward instead.",
            file=sys.stderr,
        )
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())

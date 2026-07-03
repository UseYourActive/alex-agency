#!/usr/bin/env python3
"""PreToolUse hook: block NEW code that uses field injection.

Blocks @Inject/@Autowired placed on a FIELD (declaration ending in ';' with no
parameter list). Constructor/setter injection (annotation followed by a method
signature with '(') is allowed. Only inspects text being written now, so legacy
files are not nagged until touched.
Exit 0 = allow, exit 2 = block (stderr shown to Claude).
"""
import json
import re
import sys

# @Inject or @Autowired, optional other annotations/modifiers, then a field decl:
# Type name; -- i.e. no '(' before the terminating ';'
FIELD_INJECTION = re.compile(
    r"@(?:Inject|Autowired)\b(?:\s*@\w+(?:\([^)]*\))?)*\s*"
    r"(?:(?:private|protected|public|final|transient)\s+)*"
    r"[A-Z][\w.<>,?\s\[\]]*\s+\w+\s*(?:=[^;()]*)?;"
)

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""
    if not file_path.endswith(".java") or "/test/" in file_path.replace("\\", "/"):
        return 0  # allow field injection in tests (@InjectMock etc. patterns vary)

    texts = []
    for key in ("content", "new_string", "file_text", "new_str"):
        val = tool_input.get(key)
        if isinstance(val, str):
            texts.append(val)
    for edit in tool_input.get("edits", []) or []:
        val = (edit or {}).get("new_string")
        if isinstance(val, str):
            texts.append(val)

    blob = "\n".join(texts)
    if not blob:
        return 0

    if FIELD_INJECTION.search(blob):
        print(
            f"BLOCKED: field injection (@Inject/@Autowired on a field) detected in {file_path}. "
            "This codebase requires constructor injection with final fields. "
            "Declare the dependency as a final field and assign it in a constructor "
            "(annotate the constructor with @Inject if the framework requires it).",
            file=sys.stderr,
        )
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())

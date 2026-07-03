#!/usr/bin/env python3
"""PreToolUse hook: block edits that introduce Lombok or MapStruct into Java files.

Reads the tool call JSON from stdin. Exit 0 = allow, exit 2 = block (stderr shown
to Claude so it can self-correct).
"""
import json
import re
import sys

BANNED = [
    (re.compile(r"import\s+lombok\."), "Lombok import"),
    (re.compile(r"@(?:Data|Builder|Getter|Setter|AllArgsConstructor|NoArgsConstructor|RequiredArgsConstructor|Value|Slf4j)\b"), "Lombok annotation"),
    (re.compile(r"import\s+org\.mapstruct\."), "MapStruct import"),
    (re.compile(r"@Mapper\b"), "MapStruct @Mapper annotation"),
]

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # never break the session on malformed input

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""
    if not file_path.endswith(".java"):
        return 0

    # Collect all text this edit would write.
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

    for pattern, label in BANNED:
        if pattern.search(blob):
            print(
                f"BLOCKED: {label} detected in {file_path}. "
                "This codebase forbids Lombok and MapStruct. "
                "Write constructors/getters/equals by hand or use records; "
                "write explicit mapping methods instead of generated mappers.",
                file=sys.stderr,
            )
            return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())

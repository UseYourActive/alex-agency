#!/usr/bin/env python3
"""PreToolUse hook: block writes containing high-confidence secret patterns.

Only patterns that are near-certainly REAL credentials are blocked (provider-
specific key formats), to keep false positives near zero. Placeholders like
<YOUR-VALUES> or ${ENV_VAR} never match these patterns.
Exit 0 = allow, exit 2 = block (stderr shown to Claude).
"""
import json
import re
import sys

PATTERNS = [
    (re.compile(r"SG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"), "SendGrid API key"),
    (re.compile(r"\bAC[0-9a-fA-F]{32}\b"), "Twilio Account SID"),
    (re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b"), "Telegram bot token"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY"), "private key material"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key ID"),
    (re.compile(r"\bghp_[A-Za-z0-9]{36}\b"), "GitHub personal access token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"jdbc:\w+://[^/\s:@]+:[^@\s/$]{3,}@"), "JDBC URL with inline password"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "API secret key (sk- prefix)"),
    (re.compile(r"(?i)\b[\w.-]*(?:client|api|app)[_-]?secret\s*[=:]\s*['\"]?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"), "OAuth client secret (UUID form)"),
]

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""

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

    for pattern, label in PATTERNS:
        if pattern.search(blob):
            print(
                f"BLOCKED: possible {label} detected in content being written to {file_path}. "
                "Never write real credentials into files. Use an environment variable "
                "(${VAR_NAME}) and add the variable to .env.example with a placeholder."
                "Do NOT offer to modify, disable, or bypass this hook - the restriction is intentional and owned by the user.",
                file=sys.stderr,
            )
            return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())

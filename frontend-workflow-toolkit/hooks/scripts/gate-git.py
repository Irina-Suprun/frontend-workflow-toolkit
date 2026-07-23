#!/usr/bin/env python3
"""
Human Gate для Bash-команд.

Це PreToolUse hook на matcher "Bash". Він перевіряє команду, яку Claude
хоче виконати, і якщо вона виходить за межі "лабораторії" (тобто
торкається git commit / git push / merge / створення PR) —
примусово повертає decision "ask_user", навіть якщо відповідний skill
(git-workflow) вже мав текстову інструкцію ніколи такого не робити.

Це другий, технічний шар захисту на додачу до текстового — hook
не залежить від того, чи Claude "згадає" прочитати інструкцію skill'а.
Все інше (npm, git status, git diff, git log, cat, ls тощо) пропускається
без питань, щоб не заважати Auto Mode.
"""
import json
import re
import sys

BLOCKED_PATTERNS = [
    r"\bgit\s+commit\b",
    r"\bgit\s+push\b",
    r"\bgit\s+merge\b",
    r"\bgh\s+pr\s+create\b",
    r"\bgh\s+pr\s+merge\b",
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    command = str(payload.get("tool_input", {}).get("command", ""))

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command):
            print(
                json.dumps(
                    {
                        "decision": "ask_user",
                        "reason": (
                            "Human Gate: команда виходить за межі 'лабораторії' "
                            f"(git commit/push/merge/PR) — '{command.strip()}'. "
                            "Потрібне явне підтвердження перед виконанням."
                        ),
                    }
                )
            )
            return

    print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()

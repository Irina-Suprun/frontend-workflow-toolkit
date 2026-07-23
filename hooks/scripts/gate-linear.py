#!/usr/bin/env python3
"""
Human Gate для Linear.

PreToolUse hook на matcher "mcp__linear__save_issue". Кожен виклик цього
інструменту (створення нового issue АБО оновлення статусу існуючого)
примусово переводиться в decision "ask_user" — незалежно від того, чи
skill linear-task-manager вже показав Markdown-версію issue в чаті.

Це навмисно завжди "ask_user" без додаткової логіки: сам факт виклику
save_issue означає запис у зовнішній трекер, а це завжди критична точка
за визначенням Human Gate.
"""
import json
import sys


def main() -> None:
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        pass

    print(
        json.dumps(
            {
                "decision": "ask_user",
                "reason": (
                    "Human Gate: Linear:save_issue створює або змінює запис у "
                    "зовнішньому трекері. Потрібне явне 'так' перед виконанням."
                ),
            }
        )
    )


if __name__ == "__main__":
    main()

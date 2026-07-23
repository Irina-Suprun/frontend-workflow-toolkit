#!/usr/bin/env python3
"""
Auto Mode: авто-лінт + авто-тест "всередині лабораторії".

PostToolUse hook на matcher "Write|Edit". Після кожної правки файлу
з розширенням .ts / .tsx / .scss автоматично запускає:
  - npm run lint       — для всіх трьох розширень
  - npm test           — тільки для .ts / .tsx (findRelatedTests)

Вивід скрипта потрапляє назад у контекст Claude як результат hook'а,
тож Claude одразу бачить помилки лінту/тестів і може виправити їх сам,
без додаткового запиту від тебе. Це НЕ Human Gate — це працює мовчки
для будь-яких правок коду, бо це "всередині лабораторії", а не назовні.

Якщо у проєкті інші назви npm-скриптів (не "lint"/"test") —
відредагуй команди нижче вручну.
"""
import json
import os
import subprocess
import sys

LINT_EXTENSIONS = (".ts", ".tsx", ".scss")
TEST_EXTENSIONS = (".ts", ".tsx")

# Скрипт запускається з кореня проєкту (там, де Claude Code відкрито),
# тож npm run має підхопити локальний package.json автоматично.


def run(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=100)
        output = (result.stdout or "") + (result.stderr or "")
        return f"$ {' '.join(cmd)}\nexit={result.returncode}\n{output.strip()}"
    except FileNotFoundError:
        return f"$ {' '.join(cmd)}\n[skipped] команду не знайдено"
    except subprocess.TimeoutExpired:
        return f"$ {' '.join(cmd)}\n[timeout] перевищено 100с"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in LINT_EXTENSIONS:
        return

    reports = [run(["npm", "run", "lint", "--", file_path])]

    if ext in TEST_EXTENSIONS:
        reports.append(
            run(["npm", "test", "--", "--findRelatedTests", file_path])
        )

    print("\n\n".join(reports))


if __name__ == "__main__":
    main()

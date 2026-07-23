# frontend-workflow-toolkit

Плагін для роботи над React / Next.js / Redux Toolkit / TypeScript /
SCSS / Jest проєктами. Реалізує гібридний режим **Auto Mode + Human Gate**:

```
[Написання коду / Рефакторинг]
          │
          ▼
   Auto Mode ── авто-лінт + авто-тест (PostToolUse, мовчки)
          │
          ▼
   [Критична точка: PR / Linear / commit]
          │
          ▼
   🛑 Human Gate ── жорстке підтвердження, hook блокує виклик без "так"
```

## Компоненти

### Skills (9)

| Skill | Призначення |
|---|---|
| `architecture-planner` | Проєктування архітектури фічі ДО написання коду (структура папок, дані, UI-стани) |
| `senior-frontend-standards` | Senior-стандарти для React/Next.js/TS/RTK коду (без `any`/`enum`, хуки, мемоізація) |
| `styling-expert` | Senior-рівень SCSS Modules (токени теми, `breakpoint()` mixin, a11y-фокус) |
| `debug-assistant` | Точкова діагностика багів React/Next.js/TS/RTK без переписування файлу |
| `jest-rtl-senior-tests` | Senior unit/integration тести на Jest + RTL |
| `code-reviewer` | Структуроване ревʼю diff'а (🔴 Critical / 🟡 Suggestions / 🟢 Passed) — вручну АБО напівавтоматично перед описом PR |
| `git-workflow` | Conventional Commits повідомлення + описи PR з diff (текст, без виконання команд) |
| `linear-task-manager` | Формує та створює issue в Linear, керує статусами через життєвий цикл |
| `qa-agent` | Повноцінне QA в живому браузері через `playwright`/`chrome-devtools` MCP — тест-план, крос-браузерна перевірка (Chromium/Firefox/WebKit), структурований звіт про баги, збереження звіту у MD-файл |

**Напівавтоматичний Pre-PR крок:** `git-workflow` тепер має Крок 5 —
перед тим, як згенерувати опис PR (Крок 6), він застосовує критерії
`code-reviewer` до diff'а. Якщо знайдено 🔴 Critical — зупиняється і
питає "В коде есть N критических замечаний. Исправим их перед созданием
PR?", і чекає на відповідь, перш ніж рухатись далі. Це логічний крок
усередині skill'а (виконується самим Claude), а не окремий технічний
hook — на відміну від Human Gate для Linear/commit/push, який блокується
жорстко на рівні `hooks.json`.

### MCP-сервери (3)

- **linear** — `https://mcp.linear.app/mcp` (HTTP), потрібен для `linear-task-manager`.
  При першому використанні Claude Code запросить авторизацію (OAuth) —
  жодних токенів у конфігу немає.
- **chrome-devtools** — `npx chrome-devtools-mcp@latest`, потрібен для `qa-agent`
  (консоль, мережа, performance-трейси) та для перевірки живого UI в `debug-assistant`
  і `senior-frontend-standards`.
- **playwright** — `npx @playwright/mcp@latest`, потрібен для `qa-agent`
  (навігація, кліки, форми, resize viewport).

### Hooks (2 події, 3 скрипти)

- **PreToolUse → `gate-git.py`** (matcher `Bash`): перехоплює будь-яку
  bash-команду, і якщо вона містить `git commit`, `git push`, `git merge`,
  `gh pr create` або `gh pr merge` — примусово повертає `ask_user`. Все
  інше (npm, git status/diff/log, читання файлів) пропускається без питань.
- **PreToolUse → `gate-linear.py`** (matcher `mcp__linear__save_issue`):
  завжди повертає `ask_user` перед будь-яким записом у Linear.
- **PostToolUse → `auto-lint-test.py`** (matcher `Write|Edit`): після
  правки файлу з розширенням `.ts`/`.tsx`/`.scss` мовчки запускає
  `npm run lint` (і `npm test -- --findRelatedTests` для `.ts`/`.tsx`),
  результат повертається Claude як контекст — без питань до тебе.

## Налаштування перед першим використанням

1. Скрипти в `hooks/scripts/` розраховують на `npm run lint` та `npm test`
   у `package.json` кореня проєкту. Якщо у тебе інші назви скриптів —
   відредагуй команди в `hooks/scripts/auto-lint-test.py` вручну.
2. Потрібен `python3` у PATH (для запуску hook-скриптів).
3. Для `linear-task-manager` при першому виклику Claude Code запропонує
   підключити Linear через OAuth — підтвердь підключення один раз.

## Важливо

- Плагін нічого не деплоїть і не пушить сам — навіть Auto Mode обмежений
  лінтом і тестами. `git-workflow` завжди залишає commit/push тобі.
- Human Gate — це технічний шар (hook), а не лише текстова інструкція:
  навіть якщо Claude "забуде" запитати, hook фізично не дасть виклику
  пройти без `ask_user`.

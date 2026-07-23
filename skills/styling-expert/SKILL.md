---
name: styling-expert
description: "Забезпечує senior-рівень якості SCSS Modules — заборона \"магічних\" значень (хардкод px/hex замість токенів із теми), мобільна адаптивність через mixin `breakpoint()` та мапу `$breakpoints` (min-width, mobile-first), обмежена вкладеність BEM-селекторів усередині `.module.scss`, та a11y на рівні CSS (`:focus-visible`, клас `.sr-only`, коректна робота з глобальним `outline: none`). ОБОВ'ЯЗКОВО застосовувати цей skill щоразу, коли користувач пише, генерує, рефакторить або рев'ює будь-який SCSS/CSS-код — `.module.scss`, `_theme.scss`, `_mixins.scss`, стилі компонента, адаптивну верстку, медіа-запити, кольори, spacing, typography, focus-стилі — навіть якщо слова \"стилі\" чи \"SCSS\" прямо не прозвучали, а йдеться просто про \"верстку\", \"вигляд компонента\" чи \"чому криво на мобільному\". Використовувати проактивно паралельно з `senior-frontend-standards` для будь-якого фронтенд-коду, що містить стилізацію."
---

# Styling Expert (SCSS Modules & Design Tokens)

Цей skill описує стандарти якості для SCSS Modules у стеку React/Next.js — токенізація значень, мобільна адаптивність, обмежена вкладеність BEM та доступність на рівні CSS. Застосовується до будь-якого `.module.scss`-файлу, а також до змін у `_theme.scss` / `_mixins.scss` / `globals.scss`.

**Джерело правди по токенах і міксинах:**
- `references/theme.scss` — точна копія робочого файлу зі всіма змінними (кольори, типографіка, spacing, тіні, borders, transitions, z-index, breakpoints).
- `references/mixins.scss` — робочий mixin `breakpoint($point)`.
- `references/globals.scss` — глобальний ресет, з якого важливий факт: `outline: none` знято глобально з усіх елементів, і клас `.sr-only` вже існує в проєкті (не `.visually-hidden`).

Перш ніж писати чи рев'юїти стилі, звіряй назви змінних із `references/theme.scss` — **ніколи не вигадуй нову назву токена**, якщо схожа вже існує в файлі. Якщо потрібного токена справді не існує — прямо скажи про це користувачу і запропонуй додати його в `_theme.scss` за тим самим паттерном найменування (не хардкодь значення "тимчасово").

---

## 1. Design-токени: заборона "магічних" значень

**Жодних сирих чисел чи hex-кольорів прямо в `.module.scss`.** Кожне значення кольору, spacing, radius, тіні, transition, z-index чи breakpoint має братися з `_theme.scss` через SCSS-змінну (`$neutral-4`, `$border-radius-md` тощо) — **не** через CSS custom properties `var(--...)`, бо в цьому проєкті токени — це SCSS-змінні, а не CSS-змінні.

Категорії токенів, доступні в `_theme.scss` (повний список — у `references/theme.scss`):

| Категорія | Приклади змінних |
|---|---|
| Кольори — Neutral (grayscale) | `$neutral-1` … `$neutral-13` |
| Кольори — Brand | `$brand-green-1` … `$brand-green-6` |
| Статусні кольори | `$danger-1..6`, `$success-1..6`, `$warning-1..6` |
| Типографіка | `$font-geist`, `$font-size-xs..xxhg`, `$line-height-xs..md` |
| Текст/лінки | `$text-color` |
| Тіні | `$box-shadow-focus`, `$box-shadow-focus-white`, `$box-shadow-cart` |
| Border | `$border-radius-sm/md/lg/pill/circle`, `$border-light`, `$border-base` |
| Spacing | `$base-spacing` (6px), `$secondary-spacing` (2px) |
| Transitions | `$transition-color`, `$transition-background`, `$transition-border-color`, `$transition-transform-ease(-in-out)`, `$transition-opacity-*`, `$transition-box-shadow` |
| Z-index | `$zid-base/raised/floating/overlay/modal` |
| Breakpoints | мапа `$breakpoints` (`xs, sm, 600, md, lg, xl, hg, xhg, xxhg`) |

### Spacing: у проєкті немає повної шкали spacing-токенів

Є лише `$base-spacing: 6px` і `$secondary-spacing: 2px`. Тому:
- Для нестандартних відступів використовуй **множники базового кроку**, а не нові магічні числа:
  ```scss
  // ❌ Магічне число
  .card {
    padding: 18px;
    gap: 14px;
  }

  // ✅ Множник base-spacing (18px = 6px × 3)
  .card {
    padding: $base-spacing * 3;
    gap: $secondary-spacing * 7; // або обґрунтований множник
  }
  ```
- Якщо потрібне значення регулярно повторюється і не є очевидним множником — це сигнал, що варто **запропонувати користувачу додати новий named-токен** у блок `// Spacings` у `_theme.scss` (наприклад `$spacing-lg: 24px;`), а не залишати обчислення розкидані по компонентах.

### Приклад порушення vs виправлення

```scss
// ❌ Погано — hex, px, довільна тінь
.button {
  background-color: #1e4c2f;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: background-color 0.2s ease;
}

// ✅ Добре — усе з токенів теми
@use '@/styles/theme' as *;

.button {
  background-color: $brand-green-6;
  border-radius: $border-radius-sm;
  box-shadow: $box-shadow-cart;
  transition: $transition-background;
}
```

Якщо серед існуючих токенів немає точного відповідника (наприклад, `border-radius-sm` — 8px, а дизайн вимагає 10px) — вкажи на цю розбіжність користувачу замість того, щоб мовчки округлити до найближчого токена або захардкодити нове число.

---

## 2. BEM усередині `.module.scss`: обмежена вкладеність

CSS Modules уже дають локальну ізоляцію імен, тому BEM тут потрібен **для читабельності структури**, а не для запобігання конфліктам класів. Це означає — не переносити плаский BEM 1:1 (`.block__element--modifier` як єдиний клас), а користуватися вкладеністю SCSS ощадливо.

- **Жорсткий орієнтир — не більше 3 рівнів вкладеності** селекторів у файлі. Але це орієнтир, не догма: якщо конкретний компонент має складну внутрішню структуру (наприклад картка зі списком підкарток), допускай виняток — головне свідомо це обґрунтувати, а не вкладати "бо так вийшло".
- **4+ рівні вкладеності — це завжди привід зупинитись і відрефакторити**, незалежно від контексту: винести підблок у власний клас на верхньому рівні або в окремий дочірній компонент.
- Модифікатори (`&--active`, `&--disabled`) та елементи (`&__icon`) можна комбінувати через `&`, але не занурюй `&__element` у `&__element` іншого блока.

```scss
// ❌ Занадто глибоко (4 рівні) і губиться зв'язок з BEM-структурою
.card {
  &__header {
    &__title {
      &--highlighted {
        color: $brand-green-6;
      }
    }
  }
}

// ✅ Плаский BEM-звʼязок у межах модуля (2 рівні максимум)
.card {
  &__header { display: flex; }
  &__title { font-size: $font-size-lg; }
  &__title--highlighted { color: $brand-green-6; }
}
```

- Псевдоелементи/псевдокласи (`&::before`, `&:hover`, `&:focus-visible`) **не рахуються** як BEM-рівень вкладеності — вони природньо гніздяться в межах свого класу.

---

## 3. Адаптивність: mobile-first через `breakpoint()`

У проєкті вже є готовий mixin у `_mixins.scss`:

```scss
@mixin breakpoint($point) {
  @if map.has-key($breakpoints, $point) {
    $min-width: map.get($breakpoints, $point);
    @media (min-width: $min-width) {
      @content;
    }
  }
}
```

Це **строго mobile-first** (тільки `min-width`) — базові стилі без медіа-запиту завжди для найменшого екрана, кожен наступний `@include breakpoint(...)` додає/перевизначає стилі для ширших екранів.

Правила:
- **Ніколи не писати сирий `@media (min-width: ...)` чи `@media (max-width: ...)`** у компонентних стилях — тільки через `@include breakpoint($point)`.
- **Ключ мусить існувати в мапі `$breakpoints`** (`xs, sm, 600, md, lg, xl, hg, xhg, xxhg`). Якщо потрібна нова контрольна точка — запропонуй додати ключ у саму мапу в `_theme.scss`, а не хардкодити довільне значення в медіа-запиті компонента.
- `max-width`-підхід (desktop-first) у цьому mixin не підтримується — якщо є справжня потреба саме в `max-width` (рідкісний виняток, наприклад щоб приховати щось лише на вузьких екранах при mobile-first базі), проговори це з користувачем окремо, а не імітуй через негативну логіку навколо `min-width`.
- На початку кожного `.module.scss`, де використовуються токени й/або breakpoint, підключай:
  ```scss
  @use '@/styles/theme' as *;
  @use '@/styles/mixins' as *;
  ```

```scss
// ✅ Приклад коректного мобільно-орієнтованого компонента
.card {
  padding: $base-spacing * 2;
  flex-direction: column;

  @include breakpoint(md) {
    padding: $base-spacing * 4;
    flex-direction: row;
  }

  @include breakpoint(xl) {
    gap: $base-spacing * 6;
  }
}
```

---

## 4. Доступність (a11y) на рівні CSS

Це доповнює правила з `senior-frontend-standards` (там — HTML/ARIA-семантика), тут фокус — саме на CSS-наслідках.

### 4.1 Критично: глобальний `outline: none`

У `globals.scss` вже стоїть:
```scss
*, *::before, *::after {
  outline: none;
}
```
Це означає, що **дефолтний фокус прибрано глобально для всього проєкту**. Тому будь-який інтерактивний елемент (`button`, `a`, `input`, кастомні клікабельні елементи) **обов'язково повинен отримати власний видимий стан `:focus-visible`** у своєму `.module.scss` — інакше клавіатурні користувачі просто не бачитимуть, де фокус.

```scss
// ❌ Кнопка без власного focus-стилю при глобальному outline: none — фокус невидимий
.button {
  background-color: $brand-green-6;
}

// ✅ Явний, помітний :focus-visible
.button {
  background-color: $brand-green-6;

  &:focus-visible {
    box-shadow: $box-shadow-focus;
    outline: 2px solid transparent; // зберігає geometry для деяких браузерів high-contrast режиму
  }
}
```

Під час рев'ю коду — якщо бачиш інтерактивний елемент без `&:focus-visible` у файлі стилів, **завжди озвучуй це як проблему**, навіть якщо користувач не питав про доступність напряму.

### 4.2 Текст лише для скрінрідерів — використовуй `.sr-only`, а не `display: none`

У проєкті вже є готовий глобальний клас у `globals.scss`:
```scss
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border-width: 0;
}
```
- Використовуй саме цей клас (`.sr-only`), коли текст має бути доступний скрінрідеру, але не показуватись візуально. **Не вигадуй новий `.visually-hidden`** і не приховуй такий текст через `display: none` чи `visibility: hidden` — це прибере його і зі скрінрідера.
- Декоративні елементи (іконки без семантичного значення), навпаки, приховуються через HTML-атрибут `aria-hidden="true"` (це територія `senior-frontend-standards`, не CSS), а не CSS-трюками.

### 4.3 Кросбраузерність фокусу та інпутів (Safari)

- Safari має особливості з `:focus-visible` на деяких версіях і з дефолтними стилями `input`/`textarea` (наприклад, внутрішні тіні, скруглення, `-webkit-appearance`). Явно скидай нативний вигляд там, де це важливо для консистентності:
  ```scss
  input,
  textarea {
    -webkit-appearance: none;
    appearance: none;
  }
  ```
- Ніколи не покладайся тільки на `outline` для позначення фокусу в Safari, якщо `outline` десь глобально приглушено — краще `box-shadow`/`border-color`, які рендеряться консистентно в усіх браузерах (це і робить `$box-shadow-focus` у теми).

---

## 5. Чек-лист для рев'ю SCSS-коду

- [ ] Будь-яке сире число (px, %, unitless) для spacing/radius/font-size → замінити на токен або обґрунтований множник `$base-spacing`
- [ ] Будь-який hex/rgb(a)-колір інлайн → замінити на змінну кольору з `_theme.scss`
- [ ] `var(--...)` замість SCSS-змінної (у цьому проєкті токени — SCSS, не CSS custom properties)
- [ ] Сирий `@media (min-width/max-width: ...)` замість `@include breakpoint($point)`
- [ ] Breakpoint-значення, якого немає в мапі `$breakpoints`
- [ ] Вкладеність селекторів 4+ рівні без явного обґрунтування
- [ ] Інтерактивний елемент без власного `&:focus-visible` при глобальному `outline: none`
- [ ] `display: none` / `visibility: hidden` замість `.sr-only` для контенту "тільки для скрінрідера"
- [ ] Новий вигаданий клас типу `.visually-hidden`, хоча в проєкті вже є `.sr-only`
- [ ] Відсутній `@use '@/styles/theme' as *;` / `@use '@/styles/mixins' as *;` там, де файл фактично використовує токени чи breakpoint

---

## 6. Чого НЕ робити

- Не вигадувати нові назви токенів чи класів, якщо еквівалент уже є в `_theme.scss` / `globals.scss` — завжди спершу перевіряй `references/theme.scss`.
- Не пропонувати CSS custom properties (`var(--spacing-md)`) як рішення "за замовчуванням" — це не відповідає реальній системі проєкту (SCSS-змінні).
- Не приховувати проблему з фокусом мовчки під час рефакторингу — глобальний `outline: none` робить це питання критичним, а не стилістичним.
- Не переносити плаский BEM-нейминг у глибоку вкладеність "за звичкою" — вкладеність має відображати реальну структуру, а не бути автоматичним перекладом класів у SCSS-синтаксис.
- Не хардкодити новий breakpoint прямо в медіа-запиті компонента — завжди пропонувати додати ключ у мапу `$breakpoints`.

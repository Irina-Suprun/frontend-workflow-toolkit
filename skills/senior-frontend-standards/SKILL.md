---
name: senior-frontend-standards
description: "Застосовує senior-рівень стандартів для React/Next.js/TypeScript/Redux Toolkit коду — сувора типізація без `any` та без `enum`, розділення бізнес-логіки та UI через кастомні хуки, типізовані Redux-хуки з мемоізованими селекторами, Server Components за замовчуванням у Next.js, оптимізація рендерів (`useMemo`/`useCallback`), строга файлова структура компонентів (`Component.tsx` + `Component.types.ts` + `Component.module.scss` + `index.ts`), явна обробка станів Loading/Error/Empty/Success, a11y та Jest-орієнтований код. ОБОВ'ЯЗКОВО застосовувати цей skill під час будь-якої генерації, рефакторингу або рев'ю TypeScript/React/Next.js/Redux Toolkit коду — компонентів, кастомних хуків, утиліт, API route-хендлерів, Redux/RTK слайсів та селекторів — навіть якщо користувач явно не згадує \"стандарти\" чи \"типізацію\". Цей skill застосовується проактивно до будь-якого фронтенд-коду в цьому стеку."
---

# Senior Frontend Standards (React / Next.js / TypeScript / Redux Toolkit)

Цей skill описує повний набір архітектурних та стилістичних стандартів senior-рівня, які потрібно застосовувати до **будь-якого** TypeScript/React/Next.js коду — під час генерації нового коду, рефакторингу або рев'ю. Дотримуйся цих правил навіть якщо користувач не просив про це явно.

---

## 1. Архітектура та кастомні хуки

- **UI-компоненти не повинні містити бізнес-логіку.** Стан, fetch-логіку, side-effects, обробку подій із побічними ефектами — все це виносити в кастомні хуки (`useFeature.ts`).
- Компонент отримує вже готові дані та функції з хука і відповідає лише за рендер (JSX) і розмітку.
- Приклад:
  ```ts
  // useUserProfile.ts
  export function useUserProfile(userId: string) {
    const dispatch = useAppDispatch();
    const user = useAppSelector(selectUserById(userId));
    const status = useAppSelector(selectUserStatus);

    useEffect(() => {
      dispatch(fetchUser(userId));
    }, [dispatch, userId]);

    return { user, status };
  }
  ```
  ```tsx
  // UserProfile.tsx
  export const UserProfile = ({ userId }: UserProfileProps) => {
    const { user, status } = useUserProfile(userId);

    if (status === 'loading') return <Spinner />;
    if (status === 'error') return <ErrorMessage />;
    if (!user) return <EmptyState />;

    return <ProfileCard user={user} />;
  };
  ```

## 2. Redux Toolkit: типізовані хуки та мемоізовані селектори

- **Ніколи не використовувати** нетипізовані `useDispatch`/`useSelector` напряму в компонентах чи хуках. Завжди через типізовані обгортки:
  ```ts
  // store/hooks.ts
  import { useDispatch, useSelector, type TypedUseSelectorHook } from 'react-redux';
  import type { RootState, AppDispatch } from './store';

  export const useAppDispatch: () => AppDispatch = useDispatch;
  export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
  ```
- **Складні або похідні селектори** (фільтрація, сортування, обчислення на основі кількох полів стейту) обов'язково мемоізувати через `createSelector` з `@reduxjs/toolkit`, щоб уникнути зайвих ре-рендерів:
  ```ts
  export const selectActiveUsers = createSelector(
    (state: RootState) => state.users.list,
    (users) => users.filter((user) => user.isActive)
  );
  ```
- Прості селектори (пряме читання поля стейту) не потребують `createSelector` — не переускладнюй.

## 3. Next.js та продуктивність

- **Server Components (RSC) за замовчуванням.** Компонент є Server Component, доки не з'явиться явна причина зробити його клієнтським (інтерактивність, хуки стану, браузерні API, event-хендлери).
- **`'use client'` — лише на "листках" дерева компонентів.** Директиву ставити в найменшому можливому за розміром компоненті (наприклад, окрема інтерактивна кнопка чи форма), а не в цілій сторінці чи великому контейнері — щоб не перетворювати весь піддерево на клієнтський бандл.
- **`useMemo`** — для дорогих обчислень (сортування/фільтрація великих масивів, складні трансформації даних).
- **`useCallback`** — для функцій-хендлерів, що передаються в дочірні компоненти (особливо мемоізовані через `React.memo`), щоб уникнути зайвих ре-рендерів дочірніх елементів.
- **Не створювати інлайн об'єкти/функції прямо в JSX-пропсах** — це створює новий референс на кожен рендер і ламає мемоізацію дочірніх компонентів.
  ```tsx
  // ❌ Погано — новий об'єкт і нова функція на кожен рендер
  <UserCard style={{ margin: 8 }} onSelect={() => handleSelect(user.id)} />

  // ✅ Добре
  const cardStyle = useMemo(() => ({ margin: 8 }), []);
  const handleUserSelect = useCallback(() => handleSelect(user.id), [user.id]);
  <UserCard style={cardStyle} onSelect={handleUserSelect} />
  ```

## 4. Стилізація та структура файлів компонента

- Стилізація — **SCSS Modules** (`[Name].module.scss`) для інкапсуляції стилів.
- **Строга структура папки компонента:**
  ```
  Button/
  ├── Button.tsx           ← лише рендер/JSX, імпортує типи та стилі
  ├── Button.types.ts       ← ButtonProps, ButtonVariant тощо
  ├── Button.module.scss
  └── index.ts               ← чистий реекспорт (barrel file)
  ```
  ```ts
  // index.ts
  export { Button } from './Button';
  export type { ButtonProps, ButtonVariant } from './Button.types';
  ```
- Кастомні хуки дотримуються аналогічної логіки — якщо хук має нетривіальні типи (пропси, стан, що повертається), вони виносяться в сусідній `useFeature.types.ts`:
  ```
  useUserProfile/
  ├── useUserProfile.ts
  ├── useUserProfile.types.ts
  └── index.ts
  ```
- Redux/RTK слайси дотримуються тієї ж конвенції — типи стейту, payload-ів екшенів та доменні моделі, специфічні для фічі, лежать у `[feature].types.ts` поряд зі слайсом:
  ```
  features/user/
  ├── userSlice.ts
  ├── userSlice.types.ts     ← UserState, User, UserStatus
  └── index.ts
  ```
- Тривіальні одноразові типи (наприклад, тип одного деструктуризованого параметра, що ніде більше не використовується) можна залишати інлайн — не варто створювати порожній `*.types.ts` під єдиний невеликий тип. Виносити в окремий файл типів варто, якщо тип експортується, використовується повторно або описує реальну доменну сутність (пропси, стан, API-модель).

## 5. Типізація: без `any`, без `enum`

### 5.1 Заборона `any`

`any` заборонено скрізь без винятків. Замість нього:

- **Невідомі/зовнішні дані** (відповіді API, `catch`-блоки, `JSON.parse`, колбеки сторонніх бібліотек): типізувати як `unknown` і звужувати через type guards перед використанням.
  ```ts
  function isString(value: unknown): value is string {
    return typeof value === 'string';
  }

  try {
    // ...
  } catch (error: unknown) {
    if (error instanceof Error) {
      console.error(error.message);
    }
  }
  ```
- **Гнучкі обгортки** (узагальнені хуки, HOC, обгортки API-клієнта, редʼюсери зі змінним payload): використовувати **дженерики** (`<T>`) замість послаблення типу.
  ```ts
  function useFetch<T>(url: string): { data: T | null; error: unknown } { /* ... */ }
  ```
- Якщо виникає бажання поставити `any`, бо тип "занадто складний, щоб описати зараз" — зупинись і або опиши тип повністю (навіть якщо це багатослівно), або використай `unknown` зі звуженням, або запитай у користувача реальну форму даних замість вгадування через `any`.

### 5.2 `interface` vs `type`

- **`interface`** — пропси компонентів та публічні контракти/API-моделі.
  ```ts
  interface ButtonProps {
    label: string;
    onClick: () => void;
    variant?: ButtonVariant;
  }
  ```
- **`type`** — union-типи, примітиви, tuple та utility-типи.
  ```ts
  type ButtonVariant = 'primary' | 'secondary';
  type Coordinates = [x: number, y: number];
  ```

### 5.3 Заборона `enum`

Замість `enum` — union literal types або `as const`-об'єкти (кращий tree-shaking, без зайвого runtime-об'єкта без потреби, краще дружить зі строгим TS-narrowing).

```ts
// ❌ Не так
enum Status {
  Idle,
  Loading,
  Success,
}

// ✅ Union literal type (для простих строкових станів)
type Status = 'idle' | 'loading' | 'success';

// ✅ as const-об'єкт (коли потрібні і ключі, і значення, наприклад для перебору)
const STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
} as const;
type Status = (typeof STATUS)[keyof typeof STATUS];
```

### 5.4 Type-каст `as` — теж під підозрою

Необґрунтований `as SomeType` — це замаскований `any`. Якщо `as` використовується, щоб обійти звуження типу (а не для дійсно безпечного, очевидного випадку), познач це як проблему й запропонуй type guard замість каста.

## 6. Якість коду та UX

- **Доступність (a11y) та інклюзивність за замовчуванням:**
  - **Скрінрідери та семантика:** 
    - Використовувати тільки семантичні HTML5-теги (`<nav>`, `<main>`, `<header>`, `<footer>`, `<article>`, `<aside>`, `<button>`). Заборонено використовувати `<div onClick={...}>` замість інтерактивних елементів.
    - Усі іконки-кнопки або елементи без текстового вмісту повинні мати атрибут `aria-label` або закритий скрінрідер-текст (наприклад, `<span className="visually-hidden">...</span>`).
    - Декоративні зображення та іконки обов'язково позначати через `aria-hidden="true"`, щоб скрінрідер їх ігнорував.
  - **Динамічний вміст та сповіщення:**
    - Для динамічних оновлень сторінки (повідомлення про помилки, зміна стану завантаження, сповіщення) використовувати `aria-live="polite"` (або `aria-live="assertive"` для критичних помилок), щоб скрінрідер зчитував зміну стану без втрати фокусу.
    - Для форм обов'язково зв'язувати `<label>` та `<input>` через `htmlfFor` та `id`, а помилки валідації прив'язувати через `aria-describedby` та `aria-invalid`.
  - **Керування клавіатурою:**
    - Усі інтерактивні елементи повинні бути повністю доступні з клавіатури (`Tab`, `Enter`, `Space`, стрілки).
    - Коректні й чітко помітні `:focus-visible`-стани (ніколи не скидати `outline: none` без заміни на кастомний видимий фокус).
    - Кастомні модальні вікна чи випадаючі меню повинні блокувати фокус всередині себе (Focus Trap) та закриватися за кнопкою `Escape`.

- **Early Return pattern** — уникати глибокої вкладеності `if/else`. Виходити з функції/компонента якнайшвидше для крайніх випадків.
  ```ts
  // ❌ Глибока вкладеність
  function getDiscount(user: User) {
    if (user) {
      if (user.isPremium) {
        if (user.orders.length > 10) {
          return 0.2;
        }
      }
    }
    return 0;
  }

  // ✅ Early return
  function getDiscount(user: User | null) {
    if (!user) return 0;
    if (!user.isPremium) return 0;
    if (user.orders.length <= 10) return 0;
    return 0.2;
  }
  ```
- **Явна обробка чотирьох станів UI** — Loading, Error, Empty, Success — завжди прописані окремо, без "мовчазних" провалів чи `undefined`-рендерів.
  ```tsx
  if (status === 'loading') return <Spinner />;
  if (status === 'error') return <ErrorMessage message={error} />;
  if (!items.length) return <EmptyState />;
  return <ItemList items={items} />;
  ```
- **a11y за замовчуванням**: семантичні HTML5-теги, коректні `:focus-visible`-стани, логічний `tabindex`, ARIA-атрибути там, де семантики HTML недостатньо, коректна робота зі скрінрідерами.
- **Код повинен бути легко тестованим у Jest**: чиста бізнес-логіка в хуках/утилітах (без прив'язки до UI) тестується напряму; компоненти — без надлишкового тестування самого рендеру, фокус на дефолтних станах, екшенах і селекторах.

## 7. Перевірка через Chrome DevTools MCP

Якщо доступний MCP-сервер `chrome-devtools` — під час рев'ю або після написання нетривіального UI-коду не обмежуйся статичним аналізом, а перевіряй результат у живому браузері:

- **Performance** — записуй трейс для компонентів, що рендерять великі списки або роблять важкі обчислення (п.3), і перевіряй, що `useMemo`/`useCallback` дійсно усувають зайві ре-рендери, а не додані "про всяк випадок".
- **Console** — перевіряй відсутність попереджень React/Next.js (hydration mismatch, deprecated API, warning про відсутні `key`).
- **Network** — для компонентів, що роблять fetch, перевіряй порядок і статус запитів (особливо стани Loading/Error з п.6).
- **a11y** — де можливо, перевіряй фокус-порядок і `:focus-visible`-стани (п.6) безпосередньо в браузері, а не тільки по коду.

Якщо MCP-сервер недоступний — просто вкажи користувачу, що саме варто перевірити вручну (без спроби це вгадати).

## 8. Чек-лист для рев'ю/рефакторингу

Під час рев'ю або рефакторингу існуючого коду перевіряти й виправляти:

- [ ] Будь-який `any` → замінити per п.5.1
- [ ] Будь-який `enum` → замінити per п.5.3
- [ ] `interface` для union/tuple або `type` для пропсів → поміняти місцями per п.5.2
- [ ] Бізнес-логіка (fetch, side-effects, стан) всередині компонента замість кастомного хука
- [ ] Нетипізований `useDispatch`/`useSelector` замість `useAppDispatch`/`useAppSelector`
- [ ] Складний селектор без `createSelector`
- [ ] `'use client'` на рівні сторінки/великого контейнера замість листкового компонента
- [ ] Інлайн-об'єкти/функції в JSX-пропсах замість `useMemo`/`useCallback`
- [ ] Нетривіальні типи, визначені інлайн у файлі компонента/хука/слайсу замість сусіднього `*.types.ts`
- [ ] Відсутність окремого стану Loading/Error/Empty у компоненті, що робить fetch
- [ ] Необґрунтований `as SomeType`-каст замість type guard
- [ ] Несемантична верстка (наприклад, `div`/`span` з `onClick` замість `<button>` чи `<a>`)
- [ ] Кнопки-іконки або інтерактивні елементи без `aria-label` чи доступної назви для скрінрідера
- [ ] Відсутність `aria-live` атрибутів для завантажувачів (spinners) або динамічних помилок
- [ ] Відсутність зв'язку між полем вводу та текстом помилки через `aria-describedby` / `aria-invalid`
- [ ] Прихований чи відсутній фокус (`outline: none` без альтернативи для `:focus-visible`)

## 9. Чого НЕ робити

- Не пропускати `any` чи `enum` мовчки під час рев'ю — завжди озвучувати проблему й пропонувати виправлення, навіть якщо користувач не питав конкретно про типізацію.
- Не ставити `'use client'` "на всякий випадок" вище в дереві компонентів, ніж необхідно.
- Не створювати порожній `*.types.ts` для компонента/хука, у якого немає жодного експортованого чи повторно використовуваного типу.
- Не переускладнювати мемоізацією (`useMemo`/`useCallback`/`createSelector`) там, де обчислення й так тривіальне — мемоізація має сенс лише для дорогих обчислень або запобігання зайвим ре-рендерам дочірніх компонентів.
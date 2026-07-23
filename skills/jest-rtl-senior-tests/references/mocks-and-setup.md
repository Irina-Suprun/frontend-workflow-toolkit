# Моки та спільна інфраструктура тестів

Весь код нижче (включно з коментарями та повідомленнями в тестах, що його
використовують) — англійською.

## renderWithProviders

Живе окремим файлом у проєкті, напр. `src/test-utils/renderWithProviders.tsx`.
Дає реальний RTK-стор з попередньо заповненим станом — селектори й connected-компоненти
тестуються "як насправді", без мокання Redux.

```tsx
// src/test-utils/renderWithProviders.tsx
import { render, type RenderOptions } from '@testing-library/react';
import { configureStore, type EnhancedStore } from '@reduxjs/toolkit';
import type { ReactElement, ReactNode } from 'react';
import { Provider } from 'react-redux';
import { rootReducer, type RootState } from '@/store/rootReducer';

interface RenderWithProvidersOptions extends Omit<RenderOptions, 'wrapper'> {
  preloadedState?: Partial<RootState>;
  store?: EnhancedStore<RootState>;
}

export function renderWithProviders(
  ui: ReactElement,
  {
    preloadedState,
    store = configureStore({
      reducer: rootReducer,
      preloadedState: preloadedState as RootState,
    }),
    ...renderOptions
  }: RenderWithProvidersOptions = {},
) {
  function Wrapper({ children }: { children: ReactNode }) {
    return <Provider store={store}>{children}</Provider>;
  }

  return {
    store,
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
  };
}
```

Використання в тесті компонента:

```tsx
renderWithProviders(<UserCard userId="u1" />, {
  preloadedState: {
    users: {
      entities: { u1: { id: 'u1', name: 'Irina', role: 'admin' } },
      status: 'idle',
    },
  },
});
```

Якщо потрібен той самий провайдер для хука — використовуй `renderHook` з опцією
`wrapper`, обгортку бери ту саму `Wrapper`, що і вище (винести в спільний хелпер
`createReduxWrapper(preloadedState)`, щоб не дублювати код між UI- та hook-тестами).

## Мок next/navigation

```tsx
// Place this at the top of the test file, before importing the component
// that uses these hooks.
const mockPush = jest.fn();
const mockReplace = jest.fn();

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: mockReplace,
    back: jest.fn(),
  }),
  usePathname: () => '/profile',
  useSearchParams: () => new URLSearchParams('tab=settings'),
}));

afterEach(() => {
  jest.clearAllMocks();
});
```

Перевіряй навігацію через сам факт виклику з правильними аргументами:

```tsx
expect(mockPush).toHaveBeenCalledWith('/profile/edit');
```

## Мережа: простий jest.fn() vs MSW

**Простий випадок** (один виклик, один сценарій відповіді) — досить мокнути модуль
з API-клієнтом:

```tsx
jest.mock('@/api/userClient', () => ({
  fetchUser: jest.fn(),
}));

import { fetchUser } from '@/api/userClient';

const mockedFetchUser = fetchUser as jest.MockedFunction<typeof fetchUser>;

it('shows the user data after a successful fetch', async () => {
  mockedFetchUser.mockResolvedValueOnce({ id: 'u1', name: 'Irina' });

  render(<UserProfile userId="u1" />);

  expect(await screen.findByText('Irina')).toBeInTheDocument();
});
```

**Складніший випадок** (кілька ендпоінтів, перевірка заголовків/параметрів запиту,
симуляція мережевих помилок на рівні транспорту) — MSW:

```tsx
// src/test-utils/server.ts
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

export const server = setupServer(
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Irina' });
  }),
);
```

```tsx
// in the test file
import { server } from '@/test-utils/server';
import { http, HttpResponse } from 'msw';

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  jest.clearAllMocks();
});
afterAll(() => server.close());

it('shows an error message when the server responds with 500', async () => {
  server.use(
    http.get('/api/users/:id', () => HttpResponse.json(null, { status: 500 })),
  );

  render(<UserProfile userId="u1" />);

  expect(await screen.findByRole('alert')).toHaveTextContent(/failed to load/i);
});
```

Ніколи не мокати `fetch` вручну через `global.fetch = jest.fn()` без типізації — це
джерело `any`-протікань. Або типізований jest.fn() на рівні клієнта, або MSW.

# Тестування кастомних хуків

Весь текст усередині тестового файлу — англійською (describe/it/коментарі/повідомлення
про помилки в fixtures), навіть якщо спілкування з користувачем українською.

## 1. Простий хук зі станом

```tsx
// useCounter.test.ts
import { act, renderHook } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter Hook', () => {
  it('returns 0 as the default initial value', () => {
    const { result } = renderHook(() => useCounter());

    expect(result.current.count).toBe(0);
  });

  it('accepts a custom initial value', () => {
    const { result } = renderHook(() => useCounter({ initialValue: 10 }));

    expect(result.current.count).toBe(10);
  });

  it('increments the counter when increment is called', () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('does not decrement below the configured minimum', () => {
    const { result } = renderHook(() => useCounter({ min: 0 }));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(0);
  });
});
```

## 2. Async-хук (fetch/SWR-подібний)

```tsx
// useUserProfile.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useUserProfile } from './useUserProfile';
import { fetchUser } from '@/api/userClient';

jest.mock('@/api/userClient', () => ({
  fetchUser: jest.fn(),
}));

const mockedFetchUser = fetchUser as jest.MockedFunction<typeof fetchUser>;

describe('useUserProfile Hook', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('starts with status "loading" right after mount', () => {
    mockedFetchUser.mockReturnValue(new Promise(() => {}));

    const { result } = renderHook(() => useUserProfile('u1'));

    expect(result.current.status).toBe('loading');
  });

  it('transitions to status "success" with the fetched data', async () => {
    mockedFetchUser.mockResolvedValueOnce({ id: 'u1', name: 'Irina' });

    const { result } = renderHook(() => useUserProfile('u1'));

    await waitFor(() => {
      expect(result.current.status).toBe('success');
    });
    expect(result.current.data).toEqual({ id: 'u1', name: 'Irina' });
  });

  it('transitions to status "error" with a message when the request fails', async () => {
    mockedFetchUser.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useUserProfile('u1'));

    await waitFor(() => {
      expect(result.current.status).toBe('error');
    });
    expect(result.current.error).toBe('Network error');
  });
});
```

## 3. Хук, залежний від Redux

Використовує ту саму обгортку, що і `renderWithProviders` для UI, але передану як
`wrapper` в `renderHook`.

```tsx
// useCurrentUser.test.ts
import { renderHook } from '@testing-library/react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import type { ReactNode } from 'react';
import { rootReducer, type RootState } from '@/store/rootReducer';
import { useCurrentUser } from './useCurrentUser';

function createWrapper(preloadedState: Partial<RootState>) {
  const store = configureStore({ reducer: rootReducer, preloadedState: preloadedState as RootState });

  return function Wrapper({ children }: { children: ReactNode }) {
    return <Provider store={store}>{children}</Provider>;
  };
}

describe('useCurrentUser Hook', () => {
  it('returns null when no user is authenticated', () => {
    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper({ auth: { currentUserId: null } }),
    });

    expect(result.current).toBeNull();
  });

  it('returns the user matching currentUserId from the store', () => {
    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper({
        auth: { currentUserId: 'u1' },
        users: { entities: { u1: { id: 'u1', name: 'Irina' } }, status: 'success' },
      }),
    });

    expect(result.current).toEqual({ id: 'u1', name: 'Irina' });
  });
});
```

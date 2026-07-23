# Тестування Redux Toolkit (slices, selectors, thunks)

Ключове правило: слайси й селектори тестуються **чистими юніт-тестами, без будь-якого
рендеру UI**. Це найшвидші й найстабільніші тести в проєкті — не обростай їх зайвим.
Весь текст усередині тестового файлу — англійською.

## 1. Slice reducer

```ts
// tasksSlice.test.ts
import { tasksSlice, addTask, toggleTask, removeTask } from './tasksSlice';
import type { TasksState } from './tasksSlice.types';

function createInitialState(overrides: Partial<TasksState> = {}): TasksState {
  return { entities: {}, order: [], ...overrides };
}

describe('tasksSlice', () => {
  it('returns the default state for an unknown action', () => {
    const state = tasksSlice.reducer(undefined, { type: 'unknown' });

    expect(state).toEqual(createInitialState());
  });

  it('adds a new task via addTask', () => {
    const state = tasksSlice.reducer(
      createInitialState(),
      addTask({ id: '1', title: 'New task' }),
    );

    expect(state.entities['1']).toEqual({ id: '1', title: 'New task', isDone: false });
    expect(state.order).toEqual(['1']);
  });

  it('toggles isDone via toggleTask without changing other fields', () => {
    const initial = createInitialState({
      entities: { '1': { id: '1', title: 'Task', isDone: false } },
      order: ['1'],
    });

    const state = tasksSlice.reducer(initial, toggleTask('1'));

    expect(state.entities['1'].isDone).toBe(true);
    expect(state.entities['1'].title).toBe('Task');
  });

  it('ignores toggleTask for an id that does not exist in state', () => {
    const initial = createInitialState();

    const state = tasksSlice.reducer(initial, toggleTask('missing-id'));

    expect(state).toEqual(initial);
  });

  it('removes a task and its id from order via removeTask', () => {
    const initial = createInitialState({
      entities: { '1': { id: '1', title: 'A', isDone: false } },
      order: ['1'],
    });

    const state = tasksSlice.reducer(initial, removeTask('1'));

    expect(state.entities['1']).toBeUndefined();
    expect(state.order).toEqual([]);
  });
});
```

## 2. Selector (+ тест мемоізації)

```ts
// selectors.test.ts
import { selectVisibleTasks } from './selectors';
import type { RootState } from '@/store/rootReducer';

function createState(overrides: Partial<RootState['tasks']> = {}): RootState {
  return {
    tasks: {
      entities: {
        '1': { id: '1', title: 'A', isDone: false },
        '2': { id: '2', title: 'B', isDone: true },
      },
      order: ['1', '2'],
      ...overrides,
    },
  } as RootState;
}

describe('selectVisibleTasks', () => {
  it('returns only the tasks that are not done', () => {
    const result = selectVisibleTasks(createState());

    expect(result).toEqual([{ id: '1', title: 'A', isDone: false }]);
  });

  it('returns an empty array when all tasks are done', () => {
    const state = createState({
      entities: { '1': { id: '1', title: 'A', isDone: true } },
      order: ['1'],
    });

    expect(selectVisibleTasks(state)).toEqual([]);
  });

  it('does not recompute the result for the same state (createSelector memoization)', () => {
    const state = createState();

    const firstResult = selectVisibleTasks(state);
    const secondResult = selectVisibleTasks(state);

    // Same referential identity means createSelector did not re-run the
    // computation function — the cache kicked in.
    expect(firstResult).toBe(secondResult);
  });
});
```

## 3. Thunk

Мокаємо зовнішню залежність (API-клієнт) і `dispatch`, перевіряємо послідовність
`pending → fulfilled/rejected`, без реального мережевого виклику.

```ts
// tasksThunks.test.ts
import { configureStore } from '@reduxjs/toolkit';
import { fetchTasks } from './tasksThunks';
import { tasksSlice } from './tasksSlice';
import { fetchTasksApi } from '@/api/tasksClient';

jest.mock('@/api/tasksClient', () => ({
  fetchTasksApi: jest.fn(),
}));

const mockedFetchTasksApi = fetchTasksApi as jest.MockedFunction<typeof fetchTasksApi>;

function createTestStore() {
  return configureStore({ reducer: { tasks: tasksSlice.reducer } });
}

describe('fetchTasks thunk', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('dispatches pending and then fulfilled with the fetched tasks', async () => {
    mockedFetchTasksApi.mockResolvedValueOnce([{ id: '1', title: 'A', isDone: false }]);
    const store = createTestStore();

    await store.dispatch(fetchTasks());

    expect(store.getState().tasks.entities['1']).toEqual({
      id: '1',
      title: 'A',
      isDone: false,
    });
  });

  it('dispatches rejected with a readable message when the API call fails', async () => {
    mockedFetchTasksApi.mockRejectedValueOnce(new Error('Network error'));
    const store = createTestStore();

    const result = await store.dispatch(fetchTasks());

    expect(result.type).toBe('tasks/fetchTasks/rejected');
    expect(store.getState().tasks.status).toBe('error');
  });
});
```

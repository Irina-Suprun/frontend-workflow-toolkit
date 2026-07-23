# Тестування компонентів

Чотири типові кейси нижче — адаптуй імена/пропси під реальний компонент користувача,
не копіюй буквально. Весь текст усередині тестового файлу (describe/it/коментарі) —
англійською, навіть якщо спілкування з користувачем відбувається українською.

## 1. Презентаційний компонент (без стану, без side-effects)

```tsx
// UserCard.test.tsx
import { render, screen } from '@testing-library/react';
import { UserCard } from './UserCard';
import type { UserCardProps } from './UserCard.types';

function createProps(overrides: Partial<UserCardProps> = {}): UserCardProps {
  return {
    name: 'Ірина Коваль',
    role: 'admin',
    avatarUrl: undefined,
    ...overrides,
  };
}

describe('UserCard Component', () => {
  it('renders the user name and role', () => {
    render(<UserCard {...createProps()} />);

    expect(screen.getByRole('heading', { name: 'Ірина Коваль' })).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
  });

  it('renders a fallback avatar when avatarUrl is not provided', () => {
    render(<UserCard {...createProps({ avatarUrl: undefined })} />);

    expect(screen.getByRole('img', { name: /default avatar/i })).toBeInTheDocument();
  });

  it('handles a very long name without breaking the layout', () => {
    const longName = 'A'.repeat(200);
    render(<UserCard {...createProps({ name: longName })} />);

    expect(screen.getByRole('heading', { name: longName })).toBeInTheDocument();
  });
});
```

## 2. Компонент з формою (валідація + сабміт)

```tsx
// LoginForm.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm Component', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('shows a validation error when the email is malformed', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={jest.fn()} />);

    await user.type(screen.getByLabelText(/email/i), 'not-an-email');
    await user.click(screen.getByRole('button', { name: /log in/i }));

    expect(await screen.findByText(/enter a valid email/i)).toBeInTheDocument();
  });

  it('calls onSubmit with the entered credentials when the form is valid', async () => {
    const handleSubmit = jest.fn();
    const user = userEvent.setup();
    render(<LoginForm onSubmit={handleSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'irina@example.com');
    await user.type(screen.getByLabelText(/password/i), 'securePass123');
    await user.click(screen.getByRole('button', { name: /log in/i }));

    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'irina@example.com',
      password: 'securePass123',
    });
  });

  it('disables the submit button while the request is pending to avoid duplicate submits', async () => {
    const handleSubmit = jest.fn(() => new Promise<void>((resolve) => setTimeout(resolve, 50)));
    const user = userEvent.setup();
    render(<LoginForm onSubmit={handleSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'irina@example.com');
    await user.type(screen.getByLabelText(/password/i), 'securePass123');

    const submitButton = screen.getByRole('button', { name: /log in/i });
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();
  });
});
```

## 3. Компонент зі списком (порожній / заповнений стан)

```tsx
// TaskList.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskList } from './TaskList';
import type { Task } from './TaskList.types';

function createTask(overrides: Partial<Task> = {}): Task {
  return { id: '1', title: 'Sample task', isDone: false, ...overrides };
}

describe('TaskList Component', () => {
  it('shows an empty-state message when there are no tasks', () => {
    render(<TaskList tasks={[]} />);

    expect(screen.getByText(/no tasks yet/i)).toBeInTheDocument();
    expect(screen.queryByRole('list')).not.toBeInTheDocument();
  });

  it('renders all provided tasks in the given order', () => {
    const tasks = [
      createTask({ id: '1', title: 'First' }),
      createTask({ id: '2', title: 'Second' }),
    ];
    render(<TaskList tasks={tasks} />);

    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveTextContent('First');
    expect(items[1]).toHaveTextContent('Second');
  });

  it('marks a task as done when its checkbox is clicked', async () => {
    const handleToggle = jest.fn();
    const user = userEvent.setup();
    render(<TaskList tasks={[createTask()]} onToggle={handleToggle} />);

    await user.click(screen.getByRole('checkbox', { name: 'Sample task' }));

    expect(handleToggle).toHaveBeenCalledWith('1');
  });
});
```

## 4. Компонент з async-станами (loading / success / error)

Найтиповіший кейс для connected-компонентів з Redux — комбінується з
`renderWithProviders` (див. `mocks-and-setup.md`).

```tsx
// UserProfile.test.tsx
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test-utils/renderWithProviders';
import { UserProfile } from './UserProfile';

describe('UserProfile Component', () => {
  it('shows a loading indicator when status is "loading"', () => {
    renderWithProviders(<UserProfile userId="u1" />, {
      preloadedState: { users: { entities: {}, status: 'loading' } },
    });

    expect(screen.getByRole('status', { name: /loading/i })).toBeInTheDocument();
  });

  it('shows the user data when status is "success"', () => {
    renderWithProviders(<UserProfile userId="u1" />, {
      preloadedState: {
        users: {
          entities: { u1: { id: 'u1', name: 'Ірина' } },
          status: 'success',
        },
      },
    });

    expect(screen.getByText('Ірина')).toBeInTheDocument();
  });

  it('shows an error message when status is "error"', () => {
    renderWithProviders(<UserProfile userId="u1" />, {
      preloadedState: {
        users: { entities: {}, status: 'error', error: 'Failed to load the profile' },
      },
    });

    expect(screen.getByRole('alert')).toHaveTextContent('Failed to load the profile');
  });
});
```

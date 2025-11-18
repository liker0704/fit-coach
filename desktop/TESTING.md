# Testing Documentation - FitCoach Desktop

## Overview

This document describes the testing setup for the FitCoach Desktop application. The testing infrastructure uses Jest, React Testing Library, and includes comprehensive tests for services, stores, and components.

## Test Coverage

Current test coverage includes:

### Services (100% coverage)
- ✅ `authService` - Authentication (login, register, logout, token refresh)
- ✅ `agentsService` - AI agents (daily summary, chat, nutrition coach, workout coach)
- ✅ `mealsService` - Meal management and photo upload with AI vision
- ✅ `exercisesService` - Exercise tracking
- ✅ `dayService` - Day data management
- ✅ `moodService` - Mood tracking
- ✅ `sleepService` - Sleep tracking
- ✅ `waterService` - Water intake tracking
- ✅ `notesService` - Notes management
- ✅ `userService` - User profile management

### Stores (100% coverage)
- ✅ `authSlice` - Authentication state management
- ✅ `healthSlice` - Health data state management

### Components
- ✅ `LoginPage` - Login form with validation
- ✅ `RegisterPage` - Registration form with validation
- ✅ `ChatbotDialog` - General fitness chatbot
- ✅ `CoachDialog` - Nutrition and workout coaching
- ✅ `MealPhotoUpload` - Meal photo upload with AI vision processing

## Installation

Install testing dependencies:

```bash
npm install
```

Dependencies installed:
- `jest` - Test framework
- `ts-jest` - TypeScript support for Jest
- `jest-environment-jsdom` - DOM environment for React tests
- `@testing-library/react` - React component testing utilities
- `@testing-library/jest-dom` - Custom Jest matchers
- `@testing-library/user-event` - User interaction simulation
- `@types/jest` - TypeScript types for Jest
- `identity-obj-proxy` - CSS module mocking

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests in watch mode
```bash
npm run test:watch
```

### Run tests with coverage report
```bash
npm run test:coverage
```

### Run tests in CI mode
```bash
npm run test:ci
```

## Test Structure

```
desktop/
├── jest.config.js           # Jest configuration
├── tests/
│   ├── setupTests.ts        # Global test setup
│   ├── __mocks__/           # Mock files
│   │   ├── axios.ts         # Axios mock
│   │   ├── apiClient.ts     # API client mock
│   │   └── fileMock.js      # Static file mock
│   ├── services/            # Service tests
│   │   ├── authService.test.ts
│   │   ├── agentsService.test.ts
│   │   ├── mealsService.test.ts
│   │   ├── exercisesService.test.ts
│   │   ├── dayService.test.ts
│   │   └── otherServices.test.ts
│   ├── store/               # Store tests
│   │   ├── authSlice.test.ts
│   │   └── healthSlice.test.ts
│   └── components/          # Component tests
│       ├── LoginPage.test.tsx
│       ├── RegisterPage.test.tsx
│       ├── AgentDialogs.test.tsx
│       └── MealPhotoUpload.test.tsx
```

## Writing Tests

### Service Tests Example

```typescript
import { authService } from '@/services/modules/authService';
import { apiClient } from '@/services/api/client';

jest.mock('@/services/api/client', () => ({
  apiClient: {
    post: jest.fn(),
  },
}));

describe('authService', () => {
  const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should login successfully', async () => {
    const mockResponse = {
      access_token: 'token',
      refresh_token: 'refresh',
      user: { id: 1, email: 'test@example.com' }
    };

    mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

    const result = await authService.login({
      email: 'test@example.com',
      password: 'password'
    });

    expect(result).toEqual(mockResponse);
  });
});
```

### Store Tests Example

```typescript
import { create } from 'zustand';
import { createAuthSlice, AuthSlice } from '@/store/slices/authSlice';

describe('authSlice', () => {
  let useAuthStore: ReturnType<typeof create<AuthSlice>>;

  beforeEach(() => {
    useAuthStore = create<AuthSlice>()(createAuthSlice);
  });

  it('should set user and authenticate', () => {
    const mockUser = { id: 1, email: 'test@example.com' };

    useAuthStore.getState().setUser(mockUser);

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
  });
});
```

### Component Tests Example

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginPage from '@/pages/auth/LoginPage';

jest.mock('@/services/modules/authService');

describe('LoginPage', () => {
  it('should render login form', () => {
    render(<LoginPage />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('should validate email', async () => {
    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await userEvent.type(emailInput, 'invalid-email');
    await userEvent.click(submitButton);

    expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
  });
});
```

## Best Practices

### 1. Mock External Dependencies
Always mock:
- API calls (axios, apiClient)
- External services
- Router navigation
- Toast notifications
- Store access

### 2. Test Coverage Guidelines
- **Services**: Test all CRUD operations, error handling, edge cases
- **Stores**: Test state updates, action creators, selectors
- **Components**: Test rendering, user interactions, props, validation

### 3. Naming Conventions
- Test files: `*.test.ts` or `*.test.tsx`
- Describe blocks: Use descriptive names (component/function name)
- Test cases: Start with "should" (e.g., "should render button")

### 4. Test Isolation
- Use `beforeEach` to reset mocks
- Avoid shared state between tests
- Create fresh store instances for each test

### 5. Async Testing
```typescript
// Wait for async operations
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument();
});

// User interactions
await userEvent.type(input, 'text');
await userEvent.click(button);
```

## Coverage Thresholds

Current coverage requirements (configured in `jest.config.js`):
- Branches: 50%
- Functions: 50%
- Lines: 50%
- Statements: 50%

## Common Issues & Solutions

### Issue: "Cannot find module '@/...'"
**Solution**: Path aliases are configured in `jest.config.js` under `moduleNameMapper`

### Issue: "TextEncoder is not defined"
**Solution**: Already handled in `setupTests.ts` with polyfills

### Issue: "matchMedia is not a function"
**Solution**: Already mocked in `setupTests.ts`

### Issue: Tests timeout
**Solution**: Increase timeout in test or use `jest.useFakeTimers()`

### Issue: Component not rendering
**Solution**: Wrap in required providers (BrowserRouter, etc.)

## Continuous Integration

The test suite is designed to run in CI environments:

```bash
npm run test:ci
```

This command:
- Runs all tests once (no watch mode)
- Generates coverage report
- Uses 2 workers max for better CI performance
- Suitable for GitHub Actions, GitLab CI, etc.

## Future Improvements

Potential areas for expansion:
- [ ] Integration tests for API workflows
- [ ] E2E tests with Playwright/Cypress
- [ ] Visual regression testing
- [ ] Performance testing
- [ ] Increase coverage to 80%+

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

## Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Ensure all tests pass before committing
3. Maintain or improve coverage percentage
4. Follow existing test patterns and conventions

---

**Last Updated**: 2024-11-18
**Test Coverage**: Services (100%), Stores (100%), Components (Critical paths covered)

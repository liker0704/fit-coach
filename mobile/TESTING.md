# Testing Documentation - FitCoach Mobile App

## Overview

This document describes the testing setup for the FitCoach mobile application built with React Native and Expo. The test suite uses Jest and React Native Testing Library to ensure code quality and reliability.

## Test Coverage

### Current Test Suite

- **Total Test Files**: 16
- **API Services Tests**: 13 services
- **Screen/Component Tests**: 3 critical screens

### Services Tested (API Layer)

1. **authService** (10 tests)
   - Login with email/password
   - User registration
   - Token management
   - User profile retrieval/update
   - Authentication state checks

2. **agentService** (12 tests)
   - Chat message sending
   - Streaming chat responses
   - Food image analysis (Vision AI)
   - Nutrition coach advice
   - Workout coach advice
   - Daily summaries

3. **mealService** (10 tests)
   - CRUD operations for meals
   - Photo upload and processing
   - Vision AI integration
   - Processing status polling

4. **exerciseService** (7 tests)
   - CRUD operations for exercises
   - Heart rate tracking
   - Intensity/duration management

5. **dayService** (8 tests)
   - Day retrieval by date/ID
   - Day creation and updates
   - Date range queries

6. **mealPlanService** (8 tests)
   - AI meal plan generation
   - Plan activation/deactivation
   - CRUD operations

7. **trainingProgramService** (8 tests)
   - AI training program generation
   - Program activation
   - CRUD operations

8. **waterService** (5 tests)
   - Water intake tracking
   - CRUD operations

9. **sleepService** (6 tests)
   - Sleep record management
   - Quality tracking

10. **moodService** (8 tests)
    - Mood tracking with ratings
    - Energy/stress/anxiety levels
    - Tag management

11. **noteService** (7 tests)
    - Note creation with markdown
    - CRUD operations

12. **statisticsService** (6 tests)
    - Weekly/monthly statistics
    - Custom date range queries
    - Multi-metric tracking

### Screens Tested (UI Layer)

1. **LoginScreen** (10 tests)
   - Form validation (email, password)
   - Login flow
   - Error handling
   - Navigation
   - Loading states

2. **RegisterScreen** (10 tests)
   - Form validation (all fields)
   - Password confirmation
   - Registration flow
   - Error handling

3. **DayScreen** (5 tests)
   - Day loading
   - Tab navigation
   - Data display

4. **ChatbotScreen** (9 tests)
   - Message sending
   - Voice input/transcription
   - Streaming responses
   - Error handling

5. **MealPlansScreen** (9 tests)
   - Plan listing
   - Activation/deletion
   - Pull-to-refresh
   - Empty states

## Configuration Files

### jest.config.js

Main Jest configuration with:
- Expo preset
- TypeScript support
- Transform ignore patterns for React Native modules
- Coverage collection settings

### jest.setup.ts

Test environment setup including:
- Mock implementations for Expo modules
- React Navigation mocks
- React Native Paper mocks
- Zustand store mocks
- Global test utilities

## Running Tests

### Install Dependencies

```bash
cd /home/user/fit-coach/mobile
npm install
```

### Run All Tests

```bash
npm test
```

### Run Tests in Watch Mode

```bash
npm run test:watch
```

### Run Tests with Coverage

```bash
npm run test:coverage
```

### Clear Jest Cache

```bash
npm run test:clear
```

## Test Structure

### Service Tests

Located in: `/src/services/api/__tests__/`

Each service test file follows this pattern:

```typescript
import { serviceUnderTest } from '../serviceFile';
import { apiClient } from '../apiClient';

jest.mock('../apiClient');

describe('serviceName', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('methodName', () => {
    it('should perform expected behavior', async () => {
      // Arrange
      const mockData = { /* test data */ };
      mockedApiClient.get.mockResolvedValueOnce({ data: mockData });

      // Act
      const result = await serviceUnderTest.method();

      // Assert
      expect(result).toEqual(mockData);
      expect(mockedApiClient.get).toHaveBeenCalledWith('/endpoint');
    });
  });
});
```

### Screen Tests

Located in: `/src/screens/__tests__/`

Each screen test file follows this pattern:

```typescript
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import ScreenComponent from '../ScreenComponent';

describe('ScreenComponent', () => {
  it('should render correctly', () => {
    const { getByText } = render(<ScreenComponent />);
    expect(getByText('Expected Text')).toBeTruthy();
  });

  it('should handle user interaction', async () => {
    const { getByText } = render(<ScreenComponent />);

    fireEvent.press(getByText('Button'));

    await waitFor(() => {
      expect(/* assertion */).toBeTruthy();
    });
  });
});
```

## Mocking Strategy

### API Mocks

All API calls are mocked using `jest.mock()`:
- `apiClient` (axios instance) is fully mocked
- Service methods return controlled mock data
- Network errors are simulated for error handling tests

### Expo Module Mocks

The following Expo modules are mocked in `jest.setup.ts`:
- `expo-secure-store` - Token storage
- `expo-camera` - Camera permissions and capture
- `expo-image-picker` - Image selection
- `expo-av` - Audio recording/playback
- `expo-notifications` - Push notifications

### Navigation Mocks

React Navigation hooks are mocked:
- `useNavigation()` - Returns mock navigation object
- `useRoute()` - Returns mock route parameters
- `useFocusEffect()` - Executes callback immediately

### Store Mocks

Zustand stores are mocked:
- `useAuthStore` - Authentication state
- `useDayStore` - Day data state

## Best Practices

### Test Organization

1. **Group related tests** using `describe()` blocks
2. **Clear test names** that describe expected behavior
3. **One assertion per test** when possible
4. **Clean up** between tests with `beforeEach()`

### Async Testing

Always use `async/await` and `waitFor()` for asynchronous operations:

```typescript
it('should load data asynchronously', async () => {
  const { getByText } = render(<Component />);

  await waitFor(() => {
    expect(getByText('Data Loaded')).toBeTruthy();
  });
});
```

### Error Testing

Test both success and failure scenarios:

```typescript
it('should handle API errors gracefully', async () => {
  mockedService.method.mockRejectedValueOnce(new Error('Network error'));

  await expect(service.method()).rejects.toThrow('Network error');
});
```

## Test Statistics

### Service Tests

| Service | Test Count | Coverage Areas |
|---------|-----------|----------------|
| authService | 10 | Auth flow, profile, tokens |
| agentService | 12 | AI chat, vision, coaches |
| mealService | 10 | CRUD, photo upload, AI |
| exerciseService | 7 | CRUD, tracking |
| dayService | 8 | CRUD, date queries |
| mealPlanService | 8 | Generation, CRUD |
| trainingProgramService | 8 | Generation, CRUD |
| waterService | 5 | Tracking |
| sleepService | 6 | Tracking, quality |
| moodService | 8 | Tracking, levels |
| noteService | 7 | CRUD, markdown |
| statisticsService | 6 | Aggregation, ranges |

**Total Service Tests**: ~95 tests

### Screen Tests

| Screen | Test Count | Coverage Areas |
|--------|-----------|----------------|
| LoginScreen | 10 | Validation, auth, navigation |
| RegisterScreen | 10 | Validation, registration |
| DayScreen | 5 | Loading, tabs, data |
| ChatbotScreen | 9 | Messaging, voice, streaming |
| MealPlansScreen | 9 | Listing, CRUD, activation |

**Total Screen Tests**: ~43 tests

### Overall Statistics

- **Total Tests**: ~138 tests
- **Test Files**: 16 files
- **Code Coverage**: To be measured after running `npm run test:coverage`

## Coverage Goals

While the current test suite provides comprehensive coverage of critical paths, future improvements could include:

1. **Navigation Tests**: Test routing and deep linking
2. **Store Tests**: Test Zustand state management
3. **Hook Tests**: Test custom React hooks
4. **Integration Tests**: Test complete user flows
5. **E2E Tests**: Test with Detox or Appium

## Continuous Integration

To integrate with CI/CD:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test -- --coverage
```

## Troubleshooting

### Common Issues

1. **Transform errors**: Run `npm run test:clear` to clear Jest cache
2. **Module not found**: Ensure all dependencies are installed
3. **Timeout errors**: Increase timeout in problematic tests with `jest.setTimeout(10000)`

### Debug Mode

Run tests with additional logging:

```bash
npm test -- --verbose
```

Run specific test file:

```bash
npm test -- src/services/api/__tests__/authService.test.ts
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass before committing
3. Maintain minimum 80% coverage for new code
4. Update this document with new test suites

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Native Testing Library](https://callstack.github.io/react-native-testing-library/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import MealPlansScreen from '../meal-plans/MealPlansScreen';
import { mealPlanService, MealPlan } from '../../services/api/mealPlanService';

jest.mock('../../services/api/mealPlanService');
jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({
    navigate: jest.fn(),
  }),
  useFocusEffect: (callback: () => void) => {
    callback();
  },
}));

const mockedMealPlanService = mealPlanService as jest.Mocked<
  typeof mealPlanService
>;

describe('MealPlansScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render loading state initially', () => {
    mockedMealPlanService.getAll = jest.fn(
      () => new Promise(() => {}) // Never resolves
    );

    const { getByText } = render(<MealPlansScreen />);

    expect(getByText('Loading meal plans...')).toBeTruthy();
  });

  it('should load and display meal plans', async () => {
    const mockPlans: MealPlan[] = [
      {
        id: 1,
        user_id: 1,
        name: 'Weight Loss Plan',
        calorie_target: 1800,
        is_active: true,
        created_at: '2025-01-15T10:00:00Z',
        dietary_preferences: ['low-carb'],
        plan_data: {},
      } as MealPlan,
      {
        id: 2,
        user_id: 1,
        name: 'Muscle Gain Plan',
        calorie_target: 2500,
        is_active: false,
        created_at: '2025-01-10T10:00:00Z',
        plan_data: {},
      } as MealPlan,
    ];

    mockedMealPlanService.getAll = jest.fn().mockResolvedValue(mockPlans);

    const { getByText } = render(<MealPlansScreen />);

    await waitFor(() => {
      expect(getByText('Weight Loss Plan')).toBeTruthy();
      expect(getByText('Muscle Gain Plan')).toBeTruthy();
    });
  });

  it('should display empty state when no meal plans', async () => {
    mockedMealPlanService.getAll = jest.fn().mockResolvedValue([]);

    const { getByText } = render(<MealPlansScreen />);

    await waitFor(() => {
      expect(
        getByText(/no meal plans/i) || getByText(/create.*first.*plan/i)
      ).toBeTruthy();
    });
  });

  it('should activate meal plan when activate button pressed', async () => {
    const mockPlans: MealPlan[] = [
      {
        id: 1,
        user_id: 1,
        name: 'Plan 1',
        calorie_target: 2000,
        is_active: false,
        created_at: '2025-01-15T10:00:00Z',
        plan_data: {},
      } as MealPlan,
    ];

    mockedMealPlanService.getAll = jest.fn().mockResolvedValue(mockPlans);
    mockedMealPlanService.activate = jest.fn().mockResolvedValue({
      ...mockPlans[0],
      is_active: true,
    });

    const { getByText, getByTestId } = render(<MealPlansScreen />);

    await waitFor(() => {
      expect(getByText('Plan 1')).toBeTruthy();
    });

    const activateButton =
      getByTestId('activate-button-1') || getByText(/activate/i);
    fireEvent.press(activateButton);

    await waitFor(() => {
      expect(mockedMealPlanService.activate).toHaveBeenCalledWith(1);
    });
  });

  it('should delete meal plan when delete button pressed', async () => {
    const mockPlans: MealPlan[] = [
      {
        id: 1,
        user_id: 1,
        name: 'Plan to Delete',
        calorie_target: 2000,
        is_active: false,
        created_at: '2025-01-15T10:00:00Z',
        plan_data: {},
      } as MealPlan,
    ];

    mockedMealPlanService.getAll = jest
      .fn()
      .mockResolvedValueOnce(mockPlans)
      .mockResolvedValueOnce([]);
    mockedMealPlanService.delete = jest.fn().mockResolvedValue(undefined);

    const { getByText, getByTestId } = render(<MealPlansScreen />);

    await waitFor(() => {
      expect(getByText('Plan to Delete')).toBeTruthy();
    });

    const deleteButton = getByTestId('delete-button-1') || getByText(/delete/i);
    fireEvent.press(deleteButton);

    await waitFor(() => {
      expect(mockedMealPlanService.delete).toHaveBeenCalledWith(1);
    });
  });

  it('should refresh meal plans on pull-to-refresh', async () => {
    const mockPlans: MealPlan[] = [
      {
        id: 1,
        user_id: 1,
        name: 'Test Plan',
        calorie_target: 2000,
        is_active: true,
        created_at: '2025-01-15T10:00:00Z',
        plan_data: {},
      } as MealPlan,
    ];

    mockedMealPlanService.getAll = jest.fn().mockResolvedValue(mockPlans);

    const { getByTestId } = render(<MealPlansScreen />);

    await waitFor(() => {
      expect(mockedMealPlanService.getAll).toHaveBeenCalledTimes(1);
    });

    const scrollView = getByTestId('meal-plans-scroll-view');
    fireEvent(scrollView, 'refresh');

    await waitFor(() => {
      expect(mockedMealPlanService.getAll).toHaveBeenCalledTimes(2);
    });
  });

  it('should show active plan indicator', async () => {
    const mockPlans: MealPlan[] = [
      {
        id: 1,
        user_id: 1,
        name: 'Active Plan',
        calorie_target: 2000,
        is_active: true,
        created_at: '2025-01-15T10:00:00Z',
        plan_data: {},
      } as MealPlan,
      {
        id: 2,
        user_id: 1,
        name: 'Inactive Plan',
        calorie_target: 2000,
        is_active: false,
        created_at: '2025-01-14T10:00:00Z',
        plan_data: {},
      } as MealPlan,
    ];

    mockedMealPlanService.getAll = jest.fn().mockResolvedValue(mockPlans);

    const { getByText } = render(<MealPlansScreen />);

    await waitFor(() => {
      expect(getByText(/active/i)).toBeTruthy();
    });
  });

  it('should display calorie target for each plan', async () => {
    const mockPlans: MealPlan[] = [
      {
        id: 1,
        user_id: 1,
        name: 'Test Plan',
        calorie_target: 2000,
        is_active: true,
        created_at: '2025-01-15T10:00:00Z',
        plan_data: {},
      } as MealPlan,
    ];

    mockedMealPlanService.getAll = jest.fn().mockResolvedValue(mockPlans);

    const { getByText } = render(<MealPlansScreen />);

    await waitFor(() => {
      expect(getByText(/2000.*cal/i)).toBeTruthy();
    });
  });

  it('should handle error when loading meal plans fails', async () => {
    const consoleErrorSpy = jest
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    mockedMealPlanService.getAll = jest
      .fn()
      .mockRejectedValue(new Error('Network error'));

    render(<MealPlansScreen />);

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error loading meal plans:',
        expect.any(Error)
      );
    });

    consoleErrorSpy.mockRestore();
  });
});

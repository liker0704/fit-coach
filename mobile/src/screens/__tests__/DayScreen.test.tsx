import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import DayScreen from '../calendar/DayScreen';
import { useDayStore } from '../../store/dayStore';

jest.mock('../../store/dayStore');
jest.mock('../calendar/tabs/OverviewTab', () => 'OverviewTab');
jest.mock('../calendar/tabs/MealsTab', () => 'MealsTab');
jest.mock('../calendar/tabs/ExerciseTab', () => 'ExerciseTab');
jest.mock('../calendar/tabs/WaterTab', () => 'WaterTab');
jest.mock('../calendar/tabs/SleepTab', () => 'SleepTab');
jest.mock('../calendar/tabs/MoodTab', () => 'MoodTab');
jest.mock('../calendar/tabs/NotesTab', () => 'NotesTab');

const mockedUseDayStore = useDayStore as jest.MockedFunction<typeof useDayStore>;

describe('DayScreen', () => {
  const mockLoadDay = jest.fn();
  const mockRoute = {
    params: {
      date: '2025-01-15',
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render loading state when day is loading', () => {
    mockedUseDayStore.mockReturnValue({
      currentDay: null,
      isLoading: true,
      loadDay: mockLoadDay,
    } as any);

    const { getByText } = render(<DayScreen route={mockRoute} />);

    expect(getByText('Loading day...')).toBeTruthy();
  });

  it('should load day data on mount', () => {
    mockedUseDayStore.mockReturnValue({
      currentDay: {
        id: 1,
        user_id: 1,
        date: '2025-01-15',
      },
      isLoading: false,
      loadDay: mockLoadDay,
    } as any);

    render(<DayScreen route={mockRoute} />);

    expect(mockLoadDay).toHaveBeenCalledWith('2025-01-15');
  });

  it('should render tab view when day is loaded', () => {
    mockedUseDayStore.mockReturnValue({
      currentDay: {
        id: 1,
        user_id: 1,
        date: '2025-01-15',
      },
      isLoading: false,
      loadDay: mockLoadDay,
    } as any);

    const { queryByText } = render(<DayScreen route={mockRoute} />);

    // Should not show loading
    expect(queryByText('Loading day...')).toBeNull();
  });

  it('should reload day when date parameter changes', () => {
    const { rerender } = render(<DayScreen route={mockRoute} />);

    const newRoute = {
      params: {
        date: '2025-01-16',
      },
    };

    rerender(<DayScreen route={newRoute} />);

    expect(mockLoadDay).toHaveBeenCalledWith('2025-01-16');
  });

  it('should have all required tabs', async () => {
    mockedUseDayStore.mockReturnValue({
      currentDay: {
        id: 1,
        user_id: 1,
        date: '2025-01-15',
      },
      isLoading: false,
      loadDay: mockLoadDay,
    } as any);

    const { getByText } = render(<DayScreen route={mockRoute} />);

    await waitFor(() => {
      expect(getByText('Overview')).toBeTruthy();
      expect(getByText('Meals')).toBeTruthy();
      expect(getByText('Exercise')).toBeTruthy();
      expect(getByText('Water')).toBeTruthy();
      expect(getByText('Sleep')).toBeTruthy();
      expect(getByText('Mood')).toBeTruthy();
      expect(getByText('Notes')).toBeTruthy();
    });
  });
});

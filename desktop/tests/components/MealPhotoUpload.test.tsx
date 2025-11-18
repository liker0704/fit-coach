import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MealPhotoUpload } from '@/components/day/MealPhotoUpload';
import { mealsService } from '@/services/modules/mealsService';

// Mock dependencies
jest.mock('@/services/modules/mealsService');

jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

// Mock File and FileReader
global.FileReader = class FileReader {
  onloadend: (() => void) | null = null;
  result: string | null = null;

  readAsDataURL() {
    this.result = 'data:image/jpeg;base64,mock-image-data';
    if (this.onloadend) {
      this.onloadend();
    }
  }
} as any;

describe('MealPhotoUpload', () => {
  const mockOnSuccess = jest.fn();
  const dayId = 1;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('rendering', () => {
    it('should render trigger button', () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      expect(screen.getByRole('button', { name: /add meal photo/i })).toBeInTheDocument();
    });

    it('should open dialog when trigger button clicked', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText(/upload meal photo/i)).toBeInTheDocument();
    });

    it('should render category selector', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      expect(screen.getByLabelText(/meal category/i)).toBeInTheDocument();
    });

    it('should render file upload area', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      expect(screen.getByText(/drag and drop your meal photo here/i)).toBeInTheDocument();
    });
  });

  describe('category selection', () => {
    it('should have lunch selected by default', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const categorySelect = screen.getByLabelText(/meal category/i);
      expect(categorySelect).toHaveTextContent('Lunch');
    });

    it('should allow changing category', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const categorySelect = screen.getByLabelText(/meal category/i);
      await userEvent.click(categorySelect);

      const breakfastOption = screen.getByText('Breakfast');
      await userEvent.click(breakfastOption);

      expect(categorySelect).toHaveTextContent('Breakfast');
    });
  });

  describe('file selection', () => {
    it('should show preview after file selection', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const file = new File(['test'], 'meal.jpg', { type: 'image/jpeg' });
      Object.defineProperty(file, 'size', { value: 1024 * 1024 }); // 1MB

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, file);
      });

      await waitFor(() => {
        expect(screen.getByAltText('Preview')).toBeInTheDocument();
      });
    });

    it('should show file name and size', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const file = new File(['test'], 'my-meal.jpg', { type: 'image/jpeg' });
      Object.defineProperty(file, 'size', { value: 2 * 1024 * 1024 }); // 2MB

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, file);
      });

      await waitFor(() => {
        expect(screen.getByText('my-meal.jpg')).toBeInTheDocument();
        expect(screen.getByText(/2\.00 MB/i)).toBeInTheDocument();
      });
    });

    it('should reject file larger than 10MB', async () => {
      const { toast } = require('@/hooks/use-toast').useToast();

      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const largeFile = new File(['test'], 'large-meal.jpg', { type: 'image/jpeg' });
      Object.defineProperty(largeFile, 'size', { value: 11 * 1024 * 1024 }); // 11MB

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, largeFile);
      });

      // File should not be selected due to size validation
      expect(screen.queryByAltText('Preview')).not.toBeInTheDocument();
    });

    it('should reject non-image files', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const textFile = new File(['test'], 'document.txt', { type: 'text/plain' });
      Object.defineProperty(textFile, 'size', { value: 1024 }); // 1KB

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, textFile);
      });

      // File should not be selected due to type validation
      expect(screen.queryByAltText('Preview')).not.toBeInTheDocument();
    });
  });

  describe('file upload', () => {
    it('should upload file and start processing', async () => {
      const mockUploadResponse = {
        meal_id: 1,
        status: 'processing' as const,
        message: 'Photo uploaded successfully',
        photo_path: '/uploads/meal_1.jpg',
      };

      const mockStatusResponse = {
        meal_id: 1,
        status: 'processing' as const,
      };

      (mealsService.uploadPhoto as jest.Mock).mockResolvedValueOnce(mockUploadResponse);
      (mealsService.getProcessingStatus as jest.Mock).mockResolvedValueOnce(mockStatusResponse);

      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const file = new File(['test'], 'meal.jpg', { type: 'image/jpeg' });
      Object.defineProperty(file, 'size', { value: 1024 * 1024 });

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, file);
      });

      const uploadButton = await screen.findByRole('button', { name: /upload & process/i });
      await userEvent.click(uploadButton);

      await waitFor(() => {
        expect(mealsService.uploadPhoto).toHaveBeenCalledWith(dayId, 'lunch', file);
      });
    });

    it('should show uploading state', async () => {
      (mealsService.uploadPhoto as jest.Mock).mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const file = new File(['test'], 'meal.jpg', { type: 'image/jpeg' });
      Object.defineProperty(file, 'size', { value: 1024 * 1024 });

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, file);
      });

      const uploadButton = await screen.findByRole('button', { name: /upload & process/i });
      await userEvent.click(uploadButton);

      expect(screen.getByText(/uploading/i)).toBeInTheDocument();
    });

    it('should handle upload failure', async () => {
      (mealsService.uploadPhoto as jest.Mock).mockRejectedValueOnce(
        new Error('Upload failed')
      );

      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const file = new File(['test'], 'meal.jpg', { type: 'image/jpeg' });
      Object.defineProperty(file, 'size', { value: 1024 * 1024 });

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, file);
      });

      const uploadButton = await screen.findByRole('button', { name: /upload & process/i });
      await userEvent.click(uploadButton);

      await waitFor(() => {
        expect(mealsService.uploadPhoto).toHaveBeenCalled();
      });
    });
  });

  describe('processing status', () => {
    it('should show processing state', async () => {
      const mockUploadResponse = {
        meal_id: 1,
        status: 'processing' as const,
        message: 'Photo uploaded successfully',
      };

      const mockStatusResponse = {
        meal_id: 1,
        status: 'processing' as const,
      };

      (mealsService.uploadPhoto as jest.Mock).mockResolvedValueOnce(mockUploadResponse);
      (mealsService.getProcessingStatus as jest.Mock).mockResolvedValueOnce(mockStatusResponse);

      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const file = new File(['test'], 'meal.jpg', { type: 'image/jpeg' });
      Object.defineProperty(file, 'size', { value: 1024 * 1024 });

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, file);
      });

      const uploadButton = await screen.findByRole('button', { name: /upload & process/i });
      await userEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText(/processing with ai vision/i)).toBeInTheDocument();
      });
    });

    it('should show completed state with recognized items', async () => {
      const mockUploadResponse = {
        meal_id: 1,
        status: 'processing' as const,
        message: 'Photo uploaded successfully',
      };

      const mockCompletedStatus = {
        meal_id: 1,
        status: 'completed' as const,
        recognized_items: [
          {
            name: 'Chicken breast',
            quantity: 200,
            unit: 'grams',
            confidence: 'high' as const,
          },
        ],
        meal_data: {
          id: 1,
          day_id: dayId,
          category: 'lunch' as const,
          calories: 330,
          protein: 62,
          carbs: 0,
          fat: 7,
          created_at: '2024-01-15T12:00:00Z',
        },
      };

      (mealsService.uploadPhoto as jest.Mock).mockResolvedValueOnce(mockUploadResponse);
      (mealsService.getProcessingStatus as jest.Mock).mockResolvedValueOnce(mockCompletedStatus);

      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const file = new File(['test'], 'meal.jpg', { type: 'image/jpeg' });
      Object.defineProperty(file, 'size', { value: 1024 * 1024 });

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, file);
      });

      const uploadButton = await screen.findByRole('button', { name: /upload & process/i });
      await userEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText(/processing complete/i)).toBeInTheDocument();
        expect(screen.getByText('Chicken breast')).toBeInTheDocument();
        expect(screen.getByText(/330 kcal/i)).toBeInTheDocument();
      });

      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  describe('reset and close', () => {
    it('should reset state when dialog closes', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      expect(screen.getByRole('dialog')).toBeInTheDocument();

      // Close dialog (by clicking outside or escape key)
      const dialog = screen.getByRole('dialog');
      await userEvent.keyboard('{Escape}');

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
    });

    it('should allow removing selected file', async () => {
      render(<MealPhotoUpload dayId={dayId} onSuccess={mockOnSuccess} />);

      const triggerButton = screen.getByRole('button', { name: /add meal photo/i });
      await userEvent.click(triggerButton);

      const file = new File(['test'], 'meal.jpg', { type: 'image/jpeg' });
      Object.defineProperty(file, 'size', { value: 1024 * 1024 });

      const fileInput = screen.getByLabelText(/meal category/i).parentElement?.parentElement
        ?.querySelector('input[type="file"]') as HTMLInputElement;

      await act(async () => {
        await userEvent.upload(fileInput, file);
      });

      await waitFor(() => {
        expect(screen.getByAltText('Preview')).toBeInTheDocument();
      });

      const removeButton = screen.getByRole('button', { name: '' }); // X button
      await userEvent.click(removeButton);

      expect(screen.queryByAltText('Preview')).not.toBeInTheDocument();
    });
  });
});

import { noteService } from '../noteService';
import { apiClient } from '../apiClient';
import type { Note } from '../../../types/models/health';
import type { CreateNoteDto, UpdateNoteDto } from '../noteService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('noteService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should get all notes for a day', async () => {
      const mockNotes: Note[] = [
        {
          id: 1,
          day_id: 1,
          title: 'Morning Thoughts',
          content: 'Feeling energized and ready for the day',
          created_at: '2025-01-15T08:00:00Z',
        } as Note,
        {
          id: 2,
          day_id: 1,
          title: 'Workout Notes',
          content: '# Great session today\n\n- Increased weight on squats\n- PRs on bench',
          created_at: '2025-01-15T18:00:00Z',
        } as Note,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockNotes });

      const result = await noteService.getAll(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days/1/notes');
      expect(result).toEqual(mockNotes);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no notes', async () => {
      mockedApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await noteService.getAll(1);

      expect(result).toEqual([]);
    });
  });

  describe('create', () => {
    it('should create new note with title and content', async () => {
      const createDto: CreateNoteDto = {
        title: 'Daily Reflection',
        content: 'Today was productive. Achieved all my goals.',
      };

      const mockCreatedNote: Note = {
        id: 3,
        day_id: 1,
        title: 'Daily Reflection',
        content: 'Today was productive. Achieved all my goals.',
        created_at: '2025-01-15T20:00:00Z',
      } as Note;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockCreatedNote });

      const result = await noteService.create(1, createDto);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/days/1/notes', createDto);
      expect(result).toEqual(mockCreatedNote);
    });

    it('should create note with only content (no title)', async () => {
      const createDto: CreateNoteDto = {
        content: 'Quick note without a title',
      };

      const mockNote: Note = {
        id: 4,
        day_id: 2,
        content: 'Quick note without a title',
        created_at: '2025-01-15T14:00:00Z',
      } as Note;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockNote });

      const result = await noteService.create(2, createDto);

      expect(result.content).toBe('Quick note without a title');
      expect(result.title).toBeUndefined();
    });

    it('should create note with markdown content', async () => {
      const createDto: CreateNoteDto = {
        title: 'Training Plan',
        content: `# Week 1 Plan

## Monday
- Bench Press 4x8
- Squats 4x10

## Wednesday
- Deadlifts 3x5
- Rows 4x8`,
      };

      const mockNote: Note = {
        id: 5,
        day_id: 1,
        ...createDto,
        created_at: '2025-01-15T10:00:00Z',
      } as Note;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockNote });

      const result = await noteService.create(1, createDto);

      expect(result.content).toContain('# Week 1 Plan');
      expect(result.content).toContain('## Monday');
    });

    it('should create long-form journal entry', async () => {
      const createDto: CreateNoteDto = {
        title: 'Journal Entry',
        content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(50),
      };

      const mockNote: Note = {
        id: 6,
        day_id: 1,
        ...createDto,
        created_at: '2025-01-15T21:00:00Z',
      } as Note;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockNote });

      const result = await noteService.create(1, createDto);

      expect(result.content.length).toBeGreaterThan(100);
    });
  });

  describe('update', () => {
    it('should update note content and title', async () => {
      const updateDto: UpdateNoteDto = {
        title: 'Updated Title',
        content: 'Updated content with new information',
      };

      const mockUpdatedNote: Note = {
        id: 1,
        day_id: 1,
        title: 'Updated Title',
        content: 'Updated content with new information',
        created_at: '2025-01-15T08:00:00Z',
        updated_at: '2025-01-15T09:00:00Z',
      } as Note;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockUpdatedNote });

      const result = await noteService.update(1, updateDto);

      expect(mockedApiClient.put).toHaveBeenCalledWith('/notes/1', updateDto);
      expect(result).toEqual(mockUpdatedNote);
    });

    it('should update only content', async () => {
      const updateDto: UpdateNoteDto = {
        content: 'Just updating the content',
      };

      const mockNote: Note = {
        id: 1,
        day_id: 1,
        title: 'Original Title',
        content: 'Just updating the content',
        created_at: '2025-01-15T08:00:00Z',
      } as Note;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockNote });

      const result = await noteService.update(1, updateDto);

      expect(result.content).toBe('Just updating the content');
    });

    it('should update only title', async () => {
      const updateDto: UpdateNoteDto = {
        title: 'New Title Only',
      };

      const mockNote: Note = {
        id: 1,
        day_id: 1,
        title: 'New Title Only',
        content: 'Original content',
        created_at: '2025-01-15T08:00:00Z',
      } as Note;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockNote });

      const result = await noteService.update(1, updateDto);

      expect(result.title).toBe('New Title Only');
    });
  });

  describe('delete', () => {
    it('should delete note', async () => {
      mockedApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await noteService.delete(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith('/notes/1');
    });

    it('should handle delete error', async () => {
      mockedApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(noteService.delete(999)).rejects.toThrow('Delete failed');
    });
  });
});

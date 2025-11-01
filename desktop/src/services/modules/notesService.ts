import { apiClient } from '../api/client';
import type { Note } from '@/types/models/health';

export interface CreateNoteDto {
  content: string;      // Markdown content
  title?: string;
}

export const notesService = {
  getAll: async (dayId: number): Promise<Note[]> => {
    const response = await apiClient.get(`/days/${dayId}/notes`);
    return response.data;
  },

  create: async (dayId: number, data: CreateNoteDto): Promise<Note> => {
    const response = await apiClient.post(`/days/${dayId}/notes`, data);
    return response.data;
  },

  update: async (noteId: number, data: Partial<CreateNoteDto>): Promise<Note> => {
    const response = await apiClient.put(`/notes/${noteId}`, data);
    return response.data;
  },

  delete: async (noteId: number): Promise<void> => {
    await apiClient.delete(`/notes/${noteId}`);
  }
};

import { apiClient } from './apiClient';
import type { Note } from '../../types/models/health';

export interface CreateNoteDto {
  content: string;      // Markdown content
  title?: string;
}

export interface UpdateNoteDto {
  content?: string;
  title?: string;
}

export const noteService = {
  /**
   * Get all notes for a day
   */
  getAll: async (dayId: number): Promise<Note[]> => {
    const response = await apiClient.get(`/days/${dayId}/notes`);
    return response.data;
  },

  /**
   * Create new note
   */
  create: async (dayId: number, data: CreateNoteDto): Promise<Note> => {
    const response = await apiClient.post(`/days/${dayId}/notes`, data);
    return response.data;
  },

  /**
   * Update note
   */
  update: async (noteId: number, data: UpdateNoteDto): Promise<Note> => {
    const response = await apiClient.put(`/notes/${noteId}`, data);
    return response.data;
  },

  /**
   * Delete note
   */
  delete: async (noteId: number): Promise<void> => {
    await apiClient.delete(`/notes/${noteId}`);
  },
};

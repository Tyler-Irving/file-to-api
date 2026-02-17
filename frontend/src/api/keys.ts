import apiClient from './client';
import type { APIKey } from '../types';

export const keysApi = {
  // Generate new API key
  generate: async (name: string) => {
    const response = await apiClient.post<APIKey>('/keys/', { name });
    return response.data;
  },

  // List API keys
  list: async () => {
    const response = await apiClient.get<APIKey[]>('/keys/');
    return response.data;
  },

  // Revoke API key
  revoke: async (id: string) => {
    await apiClient.delete(`/keys/${id}/`);
  },
};

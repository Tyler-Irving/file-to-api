import apiClient from './client';
import type { Dataset, PaginatedResponse, DataRecord } from '../types';

export const datasetsApi = {
  // Upload a new dataset
  upload: async (file: File, name?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (name) {
      formData.append('name', name);
    }
    
    const response = await apiClient.post<Dataset>('/datasets/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // List all datasets
  list: async () => {
    const response = await apiClient.get<Dataset[]>('/datasets/');
    return response.data;
  },

  // Get dataset detail
  get: async (slug: string) => {
    const response = await apiClient.get<Dataset>(`/datasets/${slug}/`);
    return response.data;
  },

  // Delete dataset
  delete: async (slug: string) => {
    await apiClient.delete(`/datasets/${slug}/`);
  },

  // Get dataset data
  getData: async (slug: string, page = 1, pageSize = 25, filters: Record<string, any> = {}) => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...filters,
    });
    
    const response = await apiClient.get<PaginatedResponse<DataRecord>>(
      `/data/${slug}/?${params}`
    );
    return response.data;
  },

  // Create data record
  createRecord: async (slug: string, data: Record<string, any>) => {
    const response = await apiClient.post<DataRecord>(`/data/${slug}/`, data);
    return response.data;
  },

  // Update data record
  updateRecord: async (slug: string, id: number, data: Record<string, any>) => {
    const response = await apiClient.put<DataRecord>(`/data/${slug}/${id}/`, data);
    return response.data;
  },

  // Delete data record
  deleteRecord: async (slug: string, id: number) => {
    await apiClient.delete(`/data/${slug}/${id}/`);
  },
};

import apiClient from "@/api/axios";
import type { HabitList, PaginatedResponse } from "@/types";

export const listsApi = {
  getAll: (params?: { page?: number }) =>
    apiClient.get<PaginatedResponse<HabitList>>("/lists/", { params }),

  create: (data: { title: string }) =>
    apiClient.post<HabitList>("/lists/", data),

  update: (id: string, data: { title: string }) =>
    apiClient.put<HabitList>(`/lists/${id}/`, data),

  delete: (id: string) => apiClient.delete(`/lists/${id}/`),
};

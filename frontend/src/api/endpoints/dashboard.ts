import apiClient from "@/api/axios";
import type { Habit, PaginatedResponse } from "@/types";

export const dashboardApi = {
  getAll: (params?: { page?: number }) =>
    apiClient.get<PaginatedResponse<Habit>>("/dashboard/", { params }),

  getByList: (listId: string, params?: { page?: number }) =>
    apiClient.get<PaginatedResponse<Habit>>(`/dashboard/${listId}/`, { params }),
};

import apiClient from "@/api/axios";
import type { Habit, HabitLog, PaginatedResponse } from "@/types";

export const habitsApi = {
  getAll: (params?: { page?: number }) =>
    apiClient.get<PaginatedResponse<Habit>>("/habits/", { params }),

  getById: (id: string) => apiClient.get<Habit>(`/habits/${id}/`),

  create: (data: { title: string; periodicity: string; list_id: string }) =>
    apiClient.post<Habit>("/habits/", data),

  update: (
    id: string,
    data: Partial<{ title: string; periodicity: string; list_id: string }>
  ) => apiClient.put<Habit>(`/habits/${id}/`, data),

  delete: (id: string) => apiClient.delete(`/habits/${id}/`),

  checkIn: (id: string) =>
    apiClient.post<HabitLog>(`/habits/${id}/check-in/`),
};

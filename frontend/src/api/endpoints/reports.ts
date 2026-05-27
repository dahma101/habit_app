import apiClient from "@/api/axios";
import type { GeneralReport, Habit, HabitHistoryReport, PaginatedResponse } from "@/types";

export const reportsApi = {
  general: () => apiClient.get<GeneralReport>("/report/general/"),
  all: (params?: { page?: number }) =>
    apiClient.get<PaginatedResponse<Habit>>("/report/all/", { params }),
  habit: (id: string) =>
    apiClient.get<HabitHistoryReport>(`/report/habit/${id}/`),
};

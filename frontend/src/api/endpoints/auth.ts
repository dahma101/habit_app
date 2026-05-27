import apiClient from "@/api/axios";
import type { AuthResponse, User } from "@/types";

export const authApi = {
  register: (data: {
    full_name: string;
    email: string;
    avatar: string;
    password: string;
  }) => apiClient.post<AuthResponse>("/auth/register/", data),

  login: (data: { email: string; password: string }) =>
    apiClient.post<AuthResponse>("/auth/login/", data),

  me: () => apiClient.get<User>("/auth/me/"),
};

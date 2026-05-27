import React, { createContext, useContext } from "react";
import { useAuthStore } from "@/store/authStore";
import type { User } from "@/types";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { user, accessToken, clearAuth } = useAuthStore();

  const logout = () => {
    clearAuth();
    window.location.href = "/auth";
  };

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!accessToken, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

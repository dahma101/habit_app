import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import Layout from "@/components/Layout/Layout";
import AuthPage from "@/pages/Auth/AuthPage";
import DashboardPage from "@/pages/Dashboard/DashboardPage";
import ListsPage from "@/pages/Lists/ListsPage";
import ReportsPage from "@/pages/Reports/ReportsPage";
import HabitReportPage from "@/pages/Reports/HabitReportPage";

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { accessToken } = useAuthStore();
  if (!accessToken) return <Navigate to="/auth" replace />;
  return <Layout>{children}</Layout>;
}

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/auth" element={<AuthPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedLayout>
            <DashboardPage />
          </ProtectedLayout>
        }
      />
      <Route
        path="/lists"
        element={
          <ProtectedLayout>
            <ListsPage />
          </ProtectedLayout>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedLayout>
            <ReportsPage />
          </ProtectedLayout>
        }
      />
      <Route
        path="/reports/habit/:id"
        element={
          <ProtectedLayout>
            <HabitReportPage />
          </ProtectedLayout>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

import { useEffect } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";

import Toast from "@/components/ui/Toast";
import FloatingAssistant from "@/components/properties/FloatingAssistant";
import AppShell from "@/components/layout/AppShell";
import ProtectedRoute from "@/routes/ProtectedRoute";
import LoginPage from "@/pages/LoginPage";
import TwoFactorPage from "@/pages/TwoFactorPage";
import DashboardPage from "@/pages/DashboardPage";
import SavedPage from "@/pages/SavedPage";
import AlertsPage from "@/pages/AlertsPage";
import ProfilePage from "@/pages/ProfilePage";
import SettingsPage from "@/pages/SettingsPage";
import { useAuth } from "@/store/auth";

export default function App() {
  const hydrate = useAuth((s) => s.hydrate);
  const logout = useAuth((s) => s.logout);
  const navigate = useNavigate();

  useEffect(() => {
    void hydrate();
    const onLogout = () => {
      logout();
      navigate("/login");
    };
    window.addEventListener("cb:logout", onLogout);
    return () => window.removeEventListener("cb:logout", onLogout);
  }, [hydrate, logout, navigate]);

  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/verify" element={<TwoFactorPage />} />
        <Route
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/saved" element={<SavedPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toast />
      <FloatingAssistant />
    </>
  );
}
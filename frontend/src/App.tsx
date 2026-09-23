import { Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { AdminDashboardPage } from "./pages/AdminDashboardPage";
import { AnalyticsOverviewPage } from "./pages/AnalyticsOverviewPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { MatchAnalyticsPage } from "./pages/MatchAnalyticsPage";
import { PredictionHistoryPage } from "./pages/PredictionHistoryPage";
import { PredictionsPage } from "./pages/PredictionsPage";
import { PricingPage } from "./pages/PricingPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";
import { ResultsPage } from "./pages/ResultsPage";
import { SettingsPage } from "./pages/SettingsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="analytics" element={<AnalyticsOverviewPage />} />
        <Route path="predictions" element={<PredictionsPage />} />
        <Route path="history" element={<PredictionHistoryPage />} />
        <Route path="results" element={<ResultsPage />} />
        <Route path="pricing" element={<PricingPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="admin" element={<AdminDashboardPage />} />
        <Route path="matches/:id" element={<MatchAnalyticsPage />} />
      </Route>
      <Route path="login" element={<LoginPage />} />
      <Route path="register" element={<RegisterPage />} />
    </Routes>
  );
}

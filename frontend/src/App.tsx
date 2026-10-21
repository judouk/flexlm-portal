import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth";
import { AppLayout } from "./AppLayout";
import { ProtectedRoute } from "./ProtectedRoute";
import { AuditPage } from "./pages/AuditPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DeploymentsPage } from "./pages/DeploymentsPage";
import { LicenseServersPage } from "./pages/LicenseServersPage";
import { LoginPage } from "./pages/LoginPage";
import { OptionsFilesPage } from "./pages/OptionsFilesPage";
import { PublicLicenseSummaryPage } from "./pages/PublicLicenseSummaryPage";
import { UploadsPage } from "./pages/UploadsPage";
import { useUxVersion } from "./ux";
import { ModernLayout } from "./modern/ModernLayout";
import { ModernLoginPage } from "./modern/ModernLoginPage";

export default function App() {
  const modern = useUxVersion() === 2;
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={modern ? <ModernLoginPage /> : <LoginPage />} />
          <Route path="/licences" element={<PublicLicenseSummaryPage />} />

          <Route
            element={
              <ProtectedRoute>
                {modern ? <ModernLayout /> : <AppLayout />}
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<DashboardPage />} />
            <Route path="/servers" element={<LicenseServersPage />} />
            <Route path="/uploads" element={<UploadsPage />} />
            <Route path="/deployments" element={<DeploymentsPage />} />
            <Route path="/options" element={<OptionsFilesPage />} />
            <Route path="/audit" element={<AuditPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

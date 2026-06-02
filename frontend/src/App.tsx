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
import { UploadsPage } from "./pages/UploadsPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
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

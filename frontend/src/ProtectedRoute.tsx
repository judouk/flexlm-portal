import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./auth";
import { useUxVersion } from "./ux";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const version = useUxVersion();
  if (version === 2 && isLoading) {
    return <main className="modern-loading" role="status">Checking your session…</main>;
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

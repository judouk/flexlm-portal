import { Link, Outlet } from "react-router-dom";
import { useAuth } from "./auth";

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>FlexLM</h2>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/servers">License Servers</Link>
          <Link to="/uploads">Uploads</Link>
          <Link to="/deployments">Deployments</Link>
          <Link to="/options">Options Files</Link>
          <Link to="/audit">Audit</Link>
        </nav>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <strong>{user?.sub}</strong> ({user?.role})
          </div>
          <button onClick={logout}>Logout</button>
        </header>

        <Outlet />
      </main>
    </div>
  );
}

import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth";

const navigation = [
  ["/", "Overview"], ["/servers", "License Servers"], ["/uploads", "Uploads"],
  ["/deployments", "Deployments"], ["/options", "Options Files"], ["/audit", "Audit"],
] as const;

export function ModernBrand() {
  return <Link className="modern-brand" to="/"><span aria-hidden="true">F</span> FlexLM Portal</Link>;
}

export function ModernLayout() {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();
  return (
    <div className="modern-shell">
      <a className="modern-skip" href="#portal-content">Skip to content</a>
      <header className="modern-header">
        <ModernBrand />
        <div className="modern-account">
          <div><strong>{user?.sub}</strong><small>{user?.role}</small></div>
          <button className="modern-ghost" onClick={logout}>Sign out</button>
        </div>
      </header>
      <nav className="modern-nav" aria-label="Portal navigation">
        {navigation.map(([path, label]) => (
          <NavLink key={path} to={path} end={path === "/"}>{label}</NavLink>
        ))}
        <Link to="/licences">Public Licence Summary ↗</Link>
      </nav>
      <main id="portal-content" className="modern-content">
        {pathname === "/" && <div className="page-header modern-intro">
          <p className="eyebrow">Licence management</p>
          <h1>Your licences, under control.</h1>
          <p>Manage servers, prepare vendor files and publish validated licence artifacts.</p>
          <div className="modern-shortcuts">
            <Link to="/uploads">Import a licence <span aria-hidden="true">→</span></Link>
            <Link to="/deployments">Review deployments <span aria-hidden="true">→</span></Link>
          </div>
        </div>}
        <Outlet />
      </main>
      <footer className="modern-footer">FlexLM Portal · Licence management</footer>
    </div>
  );
}

import { Link } from "react-router-dom";
import { useLoginForm } from "../useLoginForm";
import { ModernBrand } from "./ModernLayout";

export function ModernLoginPage() {
  const form = useLoginForm();
  return (
    <div className="modern-shell">
      <header className="modern-header"><ModernBrand /><Link className="secondary-link" to="/licences">Public Licence Summary ↗</Link></header>
      <main className="modern-login">
        <section className="modern-login-copy">
          <p className="eyebrow">FlexLM licence management</p>
          <h1>Confidence in every licence.</h1>
          <p className="modern-lede">One place to manage your licence servers, validate vendor files and prepare controlled deployments.</p>
          <ol className="modern-features">
            <li><span>01</span> Import and inspect vendor licence files</li>
            <li><span>02</span> Prepare deployment artifacts with validation</li>
            <li><span>03</span> Record and publish controlled changes</li>
          </ol>
        </section>
        <form className="modern-login-card form-grid" onSubmit={form.handleSubmit}>
          <p className="eyebrow">Portal access</p><h2>Welcome back</h2>
          <p>Sign in with your portal account.</p>
          <label>Username<input autoComplete="username" required value={form.username} onChange={event => form.setUsername(event.target.value)} /></label>
          <label>Password<input type="password" autoComplete="current-password" required value={form.password} onChange={event => form.setPassword(event.target.value)} /></label>
          {form.error && <div className="error" role="alert">{form.error}</div>}
          <button type="submit" disabled={form.submitting}>{form.submitting ? "Signing in…" : "Sign in"}</button>
          <p className="modern-fine-print">Access is restricted to authorised users.</p>
        </form>
      </main>
      <footer className="modern-footer">FlexLM Portal · Licence management</footer>
    </div>
  );
}

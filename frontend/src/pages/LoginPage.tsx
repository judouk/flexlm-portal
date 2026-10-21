import { Link } from "react-router-dom";
import { useLoginForm } from "../useLoginForm";

export function LoginPage() {
  const { username, setUsername, password, setPassword, error, handleSubmit } = useLoginForm("admin");

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>FlexLM Portal</h1>
        <p>Sign in to continue</p>

        <label>
          Username
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button type="submit">Login</button>
        <Link className="secondary-link" to="/licences">
          View public licence summary
        </Link>
      </form>
    </div>
  );
}

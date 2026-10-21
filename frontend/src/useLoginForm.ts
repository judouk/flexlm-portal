import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./auth";

export function useLoginForm(initialValue = "") {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState(initialValue);
  const [password, setPassword] = useState(initialValue);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return { username, setUsername, password, setPassword, error, submitting, handleSubmit };
}

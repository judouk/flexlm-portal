const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export function getToken(): string | null {
  return localStorage.getItem("flexlm_token");
}

export function setToken(token: string): void {
  localStorage.setItem("flexlm_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("flexlm_token");
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();

  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const errorBody = await response.json();

      if (errorBody.detail) {
        message = errorBody.detail;
      }
    } catch {
      // ignore
    }

    throw new Error(message);
  }

  return response.json();
}

export async function apiTextRequest(
  path: string,
  options: RequestInit = {}
): Promise<string> {
  const token = getToken();

  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return response.text();
}

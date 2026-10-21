import React, { createContext, useContext, useEffect, useState } from "react";

import { apiRequest, clearToken, getToken, setToken } from "./api";

type LoginResponse = {
  access_token: string;
  token_type: string;
  role: string;
};

type CurrentUser = {
  sub: string;
  role: string;
  email?: string;
  auth_provider?: string;
};

type AuthContextType = {
  token: string | null;
  user: CurrentUser | null;
  role: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {

  const [token, setTokenState] = useState<string | null>(
    getToken()
  );

  const [user, setUser] = useState<CurrentUser | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);


  async function loadCurrentUser() {
    try {
      const response =
        await apiRequest<CurrentUser>("/me");

      setUser(response);

    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }


  useEffect(() => {
    loadCurrentUser();
  }, []);


  async function login(
    username: string,
    password: string,
  ) {

    const response =
      await apiRequest<LoginResponse>(
        "/login",
        {
          method: "POST",
          body: JSON.stringify({
            username,
            password,
          }),
        }
      );


    setToken(response.access_token);
    setTokenState(response.access_token);

    await loadCurrentUser();
  }


  function logout() {
    clearToken();

    setTokenState(null);
    setUser(null);
  }


  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        role: user?.role ?? null,
        login,
        logout,
        isAuthenticated: Boolean(user),
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}

import { createContext, useContext, useState, useCallback, useMemo, useEffect } from "react";
import { api } from "../api/users.js";

const AuthContext = createContext(null);

const STORAGE_KEY = "auth_user";

function loadUser() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveUser(user) {
  if (user) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
}

export function AuthProvider({ children, initialHash = "" }) {
  const [user, setUser] = useState(loadUser);
  const [authLoading, setAuthLoading] = useState(false);

  const loginWithToken = useCallback(async (token) => {
    const userData = await api.syncUser(token);

    let roles = [];
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      roles = payload.roles || [];
    } catch {
    }

    const authUser = {
      id: userData.id,
      username: userData.username,
      email: userData.email,
      roles,
      token,
    };
    saveUser(authUser);
    setUser(authUser);
    return authUser;
  }, []);

  useEffect(() => {
    if (user) return;

    const hash = initialHash || window.location.hash;
    if (hash && hash.includes("access_token=")) {
      const params = new URLSearchParams(hash.slice(1));
      const accessToken = params.get("access_token");
      const refreshToken = params.get("refresh_token");
      if (accessToken) {
        if (refreshToken) localStorage.setItem("refresh_token", refreshToken);
        setAuthLoading(true);
        loginWithToken(accessToken)
          .then(() => window.location.hash = "")
          .catch(() => window.location.hash = "")
          .finally(() => setAuthLoading(false));
        return;
      }
    }

    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) return;

    setAuthLoading(true);
    loginWithToken(accessToken)
      .then(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      })
      .finally(() => setAuthLoading(false));
  }, [user, loginWithToken]);

  const logout = useCallback(() => {
    saveUser(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    window.location.href = "/auth/login";
  }, []);

  const hasRole = useCallback(
    (role) => user && user.roles.includes(role),
    [user],
  );

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      authLoading,
      isAdmin: user ? user.roles.includes("admin") : false,
      isOwner: user ? user.roles.includes("owner") : false,
      hasRole,
      loginWithToken,
      logout,
    }),
    [user, authLoading, loginWithToken, logout, hasRole],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

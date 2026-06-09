import { createContext, useContext, useState, useCallback, useMemo, useEffect } from "react";

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

export function AuthProvider({ children }) {
  const [user, setUser] = useState(loadUser);
  const [authLoading, setAuthLoading] = useState(false);

  const loginWithToken = useCallback(async (token) => {
    const res = await fetch("/api/v1/auth/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });
    const userData = await res.json();

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

  const logout = useCallback(() => {
    saveUser(null);
    localStorage.removeItem("refresh_token");
    setUser(null);
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
      isModerator: user ? user.roles.includes("moderator") : false,
      canModerate: user ? (user.roles.includes("admin") || user.roles.includes("moderator")) : false,
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

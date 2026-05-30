import { createContext, useContext, useState, useCallback, useMemo } from "react";
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

export function AuthProvider({ children }) {
  const [user, setUser] = useState(loadUser);

  const login = useCallback(async (username) => {
    const data = await api.listUsers(0, 1000);
    const found = data.users.find(
      (u) => u.username === username || u.email === username,
    );
    if (!found) {
      throw new Error("Пользователь не найден");
    }

    const detail = await api.getUser(found.id);
    const authUser = {
      id: detail.id,
      username: detail.username,
      email: detail.email,
      roles: detail.roles || [],
      token: "demo-token",
    };
    saveUser(authUser);
    setUser(authUser);
    return authUser;
  }, []);

  const logout = useCallback(() => {
    saveUser(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAdmin: user ? user.roles.includes("admin") : false,
      login,
      logout,
    }),
    [user, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

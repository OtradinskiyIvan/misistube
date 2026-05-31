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

  const loginWithToken = useCallback(async (token) => {
    const decoded = await api.decodeToken(token);
    const { sub, username, email, roles } = decoded.payload;

    let userData;
    try {
      userData = await api.getUser(sub);
    } catch {
      throw new Error("Пользователь не найден. Доступ запрещён.");
    }

    const authUser = {
      id: userData.id,
      username: userData.username,
      email: userData.email,
      roles: roles || [],
      token,
    };
    saveUser(authUser);
    setUser(authUser);
    return authUser;
  }, []);

  const logout = useCallback(() => {
    saveUser(null);
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
      isAdmin: user ? user.roles.includes("admin") : false,
      isOwner: user ? user.roles.includes("owner") : false,
      hasRole,
      loginWithToken,
      logout,
    }),
    [user, loginWithToken, logout, hasRole],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

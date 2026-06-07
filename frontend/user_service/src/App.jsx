import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import AdminPage from "./pages/AdminPage.jsx";
import SearchPage from "./pages/SearchPage.jsx";
import UserPage from "./pages/UserPage.jsx";

const AUTH_SERVICE_URL = "http://localhost:5174";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/users/:userId" element={<UserPage />} />
        <Route path="/auth/*" element={<Navigate to={AUTH_SERVICE_URL} replace />} />
        <Route path="*" element={<Navigate to="/profile" replace />} />
      </Route>
    </Routes>
  );
}

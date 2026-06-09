import { useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import AdminPage from "./pages/AdminPage.jsx";
import SearchPage from "./pages/SearchPage.jsx";
import UserPage from "./pages/UserPage.jsx";

function ExternalRedirect({ to }) {
  const location = useLocation();
  useEffect(() => {
    window.location.replace(to + location.hash);
  }, []);
  return null;
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/users/:userId" element={<UserPage />} />
        <Route path="/auth/*" element={<ExternalRedirect to="/auth/" />} />
        <Route path="*" element={<Navigate to="/profile" replace />} />
      </Route>
    </Routes>
  );
}

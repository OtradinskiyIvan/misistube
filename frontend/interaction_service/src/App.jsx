import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import VideoInteractionsPage from "./pages/VideoInteractionsPage.jsx";
import AdminCommentsPage from "./pages/AdminCommentsPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/video/:videoId" element={<VideoInteractionsPage />} />
        <Route path="/admin/comments" element={<AdminCommentsPage />} />
        <Route path="*" element={<Navigate to="/admin/comments" replace />} />
      </Route>
    </Routes>
  );
}

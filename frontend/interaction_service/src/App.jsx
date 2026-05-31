import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import VideoInteractionsPage from "./pages/VideoInteractionsPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/video/:videoId" element={<VideoInteractionsPage />} />
        <Route path="*" element={<Navigate to="/video/1" replace />} />
      </Route>
    </Routes>
  );
}

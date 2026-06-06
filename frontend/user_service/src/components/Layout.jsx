import { Outlet } from "react-router-dom";
import Header from "./Header.jsx";

export default function Layout() {
  return (
    <>
      <Header />
      <main className="container" style={{ paddingTop: "2rem", paddingBottom: "2rem" }}>
        <Outlet />
      </main>
    </>
  );
}

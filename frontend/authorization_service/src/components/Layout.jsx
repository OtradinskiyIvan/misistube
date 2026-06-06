import Header from "./Header.jsx";

export default function Layout({ children }) {
  return (
    <>
      <Header />
      <main className="container" style={{ paddingTop: "2rem", paddingBottom: "2rem" }}>
        {children}
      </main>
    </>
  );
}

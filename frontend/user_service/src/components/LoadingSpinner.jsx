export default function LoadingSpinner({ text = "Загрузка..." }) {
  return (
    <div style={{ textAlign: "center", padding: "3rem 0" }}>
      <div
        style={{
          width: "40px",
          height: "40px",
          border: "4px solid var(--misis-gray-200)",
          borderTopColor: "var(--misis-light)",
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
          margin: "0 auto 1rem",
        }}
      />
      <p style={{ color: "var(--misis-text-dark)", opacity: 0.7 }}>{text}</p>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

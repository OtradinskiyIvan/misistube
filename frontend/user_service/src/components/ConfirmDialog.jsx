export default function ConfirmDialog({ title, message, confirmLabel = "Удалить", cancelLabel = "Отмена", onConfirm, onCancel, loading }) {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0,0,0,0.4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
      onClick={onCancel}
    >
      <div
        className="card fade-in"
        style={{ maxWidth: "420px", width: "100%", padding: "1.5rem" }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ marginBottom: "0.5rem" }}>{title}</h3>
        <p style={{ marginBottom: "1.5rem", opacity: 0.8 }}>{message}</p>
        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
          <button className="btn btn-secondary" onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </button>
          <button className="btn btn-primary" onClick={onConfirm} disabled={loading}>
            {loading ? "Удаление..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

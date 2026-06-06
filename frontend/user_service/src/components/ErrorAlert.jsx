export default function ErrorAlert({ message, onClose }) {
  if (!message) return null;

  return (
    <div
      style={{
        backgroundColor: "#FEF2F2",
        border: "1px solid #FECACA",
        borderRadius: "var(--misis-radius-md)",
        padding: "0.75rem 1rem",
        marginBottom: "1rem",
        color: "#991B1B",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <span>{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            fontSize: "1.25rem",
            color: "#991B1B",
            marginLeft: "0.5rem",
          }}
        >
          &times;
        </button>
      )}
    </div>
  );
}

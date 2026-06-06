const STATUS_MAP = {
  active: { label: "Активен", className: "badge-success" },
  inactive: { label: "Неактивен", className: "badge-warning" },
  banned: { label: "Забанен", className: "badge-error" },
  suspended: { label: "Приостановлен", className: "badge-info" },
};

export default function StatusBadge({ status }) {
  const config = STATUS_MAP[status] || { label: status, className: "badge-neutral" };
  return <span className={`badge ${config.className}`}>{config.label}</span>;
}

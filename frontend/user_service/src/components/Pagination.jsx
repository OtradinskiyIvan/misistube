export default function Pagination({ skip, limit, total, onSkipChange }) {
  const totalPages = Math.ceil(total / limit) || 1;
  const currentPage = Math.floor(skip / limit) + 1;

  if (total <= limit) return null;

  return (
    <div className="pagination">
      <button
        className="btn btn-sm btn-secondary"
        disabled={currentPage <= 1}
        onClick={() => onSkipChange(Math.max(0, skip - limit))}
      >
        ← Назад
      </button>
      <span className="pagination__info">
        Страница {currentPage} из {totalPages} (всего {total})
      </span>
      <button
        className="btn btn-sm btn-secondary"
        disabled={skip + limit >= total}
        onClick={() => onSkipChange(skip + limit)}
      >
        Вперёд →
      </button>
    </div>
  );
}

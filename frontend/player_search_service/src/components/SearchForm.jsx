import React, { useState } from 'react';

function SearchForm({ onSearch, isLoading }) {
  const [query, setQuery] = useState('');
  const [limit, setLimit] = useState(10);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch({ query: query.trim(), limit, offset: 0 });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="search-form mb-6">
      <div className="form-group">
        <div style={{ display: 'flex', gap: '1rem' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Поиск видео по названию или тегам..."
            className="input"
            style={{ flex: 1 }}
            disabled={isLoading}
          />
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="input"
            style={{ width: '120px' }}
            disabled={isLoading}
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? <span className="loading-spinner" /> : 'Найти'}
          </button>
        </div>
      </div>
    </form>
  );
}

export default SearchForm;
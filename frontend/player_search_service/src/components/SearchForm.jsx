import { useState } from 'react'

export default function SearchForm({ onSearch }) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch({ q: query })
  }

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <div className="form-group">
        <label className="label" htmlFor="search-input">Поиск видео</label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            id="search-input"
            type="text"
            className="input"
            placeholder="Введите запрос..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">
            Найти
          </button>
          {query && (
            <button 
              type="button" 
              className="btn btn-outline"
              onClick={() => {
                setQuery('')
                onSearch({ q: '' })
              }}
            >
              Сбросить
            </button>
          )}
        </div>
      </div>
    </form>
  )
}
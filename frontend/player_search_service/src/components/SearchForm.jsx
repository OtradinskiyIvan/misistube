import { useState } from 'react'

export default function SearchForm({ onSearch }) {
  const [query, setQuery] = useState('')
  const [selectedTags, setSelectedTags] = useState([])

  const availableTags = ['коты', 'python', 'docker', 'tutorial', 'милота', 'devops']

  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch({ q: query, tags: selectedTags })
  }

  const toggleTag = (tag) => {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    )
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
        </div>
      </div>

      <div className="form-group">
        <label className="label">Фильтр по тегам</label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {availableTags.map(tag => (
            <button
              key={tag}
              type="button"
              className={`btn btn-sm ${selectedTags.includes(tag) ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => toggleTag(tag)}
            >
              #{tag}
            </button>
          ))}
        </div>
      </div>
    </form>
  )
}
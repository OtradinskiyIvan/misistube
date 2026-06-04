import { useState, useCallback, useRef } from 'react'
import SearchForm from '../components/SearchForm'
import VideoCard from '../components/VideoCard'

export default function SearchPage() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const abortControllerRef = useRef(null)

  const handleSearch = useCallback(async ({ q, tags }) => {
    if (!q && tags.length === 0) return

    if (abortControllerRef.current) abortControllerRef.current.abort()
    abortControllerRef.current = new AbortController()

    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (q) params.append('q', q)
      tags.forEach(tag => params.append('tags', tag))
      params.append('limit', '10')

      const response = await fetch(`http://localhost:8000/api/v1/search?${params.toString()}`, {
        signal: abortControllerRef.current.signal
      })
      const data = await response.json()
      setResults(data.items || [])
      setHasSearched(true)
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Search error:', error)
        setResults([])
      }
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <div className="container" style={{ paddingTop: '1.5rem', paddingBottom: '3rem' }}>
      <h1 style={{ marginBottom: '1.5rem' }}>Поиск видео</h1>
      <SearchForm onSearch={handleSearch} />

      {loading && <div className="text-center" style={{ padding: '2rem' }}>Загрузка...</div>}

      {!loading && !hasSearched && (
        <p className="text-center" style={{ color: 'var(--misis-gray-300)', marginTop: '2rem' }}>
          Введите запрос или выберите теги для поиска
        </p>
      )}

      {!loading && hasSearched && results.length === 0 && (
        <p className="text-center" style={{ color: 'var(--misis-gray-300)', marginTop: '2rem' }}>
          Ничего не найдено. Попробуйте изменить запрос или выбрать другие теги.
        </p>
      )}

      {!loading && results.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3" style={{ display: 'grid', gap: '1rem' }}>
          {results.map(video => (
            <VideoCard key={video.id} video={video} />
          ))}
        </div>
      )}
    </div>
  )
}
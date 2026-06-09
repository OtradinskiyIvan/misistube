import { useState, useCallback, useRef, useEffect } from 'react'
import SearchForm from '../components/SearchForm'
import VideoCard from '../components/VideoCard'

export default function SearchPage() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const abortControllerRef = useRef(null)

  const handleSearch = useCallback(async ({ q }) => {
    if (abortControllerRef.current) abortControllerRef.current.abort()
    abortControllerRef.current = new AbortController()

    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (q) params.append('q', q)
      params.append('limit', '50')

      const response = await fetch(`/api/v1/search?${params.toString()}`, {
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

  // Автозагрузка всех видео при открытии страницы
  useEffect(() => {
    handleSearch({ q: '' })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="container" style={{ paddingTop: '1.5rem', paddingBottom: '3rem' }}>
      <h1 style={{ marginBottom: '1.5rem' }}>Видео</h1>
      <SearchForm onSearch={handleSearch} />

      {loading && <div className="text-center" style={{ padding: '2rem' }}>Загрузка...</div>}

      {!loading && !hasSearched && (
        <p className="text-center" style={{ color: 'var(--misis-gray-300)', marginTop: '2rem' }}>
          Загрузка видео...
        </p>
      )}

      {!loading && hasSearched && results.length === 0 && (
        <p className="text-center" style={{ color: 'var(--misis-gray-300)', marginTop: '2rem' }}>
          Ничего не найдено. Попробуйте изменить запрос.
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
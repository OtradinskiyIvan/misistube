import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import AuthorCard from '../components/AuthorCard'

export default function WatchPage() {
  const { id } = useParams()
  const [videoUrl, setVideoUrl] = useState(null)
  const [video, setVideo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        setLoading(true)
        // Получаем presigned URL для видео
        const response = await fetch(`/api/v1/playback/${id}`)
        
        if (!response.ok) {
          throw new Error('Видео не найдено')
        }
        
        const data = await response.json()
        setVideoUrl(data.hls_master_url)
        
        // Дополнительно получаем информацию о видео
        const searchResponse = await fetch(`/api/v1/search?q=&limit=100`)
        const searchData = await searchResponse.json()
        const foundVideo = searchData.items?.find(v => v.id === id)
        if (foundVideo) {
          setVideo(foundVideo)
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchVideo()
  }, [id])

  if (loading) {
    return (
      <div className="container" style={{ padding: '3rem 0' }}>
        <div className="text-center">Загрузка видео...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container" style={{ padding: '3rem 0' }}>
        <div className="card" style={{ padding: '2rem', textAlign: 'center' }}>
          <h2 style={{ color: 'var(--misis-dark)', marginBottom: '1rem' }}>Ошибка</h2>
          <p style={{ color: 'var(--misis-gray-300)', marginBottom: '1.5rem' }}>{error}</p>
          <Link to="/search" className="btn btn-primary">
            ← Вернуться к поиску
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="container" style={{ paddingTop: '1.5rem', paddingBottom: '3rem' }}>
      {/* Кнопка назад */}
      <Link to="/search" className="btn btn-sm btn-outline" style={{ marginBottom: '1rem', width: 'fit-content' }}>
        ← Назад к поиску
      </Link>

      {/* Видео плеер */}
      <div className="card" style={{ marginBottom: '1.5rem', overflow: 'hidden' }}>
        {videoUrl ? (
          <video
            controls
            autoPlay
            style={{
              width: '100%',
              maxHeight: '70vh',
              backgroundColor: '#000'
            }}
            src={videoUrl}
          >
            Ваш браузер не поддерживает видео
          </video>
        ) : (
          <div style={{ 
            padding: '15rem', 
            textAlign: 'center', 
            backgroundColor: 'var(--misis-gray-100)',
            color: 'var(--misis-gray-300)'
          }}>
            Видео недоступно
          </div>
        )}
      </div>

      {/* Информация о видео */}
      {video && (
        <>
          <div className="card" style={{ padding: '1.5rem', marginBottom: '1rem' }}>
            <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{video.title}</h1>
            
            {video.description && (
              <p style={{ color: 'var(--misis-text-dark)', opacity: 0.8, marginBottom: '1rem' }}>
                {video.description}
              </p>
            )}

            <div style={{ 
              display: 'flex', 
              gap: '1rem', 
              alignItems: 'center',
              flexWrap: 'wrap',
              marginBottom: '1rem'
            }}>
              <span style={{ color: 'var(--misis-gray-300)', fontSize: '0.875rem' }}>
                ⏱ {Math.floor((video.duration_seconds || 0) / 60)}:{String((video.duration_seconds || 0) % 60).padStart(2, '0')}
              </span>
              
              {video.status && (
                <span className={`badge status-${video.status.toLowerCase()}`}>
                  {video.status}
                </span>
              )}
            </div>

            {video.tags && video.tags.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {video.tags.map((tag, idx) => (
                  <span key={idx} className="badge badge-info">
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Плашка автора */}
          <AuthorCard 
            author={{
              user_id: video.user_id,
              username: video.username
            }} 
          />
        </>
      )}

      {/* Действия */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        <button className="btn btn-secondary">
          ♡ В избранное
        </button>
        <button className="btn btn-outline">
          ↗ Поделиться
        </button>
        <button className="btn btn-outline">
          ⬇ Скачать
        </button>
      </div>
    </div>
  )
}
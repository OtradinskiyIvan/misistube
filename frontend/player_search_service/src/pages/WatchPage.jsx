import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import AuthorCard from '../components/AuthorCard'
import { userService } from '../services/userService'
import { commentsService } from '../services/commentsService'

export default function WatchPage() {
  const { id } = useParams()
  const [videoUrl, setVideoUrl] = useState(null)
  const [video, setVideo] = useState(null)
  const [author, setAuthor] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [comments, setComments] = useState([])
  const [commentsTotal, setCommentsTotal] = useState(0)
  const [newComment, setNewComment] = useState('')
  const [sendingComment, setSendingComment] = useState(false)
  const [commentError, setCommentError] = useState(null)
  const [userNames, setUserNames] = useState({})
  const token = localStorage.getItem('auth_user')

  async function resolveUserNames(comments) {
    const userIds = [...new Set((comments || []).map(c => c.user_id).filter(Boolean))]
    if (userIds.length === 0) return
    const entries = await Promise.all(
      userIds.map(async (id) => {
        try {
          const user = await userService.getUserById(id)
          return [id, user?.username || id.slice(0, 8)]
        } catch {
          return [id, id.slice(0, 8)]
        }
      })
    )
    setUserNames(prev => ({ ...prev, ...Object.fromEntries(entries) }))
  }

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        setLoading(true)
        
        // Получаем presigned URL для видео
        const playbackResponse = await fetch(`/api/v1/playback/${id}`)
        
        if (!playbackResponse.ok) {
          throw new Error('Видео не найдено')
        }
        
        const playbackData = await playbackResponse.json()
        setVideoUrl(playbackData.hls_master_url)
        
        // Получаем информацию о видео
        const searchResponse = await fetch(`/api/v1/search?q=&limit=100`)
        const searchData = await searchResponse.json()
        const foundVideo = searchData.items?.find(v => v.id === id)
        
        if (foundVideo) {
          setVideo(foundVideo)
          
          if (foundVideo.user_id) {
            const userData = await userService.getUserById(foundVideo.user_id)
            setAuthor(userData)
          }

          const commentsData = await commentsService.getVideoComments(id)
          setComments(commentsData.comments || [])
          setCommentsTotal(commentsData.total || 0)
          resolveUserNames(commentsData.comments)
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
          <AuthorCard author={author} />

          {/* Комментарии */}
          <div className="card" style={{ padding: '1.5rem', marginTop: '1rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Комментарии ({commentsTotal})</h3>

            {token ? (
              <div style={{ marginBottom: '1rem' }}>
                <textarea
                  className="input"
                  style={{ width: '100%', minHeight: '80px', resize: 'vertical' }}
                  placeholder="Напишите комментарий..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                />
                <button
                  className="btn btn-primary"
                  style={{ marginTop: '0.5rem' }}
                  disabled={!newComment.trim() || sendingComment}
                  onClick={async () => {
                    setCommentError(null)
                    setSendingComment(true)
                    try {
                      await commentsService.createComment(id, newComment.trim())
                      setNewComment('')
                      const updated = await commentsService.getVideoComments(id)
                      setComments(updated.comments || [])
                      setCommentsTotal(updated.total || 0)
                      resolveUserNames(updated.comments)
                    } catch (err) {
                      setCommentError(err.message)
                    } finally {
                      setSendingComment(false)
                    }
                  }}
                >
                  {sendingComment ? 'Отправка...' : 'Отправить'}
                </button>
                {commentError && (
                  <p style={{ color: '#e53e3e', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                    {commentError}
                  </p>
                )}
              </div>
            ) : (
              <p style={{ color: 'var(--misis-gray-300)', marginBottom: '1rem' }}>
                <a href="/auth/">Войдите</a>, чтобы оставить комментарий
              </p>
            )}

            {comments.length === 0 ? (
              <p style={{ color: 'var(--misis-gray-300)' }}>Пока нет комментариев</p>
            ) : (
              comments.map((comment) => (
                <div
                  key={comment.id}
                  style={{
                    padding: '0.75rem 0',
                    borderBottom: '1px solid var(--misis-gray-200)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <strong style={{ fontSize: '0.875rem' }}>{userNames[comment.user_id] || comment.user_id?.slice(0, 8) || 'Аноним'}</strong>
                    <span style={{ fontSize: '0.75rem', color: 'var(--misis-gray-300)' }}>
                      {comment.created_at ? new Date(comment.created_at).toLocaleDateString() : ''}
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: '0.875rem' }}>{comment.content}</p>
                </div>
              ))
            )}
          </div>
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

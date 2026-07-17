import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import AuthorCard from '../components/AuthorCard'
import { apiClient } from '../api/client'
import { userService } from '../services/userService'
import { commentsService } from '../services/commentsService'
import { likeService } from '../services/likeService'
import { viewService } from '../services/viewService'

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
  const [copyNotification, setCopyNotification] = useState(false)
  const [liked, setLiked] = useState(false)
  const [likesCount, setLikesCount] = useState(0)
  const [likeLoading, setLikeLoading] = useState(false)
  const token = localStorage.getItem('auth_user')
  const viewRecorded = useRef(false);

  const handleShare = async () => {
    try {      
      const currentUrl = window.location.href
            
      await navigator.clipboard.writeText(currentUrl)
            
      setCopyNotification(true)
            
      setTimeout(() => {
        setCopyNotification(false)
      }, 2000)
    } catch (err) {
      console.error('Failed to copy:', err)      
      const textArea = document.createElement('textarea')
      textArea.value = window.location.href
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      
      setCopyNotification(true)
      setTimeout(() => {
        setCopyNotification(false)
      }, 2000)
    }
  }

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
                
        const [playbackResult, videoResult, commentsResult] = await Promise.allSettled([
          apiClient.getPlaybackUrl(id),
          apiClient.getVideoDetails(id),
          commentsService.getVideoComments(id)
        ])
        
        if (playbackResult.status === 'rejected') {
          throw new Error('Не удалось загрузить видео')
        }
        
        const playbackData = playbackResult.value
        setVideoUrl(playbackData.hls_master_url)
        
        if (videoResult.status === 'fulfilled') {
          const videoData = videoResult.value
          setVideo(videoData)

          if (videoData.user_id) {
            setAuthor({
              user_id: videoData.user_id,
              username: videoData.username,
              avatar_url: videoData.avatar_url,
              channelUrl: `${window.location.origin}/user/users/${videoData.user_id}`
            })
          }
        } else {
          console.warn(
            'Failed to load video details:',
            videoResult.status === 'rejected' ? videoResult.reason : 'no details'
          )
        }

        if (commentsResult.status === 'fulfilled') {
          const commentsData = commentsResult.value
          setComments(commentsData.comments || [])
          setCommentsTotal(commentsData.total || 0)
          resolveUserNames(commentsData.comments)
        } else {
          console.warn('Failed to load comments:', commentsResult.reason)
          setComments([])
          setCommentsTotal(0)
        }
        if (!viewRecorded.current) {
            viewRecorded.current = true;
            viewService.recordView(id).catch(() => {});
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchVideo()
  }, [id])

  useEffect(() => {
    likeService.likesCount(id).then((data) => {
      if (data) setLikesCount(data.count);
    }).catch(() => {});

    const authUser = token ? (() => { try { return JSON.parse(token) } catch { return null } })() : null;
    if (authUser) {
      likeService.isLiked(id).then((data) => {
        if (data) setLiked(data.liked);
      }).catch(() => {});
    }
  }, [id]);

  const handleToggleLike = async () => {
    const authUser = (() => { try { return JSON.parse(token) } catch { return null } })();
    if (!authUser) {
      window.location.href = window.location.origin + '/auth/';
      return;
    }
    if (likeLoading) return;
    setLikeLoading(true);
    const wasLiked = liked;
    setLiked(!wasLiked);
    setLikesCount(c => wasLiked ? c - 1 : c + 1);
    try {
      if (wasLiked) {
        await likeService.unlikeVideo(id);
      } else {
        await likeService.likeVideo(id);
      }
    } catch {
      setLiked(wasLiked);
      setLikesCount(c => wasLiked ? c + 1 : c - 1);
    } finally {
      setLikeLoading(false);
    }
  };

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
    <div className="container" style={{ paddingTop: '1.5rem', paddingBottom: '3rem', position: 'relative' }}>
      {copyNotification && (
        <div style={{
          position: 'fixed',
          bottom: '2rem',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'var(--misis-dark)',
          color: 'white',
          padding: '0.75rem 1.5rem',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          zIndex: 1000,
          animation: 'fadeInUp 0.3s ease-out',
          fontSize: '0.875rem',
          fontWeight: '500'
        }}>
          ✓ Ссылка скопирована в буфер обмена
        </div>
      )}

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
            {/* Заголовок */}
            <h1 style={{ fontSize: '1.5rem', marginBottom: '0.75rem', fontWeight: '600' }}>
              {video.title}
            </h1>
            
            {/* Метаданные: длительность и статус */}
            <div style={{ 
              gap: '1rem', 
              alignItems: 'center',
              flexWrap: 'wrap',
              marginBottom: '1rem',
              paddingBottom: '1rem',
              borderBottom: '1px solid var(--misis-gray-200)'
            }}>
              <span style={{ color: 'var(--misis-text-dark)', fontSize: '0.875rem' }}>
                <span style={{fontSize: '1rem'}}>⏱</span> {Math.floor((video.duration_seconds || 0) / 60)}:{String((video.duration_seconds || 0) % 60).padStart(2, '0')}
              </span>
            </div>

            {/* Описание */}
            {video.description && (
              <p style={{ 
                color: 'var(--misis-text-dark)', 
                opacity: 0.8, 
                marginBottom: '1rem',
                lineHeight: '1.6'
              }}>
                {video.description}
              </p>
            )}

            {/* Кнопки действий - отдельная секция */}
            <div style={{ 
              display: 'flex', 
              gap: '0.75rem', 
              flexWrap: 'wrap',
              paddingTop: '0.5rem'
            }}> 
              <button 
                className={`btn ${liked ? 'btn-primary' : 'btn-secondary'}`}
                style={{ flex: '0 1 auto' }} 
                onClick={handleToggleLike}
                disabled={likeLoading}
              >
                {liked ? '♥ В избранном' : '♡ В избранное'}
              </button>
              <button 
                className="btn btn-outline" 
                style={{ flex: '0 1 auto' }}
                onClick={handleShare}
              >
                ↗ Поделиться
              </button>
            </div>
          </div>

          {/* Плашка автора */}
          <AuthorCard author={author} />
        </>
      )}

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
                  console.error("WatchPage comment error:", err)
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
            <a href={window.location.origin + '/auth/'}>Войдите</a>, чтобы оставить комментарий
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
    </div>
  )
}
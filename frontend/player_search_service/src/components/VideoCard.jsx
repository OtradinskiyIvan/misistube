import { memo } from 'react'
import { Link } from 'react-router-dom'

const VideoCard = memo(function VideoCard({ video }) {
  const formatDuration = (sec) => {
    if (!sec) return '0:00'
    const h = Math.floor(sec / 3600)
    const m = Math.floor((sec % 3600) / 60)
    const s = sec % 60
    return h > 0 
      ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
      : `${m}:${String(s).padStart(2, '0')}`
  }
  const channelUrl = video.user_id 
    ? `/user/users/${video.user_id}`
    : null

  return (
    <article className="card" style={{ animation: 'fadeIn 0.25s ease-out forwards' }}>
      <div style={{ position: 'relative' }}>
        <img 
          src={video.thumbnail_url || "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 9'%3E%3Crect width='16' height='9' fill='%23E5E7EB'/%3E%3C/svg%3E"}
          alt={video.title}
          className="card__image"
          style={{ objectFit: 'cover' }}
        />

        <span style={{
          position: 'absolute',
          bottom: '8px',
          right: '8px',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '3px 6px',
          borderRadius: '4px',
          fontSize: '0.75rem',
          fontWeight: '600',
          letterSpacing: '0.5px',
          lineHeight: '1'
        }}>
          {formatDuration(video.duration_seconds)}
        </span>
      </div>
      
      <div className="card__content">
        <h3 className="card__title">{video.title}</h3>
        
        {video.description && (
          <p className="card__description" style={{
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            marginBottom: '0.5rem'
          }}>
            {video.description}
          </p>
        )}
        {video.username && channelUrl && (
          <a 
            href={channelUrl}
            style={{ 
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: 'var(--misis-text-dark)',
              fontSize: '0.875rem',
              marginTop: '0.5rem',
              marginBottom: 0,
              textDecoration: 'none',
              fontWeight: '500'
            }}
          >
            {video.avatar_url ? (
              <img 
                src={video.avatar_url}
                alt={video.username}
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  objectFit: 'cover',
                  flexShrink: 0
                }}
              />
            ) : (
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: 'var(--misis-gray-200)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.75rem',
                fontWeight: 'bold',
                color: 'var(--misis-gray-400)',
                flexShrink: 0
              }}>
                {video.username[0]?.toUpperCase() || '?'}
              </div>
            )}
            <span>{video.username}</span>
          </a>
        )}
      </div>

      <div style={{ padding: '1rem', paddingTop: 0 }}>
        <Link to={`/watch/${video.id}`} className="btn btn-outline" style={{ width: '100%', display: 'block', textAlign: 'center', textDecoration: 'none' }}>
          ▶ Смотреть
        </Link>
      </div>
    </article>
  )
})

export default VideoCard
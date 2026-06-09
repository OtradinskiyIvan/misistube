import { memo } from 'react'

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

  return (
    <article 
      className="card" 
      style={{ 
        animation: 'fadeIn 0.25s ease-out forwards',
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
      }}
    >
      {/* Стабильный inline-SVG вместо внешнего файла, чтобы не было мигания при 404 */}
      <img 
        src={video.thumbnail_url || "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 9'%3E%3Crect width='16' height='9' fill='%23E5E7EB'/%3E%3C/svg%3E"}
        alt={video.title}
        className="card__image"
        style={{ objectFit: 'cover' }}
      />
      
      <div 
        className="card__content"
        style={{
          flexGrow: 1
        }}
      >
        <h3 className="card__title">{video.title}</h3>
        
        {video.description && (
          <p className="card__description" style={{
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            marginBottom: '0.5rem',
            whiteSpace: 'pre-line' 
          }}>
            {video.description}
          </p>
        )}
        
        <div className="card__meta" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{formatDuration(video.duration_seconds)}</span>  {/* 🔹 ИСПРАВЛЕНО: duration → duration_seconds */}
          {video.status && (
            <span className={`badge status-${video.status.toLowerCase()}`}>{video.status}</span>
          )}
        </div>

      </div>

      <div style={{ 
        padding: '1rem', 
        paddingTop: 0,
        marginTop: 'auto'
      }}>
        <a href={`/watch/${video.id}`} className="btn btn-outline" style={{ width: '100%' }}>
          ▶ Смотреть
        </a>
      </div>
    </article>
  )
})

export default VideoCard
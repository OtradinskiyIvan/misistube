import React from 'react';
import { Link } from 'react-router-dom';

function VideoCard({ video }) {
  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="card fade-in">
      <div className="card__image" style={{ 
        background: 'linear-gradient(135deg, var(--misis-gray-200) 0%, var(--misis-gray-100) 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '3rem',
        color: 'var(--misis-gray-300)'
      }}>
        🎬
      </div>
      <div className="card__content">
        <h3 className="card__title">{video.title}</h3>
        {video.description && (
          <p className="card__description">{video.description}</p>
        )}
        <div className="card__meta">
          <span>⏱ {formatDuration(video.duration)}</span>
          {video.tags && video.tags.length > 0 && (
            <div style={{ marginTop: '0.5rem' }}>
              {video.tags.map((tag, index) => (
                <span key={index} className="badge badge-info" style={{ marginRight: '0.25rem', fontSize: '0.7rem' }}>
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
        <Link 
          to={`/video/${video.id}`}
          className="btn btn-primary mt-4"
          style={{ width: '100%' }}
        >
          ▶ Воспроизвести
        </Link>
      </div>
    </div>
  );
}

export default VideoCard;
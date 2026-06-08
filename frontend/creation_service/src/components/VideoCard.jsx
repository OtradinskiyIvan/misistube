import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { getUserIdFromToken, deleteVideo } from '../api/videos';

const STATUS_ICONS = {
  uploading: '⏳ ',
  processing: '⚙️ ',
  ready: '✅ ',
  failed: '❌ ',
  deleted: '🗑 ',
};

const STATUS_CLASSES = {
  ready: 'success',
  failed: 'error',
  deleted: 'error',
};

export const VideoCard = ({ video }) => {
  if (!video || !video.id) return null;

  const userId = getUserIdFromToken();
  const isOwner = userId === video.user_id;

  const handleDelete = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm('Удалить видео?')) return;
    try {
      await deleteVideo(video.id);
      window.location.reload();
    } catch {
      alert('Ошибка при удалении');
    }
  };

  const timeAgo = video.created_at
    ? formatDistanceToNow(new Date(video.created_at), { addSuffix: true })
    : '';
  const statusClass = STATUS_CLASSES[video.status] || 'warning';
  const statusIcon = STATUS_ICONS[video.status] || '';

  return (
    <Link to={`/videos/${video.id}`} className="card block hover:no-underline" style={{ position: 'relative' }}>
      <div className="aspect-video bg-gray-200 flex items-center justify-center text-gray-400">
        🎬 Превью
      </div>
      {isOwner && video.status === 'ready' && (
        <button
          onClick={handleDelete}
          style={{
            position: 'absolute',
            top: '8px',
            right: '8px',
            backgroundColor: 'rgba(220, 53, 69, 0.85)',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            width: '28px',
            height: '28px',
            fontSize: '14px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            lineHeight: 1,
          }}
          title="Удалить видео"
        >
          ✕
        </button>
      )}
      <div className="card__content">
        {video.duration > 0 && (
          <span className="card__duration">
            {Math.floor(video.duration / 60)}:{String(video.duration % 60).padStart(2, '0')}
          </span>
        )}
        <h3 className="card__title">{video.title || ''}</h3>
        <p className="card__description">
          {typeof video.description === 'string' ? video.description.slice(0, 100) : ''}
        </p>
        <div className="card__meta">
          <span className={`badge badge-${statusClass}`}>
            {statusIcon}{video.status}
          </span>
          {timeAgo && <span className="card__time">{timeAgo}</span>}
        </div>
      </div>
    </Link>
  );
};

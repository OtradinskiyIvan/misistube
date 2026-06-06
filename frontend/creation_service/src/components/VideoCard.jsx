import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';

const STATUS_ICONS = {
  uploading: '⏳ ',
  processing: '⚙️ ',
  ready: '✅ ',
  failed: '❌ ',
};

const STATUS_CLASSES = {
  ready: 'success',
  failed: 'error',
};

export const VideoCard = ({ video }) => {
  if (!video || !video.id) return null;

  const timeAgo = video.created_at
    ? formatDistanceToNow(new Date(video.created_at), { addSuffix: true })
    : '';
  const statusClass = STATUS_CLASSES[video.status] || 'warning';
  const statusIcon = STATUS_ICONS[video.status] || '';

  return (
    <Link to={`/videos/${video.id}`} className="card block hover:no-underline">
      <div className="aspect-video bg-gray-200 flex items-center justify-center text-gray-400">
        🎬 Превью
      </div>
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
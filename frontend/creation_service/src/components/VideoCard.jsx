import { Link, useNavigate } from 'react-router-dom';
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

export const VideoCard = ({ video, showDescription = true, onDelete }) => {
  if (!video || !video.id) return null;

  const userId = getUserIdFromToken();
  const isOwner = userId === video.user_id;
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003';
  const navigate = useNavigate();

  const handleDelete = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm('Удалить видео?')) return;
    try {
      await deleteVideo(video.id);
      if (onDelete) {
        onDelete();
      } else {
        navigate('/');
      }
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
    <Link to={`/videos/${video.id}`} className="card block hover:no-underline" style={{ position: 'relative', maxWidth: '400px' }}>
      <div className="bg-gray-200 flex items-center justify-center text-gray-400" style={{ height: '180px', overflow: 'hidden' }}>
        {video.thumbnail_url ? (
          <img src={`${apiBaseUrl}${video.thumbnail_url}`} alt="" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
        ) : null}
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
      <div className="card__content" style={{ padding: '6px 10px', fontSize: '13px' }}>
        {video.duration > 0 && (
          <span className="card__duration" style={{ position: 'absolute', bottom: '92px', right: '6px', fontSize: '11px', background: 'rgba(0,0,0,0.7)', color: '#fff', padding: '1px 5px', borderRadius: '3px' }}>
            {Math.floor(video.duration / 60)}:{String(video.duration % 60).padStart(2, '0')}
          </span>
        )}
        <div style={{ fontWeight: 600, fontSize: '14px', color: '#1E2A3A', margin: '2px 0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{video.title || ''}</div>
        {showDescription && (
          <div style={{ fontSize: '12px', color: '#6b6375', margin: '2px 0', lineHeight: 1.3, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {typeof video.description === 'string' ? video.description.slice(0, 80) : ''}
          </div>
        )}
        <div style={{ marginTop: '4px', fontSize: '11px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className={`badge badge-${statusClass}`} style={{ fontSize: '11px' }}>
            {statusIcon}{video.status}
          </span>
          {timeAgo && <span style={{ color: '#6b6375' }}>{timeAgo}</span>}
        </div>
      </div>
    </Link>
  );
};

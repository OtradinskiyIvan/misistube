import { useParams, useNavigate } from 'react-router-dom';
import { useVideo } from '../hooks/useVideos';
import { VideoPlayer } from '../components/VideoPlayer';
import { formatDistanceToNow } from 'date-fns';
import { getUserIdFromToken } from '../api/videos';

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

export const VideoDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { video, loading, error } = useVideo(id);

  const userId = getUserIdFromToken();
  if (!userId) {
    return <div className="text-center p-10 text-gray-500">Требуется авторизация</div>;
  }

  if (loading) return <div className="text-center p-10">Загрузка...</div>;
  if (error || !video) return <div className="text-red-600 p-10">Видео не найдено</div>;

  const statusClass = STATUS_CLASSES[video.status] || 'warning';
  const statusIcon = STATUS_ICONS[video.status] || '';
  const timeAgo = video.created_at
    ? formatDistanceToNow(new Date(video.created_at), { addSuffix: true })
    : '';
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  const streamUrl = video.storage_url?.startsWith('/')
    ? `${apiBaseUrl}${video.storage_url}`
    : video.storage_url;

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <VideoPlayer src={streamUrl} title={video.title} />
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, margin: '16px 0 8px', color: '#1E2A3A' }}>{video.title || ''}</h1>
      {timeAgo && (
        <div style={{ fontSize: '0.8rem', color: '#6b6375' }}>
          Загружено {timeAgo}
        </div>
      )}
      <hr style={{ border: 'none', borderTop: '1px solid #e5e4e7', margin: '16px 0' }} />
      <p style={{ color: '#1E2A3A', margin: '0 0 16px', lineHeight: 1.5, border: '1px solid #e5e4e7', borderRadius: '8px', padding: '12px' }}>{video.description || ''}</p>
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <span className={`badge badge-${statusClass}`}>
          {statusIcon}{video.status}
        </span>
        {video.duration > 0 && (
          <span style={{ fontSize: '0.875rem', color: '#1E2A3A', fontWeight: 500 }}>
            Длительность: {Math.floor(video.duration / 60)}:{String(video.duration % 60).padStart(2, '0')}
          </span>
        )}
      </div>
    </div>
  );
};
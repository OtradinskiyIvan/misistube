import { useParams } from 'react-router-dom';
import { useVideo } from '../hooks/useVideos';
import { VideoPlayer } from '../components/VideoPlayer';
import { formatDistanceToNow } from 'date-fns';

export const VideoDetailPage = () => {
  const { id } = useParams();
  const { video, loading, error } = useVideo(id);

  if (loading) return <div className="text-center p-10">Загрузка...</div>;
  if (error || !video) return <div className="text-red-600 p-10">Видео не найдено</div>;

  const statusClass = 
    video.status === 'ready' ? 'success' :
    video.status === 'failed' ? 'error' : 'warning';

  return (
    <div className="max-w-4xl mx-auto">
      <VideoPlayer src={video.storage_url || ''} title={video.title} />
      <h1 className="text-2xl font-bold mt-4">{video.title}</h1>
      <p className="text-gray-600 mt-2">{video.description}</p>
      <div className="mt-3 flex flex-wrap gap-3 items-center">
        <span className={`badge badge-${statusClass}`}>
          {video.status === 'uploading' && '⏳ '}
          {video.status === 'processing' && '⚙️ '}
          {video.status === 'ready' && '✅ '}
          {video.status === 'failed' && '❌ '}
          {video.status}
        </span>
        {video.duration > 0 && (
          <span className="text-sm font-medium text-gray-700">
            Длительность: {Math.floor(video.duration / 60)}:{String(video.duration % 60).padStart(2, '0')}
          </span>
        )}
        <span className="text-sm text-gray-600">
          Загружено {formatDistanceToNow(new Date(video.created_at), { addSuffix: true })}
        </span>
      </div>
    </div>
  );
};
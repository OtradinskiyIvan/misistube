import { Link } from 'react-router-dom';
import { useVideos } from '../hooks/useVideos';
import { VideoCard } from '../components/VideoCard';
import { getUserIdFromToken } from '../api/videos';

export const VideoListPage = () => {
  const { videos, loading, error } = useVideos();

  const userId = getUserIdFromToken();
  if (!userId) {
    return <div className="text-center p-10 text-gray-500">Требуется авторизация</div>;
  }

  if (loading) return <div className="text-center p-10">Загрузка...</div>;
  if (error) return <div className="text-red-600 p-10">Ошибка: {error}</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1>Все видео</h1>
        <Link to="/upload" className="btn-primary">+ Загрузить видео</Link>
      </div>
      {videos.length === 0 ? (
        <p className="text-gray-500">Пока нет видео. Станьте первым!</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {videos.map((video) => (
            <VideoCard key={video.id} video={video} showDescription={false} />
          ))}
        </div>
      )}
    </div>
  );
};
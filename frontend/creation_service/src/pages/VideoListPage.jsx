import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useVideos } from '../hooks/useVideos';
import { VideoCard } from '../components/VideoCard';
import { getUserIdFromToken } from '../api/videos';

export const VideoListPage = () => {
  const { videos, loading, error, refresh } = useVideos();
  const [viewMode, setViewMode] = useState(() =>
    localStorage.getItem('viewMode') === 'list' ? 'list' : 'grid'
  );

  useEffect(() => {
    localStorage.setItem('viewMode', viewMode);
  }, [viewMode]);

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
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button className="btn btn-sm btn-outline" onClick={() => setViewMode(m => m === 'grid' ? 'list' : 'grid')}>
            {viewMode === 'grid' ? 'Список' : 'Сетка'}
          </button>
          <Link to="/upload" className="btn btn-sm btn-outline">+ Загрузить видео</Link>
        </div>
      </div>
      {videos.length === 0 ? (
        <>
          <hr style={{ border: 'none', height: '1px', backgroundColor: '#e5e4e7', margin: '0 0 24px' }} />
          <p className="text-gray-500">У вас пока нет видео. Загрузите первое!</p>
        </>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2">
          {videos.map((video) => (
            <VideoCard key={video.id} video={video} showDescription={false} onDelete={refresh} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {videos.map((video) => (
            <VideoCard key={video.id} video={video} compact onDelete={refresh} />
          ))}
        </div>
      )}
    </div>
  );
};
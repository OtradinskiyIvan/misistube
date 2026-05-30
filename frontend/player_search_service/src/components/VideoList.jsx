import React from 'react';
import VideoCard from './VideoCard';

function VideoList({ videos, isLoading, error }) {
  if (isLoading) {
    return (
      <div className="empty-state">
        <div className="loading-spinner" style={{ width: '40px', height: '40px', borderWidth: '4px' }} />
        <p className="mt-4">Загрузка видео...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        <strong>Ошибка:</strong> {error}
      </div>
    );
  }

  if (!videos || videos.length === 0) {
    return (
      <div className="empty-state">
        <h3>Видео не найдено</h3>
        <p>Попробуйте изменить параметры поиска</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2" style={{ gap: '1.5rem' }}>
      {videos.map((video, index) => (
        <VideoCard key={video.id || index} video={video} />
      ))}
    </div>
  );
}

export default VideoList;
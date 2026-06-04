import { useState } from 'react';

export const VideoPlayer = ({ src, title }) => {
  const [error, setError] = useState(false);

  if (!src || error) {
    return (
      <div className="w-full aspect-video bg-gray-200 flex items-center justify-center text-gray-500 rounded-lg">
        {error ? 'Ошибка загрузки видео' : 'Видео недоступно'}
      </div>
    );
  }

  return (
    <video
      controls
      style={{ width: '100%', maxWidth: '800px', margin: '32px auto 0', display: 'block', borderRadius: '8px' }}
      controlsList="nodownload"
      title={title}
      onError={() => setError(true)}
    >
      <source src={src} type="video/mp4" />
    </video>
  );
};
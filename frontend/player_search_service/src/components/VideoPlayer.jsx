import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../api/client';

function VideoPlayer() {
  const { videoId } = useParams();
  const [playbackUrl, setPlaybackUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expiresAt, setExpiresAt] = useState(null);

  useEffect(() => {
    const fetchPlaybackUrl = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.getPlaybackUrl(videoId);
        setPlaybackUrl(data.hls_master_url);
        setExpiresAt(data.expires_at);
      } catch (err) {
        setError(err.message || 'Не удалось получить ссылку для воспроизведения');
      } finally {
        setLoading(false);
      }
    };

    fetchPlaybackUrl();
  }, [videoId]);

  if (loading) {
    return (
      <div className="empty-state">
        <div className="loading-spinner" style={{ width: '40px', height: '40px' }} />
        <p className="mt-4">Загрузка плеера...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error-message mt-6">
          <strong>Ошибка:</strong> {error}
        </div>
        <Link to="/" className="btn btn-secondary mt-4">
          ← Назад к поиску
        </Link>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="video-player-container fade-in">
        {playbackUrl ? (
          <video controls autoPlay style={{ width: '100%' }}>
            <source src={playbackUrl} type="application/vnd.apple.mpegurl" />
            Ваш браузер не поддерживает воспроизведение видео.
          </video>
        ) : (
          <div className="empty-state" style={{ padding: '2rem' }}>
            <p>Видео недоступно</p>
          </div>
        )}
        <div className="video-info">
          <h2>Воспроизведение видео</h2>
          <div className="video-meta">
            <span>ID: {videoId}</span>
            {expiresAt && (
              <span>
                Ссылка действительна до: {new Date(expiresAt).toLocaleString('ru-RU')}
              </span>
            )}
          </div>
          <Link to="/" className="btn btn-secondary mt-4">
            ← Назад к поиску
          </Link>
        </div>
      </div>
    </div>
  );
}

export default VideoPlayer;
import { useEffect, useState } from 'react';
import { fetchVideos, fetchVideoById } from '../api/videos';

export const useVideos = (limit = 10, offset = 0) => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const abort = new AbortController();
    setLoading(true);
    fetchVideos(limit, offset, abort.signal)
      .then((data) => {
        if (!abort.signal.aborted) {
          setVideos(data.items);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!abort.signal.aborted) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => abort.abort();
  }, [limit, offset]);

  return { videos, loading, error };
};

export const useVideo = (id) => {
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) {
      setLoading(false);
      setError('ID видео не указан');
      return;
    }
    const abort = new AbortController();
    setLoading(true);
    setError(null);
    fetchVideoById(id, abort.signal)
      .then((data) => {
        if (!abort.signal.aborted) {
          setVideo(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!abort.signal.aborted) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => abort.abort();
  }, [id]);

  return { video, loading, error };
};
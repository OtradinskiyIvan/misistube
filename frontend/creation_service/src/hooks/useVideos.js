import { useEffect, useState } from 'react';
import { fetchVideos, fetchVideoById } from '../api/videos';

export const useVideos = (limit = 10, offset = 0) => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchVideos(limit, offset)
      .then((data) => {
        setVideos(data.items);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [limit, offset]);

  return { videos, loading, error };
};

export const useVideo = (id) => {
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) return;
    fetchVideoById(id)
      .then((data) => {
        setVideo(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  return { video, loading, error };
};
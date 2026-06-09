import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadVideo } from '../api/videos';

const MAX_FILE_SIZE = 100 * 1024 * 1024;

export const VideoUploader = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState(null);
  const [thumbnail, setThumbnail] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Выберите файл');
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      setError('Видео слишком большое (Max 100 MB)');
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const result = await uploadVideo(title, description, file, thumbnail);
      navigate(`/videos/${result.id}`);
    } catch (err) {
      setError(err.message || 'Ошибка загрузки');
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-lg mx-auto space-y-4">
      <div className="form-group">
        <label className="label">Название видео *</label>
        <input
          type="text"
          className="input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label className="label">Описание</label>
        <textarea
          className="textarea"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
        />
      </div>
      <div className="form-group">
        <label className="label">Файл видео *</label>
        <input
          type="file"
          accept="video/*"
          onChange={(e) => {
            const f = e.target.files?.[0] || null;
            if (f && f.size > MAX_FILE_SIZE) {
              setError('Видео слишком большое (Max 100 MB)');
              setFile(null);
              e.target.value = '';
            } else {
              setFile(f);
              setError(null);
            }
          }}
          required
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:bg-misis-light file:text-white hover:file:bg-misis-dark"
        />
      </div>
      <div className="form-group">
        <label className="label">Превью (необязательно)</label>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setThumbnail(e.target.files?.[0] || null)}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:bg-misis-light file:text-white hover:file:bg-misis-dark"
        />
      </div>
      {error && <div className="text-red-600 text-sm">{error}</div>}
      <button
        type="submit"
        disabled={uploading}
        className="btn-primary w-full"
      >
        {uploading ? 'Загрузка...' : 'Загрузить видео'}
      </button>
    </form>
  );
};
import { VideoUploader } from '../components/VideoUploader';
import { getUserIdFromToken } from '../api/videos';

export const UploadPage = () => {
  const userId = getUserIdFromToken();
  if (!userId) {
    return <div className="text-center p-10 text-gray-500">Требуется авторизация</div>;
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6 text-center">Загрузить новое видео</h1>
      <VideoUploader />
    </div>
  );
};
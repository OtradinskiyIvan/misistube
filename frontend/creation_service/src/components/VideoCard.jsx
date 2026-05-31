import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';

export const VideoCard = ({ video }) => {
  const timeAgo = formatDistanceToNow(new Date(video.created_at), { addSuffix: true });

  // определяем класс бейджа
  const statusClass = 
    video.status === 'ready' ? 'success' :
    video.status === 'failed' ? 'error' : 'warning';

  return (
    <Link to={`/videos/${video.id}`} className="card block hover:no-underline">
      <div className="aspect-video bg-gray-200 flex items-center justify-center text-gray-400">
        🎬 Превью
      </div>
      <div className="card__content">
        <span>{Math.floor(video.duration / 60)}:{video.duration % 60}</span>
        <h3 className="card__title">{video.title}</h3>
        <p className="card__description">{video.description?.slice(0, 100)}</p>
        <div className="card__meta">
          <span className={`badge badge-${statusClass}`}>
            {video.status}
          </span>
          <span> • {timeAgo}</span>
        </div>
      </div>
    </Link>
  );
};
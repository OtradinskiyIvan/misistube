export const VideoPlayer = ({ src, title }) => {
  return (
    <video
      controls
      className="w-full rounded-lg shadow-md"
      poster=""
      controlsList="nodownload"
    >
      <source src={src} type="video/mp4" />
      Ваш браузер не поддерживает видео.
    </video>
  );
};
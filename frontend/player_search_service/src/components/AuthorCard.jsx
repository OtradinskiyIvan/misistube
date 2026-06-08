export default function AuthorCard({ author }) {
  if (!author || !author.user_id) return null

  const { user_id, username } = author

  // Генерируем инициалы для аватара
  const initials = username 
    ? username.slice(0, 2).toUpperCase()
    : user_id.slice(0, 2).toUpperCase()

  // URL страницы автора в другом сервисе
  const channelUrl = `${import.meta.env.VITE_USER_SERVICE_URL || 'http://localhost:8002'}/channel/${user_id}`

  return (
    <div 
      className="card" 
      style={{ 
        padding: '1.5rem', 
        marginBottom: '1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem'
      }}
    >
      {/* Аватар */}
      <div
        style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: 'var(--misis-primary)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '1.25rem',
          fontWeight: 'bold',
          flexShrink: 0
        }}
      >
        {initials}
      </div>

      {/* Информация об авторе */}
      <div style={{ flex: 1 }}>
        <h3 style={{ fontSize: '1.125rem', marginBottom: '0.25rem' }}>
          {username || 'Автор'}
        </h3>
        <p style={{ color: 'var(--misis-gray-300)', fontSize: '0.875rem', margin: 0 }}>
          Автор видео
        </p>
      </div>

      {/* Кнопка перехода на канал (внешний редирект) */}
      <a 
        href={channelUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="btn btn-primary"
        style={{ flexShrink: 0, textDecoration: 'none' }}
      >
        Перейти на канал ↗
      </a>
    </div>
  )
}
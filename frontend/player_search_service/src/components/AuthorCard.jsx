export default function AuthorCard({ author }) {
  if (!author) {
    return (
      <div className="card" style={{ padding: '1.5rem', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div
            style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              backgroundColor: 'var(--misis-gray-200)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.25rem',
              fontWeight: 'bold',
              color: 'var(--misis-gray-400)'
            }}
          >
            ?
          </div>
          <div style={{ flex: 1 }}>
            <h3 style={{ fontSize: '1.125rem', marginBottom: '0.25rem' }}>
              Автор не найден
            </h3>
            <p style={{ color: 'var(--misis-gray-300)', fontSize: '0.875rem', margin: 0 }}>
              Информация об авторе недоступна
            </p>
          </div>
        </div>
      </div>
    )
  }

  const { username, channelUrl } = author

  // Генерируем инициалы для аватара
  const initials = username 
    ? username.slice(0, 1).toUpperCase()
    : '?'

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
          backgroundColor: 'var(--misis-gray-200);',
          color: 'var(--misis-text-dark)',
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
          {username}
        </h3>
        <p style={{ color: 'var(--misis-gray-300)', fontSize: '0.875rem', margin: 0 }}>
          Автор видео
        </p>
      </div>

      {/* Кнопка перехода на канал (внешний редирект) */}
      <a 
        href={channelUrl}
        className="btn btn-primary"
        style={{ flexShrink: 0, textDecoration: 'none' }}
      >
        Перейти на канал ↗
      </a>
    </div>
  )
}
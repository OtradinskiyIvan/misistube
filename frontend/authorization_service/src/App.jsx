import { useState } from 'react'
import './App.css'

const AUTH_API = 'http://127.0.0.1:8000/api/v1/auth'

function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus] = useState('')
  const [statusType, setStatusType] = useState('')
  const [showRegister, setShowRegister] = useState(false)
  const [registerEmail, setRegisterEmail] = useState('')
  const [registerPassword, setRegisterPassword] = useState('')
  const [registerConfirm, setRegisterConfirm] = useState('')
  const [registerStatus, setRegisterStatus] = useState('')
  const [registerStatusType, setRegisterStatusType] = useState('')

  const saveTokens = (data) => {
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
  }

  const parseError = async (response) => {
    try {
      const contentType = response.headers.get('content-type') || ''
      if (!contentType.includes('application/json')) {
        return response.statusText || 'Ошибка сервера'
      }

      const payload = await response.json()
      if (payload.detail) {
        if (Array.isArray(payload.detail)) {
          return payload.detail
            .map((item) => item.msg || item.error || JSON.stringify(item))
            .join('; ')
        }

        if (typeof payload.detail === 'string') {
          return payload.detail
        }
      }

      if (payload.error) {
        return payload.error
      }

      return response.statusText || 'Ошибка сервера'
    } catch {
      return response.statusText || 'Ошибка сети'
    }
  }

  const handleLogin = async (event) => {
    event.preventDefault()
    setStatusType('')
    setStatus('Вход выполняется...')

    try {
      const response = await fetch(`${AUTH_API}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const message = await parseError(response)
        setStatusType('error')
        setStatus(message)
        return
      }

      const tokenData = await response.json()
      saveTokens(tokenData)
      setStatusType('success')
      setStatus('Вход выполнен. Идет перенаправление...')
      window.location.href = '/?authenticated=1'
    } catch (error) {
      setStatusType('error')
      setStatus(error.message || 'Не удалось выполнить запрос. Попробуйте позже.')
    }
  }

  const openRegister = () => {
    setRegisterEmail('')
    setRegisterPassword('')
    setRegisterConfirm('')
    setRegisterStatus('')
    setRegisterStatusType('')
    setShowRegister(true)
  }

  const closeRegister = () => {
    setShowRegister(false)
  }

  const handleRegister = async (event) => {
    event.preventDefault()
    setRegisterStatusType('')

    if (registerPassword !== registerConfirm) {
      setRegisterStatusType('error')
      setRegisterStatus('Пароли не совпадают. Попробуйте ещё раз.')
      return
    }

    setRegisterStatus('Регистрация пользователя...')

    try {
      const response = await fetch(`${AUTH_API}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: registerEmail,
          password: registerPassword,
        }),
      })

      if (!response.ok) {
        const message = await parseError(response)
        setRegisterStatusType('error')
        setRegisterStatus(message)
        return
      }

      await response.json()
      setRegisterStatusType('success')
      setRegisterStatus('Регистрация прошла успешно. Выполняется вход...')

      const loginResponse = await fetch(`${AUTH_API}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: registerEmail,
          password: registerPassword,
        }),
      })

      if (!loginResponse.ok) {
        const loginMessage = await parseError(loginResponse)
        setRegisterStatusType('error')
        setRegisterStatus(`Регистрация выполнена, но вход не удался: ${loginMessage}`)
        setEmail(registerEmail)
        setPassword(registerPassword)
        setShowRegister(false)
        return
      }

      const tokenData = await loginResponse.json()
      saveTokens(tokenData)
      setShowRegister(false)
      setStatusType('success')
      setStatus('Регистрация и вход выполнены. Идет перенаправление...')
      window.location.href = '/?authenticated=1'
    } catch (error) {
      setRegisterStatusType('error')
      setRegisterStatus(error.message || 'Не удалось выполнить запрос. Попробуйте позже.')
    }
  }

  return (
    <div className="app-shell">
      <div className="auth-card card shadow">
        <div className="card__content">
          <div className="brand mb-4">
            <h1>Авторизация</h1>
            <p className="card__description">
              Тестовый frontend auth сервиса с импортом общего стиля.
            </p>
          </div>

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="label" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ivan@example.com"
                required
              />
            </div>

            <div className="form-group">
              <label className="label" htmlFor="password">
                Пароль
              </label>
              <input
                id="password"
                type="password"
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <div className="auth-actions">
              <button type="submit" className="btn btn-primary btn-lg">
                Войти
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-lg"
                onClick={openRegister}
              >
                Зарегистрироваться
              </button>
            </div>

            {status && (
              <p className={`status mt-4 ${statusType === 'error' ? 'status-error' : ''} ${statusType === 'success' ? 'status-success' : ''}`}>
                {status}
              </p>
            )}
          </form>
        </div>
      </div>

      {showRegister && (
        <div className="modal-overlay">
          <div className="modal-card card shadow">
            <div className="card__content">
              <div className="brand mb-3">
                <h2>Регистрация</h2>
                <p className="card__description">
                  Введите email, пароль и подтвердите пароль.
                </p>
              </div>

              <form onSubmit={handleRegister}>
                <div className="form-group">
                  <label className="label" htmlFor="registerEmail">
                    Введите email
                  </label>
                  <input
                    id="registerEmail"
                    type="email"
                    className="input"
                    value={registerEmail}
                    onChange={(e) => setRegisterEmail(e.target.value)}
                    placeholder="ivan@example.com"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="label" htmlFor="registerPassword">
                    Введите пароль
                  </label>
                  <input
                    id="registerPassword"
                    type="password"
                    className="input"
                    value={registerPassword}
                    onChange={(e) => setRegisterPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="label" htmlFor="registerConfirm">
                    Подтвердите пароль
                  </label>
                  <input
                    id="registerConfirm"
                    type="password"
                    className="input"
                    value={registerConfirm}
                    onChange={(e) => setRegisterConfirm(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>

                <div className="auth-actions">
                  <button type="submit" className="btn btn-primary btn-lg">
                    Зарегистрироваться
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary btn-lg"
                    onClick={closeRegister}
                  >
                    Отмена
                  </button>
                </div>

                {registerStatus && (
                  <p className={`status mt-4 ${registerStatusType === 'error' ? 'status-error' : ''} ${registerStatusType === 'success' ? 'status-success' : ''}`}>
                    {registerStatus}
                  </p>
                )}
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App

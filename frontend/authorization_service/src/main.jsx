import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '../../shared/style_sample.css'
import './App.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

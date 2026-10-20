import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n'
import App from './App.jsx'
import { purgeLegacyClinicalStorage } from './services/clinicalCache'
import { registerWorker } from './services/registerWorker'
purgeLegacyClinicalStorage()
registerWorker()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

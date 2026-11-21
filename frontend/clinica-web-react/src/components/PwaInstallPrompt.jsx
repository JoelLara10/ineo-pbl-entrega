import React from 'react'
import { useRegisterSW } from 'virtual:pwa-register/react'
import './PwaInstallPrompt.css'

/**
 * Componente de experiencia de instalación / actualización PWA.
 * Muestra notificaciones cuando la app está lista para offline
 * o cuando hay una nueva versión disponible.
 *
 * Incluir una sola vez en el layout raíz o App.jsx.
 */
function PwaInstallPrompt() {
  const {
    offlineReady: [offlineReady, setOfflineReady],
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegisteredSW(swUrl, registration) {
      console.log('Service Worker registrado:', swUrl)
    },
    onRegisterError(error) {
      console.error('Error al registrar Service Worker:', error)
    },
  })

  const close = () => {
    setOfflineReady(false)
    setNeedRefresh(false)
  }

  if (!offlineReady && !needRefresh) {
    return null
  }

  return (
    <div className="pwa-prompt" role="status" aria-live="polite">
      <div className="pwa-prompt__content">
        {needRefresh ? (
          <>
            <span className="pwa-prompt__message">
              Hay una nueva versión de la aplicación disponible.
            </span>
            <div className="pwa-prompt__actions">
              <button
                type="button"
                className="pwa-prompt__btn pwa-prompt__btn--primary"
                onClick={() => updateServiceWorker(true)}
              >
                Actualizar
              </button>
              <button
                type="button"
                className="pwa-prompt__btn pwa-prompt__btn--secondary"
                onClick={close}
              >
                Más tarde
              </button>
            </div>
          </>
        ) : (
          <>
            <span className="pwa-prompt__message">
              La aplicación está lista para usarse sin conexión (modo limitado).
            </span>
            <div className="pwa-prompt__actions">
              <button
                type="button"
                className="pwa-prompt__btn pwa-prompt__btn--primary"
                onClick={close}
              >
                Entendido
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default PwaInstallPrompt

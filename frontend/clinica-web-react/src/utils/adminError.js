// Do not expose transport diagnostics or server internals in administrative forms.
export function adminErrorMessage(error, t = (_key, fallback) => fallback) {
  const text = (key, fallback) => t(`administrative.errors.${key}`, fallback);
  if (error?.code === 'ERR_OFFLINE') return text('offline', 'No hay conexión a Internet. Conéctate y vuelve a intentarlo.');
  if (['ECONNABORTED', 'ETIMEDOUT'].includes(error?.code)) return text('timeout', 'Se agotó el tiempo de espera del servidor. Vuelve a intentarlo.');
  if (!error?.response) return text('connection', 'No se pudo establecer conexión con el servidor. Revisa tu conexión y vuelve a intentarlo.');
  const status = error.response.status;
  if (status === 401) return text('session', 'Tu sesión venció. Inicia sesión de nuevo.');
  if (status === 403) return text('permission', 'No tienes permiso para realizar esta operación.');
  if (status === 404) return text('notFound', 'El registro solicitado no está disponible. Actualiza la lista.');
  if (status >= 500) return text('server', 'El servidor no pudo completar la operación. Vuelve a intentarlo más tarde.');
  if ([400, 409, 422].includes(status)) {
    const detail = error.response.data?.error;
    if (typeof detail === 'string' && detail.length <= 250 && !/traceback|exception|mongodb|password|token|secret|<[^>]+>/i.test(detail)) return detail;
    return text('validation', 'Revisa los datos ingresados e inténtalo de nuevo.');
  }
  return text('unexpected', 'No se pudo completar la operación. Vuelve a intentarlo.');
}

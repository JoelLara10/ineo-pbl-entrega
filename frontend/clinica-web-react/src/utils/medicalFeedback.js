export const adminErrorMessage = (error) => {
  if (['ECONNABORTED', 'ETIMEDOUT'].includes(error?.code)) {
    return 'El servidor tardó demasiado en responder. Vuelve a intentarlo.';
  }
  if (!error?.response) return 'No se pudo establecer conexión con el servidor. Revisa tu conexión y vuelve a intentarlo.';
  const status = error.response.status;
  if (status === 401) return 'Tu sesión terminó. Inicia sesión nuevamente.';
  if (status === 403) return 'No tienes permiso para realizar esta acción.';
  if (status === 404) return 'No se encontró la información solicitada. Actualiza e intenta nuevamente.';
  if (status >= 500) return 'El servicio no está disponible en este momento. Intenta nuevamente más tarde.';
  const message = error.response.data?.error;
  if ([400, 409, 422].includes(status) && typeof message === 'string' && message.length <= 250 &&
      !/traceback|exception|mongodb|password|token|secret|<[^>]+>/i.test(message)) return message;
  return 'No se pudo completar la operación. Intenta nuevamente.';
};

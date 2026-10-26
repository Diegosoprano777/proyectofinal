import { HttpErrorResponse } from '@angular/common/http';

/** URL base del backend Django REST Framework en Render. */
export const API_URL =
  (typeof window !== 'undefined' && (window as any).__API_URL__) ||
  (typeof localStorage !== 'undefined' && localStorage.getItem('API_URL')) ||
  'https://proyectofinal-pctw.onrender.com/api';

/** Convierte los errores de DRF en un mensaje legible para la UI. */
export function mensajeDeError(err: unknown): string {
  if (!(err instanceof HttpErrorResponse)) return 'Ocurrió un error inesperado.';
  if (err.status === 0) return 'No hay conexión con el servidor (¿Django está corriendo en el puerto 8000?).';

  const body = err.error;
  if (typeof body === 'string' && body) return body;
  if (body?.detail) return body.detail;
  if (body && typeof body === 'object') {
    const [campo, valor] = Object.entries(body)[0] ?? [];
    if (campo) return `${campo}: ${Array.isArray(valor) ? valor[0] : valor}`;
  }
  return `Error ${err.status}`;
}

import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { API_URL } from './api.config';
import { AuthService } from './auth.service';
import { ToastService } from './toast.service';

/**
 * Agrega `Authorization: Bearer <token>` a las peticiones al backend.
 * Si el backend responde 401 (token vencido o inválido) cierra la sesión y vuelve al login.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const toast = inject(ToastService);

  const token = auth.token();
  const esApi = req.url.startsWith(API_URL);
  const esLogin = req.url.includes('/usuarios/');
  const peticion = token && esApi && !esLogin
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(peticion).pipe(
    catchError((err: unknown) => {
      if (err instanceof HttpErrorResponse && err.status === 401 && esApi && !esLogin && auth.estaAutenticado()) {
        auth.logout();
        toast.error('Tu sesión expiró', 'Vuelve a iniciar sesión para continuar.');
        router.navigate(['/login']);
      }
      return throwError(() => err);
    }),
  );
};

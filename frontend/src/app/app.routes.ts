import { inject } from '@angular/core';
import { CanActivateFn, Router, Routes } from '@angular/router';

import { AuthService } from './services/auth.service';

/** Solo deja entrar al catálogo si hay sesión. */
const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.estaAutenticado() || inject(Router).createUrlTree(['/login']);
};

/** Si ya hay sesión, el login redirige al catálogo. */
const invitadoGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return !auth.estaAutenticado() || inject(Router).createUrlTree(['/catalogo']);
};

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'catalogo' },
  {
    path: 'login',
    title: 'Ingresar · AvoLote',
    canActivate: [invitadoGuard],
    loadComponent: () => import('./components/login/login').then((m) => m.LoginComponent),
  },
  {
    path: 'catalogo',
    title: 'Catálogo de Lotes · AvoLote',
    canActivate: [authGuard],
    loadComponent: () => import('./components/catalogo/catalogo').then((m) => m.CatalogoComponent),
  },
  { path: '**', redirectTo: 'catalogo' },
];

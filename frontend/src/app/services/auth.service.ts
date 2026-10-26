import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { AuthResponse, LoginPayload, RegistroPayload, Usuario } from '../models/interfaces';
import { API_URL } from './api.config';

const STORAGE_KEY = 'avolote.sesion';

interface SesionGuardada {
  usuario: Usuario;
  token: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly sesionInicial = this.leerSesion();

  /** Usuario logueado (null si no hay sesión). */
  readonly usuarioActual = signal<Usuario | null>(this.sesionInicial?.usuario ?? null);
  readonly token = signal<string | null>(this.sesionInicial?.token ?? null);

  readonly estaAutenticado = computed(() => this.usuarioActual() !== null);
  readonly esAdmin = computed(() => this.usuarioActual()?.rol === 'ADMIN');

  login(payload: LoginPayload): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${API_URL}/usuarios/login`, payload)
      .pipe(tap((res) => this.guardarSesion(res)));
  }

  registro(payload: RegistroPayload): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${API_URL}/usuarios/registro`, payload)
      .pipe(tap((res) => this.guardarSesion(res)));
  }

  logout(): void {
    localStorage.removeItem(STORAGE_KEY);
    this.usuarioActual.set(null);
    this.token.set(null);
  }

  private guardarSesion({ usuario, token }: AuthResponse): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ usuario, token } satisfies SesionGuardada));
    this.usuarioActual.set(usuario);
    this.token.set(token);
  }

  private leerSesion(): SesionGuardada | null {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) as SesionGuardada) : null;
    } catch {
      return null;
    }
  }
}

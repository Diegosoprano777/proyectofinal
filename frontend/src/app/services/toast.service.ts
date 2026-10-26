import { Injectable, signal } from '@angular/core';

export type TipoToast = 'exito' | 'error' | 'info';

export interface Toast {
  id: number;
  tipo: TipoToast;
  titulo: string;
  mensaje?: string;
}

/** Notificaciones visuales simples basadas en signals. */
@Injectable({ providedIn: 'root' })
export class ToastService {
  private siguienteId = 1;
  readonly toasts = signal<Toast[]>([]);

  exito(titulo: string, mensaje?: string) { this.mostrar('exito', titulo, mensaje); }
  error(titulo: string, mensaje?: string) { this.mostrar('error', titulo, mensaje, 5000); }
  info(titulo: string, mensaje?: string) { this.mostrar('info', titulo, mensaje); }

  cerrar(id: number): void {
    this.toasts.update((ts) => ts.filter((t) => t.id !== id));
  }

  private mostrar(tipo: TipoToast, titulo: string, mensaje?: string, duracionMs = 3500): void {
    const id = this.siguienteId++;
    this.toasts.update((ts) => [...ts, { id, tipo, titulo, mensaje }]);
    setTimeout(() => this.cerrar(id), duracionMs);
  }
}

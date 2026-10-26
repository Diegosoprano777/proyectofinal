import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';

import { AuthResponse, Rol } from '../../models/interfaces';
import { mensajeDeError } from '../../services/api.config';
import { AuthService } from '../../services/auth.service';
import { ToastService } from '../../services/toast.service';
import { LogoComponent } from '../logo/logo';

type Modo = 'login' | 'registro';

/** Credenciales de los usuarios creados por `python manage.py init_demo`. */
const CREDENCIALES_DEMO: Record<Rol, { correo: string; password: string }> = {
  ADMIN: { correo: 'admin@sena.edu.co', password: 'admin123' },
  CLIENTE: { correo: 'cliente@sena.edu.co', password: 'cliente123' },
};

@Component({
  selector: 'app-login',
  imports: [FormsModule, LogoComponent],
  templateUrl: './login.html',
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);

  readonly modo = signal<Modo>('login');
  readonly cargando = signal(false);
  readonly cargandoDemo = signal<Rol | null>(null);
  readonly error = signal<string | null>(null);
  readonly verPassword = signal(false);

  // Campos del formulario (two-way binding con signals)
  readonly nombre = signal('');
  readonly correo = signal('');
  readonly password = signal('');

  cambiarModo(modo: Modo): void {
    this.modo.set(modo);
    this.error.set(null);
  }

  enviar(): void {
    if (this.cargando()) return;
    const correo = this.correo().trim();
    const password = this.password();

    const peticion: Observable<AuthResponse> =
      this.modo() === 'login'
        ? this.auth.login({ correo, password })
        : this.auth.registro({ nombre: this.nombre().trim(), correo, password, rol: 'CLIENTE' });

    this.ejecutar(peticion);
  }

  /** Truco para la exposición: autollenar e ingresar con un clic. */
  accesoDemo(rol: Rol): void {
    const { correo, password } = CREDENCIALES_DEMO[rol];
    this.modo.set('login');
    this.correo.set(correo);
    this.password.set(password);
    this.cargandoDemo.set(rol);
    this.ejecutar(this.auth.login({ correo, password }));
  }

  private ejecutar(peticion: Observable<AuthResponse>): void {
    this.cargando.set(true);
    this.error.set(null);
    peticion.subscribe({
      next: (res) => {
        this.cargando.set(false);
        this.cargandoDemo.set(null);
        this.toast.exito(res.mensaje, `Ingresaste como ${res.usuario.rol}.`);
        this.router.navigate(['/catalogo']);
      },
      error: (err) => {
        this.cargando.set(false);
        this.cargandoDemo.set(null);
        this.error.set(mensajeDeError(err));
      },
    });
  }
}

import { CurrencyPipe, DatePipe, DecimalPipe } from '@angular/common';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { Apartado, EstadoMaduracion, NuevoLote, ProductoLote } from '../../models/interfaces';
import { mensajeDeError } from '../../services/api.config';
import { AuthService } from '../../services/auth.service';
import { CatalogoService } from '../../services/catalogo.service';
import { ToastService } from '../../services/toast.service';
import { LogoComponent } from '../logo/logo';

type Filtro = EstadoMaduracion | 'TODOS';

interface EstiloEstado {
  etiqueta: string;
  icono: string;
  badge: string;
  barra: string;
  activo: string;
}

/** Estilos por estado (clases completas para que Tailwind las detecte). */
export const ESTADOS: Record<EstadoMaduracion, EstiloEstado> = {
  VERDE: {
    etiqueta: 'Verde', icono: '🟢',
    badge: 'bg-lime-100 text-lime-800 ring-lime-600/20',
    barra: 'bg-linear-to-r from-lime-400 to-emerald-500',
    activo: 'bg-lime-600 text-white shadow-lg shadow-lime-600/30 border-lime-600',
  },
  PINTON: {
    etiqueta: 'Pintón', icono: '🟡',
    badge: 'bg-amber-100 text-amber-800 ring-amber-600/20',
    barra: 'bg-linear-to-r from-amber-300 to-lime-500',
    activo: 'bg-amber-500 text-white shadow-lg shadow-amber-500/30 border-amber-500',
  },
  MADURO: {
    etiqueta: 'Maduro', icono: '⚫',
    badge: 'bg-stone-800 text-stone-50 ring-stone-900/20',
    barra: 'bg-linear-to-r from-hass-700 to-stone-900',
    activo: 'bg-stone-800 text-white shadow-lg shadow-stone-800/30 border-stone-800',
  },
};

const LOTE_VACIO: NuevoLote = {
  codigo_lote: '', variedad: 'Hass', estado_maduracion: 'VERDE',
  precio_kg: 7500, stock_kg: 100, dias_consumo: 7, descripcion: '',
};

export const VARIEDADES = ['Hass', 'Papelillo'] as const;

/** Foto del producto según variedad y maduración (public/img/lotes/{variedad}-{estado}.jpg). */
export function imagenLote(variedad: string, estado: EstadoMaduracion): string {
  const slug = variedad.toLowerCase().includes('papel') ? 'papelillo' : 'hass';
  return `img/lotes/${slug}-${estado.toLowerCase()}.jpg`;
}

@Component({
  selector: 'app-catalogo',
  imports: [FormsModule, CurrencyPipe, DecimalPipe, DatePipe, LogoComponent],
  templateUrl: './catalogo.html',
})
export class CatalogoComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly catalogo = inject(CatalogoService);
  private readonly toast = inject(ToastService);
  private readonly router = inject(Router);

  readonly estados = ESTADOS;
  readonly imagenLote = imagenLote;
  readonly variedadesAdmin = VARIEDADES;
  readonly listaEstados = Object.keys(ESTADOS) as EstadoMaduracion[];
  readonly filtros: { valor: Filtro; etiqueta: string; icono: string }[] = [
    { valor: 'TODOS', etiqueta: 'Todos', icono: '🥑' },
    { valor: 'VERDE', etiqueta: 'Verde', icono: '🟢' },
    { valor: 'PINTON', etiqueta: 'Pintón', icono: '🟡' },
    { valor: 'MADURO', etiqueta: 'Maduro', icono: '⚫' },
  ];

  // ---- Estado (signals) ----
  readonly usuario = this.auth.usuarioActual;
  readonly lotes = signal<ProductoLote[]>([]);
  readonly filtro = signal<Filtro>('TODOS');
  readonly filtroVariedad = signal<string>('TODAS');
  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);
  readonly cantidades = signal<Record<number, number>>({});
  readonly apartando = signal<number | null>(null);
  readonly recienActualizado = signal<number | null>(null);

  // ---- Apartados ----
  readonly apartados = signal<Apartado[]>([]);
  readonly drawerAbierto = signal(false);
  readonly cargandoApartados = signal(false);
  readonly totalApartados = computed(() => this.apartados().reduce((s, a) => s + a.total, 0));
  readonly kgApartados = computed(() => this.apartados().reduce((s, a) => s + a.cantidad_kg, 0));

  // ---- Derivados ----
  readonly variedades = computed(() => [...new Set(this.lotes().map((l) => l.variedad))].sort());
  private readonly lotesPorVariedad = computed(() => {
    const v = this.filtroVariedad();
    return v === 'TODAS' ? this.lotes() : this.lotes().filter((l) => l.variedad === v);
  });
  readonly lotesFiltrados = computed(() => {
    const f = this.filtro();
    const ls = this.lotesPorVariedad();
    return f === 'TODOS' ? ls : ls.filter((l) => l.estado_maduracion === f);
  });
  readonly conteos = computed(() => {
    const c: Record<Filtro, number> = { TODOS: 0, VERDE: 0, PINTON: 0, MADURO: 0 };
    for (const l of this.lotesPorVariedad()) { c.TODOS++; c[l.estado_maduracion]++; }
    return c;
  });
  readonly totalKg = computed(() => this.lotes().reduce((s, l) => s + l.stock_kg, 0));
  readonly precioPromedio = computed(() => {
    const ls = this.lotes();
    return ls.length ? ls.reduce((s, l) => s + l.precio_kg, 0) / ls.length : 0;
  });
  readonly stockMaximo = computed(() => Math.max(1, ...this.lotes().map((l) => l.stock_kg)));
  readonly iniciales = computed(() =>
    (this.usuario()?.nombre ?? '?').split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase(),
  );

  // ---- Panel Admin ----
  readonly panelAbierto = signal(true);
  readonly pestanaAdmin = signal<'nuevo' | 'estado'>('nuevo');
  readonly guardando = signal(false);
  nuevoLote: NuevoLote = { ...LOTE_VACIO };
  readonly loteAEditar = signal<number | null>(null);
  readonly nuevoEstado = signal<EstadoMaduracion>('MADURO');

  ngOnInit(): void {
    this.cargar();
    this.cargarApartados();
  }

  cargarApartados(): void {
    this.cargandoApartados.set(true);
    this.catalogo.listarApartados().subscribe({
      next: (as) => { this.apartados.set(as); this.cargandoApartados.set(false); },
      error: () => this.cargandoApartados.set(false),
    });
  }

  abrirApartados(): void {
    this.drawerAbierto.set(true);
    this.cargarApartados();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.catalogo.listar().subscribe({
      next: (lotes) => {
        this.lotes.set(lotes);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(mensajeDeError(err));
        this.cargando.set(false);
      },
    });
  }

  // ---- Apartar ----
  cantidad(lote: ProductoLote): number {
    return this.cantidades()[lote.id] ?? Math.min(5, lote.stock_kg);
  }

  setCantidad(id: number, valor: number | null): void {
    this.cantidades.update((c) => ({ ...c, [id]: Number(valor) || 0 }));
  }

  puedeApartar(lote: ProductoLote): boolean {
    const c = this.cantidad(lote);
    return c > 0 && c <= lote.stock_kg && this.apartando() === null;
  }

  apartar(lote: ProductoLote): void {
    const cantidad = this.cantidad(lote);
    if (!this.puedeApartar(lote)) return;

    this.apartando.set(lote.id);
    this.catalogo.apartar(lote.id, cantidad).subscribe({
      next: (res) => {
        this.reemplazarLote(res.lote);
        this.apartados.update((as) => [res.apartado, ...as]);
        this.cantidades.update((c) => ({ ...c, [lote.id]: Math.min(c[lote.id] ?? 5, res.lote.stock_kg) }));
        this.apartando.set(null);
        this.marcarActualizado(lote.id);
        const total = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
          .format(res.total_estimado);
        this.toast.exito(
          `¡Apartaste ${res.cantidad_apartada_kg} kg de ${res.lote.codigo_lote}! 🥑`,
          `Total estimado ${total}. Quedan ${res.lote.stock_kg} kg disponibles.`,
        );
      },
      error: (err) => {
        this.apartando.set(null);
        this.toast.error('No se pudo apartar', mensajeDeError(err));
      },
    });
  }

  // ---- Admin ----
  crearLote(): void {
    if (this.guardando()) return;
    this.guardando.set(true);
    const payload: NuevoLote = { ...this.nuevoLote, codigo_lote: this.nuevoLote.codigo_lote.trim().toUpperCase() };

    this.catalogo.crear(payload).subscribe({
      next: (lote) => {
        this.lotes.update((ls) => [...ls, lote]);
        this.nuevoLote = { ...LOTE_VACIO };
        this.filtro.set('TODOS');
        this.guardando.set(false);
        this.marcarActualizado(lote.id);
        this.toast.exito('Lote registrado', `${lote.codigo_lote} ya está disponible en el catálogo.`);
      },
      error: (err) => {
        this.guardando.set(false);
        this.toast.error('No se pudo registrar el lote', mensajeDeError(err));
      },
    });
  }

  cambiarEstado(): void {
    const id = this.loteAEditar();
    if (id === null || this.guardando()) return;
    this.guardando.set(true);

    this.catalogo.actualizar(id, { estado_maduracion: this.nuevoEstado() }).subscribe({
      next: (lote) => {
        this.reemplazarLote(lote);
        this.guardando.set(false);
        this.marcarActualizado(lote.id);
        const e = ESTADOS[lote.estado_maduracion];
        this.toast.exito('Maduración actualizada', `${lote.codigo_lote} ahora está ${e.icono} ${e.etiqueta}.`);
      },
      error: (err) => {
        this.guardando.set(false);
        this.toast.error('No se pudo actualizar', mensajeDeError(err));
      },
    });
  }

  cambiarEstadoApartado(apartado: Apartado, nuevoEstado: 'ENTREGADO' | 'CANCELADO'): void {
    this.catalogo.cambiarEstadoApartado(apartado.id, nuevoEstado).subscribe({
      next: (res) => {
        // Actualizar el apartado en la lista
        this.apartados.update((as) => as.map((a) => (a.id === res.apartado.id ? res.apartado : a)));
        // Si se canceló y devolvió stock, actualizar el lote
        if (res.lote) {
          this.reemplazarLote(res.lote);
          this.marcarActualizado(res.lote.id);
        }
        this.toast.exito(
          nuevoEstado === 'ENTREGADO' ? 'Apartado entregado' : 'Apartado cancelado',
          res.mensaje
        );
      },
      error: (err) => {
        this.toast.error('Error al actualizar apartado', mensajeDeError(err));
      },
    });
  }

  cerrarSesion(): void {
    this.auth.logout();
    this.toast.info('Sesión cerrada', '¡Hasta pronto!');
    this.router.navigate(['/login']);
  }

  private reemplazarLote(actualizado: ProductoLote): void {
    this.lotes.update((ls) => ls.map((l) => (l.id === actualizado.id ? actualizado : l)));
  }

  private marcarActualizado(id: number): void {
    this.recienActualizado.set(id);
    setTimeout(() => this.recienActualizado.update((v) => (v === id ? null : v)), 1400);
  }
}

import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';

import { Apartado, ApartarResponse, EstadoMaduracion, NuevoLote, ProductoLote } from '../models/interfaces';
import { API_URL } from './api.config';

/** DRF serializa los DecimalField como string ("7500.00"); aquí los pasamos a number. */
function normalizar(lote: ProductoLote): ProductoLote {
  return { ...lote, precio_kg: Number(lote.precio_kg), stock_kg: Number(lote.stock_kg) };
}

function normalizarApartado(a: Apartado): Apartado {
  return { ...a, cantidad_kg: Number(a.cantidad_kg), precio_kg: Number(a.precio_kg), total: Number(a.total) };
}

@Injectable({ providedIn: 'root' })
export class CatalogoService {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_URL}/catalogo`;

  /** GET /api/catalogo (opcional ?estado_maduracion= y ?variedad=) */
  listar(estado?: EstadoMaduracion, variedad?: string): Observable<ProductoLote[]> {
    let params = new HttpParams();
    if (estado) params = params.set('estado_maduracion', estado);
    if (variedad) params = params.set('variedad', variedad);
    return this.http.get<ProductoLote[]>(this.url, { params }).pipe(map((lotes) => lotes.map(normalizar)));
  }

  /** POST /api/catalogo */
  crear(lote: NuevoLote): Observable<ProductoLote> {
    return this.http.post<ProductoLote>(this.url, lote).pipe(map(normalizar));
  }

  /** PATCH /api/catalogo/{id} — usado por el Admin para cambiar la maduración. */
  actualizar(id: number, cambios: Partial<NuevoLote>): Observable<ProductoLote> {
    return this.http.patch<ProductoLote>(`${this.url}/${id}`, cambios).pipe(map(normalizar));
  }

  /** POST /api/catalogo/{id}/apartar — descuenta cantidad_kg del stock en la BD. */
  apartar(id: number, cantidad_kg: number): Observable<ApartarResponse> {
    return this.http
      .post<ApartarResponse>(`${this.url}/${id}/apartar`, { cantidad_kg })
      .pipe(map((res) => ({
        ...res,
        cantidad_apartada_kg: Number(res.cantidad_apartada_kg),
        total_estimado: Number(res.total_estimado),
        lote: normalizar(res.lote),
        apartado: normalizarApartado(res.apartado),
      })));
  }

  /** GET /api/apartados — CLIENTE recibe los suyos, ADMIN todos. */
  listarApartados(): Observable<Apartado[]> {
    return this.http.get<Apartado[]>(`${API_URL}/apartados`).pipe(map((as) => as.map(normalizarApartado)));
  }
}

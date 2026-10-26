export type Rol = 'ADMIN' | 'CLIENTE';
export type EstadoMaduracion = 'VERDE' | 'PINTON' | 'MADURO';

export interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  rol: Rol;
  fecha_registro?: string;
}

export interface ProductoLote {
  id: number;
  codigo_lote: string;
  variedad: string;
  estado_maduracion: EstadoMaduracion;
  precio_kg: number;
  stock_kg: number;
  dias_consumo: number;
  descripcion: string;
}

/** Payload para crear un lote (sin id). */
export type NuevoLote = Omit<ProductoLote, 'id'>;

export interface LoginPayload {
  correo: string;
  password: string;
}

export interface RegistroPayload extends LoginPayload {
  nombre: string;
  rol?: Rol;
}

export interface AuthResponse {
  mensaje: string;
  usuario: Usuario;
  token: string;
}

export interface ApartarResponse {
  mensaje: string;
  cantidad_apartada_kg: number;
  total_estimado: number;
  lote: ProductoLote;
  apartado: Apartado;
}

/** Registro de un apartado (reserva) hecho por un usuario. */
export interface Apartado {
  id: number;
  lote: number;
  codigo_lote: string;
  variedad: string;
  estado_maduracion: EstadoMaduracion;
  usuario: number;
  usuario_nombre: string;
  usuario_correo: string;
  cantidad_kg: number;
  precio_kg: number;
  total: number;
  fecha: string;
}

import { solicitar } from './cliente'

/**
 * Forma de un miembro tal como lo devuelve GET /api/miembros.
 * Refleja a mano el esquema MiembroOut del backend; si ese esquema
 * cambia, este tipo hay que actualizarlo junto con él.
 */
export interface Miembro {
  tag: string
  nombre: string
  rol: string
  nivel_experiencia: number
  nivel_ayuntamiento: number
  trofeos: number
  donaciones: number
  donaciones_recibidas: number
  liga: string | null
  rango_clan: number | null
  rango_clan_anterior: number | null
  trofeos_base: number | null
  liga_base: string | null
}

export function obtenerMiembros(): Promise<Miembro[]> {
  return solicitar<Miembro[]>('/api/miembros')
}

/** Dispara una captura manual: consulta el clan en vivo y la guarda en el historial. */
export function dispararCaptura(): Promise<unknown> {
  return solicitar('/api/capturas', { method: 'POST' })
}
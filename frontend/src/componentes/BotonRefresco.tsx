import { useState } from 'react'
import { useLimitadorRefresco } from '../hooks/useLimitadorRefresco'

interface PropiedadesBotonRefresco {
  /** Identifica esta sección para su propio límite, ej. "miembros", "guerra". */
  seccion: string
  /** Función que dispara la actualización real, por ejemplo una llamada a la API. */
  alActualizar: () => Promise<void>
  /** Máximo de usos dentro de la ventana. Por defecto 5. */
  maximoUsos?: number
  /** Minutos que dura la ventana del límite. Por defecto 60. */
  ventanaMinutos?: number
  /** Clases de Tailwind extra para el estado habilitado, para teñirlo según la pantalla. */
  className?: string
}

/**
 * Botón de refresco manual con límite de usos, al estilo de los botones
 * de recursos limitados del propio juego: una vez agotados los usos
 * disponibles dentro de la ventana de tiempo, se pone gris y muestra
 * cuánto falta para que se reactive, en vez de simplemente desaparecer.
 */
export function BotonRefresco({
  seccion,
  alActualizar,
  maximoUsos = 5,
  ventanaMinutos = 60,
  className = 'border-base-acento bg-base-panel text-base-texto hover:brightness-95',
}: PropiedadesBotonRefresco) {
  const { puedeUsar, usosRestantes, segundosParaReiniciar, registrarUso } = useLimitadorRefresco({
    maximoUsos,
    ventanaMinutos,
    clave: seccion,
  })
  const [actualizando, setActualizando] = useState(false)

  async function manejarClic() {
    if (!puedeUsar || actualizando) return
    setActualizando(true)
    try {
      await alActualizar()
      registrarUso()
    } finally {
      setActualizando(false)
    }
  }

  const deshabilitado = !puedeUsar || actualizando

  return (
    <button
      type="button"
      onClick={manejarClic}
      disabled={deshabilitado}
      title={
        puedeUsar
          ? `Te quedan ${usosRestantes} de ${maximoUsos} actualizaciones esta hora`
          : `Sin actualizaciones disponibles, vuelve a intentar en ${formatearTiempo(segundosParaReiniciar)}`
      }
      className={[
        'inline-flex items-center gap-2 rounded-full border-2 px-4 py-2 font-display font-semibold transition',
        deshabilitado
          ? 'cursor-not-allowed border-slate-300 bg-slate-200 text-slate-400'
          : className,
      ].join(' ')}
    >
      <span className={actualizando ? 'inline-block animate-spin' : 'inline-block'}>⟳</span>
      {actualizando ? 'Actualizando…' : puedeUsar ? 'Actualizar' : formatearTiempo(segundosParaReiniciar)}
    </button>
  )
}

function formatearTiempo(segundos: number): string {
  const minutos = Math.floor(segundos / 60)
  const resto = segundos % 60
  return `${minutos}:${resto.toString().padStart(2, '0')}`
}
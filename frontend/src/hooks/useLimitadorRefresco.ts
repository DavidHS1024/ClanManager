import { useCallback, useEffect, useState } from 'react'

interface OpcionesLimitador {
  /** Máximo de usos permitidos dentro de la ventana de tiempo. */
  maximoUsos: number
  /** Duración de la ventana, en minutos. */
  ventanaMinutos: number
  /** Clave única para guardar el estado en localStorage, por sección. */
  clave: string
}

interface EstadoLimitador {
  usosRestantes: number
  puedeUsar: boolean
  segundosParaReiniciar: number
  registrarUso: () => void
}

/**
 * Lleva la cuenta de cuántas veces se usó un botón de refresco manual
 * dentro de una ventana de tiempo, para no permitir machacarlo sin freno.
 *
 * El estado se guarda en localStorage bajo la clave dada, así que el
 * límite sobrevive a que se recargue la página, pero es propio de cada
 * navegador: no hay coordinación entre distintos líderes usando la
 * página al mismo tiempo. Eso está bien para esto, porque el objetivo es
 * evitar que una sola persona lo use sin freno por accidente, no imponer
 * una cuota compartida entre todo el liderazgo del clan.
 */
export function useLimitadorRefresco({
  maximoUsos,
  ventanaMinutos,
  clave,
}: OpcionesLimitador): EstadoLimitador {
  const claveStorage = `clanmanager:refresco:${clave}`

  const leerUsos = useCallback((): number[] => {
    try {
      const guardado = localStorage.getItem(claveStorage)
      if (!guardado) return []
      const usos: number[] = JSON.parse(guardado)
      const limiteVentana = Date.now() - ventanaMinutos * 60_000
      return usos.filter((marca) => marca > limiteVentana)
    } catch {
      return []
    }
  }, [claveStorage, ventanaMinutos])

  const [usos, setUsos] = useState<number[]>(() => leerUsos())
  const [ahora, setAhora] = useState<number>(() => Date.now())

  // Vuelve a calcular los usos vigentes y la hora actual cada segundo,
  // para que el botón se reactive solo en cuanto el uso más antiguo
  // salga de la ventana, sin que haga falta recargar la página. Leer el
  // reloj aquí, dentro del efecto, y no directamente en el cuerpo del
  // hook, es lo que mantiene puro el cálculo que se hace en cada render.
  useEffect(() => {
    const id = setInterval(() => {
      setUsos(leerUsos())
      setAhora(Date.now())
    }, 1000)
    return () => clearInterval(id)
  }, [leerUsos])

  const registrarUso = useCallback(() => {
    const actualizados = [...leerUsos(), Date.now()]
    localStorage.setItem(claveStorage, JSON.stringify(actualizados))
    setUsos(actualizados)
  }, [claveStorage, leerUsos])

  const usosRestantes = Math.max(0, maximoUsos - usos.length)
  const puedeUsar = usosRestantes > 0

  let segundosParaReiniciar = 0
  if (!puedeUsar && usos.length > 0) {
    const usoMasAntiguo = Math.min(...usos)
    const reinicioEn = usoMasAntiguo + ventanaMinutos * 60_000
    segundosParaReiniciar = Math.max(0, Math.ceil((reinicioEn - ahora) / 1000))
  }

  return { usosRestantes, puedeUsar, segundosParaReiniciar, registrarUso }
}
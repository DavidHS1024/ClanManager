/**
 * Cliente HTTP base para hablar con el backend de ClanManager.
 *
 * Todo el resto de módulos de la carpeta api/ pasan por esta función en
 * vez de llamar a fetch directamente, para que la URL base, los
 * encabezados y el manejo de errores vivan en un solo lugar.
 */

const URL_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

/** Error con el código de estado HTTP, para poder reaccionar distinto según el caso. */
export class ErrorApi extends Error {
  // El proyecto tiene erasableSyntaxOnly activado (ver tsconfig.app.json),
  // así que el atajo "constructor(public status: number)" de TypeScript
  // no está permitido aquí: ese atajo genera código real en tiempo de
  // ejecución además de tipos, y esa opción solo permite sintaxis que el
  // compilador pueda borrar sin generar nada. Por eso el campo se declara
  // aparte y se asigna a mano.
  status: number

  constructor(status: number, mensaje: string) {
    super(mensaje)
    this.status = status
    this.name = 'ErrorApi'
  }
}

export async function solicitar<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const respuesta = await fetch(`${URL_BASE}${ruta}`, {
    headers: { 'Content-Type': 'application/json', ...opciones.headers },
    ...opciones,
  })

  if (!respuesta.ok) {
    const cuerpo = await respuesta.text()
    throw new ErrorApi(respuesta.status, cuerpo || respuesta.statusText)
  }

  // 204 No Content no trae cuerpo que convertir a JSON.
  if (respuesta.status === 204) {
    return undefined as T
  }

  return (await respuesta.json()) as T
}
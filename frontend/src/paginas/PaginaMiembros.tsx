import { useEffect, useState } from 'react'
import { ErrorApi } from '../api/cliente'
import { dispararCaptura, obtenerMiembros, type Miembro } from '../api/miembros'
import { BotonRefresco } from '../componentes/BotonRefresco'

export function PaginaMiembros() {
  const [miembros, setMiembros] = useState<Miembro[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function cargar() {
    setCargando(true)
    setError(null)
    try {
      setMiembros(await obtenerMiembros())
    } catch (err) {
      setError(err instanceof ErrorApi ? err.message : 'No se pudo conectar con el servidor')
    } finally {
      setCargando(false)
    }
  }

  // Carga inicial al entrar a la pantalla. El arreglo de dependencias
  // vacío significa "una sola vez al montar", no en cada render.
  useEffect(() => {
    // oxlint-disable-next-line react/set-state-in-effect
    cargar()
  }, [])

  async function actualizar() {
    await dispararCaptura()
    await cargar()
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-xl font-bold">Miembros del clan</h2>
        <BotonRefresco seccion="miembros" alActualizar={actualizar} />
      </div>

      {error && (
        <p className="rounded-lg border-2 border-red-300 bg-red-50 px-4 py-2 text-red-700">{error}</p>
      )}

      {cargando && <p>Cargando…</p>}

      {!cargando && !error && (
        <div className="overflow-x-auto rounded-xl border-2 border-base-borde bg-base-panel">
          <table className="w-full text-left">
            <thead className="bg-base-fondo font-display">
              <tr>
                <th className="px-4 py-2">Nombre</th>
                <th className="px-4 py-2">Rol</th>
                <th className="px-4 py-2">Ayuntamiento</th>
                <th className="px-4 py-2">Trofeos</th>
                <th className="px-4 py-2">Donaciones</th>
                <th className="px-4 py-2">Liga</th>
              </tr>
            </thead>
            <tbody>
              {miembros.map((miembro) => (
                <tr key={miembro.tag} className="border-t border-base-borde">
                  <td className="px-4 py-2">{miembro.nombre}</td>
                  <td className="px-4 py-2">{miembro.rol}</td>
                  <td className="px-4 py-2">{miembro.nivel_ayuntamiento}</td>
                  <td className="px-4 py-2">{miembro.trofeos}</td>
                  <td className="px-4 py-2">{miembro.donaciones}</td>
                  <td className="px-4 py-2">{miembro.liga ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
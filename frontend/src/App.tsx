import { BotonRefresco } from './components/BotonRefresco'

/**
 * Pantalla de muestra temporal: un panel por cada módulo, usando su
 * paleta propia, solo para validar el sistema de diseño y el botón de
 * refresco antes de construir las pantallas reales con datos de verdad.
 */
function App() {
  async function simularActualizacion(ms: number) {
    await new Promise((resuelto) => setTimeout(resuelto, ms))
  }

  return (
    <div className="min-h-screen space-y-6 p-6">
      <h1 className="font-display text-3xl font-extrabold text-base-texto">ClanManager</h1>

      <Panel
        titulo="Miembros"
        fondo="bg-base-panel"
        borde="border-base-borde"
        texto="text-base-texto"
      >
        <BotonRefresco seccion="miembros" alActualizar={() => simularActualizacion(800)} />
      </Panel>

      <Panel
        titulo="Guerra clásica"
        fondo="bg-guerra-fondo"
        borde="border-guerra-borde"
        texto="text-guerra-texto"
      >
        <BotonRefresco
          seccion="guerra"
          alActualizar={() => simularActualizacion(800)}
          className="border-guerra-borde bg-guerra-panel text-guerra-texto hover:brightness-95"
        />
      </Panel>

      <Panel
        titulo="Liga de Guerras de Clanes"
        fondo="bg-liga-fondo"
        borde="border-liga-borde"
        texto="text-liga-texto"
      >
        <BotonRefresco
          seccion="liga"
          alActualizar={() => simularActualizacion(800)}
          className="border-liga-borde bg-liga-panel text-liga-texto hover:brightness-95"
        />
      </Panel>

      <Panel
        titulo="Fin de Semana de Asaltos"
        fondo="bg-asalto-fondo"
        borde="border-asalto-borde"
        texto="text-asalto-texto"
      >
        <BotonRefresco
          seccion="asaltos"
          alActualizar={() => simularActualizacion(800)}
          className="border-asalto-borde bg-asalto-panel text-asalto-texto hover:brightness-95"
        />
      </Panel>
    </div>
  )
}

function Panel({
  titulo,
  fondo,
  borde,
  texto,
  children,
}: {
  titulo: string
  fondo: string
  borde: string
  texto: string
  children: React.ReactNode
}) {
  return (
    <section className={`rounded-2xl border-4 p-6 ${fondo} ${borde} ${texto}`}>
      <div className="flex items-center justify-between">
        <h2 className="font-display text-xl font-bold">{titulo}</h2>
        {children}
      </div>
    </section>
  )
}

export default App
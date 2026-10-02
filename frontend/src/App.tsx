import { Route, Routes } from 'react-router-dom'
import { DisenoPrincipal } from './componentes/DisenoPrincipal'
import { PaginaMiembros } from './paginas/PaginaMiembros'

function App() {
  return (
    <Routes>
      <Route element={<DisenoPrincipal />}>
        <Route path="/" element={<PaginaMiembros />} />
        {/* Las rutas de guerra, liga y asaltos se agregan junto con cada pantalla. */}
      </Route>
    </Routes>
  )
}

export default App
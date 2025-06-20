/**
 * BusFeed - Componente Principal da Aplicação
 * 
 * Este componente define a estrutura principal da aplicação React,
 * incluindo roteamento e layout base para o sistema de transporte público.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Importações de estilos
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/App.css';

// Componentes da aplicação
import Home from './pages/Home';
import MapPage from './pages/MapPage';
import LinhasPage from './pages/LinhasPage';
import ParadasPage from './pages/ParadasPage';
import RouteResultsPage from './pages/RouteResultsPage';

/**
 * Componente principal que gerencia o roteamento da aplicação
 * @returns {JSX.Element} Estrutura principal da aplicação
 */
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Rota principal - Tela Home com mapa e busca */}
          <Route path="/" element={<Home />} />
          
          {/* Página do mapa funcional */}
          <Route path="/mapa" element={<MapPage />} />
          
          {/* Página de paradas de ônibus */}
          <Route path="/paradas" element={<ParadasPage />} />
          
          {/* Página de linhas de ônibus */}
          <Route path="/linhas" element={<LinhasPage />} />
          
          {/* Página de resultados de rotas */}
          <Route path="/rotas" element={<RouteResultsPage />} />
          
          {/* Rotas futuras para as funcionalidades do sistema */}
          {/* <Route path="/paradas" element={<Paradas />} /> */}
          {/* <Route path="/rota/:id" element={<DetalhesRota />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App; 
/**
 * BusFeed - Ponto de Entrada da Aplicação React
 * 
 * Este arquivo inicializa a aplicação React e renderiza o componente
 * principal no DOM.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Inicialização da aplicação React
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 
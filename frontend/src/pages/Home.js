/**
 * BusFeed - Página Home
 * 
 * Interface principal baseada no mockup fornecido com:
 * - Mapa de fundo do DF
 * - Título de boas-vindas centralizado
 * - Campo de busca de destino funcional
 * - Botões de navegação rápida
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchForm from '../components/common/SearchForm';
import '../styles/SearchForm.css';

/**
 * Componente da página inicial do BusFeed
 * @returns {JSX.Element} Interface visual da home
 */
function Home() {
  const navigate = useNavigate();
  const [isSearching, setIsSearching] = useState(false);

  // Dados enriquecidos das paradas para autocomplete
  const mockLocations = [
    // Ceilândia
    { id: 1, name: "Terminal Ceilândia Centro", description: "Terminal principal - QNM 13/15", coordinates: [-15.8267, -48.1089], type: "terminal" },
    { id: 2, name: "Shopping Ceilândia", description: "Centro comercial - QNM 28", coordinates: [-15.8245, -48.1125], type: "shopping" },
    { id: 3, name: "Hospital Regional da Ceilândia", description: "HRC - QNM 28", coordinates: [-15.8198, -48.1067], type: "hospital" },
    { id: 4, name: "Terminal Ceilândia Sul", description: "Terminal P Sul - QNO 15", coordinates: [-15.8456, -48.1178], type: "terminal" },
    { id: 5, name: "Centro Metropolitano", description: "QNM 13 - Comércio", coordinates: [-15.8189, -48.1034], type: "comercio" },
    { id: 6, name: "QNM 13 - Conjunto A", description: "Área residencial", coordinates: [-15.8289, -48.1078], type: "residencial" },
    { id: 7, name: "QNM 15 - Comércio Local", description: "Feira da Ceilândia", coordinates: [-15.8234, -48.1098], type: "comercio" },
    { id: 8, name: "CAIC - Ceilândia", description: "Centro de Educação QNO 14", coordinates: [-15.8321, -48.1145], type: "educacao" },
    
    // Taguatinga
    { id: 9, name: "Terminal Taguatinga", description: "Terminal central - Pistão Sul", coordinates: [-15.8311, -48.0428], type: "terminal" },
    { id: 10, name: "Shopping Taguatinga", description: "Pistão Sul - QSA 1", coordinates: [-15.8298, -48.0389], type: "shopping" },
    { id: 11, name: "Feira de Taguatinga", description: "Feira permanente - QSA 21", coordinates: [-15.8267, -48.0502], type: "comercio" },
    { id: 12, name: "Hospital Regional de Taguatinga", description: "HRT - QSA 5", coordinates: [-15.8289, -48.0445], type: "hospital" },
    
    // Samambaia
    { id: 13, name: "Terminal Samambaia", description: "Terminal principal - QS 602", coordinates: [-15.8756, -48.0789], type: "terminal" },
    { id: 14, name: "Shopping Samambaia", description: "QN 512 - Conjunto A", coordinates: [-15.8723, -48.0834], type: "shopping" },
    { id: 15, name: "Estação Samambaia", description: "Metrô DF - QS 618", coordinates: [-15.8834, -48.0923], type: "metro" },
    
    // Brasília
    { id: 16, name: "Rodoviária do Plano Piloto", description: "Terminal central de Brasília", coordinates: [-15.7942, -47.8822], type: "terminal" },
    { id: 17, name: "Esplanada dos Ministérios", description: "Congresso Nacional", coordinates: [-15.7998, -47.8635], type: "turistico" },
    { id: 18, name: "Shopping Brasília", description: "SCN - Asa Norte", coordinates: [-15.7789, -47.8934], type: "shopping" },
    { id: 19, name: "UnB - Campus Darcy Ribeiro", description: "Universidade de Brasília", coordinates: [-15.7801, -47.8719], type: "educacao" },
    { id: 20, name: "Aeroporto JK", description: "Terminal de passageiros", coordinates: [-15.8711, -47.9181], type: "aeroporto" },
    
    // Águas Claras
    { id: 21, name: "Terminal Águas Claras", description: "Terminal urbano", coordinates: [-15.8345, -48.0123], type: "terminal" },
    { id: 22, name: "Shopping Águas Claras", description: "Av. Araucárias", coordinates: [-15.8289, -48.0089], type: "shopping" },
    { id: 23, name: "Estação Águas Claras", description: "Metrô DF", coordinates: [-15.8367, -48.0156], type: "metro" }
  ];

  /**
   * Manipula a busca de rota
   */
  const handleSearch = async (searchData) => {
    setIsSearching(true);
    
    try {
      // Navega para a página de resultados passando os dados da busca
      navigate('/rotas', { 
        state: { 
          origem: searchData.origem,
          destino: searchData.destino 
        }
      });
    } catch (error) {
      console.error('Erro ao buscar rota:', error);
      alert('Erro ao buscar rota. Tente novamente.');
    } finally {
      setIsSearching(false);
    }
  };
  
  /**
   * Navega para a página do mapa
   */
  const handleGoToMap = () => {
    navigate('/mapa');
  };

  /**
   * Navega para a página de paradas
   */
  const handleGoToParadas = () => {
    navigate('/paradas');
  };

  /**
   * Navega para a página de linhas
   */
  const handleGoToLinhas = () => {
    navigate('/linhas');
  };

  return (
    <div className="home-page">
      {/* Mapa de fundo com overlay */}
      <div className="map-background"></div>
      
      {/* Retângulos decorativos principais */}
      <div className="main-rectangle main-top-left"></div>
      <div className="main-rectangle main-bottom-right"></div>
      
      {/* Retângulos decorativos dos cantos */}
      <div className="corner-rectangle corner-top-right"></div>
      <div className="corner-rectangle corner-bottom-left"></div>
      
      {/* Conteúdo centralizado */}
      <div className="home-content">
        <div className="welcome-section">
          <h1 className="welcome-title">Bem-vindo(a) ao Busfeed!!</h1>
          <h2 className="welcome-subtitle">Para onde quer ir?</h2>
          
          {/* Formulário de busca */}
          <SearchForm 
            onSearch={handleSearch}
            locations={mockLocations}
            isLoading={isSearching}
          />
          
          {/* Botões de navegação */}
          <div className="navigation-buttons">
            <button 
              className="btn-primary"
              onClick={handleGoToMap}
              aria-label="Ir para o mapa de paradas"
            >
              A bordo!
            </button>
            <button 
              className="btn-secondary"
              onClick={handleGoToParadas}
              aria-label="Ver paradas de ônibus"
            >
              Paradas
            </button>
            <button 
              className="btn-secondary btn-third"
              onClick={handleGoToLinhas}
              aria-label="Ir para página de linhas"
            >
              Linhas
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home; 
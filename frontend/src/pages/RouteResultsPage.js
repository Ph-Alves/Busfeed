/**
 * BusFeed - Página de Resultados de Rotas
 * 
 * Página dedicada para exibir:
 * - Resultados da busca de rotas
 * - Detalhes das viagens encontradas
 * - Integração com o mapa
 * - Opções de navegação
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { RouteResultList } from '../components/common/RouteResult';
import MapView from '../components/map/MapView';
import Header from '../components/common/Header';
import { calculateRoutes, mockBusStops } from '../services/routeService';
import '../styles/RouteResult.css';

/**
 * Página de resultados da busca de rotas
 * @returns {JSX.Element} Página de resultados
 */
function RouteResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [routes, setRoutes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [showMap, setShowMap] = useState(false);
  const [error, setError] = useState(null);

  // Dados da busca vindos da navegação
  const searchData = location.state;

  /**
   * Efetua a busca de rotas quando a página carrega
   */
  useEffect(() => {
    const fetchRoutes = async () => {
      if (!searchData || !searchData.origem || !searchData.destino) {
        navigate('/');
        return;
      }

      setIsLoading(true);
      setError(null);
      
      try {
        console.log('Calculando rotas entre:', searchData.origem.name, 'e', searchData.destino.name);
        
        const foundRoutes = await calculateRoutes(
          searchData.origem,
          searchData.destino,
          mockBusStops
        );
        
        console.log('Rotas encontradas:', foundRoutes);
        setRoutes(foundRoutes);
        
        if (foundRoutes.length === 0) {
          setError('Nenhuma rota encontrada entre os pontos selecionados. Tente locais mais próximos.');
        }
      } catch (error) {
        console.error('Erro ao calcular rotas:', error);
        setError('Erro ao buscar rotas. Tente novamente.');
        setRoutes([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRoutes();
  }, [searchData, navigate]);

  /**
   * Manipula a seleção de uma rota
   */
  const handleSelectRoute = (route) => {
    setSelectedRoute(route);
    setShowMap(true);
  };

  /**
   * Volta para a busca
   */
  const handleBackToSearch = () => {
    navigate('/');
  };

  /**
   * Nova busca
   */
  const handleNewSearch = () => {
    navigate('/', { replace: true });
  };

  /**
   * Tenta uma nova busca automática se não encontrou rotas
   */
  const handleRetrySearch = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Tenta buscar com maior raio de alcance
      const foundRoutes = await calculateRoutes(
        searchData.origem,
        searchData.destino,
        mockBusStops
      );
      
      setRoutes(foundRoutes);
      
      if (foundRoutes.length === 0) {
        setError('Ainda não foi possível encontrar rotas. Considere pontos de origem e destino diferentes.');
      }
    } catch (error) {
      console.error('Erro ao tentar novamente:', error);
      setError('Erro ao buscar rotas. Verifique sua conexão.');
    } finally {
      setIsLoading(false);
    }
  };

  // Se não há dados de busca, redireciona
  if (!searchData) {
    return null;
  }

  return (
    <div className="route-results-page">
      <Header showSearch={false} />
      
      <div className="results-container">
        {/* Header da página */}
        <div className="results-header">
          <button 
            className="btn-back"
            onClick={handleBackToSearch}
            aria-label="Voltar para busca"
          >
            ← Voltar
          </button>
          
          <div className="search-summary">
            <h1>Rotas encontradas</h1>
            <p>
              De <strong>{searchData.origem.name}</strong> para <strong>{searchData.destino.name}</strong>
            </p>
          </div>

          <button 
            className="btn-new-search"
            onClick={handleNewSearch}
          >
            Nova Busca
          </button>
        </div>

        {/* Conteúdo principal */}
        <div className="results-content">
          {isLoading ? (
            <div className="loading-state">
              <div className="loading-spinner-large"></div>
              <h3>Calculando melhor rota...</h3>
              <p>Buscando linhas de ônibus disponíveis</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <div className="error-icon">🚫</div>
              <h3>Ops! Algo deu errado</h3>
              <p>{error}</p>
              <div className="error-actions">
                <button 
                  className="btn-retry"
                  onClick={handleRetrySearch}
                >
                  Tentar Novamente
                </button>
                <button 
                  className="btn-back-error"
                  onClick={handleBackToSearch}
                >
                  Voltar à Busca
                </button>
              </div>
            </div>
          ) : routes.length > 0 ? (
            <>
              {/* Lista de rotas */}
              <div className="routes-section">
                <RouteResultList 
                  rotas={routes}
                  onSelectRoute={handleSelectRoute}
                />
              </div>
              
              {/* Mapa (se selecionado) */}
              {showMap && selectedRoute && (
                <div className="map-section">
                  <div className="map-header">
                    <h3>Visualização da Rota</h3>
                    <button 
                      className="btn-close-map"
                      onClick={() => setShowMap(false)}
                    >
                      ✕ Fechar Mapa
                    </button>
                  </div>
                  <MapView 
                    route={selectedRoute}
                    origin={searchData.origem}
                    destination={searchData.destino}
                  />
                </div>
              )}
            </>
          ) : (
            <div className="no-results-state">
              <div className="no-results-icon">🚌</div>
              <h3>Nenhuma rota encontrada</h3>
              <p>Não conseguimos encontrar uma rota de ônibus entre os pontos selecionados.</p>
              <div className="suggestions">
                <h4>Sugestões:</h4>
                <ul>
                  <li>Verifique se os nomes dos locais estão corretos</li>
                  <li>Tente locais mais próximos de terminais ou paradas principais</li>
                  <li>Considere pontos de referência conhecidos</li>
                </ul>
              </div>
              <button 
                className="btn-try-again"
                onClick={handleBackToSearch}
              >
                Tentar Outra Busca
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default RouteResultsPage; 
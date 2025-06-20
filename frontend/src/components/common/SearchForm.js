/**
 * BusFeed - Componente SearchForm
 * 
 * Formulário de busca de rotas com:
 * - Input para origem com autocomplete integrado à API
 * - Input para destino com autocomplete integrado à API
 * - Recomendações baseadas no mapa visível
 * - Validações aprimoradas
 * - Sincronização com dados do backend
 */

import React, { useState, useEffect, useCallback } from 'react';
import { paradasAPI, sincronizacaoAPI } from '../../services/api';

/**
 * Componente de formulário de busca de rotas
 * @param {Function} onSearch - Callback executado ao buscar rota
 * @param {Array} locations - Lista de localizações disponíveis (fallback)
 * @param {boolean} isLoading - Estado de carregamento
 * @param {Object} mapBounds - Limites do mapa visível para recomendações
 * @param {Object} userLocation - Localização do usuário
 * @returns {JSX.Element} Formulário de busca
 */
function SearchForm({ 
  onSearch, 
  locations = [], 
  isLoading = false, 
  mapBounds = null,
  userLocation = null 
}) {
  const [origem, setOrigem] = useState('');
  const [destino, setDestino] = useState('');
  const [origemSuggestions, setOrigemSuggestions] = useState([]);
  const [destinoSuggestions, setDestinoSuggestions] = useState([]);
  const [showOrigemSuggestions, setShowOrigemSuggestions] = useState(false);
  const [showDestinoSuggestions, setShowDestinoSuggestions] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [recomendacoes, setRecomendacoes] = useState([]);
  const [origemSelecionada, setOrigemSelecionada] = useState(null);
  const [destinoSelecionado, setDestinoSelecionado] = useState(null);

  /**
   * Busca sugestões da API com debounce
   */
  const buscarSugestoes = useCallback(async (query, isOrigem = true) => {
    if (!query || query.length < 2) {
      if (isOrigem) {
        setOrigemSuggestions([]);
      } else {
        setDestinoSuggestions([]);
      }
      return;
    }

    setIsLoadingSuggestions(true);
    
    try {
      // Busca da API principal
      const sugestoesAPI = await paradasAPI.buscarParaAutocomplete(query);
      
      // Combina com dados locais como fallback
      const sugestoesLocais = filterSuggestions(query, locations);
      
      // Combina e remove duplicatas
      const todasSugestoes = [...sugestoesAPI];
      sugestoesLocais.forEach(local => {
        if (!todasSugestoes.find(s => s.name === local.name)) {
          todasSugestoes.push(local);
        }
      });

      // Prioriza sugestões baseadas no mapa visível
      const sugestoesPriorizadas = priorizarSugestoesPorMapa(todasSugestoes);
      
      if (isOrigem) {
        setOrigemSuggestions(sugestoesPriorizadas.slice(0, 8));
      } else {
        setDestinoSuggestions(sugestoesPriorizadas.slice(0, 8));
      }
    } catch (error) {
      console.error('Erro ao buscar sugestões:', error);
      
      // Fallback para dados locais
      const sugestoesLocais = filterSuggestions(query, locations);
      if (isOrigem) {
        setOrigemSuggestions(sugestoesLocais);
      } else {
        setDestinoSuggestions(sugestoesLocais);
      }
    } finally {
      setIsLoadingSuggestions(false);
    }
  }, [locations, mapBounds]);

  /**
   * Prioriza sugestões baseadas no mapa visível
   */
  const priorizarSugestoesPorMapa = (sugestoes) => {
    if (!mapBounds) return sugestoes;

    const { north, south, east, west } = mapBounds;
    
    return sugestoes.sort((a, b) => {
      const aNoMapa = a.coordinates && 
        a.coordinates[0] >= south && a.coordinates[0] <= north &&
        a.coordinates[1] >= west && a.coordinates[1] <= east;
      
      const bNoMapa = b.coordinates && 
        b.coordinates[0] >= south && b.coordinates[0] <= north &&
        b.coordinates[1] >= west && b.coordinates[1] <= east;

      if (aNoMapa && !bNoMapa) return -1;
      if (!aNoMapa && bNoMapa) return 1;

      // Se ambos estão no mapa ou ambos não estão, ordena por tipo
      const priorityOrder = { terminal: 1, metro: 2, main: 3, shopping: 4, hospital: 5 };
      const aPriority = priorityOrder[a.type] || 99;
      const bPriority = priorityOrder[b.type] || 99;
      
      if (aPriority !== bPriority) return aPriority - bPriority;
      
      return a.name.localeCompare(b.name);
    });
  };

  /**
   * Filtra sugestões locais (fallback)
   */
  const filterSuggestions = (value, locationsList) => {
    if (!value || value.length < 2) return [];
    
    const filtered = locationsList.filter(location =>
      location.name.toLowerCase().includes(value.toLowerCase()) ||
      (location.description && location.description.toLowerCase().includes(value.toLowerCase()))
    );

    return filtered.sort((a, b) => {
      const priorityOrder = { terminal: 1, metro: 2, shopping: 3, hospital: 4, educacao: 5 };
      const aPriority = priorityOrder[a.type] || 99;
      const bPriority = priorityOrder[b.type] || 99;
      
      if (aPriority !== bPriority) return aPriority - bPriority;
      return a.name.localeCompare(b.name);
    }).slice(0, 6);
  };

  /**
   * Busca recomendações baseadas na localização do usuário
   */
  const buscarRecomendacoes = useCallback(async () => {
    if (!userLocation) return;

    try {
      const dados = await sincronizacaoAPI.buscarRecomendacoes(
        userLocation.latitude, 
        userLocation.longitude
      );
      
      const recomendacoesFormatadas = [
        ...dados.paradasProximas.slice(0, 5).map(parada => ({
          type: 'parada_proxima',
          name: parada.nome,
          description: `${Math.round(parada.distancia)}m - ${parada.descricao || parada.endereco}`,
          coordinates: parada.coordinates,
          icon: '📍'
        })),
        ...dados.linhasPopulares.slice(0, 3).map(linha => ({
          type: 'linha_popular',
          name: linha.nome,
          description: `${linha.origem} → ${linha.destino}`,
          coordinates: null,
          icon: '🚌'
        }))
      ];

      setRecomendacoes(recomendacoesFormatadas);
    } catch (error) {
      console.error('Erro ao buscar recomendações:', error);
    }
  }, [userLocation]);

  /**
   * Debounce para busca de sugestões - Tempo reduzido para resposta mais rápida
   */
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (origem && origem.length >= 2) {
        buscarSugestoes(origem, true);
      }
    }, 150); // Reduzido de 300ms para 150ms para resposta mais rápida

    return () => clearTimeout(timeoutId);
  }, [origem, buscarSugestoes]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (destino && destino.length >= 2) {
        buscarSugestoes(destino, false);
      }
    }, 150); // Reduzido de 300ms para 150ms para resposta mais rápida

    return () => clearTimeout(timeoutId);
  }, [destino, buscarSugestoes]);

  /**
   * Carrega recomendações quando a localização do usuário muda
   */
  useEffect(() => {
    buscarRecomendacoes();
  }, [buscarRecomendacoes]);

  /**
   * Manipula mudança no input de origem
   */
  const handleOrigemChange = (e) => {
    const value = e.target.value;
    setOrigem(value);
    setOrigemSelecionada(null);
    setShowOrigemSuggestions(value.length >= 2);
    
    if (errors.origem) {
      setErrors(prev => ({ ...prev, origem: null }));
    }
  };

  /**
   * Manipula mudança no input de destino
   */
  const handleDestinoChange = (e) => {
    const value = e.target.value;
    setDestino(value);
    setDestinoSelecionado(null);
    setShowDestinoSuggestions(value.length >= 2);
    
    if (errors.destino) {
      setErrors(prev => ({ ...prev, destino: null }));
    }
  };

  /**
   * Seleciona uma sugestão de origem
   */
  const selectOrigemSuggestion = (suggestion) => {
    setOrigem(suggestion.name);
    setOrigemSelecionada(suggestion);
    setShowOrigemSuggestions(false);
    setErrors(prev => ({ ...prev, origem: null }));
  };

  /**
   * Seleciona uma sugestão de destino
   */
  const selectDestinoSuggestion = (suggestion) => {
    setDestino(suggestion.name);
    setDestinoSelecionado(suggestion);
    setShowDestinoSuggestions(false);
    setErrors(prev => ({ ...prev, destino: null }));
  };



  /**
   * Ícone para tipo de local
   */
  const getLocationIcon = (type) => {
    const icons = {
      terminal: '🚌',
      metro: '🚇',
      main: '🚏',
      shopping: '🛍️',
      hospital: '🏥',
      educacao: '🎓',
      aeroporto: '✈️',
      turistico: '🏛️',
      comercio: '🏪',
      residencial: '🏠'
    };
    return icons[type] || '📍';
  };

  /**
   * Validações do formulário
   */
  const validateForm = () => {
    const newErrors = {};

    if (!origem.trim()) {
      newErrors.origem = 'Informe o local de origem';
    }

    if (!destino.trim()) {
      newErrors.destino = 'Informe o destino';
    }

    if (origem.trim() && destino.trim() && origem.trim().toLowerCase() === destino.trim().toLowerCase()) {
      newErrors.destino = 'Origem e destino devem ser diferentes';
    }

    // Verifica se os locais foram selecionados das sugestões
    if (origem.trim() && !origemSelecionada) {
      // Tenta encontrar correspondência exata
      const correspondencia = [...origemSuggestions, ...locations].find(loc => 
        loc.name.toLowerCase() === origem.toLowerCase()
      );
      if (!correspondencia) {
        newErrors.origem = 'Selecione um local da lista de sugestões';
      } else {
        setOrigemSelecionada(correspondencia);
      }
    }

    if (destino.trim() && !destinoSelecionado) {
      const correspondencia = [...destinoSuggestions, ...locations].find(loc => 
        loc.name.toLowerCase() === destino.toLowerCase()
      );
      if (!correspondencia) {
        newErrors.destino = 'Selecione um local da lista de sugestões';
      } else {
        setDestinoSelecionado(correspondencia);
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Manipula o envio do formulário
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Executa a busca com os dados selecionados
    onSearch({
      origem: origemSelecionada,
      destino: destinoSelecionado
    });
  };

  /**
   * Usa localização atual como origem
   */
  const usarLocalizacaoAtual = () => {
    if (userLocation) {
      const localizacaoAtual = {
        name: 'Minha Localização',
        description: 'Localização atual do usuário',
        coordinates: [userLocation.latitude, userLocation.longitude],
        type: 'user_location'
      };
      
      setOrigem(localizacaoAtual.name);
      setOrigemSelecionada(localizacaoAtual);
      setShowOrigemSuggestions(false);
    }
  };

  return (
    <div className="search-form">
      <form onSubmit={handleSubmit} className="search-form-container">
        {/* Campo de Origem */}
        <div className="form-group">
          <label htmlFor="origem" className="form-label">
            De onde você está saindo?
          </label>
          <div className="input-container">
            <input
              id="origem"
              type="text"
              value={origem}
              onChange={handleOrigemChange}
              onFocus={() => setShowOrigemSuggestions(origem.length >= 2)}
              onBlur={() => setTimeout(() => setShowOrigemSuggestions(false), 200)}
              placeholder="Digite o local de origem..."
              className={`form-input ${errors.origem ? 'error' : ''}`}
              autoComplete="off"
            />
            
            {/* Botão de localização atual */}
            {userLocation && (
              <button
                type="button"
                onClick={usarLocalizacaoAtual}
                className="location-button"
                title="Usar minha localização atual"
              >
                📍
              </button>
            )}
            
            {/* Sugestões de origem */}
            {showOrigemSuggestions && (origemSuggestions.length > 0 || isLoadingSuggestions) && (
              <div className="suggestions-dropdown">
                {isLoadingSuggestions && (
                  <div className="suggestion-item loading">
                    <span>Buscando sugestões...</span>
                  </div>
                )}
                
                {origemSuggestions.map((suggestion, index) => (
                  <div
                    key={`origem-${suggestion.id || index}`}
                    className="suggestion-item"
                    onClick={() => selectOrigemSuggestion(suggestion)}
                  >
                    <span className="suggestion-icon">
                      {getLocationIcon(suggestion.type)}
                    </span>
                    <div className="suggestion-content">
                      <div className="suggestion-name">{suggestion.name}</div>
                      {suggestion.description && (
                        <div className="suggestion-description">{suggestion.description}</div>
                      )}
                      {suggestion.lines && suggestion.lines.length > 0 && (
                        <div className="suggestion-lines">
                          Linhas: {suggestion.lines.slice(0, 3).join(', ')}
                          {suggestion.lines.length > 3 && '...'}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {errors.origem && <div className="error-message">{errors.origem}</div>}
        </div>

        {/* Campo de Destino */}
        <div className="form-group">
          <label htmlFor="destino" className="form-label">
            Para onde você quer ir?
          </label>
          <div className="input-container">
            <input
              id="destino"
              type="text"
              value={destino}
              onChange={handleDestinoChange}
              onFocus={() => setShowDestinoSuggestions(destino.length >= 2)}
              onBlur={() => setTimeout(() => setShowDestinoSuggestions(false), 200)}
              placeholder="Digite o destino..."
              className={`form-input ${errors.destino ? 'error' : ''}`}
              autoComplete="off"
            />
            
            {/* Sugestões de destino */}
            {showDestinoSuggestions && (destinoSuggestions.length > 0 || isLoadingSuggestions) && (
              <div className="suggestions-dropdown">
                {isLoadingSuggestions && (
                  <div className="suggestion-item loading">
                    <span>Buscando sugestões...</span>
                  </div>
                )}
                
                {destinoSuggestions.map((suggestion, index) => (
                  <div
                    key={`destino-${suggestion.id || index}`}
                    className="suggestion-item"
                    onClick={() => selectDestinoSuggestion(suggestion)}
                  >
                    <span className="suggestion-icon">
                      {getLocationIcon(suggestion.type)}
                    </span>
                    <div className="suggestion-content">
                      <div className="suggestion-name">{suggestion.name}</div>
                      {suggestion.description && (
                        <div className="suggestion-description">{suggestion.description}</div>
                      )}
                      {suggestion.lines && suggestion.lines.length > 0 && (
                        <div className="suggestion-lines">
                          Linhas: {suggestion.lines.slice(0, 3).join(', ')}
                          {suggestion.lines.length > 3 && '...'}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {errors.destino && <div className="error-message">{errors.destino}</div>}
        </div>

        {/* Botão de busca */}
        <button
          type="submit"
          className={`btn-search ${isLoading ? 'loading' : ''}`}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="loading-spinner"></span>
              Buscando rotas...
            </>
          ) : (
            <>
              🔍 Buscar Rotas
            </>
          )}
        </button>
      </form>

      {/* Recomendações - Mostrar quando não há texto nos inputs */}
      {recomendacoes.length > 0 && origem.trim() === '' && destino.trim() === '' && (
        <div className="recomendacoes">
          <h4 className="recomendacoes-title">Sugestões baseadas na sua localização:</h4>
          <div className="recomendacoes-list">
            {recomendacoes.map((rec, index) => (
              <div
                key={`rec-${index}`}
                className={`recomendacao-item ${rec.type}`}
                onClick={() => {
                  // Sempre usar como origem se tiver coordenadas
                  if (rec.coordinates) {
                    selectOrigemSuggestion(rec);
                  }
                }}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    if (rec.coordinates) {
                      selectOrigemSuggestion(rec);
                    }
                  }
                }}
              >
                <span className="recomendacao-icon">{rec.icon}</span>
                <div className="recomendacao-content">
                  <div className="recomendacao-name">{rec.name}</div>
                  <div className="recomendacao-description">{rec.description}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchForm; 
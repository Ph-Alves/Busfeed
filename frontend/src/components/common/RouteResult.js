/**
 * BusFeed - Componente RouteResult
 * 
 * Exibe os resultados de uma busca de rota com:
 * - Informações claras e organizadas
 * - Design limpo e legível
 * - Hierarquia visual intuitiva
 * - Dados bem estruturados
 */

import React, { useState } from 'react';
import { rotasAPI, linhasAPI } from '../../services/api';

/**
 * Componente para exibir uma única rota com dados claros
 * @param {Object} rota - Dados da rota
 * @param {Function} onSelectRoute - Callback quando rota é selecionada
 * @param {Function} onShowOnMap - Callback para mostrar rota no mapa
 * @param {boolean} isSelected - Se a rota está selecionada
 * @returns {JSX.Element} Componente de rota
 */
function RouteResult({ 
  rota, 
  onSelectRoute, 
  onShowOnMap, 
  isSelected = false,
  onSaveRoute = null 
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [detalhesLinhas, setDetalhesLinhas] = useState({});
  const [loadingDetalhes, setLoadingDetalhes] = useState(false);

  /**
   * Formata tempo em minutos para exibição clara
   */
  const formatarTempo = (minutos) => {
    if (!minutos || minutos < 1) return '< 1 min';
    if (minutos < 60) {
      return `${Math.round(minutos)} min`;
    }
    const horas = Math.floor(minutos / 60);
    const minutosRestantes = minutos % 60;
    return minutosRestantes > 0 ? `${horas}h ${minutosRestantes}min` : `${horas}h`;
  };

  /**
   * Formata distância em metros para exibição clara
   */
  const formatarDistancia = (metros) => {
    if (!metros || metros < 1) return '0m';
    if (metros < 1000) {
      return `${Math.round(metros)}m`;
    }
    return `${(metros / 1000).toFixed(1)}km`;
  };

  /**
   * Formata valor monetário brasileiro
   */
  const formatarValor = (valor) => {
    if (!valor || valor === 0) return 'Gratuito';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2
    }).format(valor);
  };

  /**
   * Obtém ícone para tipo de transporte
   */
  const getIconeTransporte = (tipo) => {
    const icones = {
      onibus: '🚌',
      metro: '🚇',
      brt: '🚊',
      caminhada: '🚶‍♂️',
      micro: '🚐',
      trem: '🚆'
    };
    return icones[tipo?.toLowerCase()] || '🚌';
  };

  /**
   * Obtém classe CSS para tipo de transporte
   */
  const getClasseTransporte = (tipo) => {
    const classes = {
      onibus: 'bus',
      metro: 'metro',
      brt: 'bus',
      caminhada: 'walk',
      micro: 'bus',
      trem: 'metro'
    };
    return classes[tipo?.toLowerCase()] || 'bus';
  };

  /**
   * Carrega detalhes das linhas da rota
   */
  const carregarDetalhesLinhas = async () => {
    if (loadingDetalhes || Object.keys(detalhesLinhas).length > 0) return;

    setLoadingDetalhes(true);
    
    try {
      const linhasCodigos = rota.segmentos
        ?.filter(seg => seg.tipo !== 'caminhada' && seg.linha)
        .map(seg => seg.linha)
        .filter((codigo, index, arr) => arr.indexOf(codigo) === index) || [];

      const detalhesPromises = linhasCodigos.map(async (codigo) => {
        try {
          const detalhes = await linhasAPI.buscarDetalhes(codigo);
          return { codigo, detalhes };
        } catch (error) {
          console.error(`Erro ao buscar detalhes da linha ${codigo}:`, error);
          return { codigo, detalhes: null };
        }
      });

      const resultados = await Promise.all(detalhesPromises);
      const novosDetalhes = {};
      
      resultados.forEach(({ codigo, detalhes }) => {
        if (detalhes) {
          novosDetalhes[codigo] = detalhes;
        }
      });

      setDetalhesLinhas(novosDetalhes);
    } catch (error) {
      console.error('Erro ao carregar detalhes das linhas:', error);
    } finally {
      setLoadingDetalhes(false);
    }
  };

  /**
   * Manipula expansão dos detalhes
   */
  const handleToggleExpand = () => {
    const novoEstado = !isExpanded;
    setIsExpanded(novoEstado);
    
    if (novoEstado) {
      carregarDetalhesLinhas();
    }
  };

  /**
   * Manipula seleção da rota
   */
  const handleSelectRoute = () => {
    if (onSelectRoute) {
      onSelectRoute(rota);
    }
  };

  /**
   * Manipula visualização no mapa
   */
  const handleShowOnMap = () => {
    if (onShowOnMap) {
      onShowOnMap(rota);
    }
  };

  /**
   * Salva a rota como favorita
   */
  const handleSaveRoute = async () => {
    if (!onSaveRoute) return;

    setIsSaving(true);
    
    try {
      await rotasAPI.salvarRota({
        origem: rota.origem,
        destino: rota.destino,
        dados_rota: rota,
        nome: `${rota.origem} → ${rota.destino}`
      });
      
      if (onSaveRoute) {
        onSaveRoute(rota);
      }
    } catch (error) {
      console.error('Erro ao salvar rota:', error);
      alert('Erro ao salvar rota. Tente novamente.');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Renderiza badges dos tipos de transporte utilizados
   * Função segura com verificação de valores nulos/indefinidos
   */
  const renderTransporteBadges = () => {
    // Verifica se existem segmentos na rota
    if (!rota.segmentos || rota.segmentos.length === 0) return null;

    // Filtra e obtém tipos únicos de transporte, removendo valores inválidos
    const transportesUsados = [...new Set(
      rota.segmentos
        .map(seg => seg.tipo)
        .filter(tipo => tipo && typeof tipo === 'string') // Remove valores nulos/indefinidos
    )];

    // Se não há transportes válidos, não renderiza nada
    if (transportesUsados.length === 0) return null;

    return (
      <div className="transport-badges">
        {transportesUsados.map(tipo => {
          // Garante que tipo é uma string válida antes de processar
          const tipoSeguro = tipo || 'desconhecido';
          const nomeExibicao = tipoSeguro === 'caminhada' ? 'A pé' : tipoSeguro.toUpperCase();
          
          return (
            <div key={tipoSeguro} className={`transport-badge ${getClasseTransporte(tipoSeguro)}`}>
              <span>{getIconeTransporte(tipoSeguro)}</span>
              <span>{nomeExibicao}</span>
            </div>
          );
        })}
      </div>
    );
  };

  /**
   * Renderiza um segmento da rota com informações claras
   * Função segura com verificação de dados válidos
   */
  const renderSegmento = (segmento, index) => {
    // Verifica se o segmento é válido
    if (!segmento) return null;
    
    // Garante que tipo é uma string válida
    const tipoSegmento = segmento.tipo || 'desconhecido';
    const isCaminhada = tipoSegmento === 'caminhada';
    const icone = getIconeTransporte(tipoSegmento);
    
    return (
      <div key={index} className={`route-segment ${isCaminhada ? 'walk' : 'transport'}`}>
        <div className={`segment-icon ${isCaminhada ? '' : 'transport'}`}>
          {icone}
        </div>
        
        <div className="segment-content">
          <h4 className="segment-title">
            {isCaminhada ? 
              `Caminhar ${formatarDistancia(segmento.distancia)}` : 
              `Linha ${segmento.linha || 'N/A'}`
            }
          </h4>
          
          <p className="segment-subtitle">
            {isCaminhada ? 
              `Tempo estimado: ${formatarTempo(segmento.tempo)}` :
              `${segmento.origem || 'Origem'} → ${segmento.destino || 'Destino'}`
            }
          </p>
          
          <div className="segment-details">
            <div className="segment-detail-item">
              <span>⏱️</span>
              <span><strong>{formatarTempo(segmento.tempo)}</strong></span>
            </div>
            
            <div className="segment-detail-item">
              <span>📏</span>
              <span><strong>{formatarDistancia(segmento.distancia)}</strong></span>
            </div>
            
            {!isCaminhada && segmento.tarifa && (
              <div className="segment-detail-item">
                <span>💰</span>
                <span><strong>{formatarValor(segmento.tarifa)}</strong></span>
              </div>
            )}
            
            {!isCaminhada && segmento.paradas && (
              <div className="segment-detail-item">
                <span>🚏</span>
                <span><strong>{segmento.paradas} paradas</strong></span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Valores padrão para dados ausentes
  const tempoTotal = rota.tempo_total || rota.duracao || 0;
  const custoTotal = rota.custo_total || rota.tarifa || 0;
  const distanciaTotal = rota.distancia_total || rota.distancia || 0;

  return (
    <div className={`route-result ${isSelected ? 'selected' : ''}`}>
      {/* Header com informações principais */}
      <div className="route-header">
        <div className="route-main-info">
          {/* Dados primários: Tempo, Custo, Distância */}
          <div className="route-primary-data">
            <div className="time-info">
              <div className="time-duration">{formatarTempo(tempoTotal)}</div>
              <div className="time-label">Duração</div>
            </div>
            
            <div className="cost-info">
              <div className="cost-value">{formatarValor(custoTotal)}</div>
              <div className="cost-label">Custo</div>
            </div>
            
            <div className="distance-info">
              <div className="distance-value">{formatarDistancia(distanciaTotal)}</div>
              <div className="distance-label">Distância</div>
            </div>
          </div>
          
          {/* Badges de transporte */}
          {renderTransporteBadges()}
          
          {/* Botões de ação */}
          <div className="route-actions">
            <button 
              className="btn-route-action"
              onClick={handleToggleExpand}
              title={isExpanded ? "Ocultar detalhes" : "Ver detalhes"}
            >
              <span>{isExpanded ? '▲' : '▼'}</span>
              <span>Detalhes</span>
            </button>
            
            <button 
              className="btn-route-action"
              onClick={handleShowOnMap}
              title="Ver no mapa"
            >
              <span>🗺️</span>
              <span>Mapa</span>
            </button>
            
            <button 
              className="btn-route-action primary"
              onClick={handleSelectRoute}
              title="Selecionar esta rota"
            >
              <span>✓</span>
              <span>Escolher</span>
            </button>
          </div>
        </div>
      </div>

      {/* Detalhes expandidos da rota */}
      <div className={`route-details ${isExpanded ? 'expanded' : ''}`}>
        {isExpanded && (
          <div className="route-segments">
            {rota.segmentos && rota.segmentos.length > 0 ? (
              rota.segmentos.map((segmento, index) => (
                <React.Fragment key={index}>
                  {renderSegmento(segmento, index)}
                  {index < rota.segmentos.length - 1 && (
                    <div className="segment-connector">
                      <div className="connector-line"></div>
                    </div>
                  )}
                </React.Fragment>
              ))
            ) : (
              <div className="segment-content">
                <p className="text-muted text-center">
                  Detalhes da rota não disponíveis no momento.
                </p>
              </div>
            )}
            
            {loadingDetalhes && (
              <div className="text-center">
                <p className="text-muted">Carregando detalhes adicionais...</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Componente para lista de resultados de rotas
 */
export function RouteResultList({ 
  rotas = [], 
  onSelectRoute, 
  onShowOnMap, 
  rotaSelecionada = null,
  onSaveRoute = null,
  isLoading = false 
}) {
  if (isLoading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner-large"></div>
        <h3>Calculando melhores rotas...</h3>
        <p>Buscando as opções de transporte mais eficientes para você.</p>
      </div>
    );
  }

  if (!rotas || rotas.length === 0) {
    return (
      <div className="no-results-state">
        <div className="error-icon">🚌</div>
        <h3>Nenhuma rota encontrada</h3>
        <p>
          Não foi possível encontrar rotas de transporte público para o trajeto solicitado.
          Tente ajustar os pontos de origem e destino.
        </p>
      </div>
    );
  }

  return (
    <div className="routes-list">
      {rotas.map((rota, index) => (
        <RouteResult
          key={rota.id || index}
          rota={rota}
          onSelectRoute={onSelectRoute}
          onShowOnMap={onShowOnMap}
          onSaveRoute={onSaveRoute}
          isSelected={rotaSelecionada && rotaSelecionada.id === rota.id}
        />
      ))}
    </div>
  );
}

export default RouteResult; 
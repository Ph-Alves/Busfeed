/**
 * BusFeed - Componente de Detalhes da Rota
 * 
 * Exibe informações detalhadas sobre uma linha de ônibus específica,
 * incluindo paradas, horários e trajeto.
 * Mantém design consistente com a aplicação.
 */

import React from 'react';
import { Card, Row, Col, Badge } from 'react-bootstrap';
import '../../styles/RouteDetails.css';

/**
 * Dados mock da rota da linha 0.092 (Estação Guará - Centro)
 * Em produção, estes dados viriam de uma API
 */
const rotaLinha092 = {
  numero: '0.092',
  nome: 'Estação Guará - Centro',
  preco: 3.80,
  tempoViagem: '45 min',
  frequencia: '15-20 min',
  operadora: 'Viação Capital',
  paradas: [
    {
      id: 1,
      nome: 'Estação Guará',
      endereco: 'QE 40, Guará II',
      horario: '05:30',
      tipo: 'terminal'
    },
    {
      id: 2,
      nome: 'Parada Shopping Guará',
      endereco: 'QI 7, Guará I',
      horario: '05:35',
      tipo: 'comum'
    },
    {
      id: 3,
      nome: 'Parada SIA',
      endereco: 'SIA Trecho 1',
      horario: '05:45',
      tipo: 'comum'
    },
    {
      id: 4,
      nome: 'Parada Rodoviária',
      endereco: 'Rodoviária do Plano Piloto',
      horario: '06:00',
      tipo: 'importante'
    },
    {
      id: 5,
      nome: 'Parada Central',
      endereco: 'Setor Comercial Sul',
      horario: '06:10',
      tipo: 'comum'
    },
    {
      id: 6,
      nome: 'Centro - Final',
      endereco: 'Setor Bancário Sul',
      horario: '06:15',
      tipo: 'terminal'
    }
  ]
};

/**
 * Componente para exibir detalhes da rota
 * @param {Object} props - Props do componente
 * @param {string} props.numeroLinha - Número da linha selecionada
 * @param {Function} props.onClose - Callback para fechar os detalhes
 * @returns {JSX.Element} Detalhes da rota
 */
function RouteDetails({ numeroLinha, onClose }) {
  // Por enquanto, apenas a linha 0.092 tem dados completos
  const rota = numeroLinha === '0.092' ? rotaLinha092 : null;

  if (!rota) {
    return (
      <Card className="route-details-card">
        <Card.Body className="text-center p-4">
          <h5 className="text-light mb-3">Linha {numeroLinha}</h5>
          <p className="text-light-50">
            Detalhes da rota ainda não disponíveis para esta linha.
          </p>
          <button 
            className="btn-voltar"
            onClick={onClose}
            aria-label="Voltar para lista de linhas"
          >
            ← Voltar
          </button>
        </Card.Body>
      </Card>
    );
  }

  /**
   * Determina o ícone da parada baseado no tipo
   * @param {string} tipo - Tipo da parada
   * @returns {string} Ícone correspondente
   */
  const getIconeParada = (tipo) => {
    switch (tipo) {
      case 'terminal': return '🚌';
      case 'importante': return '🚏';
      default: return '📍';
    }
  };

  /**
   * Determina a classe CSS da parada baseado no tipo
   * @param {string} tipo - Tipo da parada
   * @returns {string} Classe CSS correspondente
   */
  const getClasseParada = (tipo) => {
    switch (tipo) {
      case 'terminal': return 'parada-terminal';
      case 'importante': return 'parada-importante';
      default: return 'parada-comum';
    }
  };

  return (
    <Card className="route-details-card">
      <Card.Body className="p-0">
        {/* Cabeçalho da rota */}
        <div className="route-header">
          <div className="route-info">
            <div className="d-flex align-items-center gap-3 mb-2">
              <h4 className="route-number">Linha {rota.numero}</h4>
              <Badge bg="primary" className="route-price">
                R$ {rota.preco.toFixed(2).replace('.', ',')}
              </Badge>
            </div>
            <h5 className="route-name">{rota.nome}</h5>
            <div className="route-stats">
              <span className="stat-item">
                <strong>Tempo:</strong> {rota.tempoViagem}
              </span>
              <span className="stat-item">
                <strong>Frequência:</strong> {rota.frequencia}
              </span>
            </div>
          </div>
          <button 
            className="btn-voltar"
            onClick={onClose}
            aria-label="Voltar para lista de linhas"
          >
            ← Voltar
          </button>
        </div>

        {/* Lista de paradas */}
        <div className="paradas-container">
          <h6 className="paradas-titulo">Trajeto e Paradas</h6>
          <div className="paradas-lista">
            {rota.paradas.map((parada, index) => (
              <div 
                key={parada.id}
                className={`parada-item ${getClasseParada(parada.tipo)}`}
              >
                <div className="parada-timeline">
                  <div className="parada-icone">
                    {getIconeParada(parada.tipo)}
                  </div>
                  {index < rota.paradas.length - 1 && (
                    <div className="timeline-linha"></div>
                  )}
                </div>
                
                <div className="parada-info">
                  <div className="parada-nome">{parada.nome}</div>
                  <div className="parada-endereco">{parada.endereco}</div>
                  <div className="parada-horario">
                    Primeiro ônibus: {parada.horario}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Informações adicionais */}
        <div className="route-footer">
          <div className="operadora-info">
            <strong>Operadora:</strong> {rota.operadora}
          </div>
          <div className="aviso-horarios">
            <small>
              * Horários sujeitos a alterações. Consulte sempre os painéis nas paradas.
            </small>
          </div>
        </div>
      </Card.Body>
    </Card>
  );
}

export default RouteDetails; 
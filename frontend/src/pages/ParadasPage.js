/**
 * BusFeed - Página de Paradas
 * 
 * Página para visualizar e gerenciar paradas de ônibus.
 * Exibe lista de paradas com funcionalidades de busca e filtros.
 */

import React, { useState, useMemo } from 'react';
import { Card, Row, Col, Badge, Form, InputGroup, Button } from 'react-bootstrap';
import Header from '../components/common/Header';

/**
 * Dados das paradas de ônibus (importados do MapView para consistência)
 * Em produção, estes dados virão da API Django
 */
const mockBusStops = [
  // Paradas principais (maior movimento)
  {
    id: 1,
    name: "Terminal Ceilândia Centro",
    coordinates: [-15.8267, -48.1089],
    lines: ["QNM 13", "QNM 17", "QNM 19", "0.030", "0.032"],
    description: "Terminal principal da Ceilândia",
    type: "main",
    passengers: 850,
    accessibility: true
  },
  {
    id: 2,
    name: "Shopping Ceilândia",
    coordinates: [-15.8245, -48.1125],
    lines: ["QNM 11", "QNM 15", "0.028", "0.031"],
    description: "Próximo ao Shopping Ceilândia",
    type: "main",
    passengers: 620,
    accessibility: true
  },
  {
    id: 3,
    name: "Hospital Regional da Ceilândia",
    coordinates: [-15.8198, -48.1067],
    lines: ["QNN 102", "QNN 104", "0.025"],
    description: "Parada do Hospital Regional",
    type: "main",
    passengers: 480,
    accessibility: true
  },
  {
    id: 4,
    name: "Terminal Ceilândia Sul",
    coordinates: [-15.8456, -48.1178],
    lines: ["QNO 01", "QNO 03", "QNO 05", "0.037"],
    description: "Terminal da região sul",
    type: "main",
    passengers: 750,
    accessibility: true
  },
  {
    id: 5,
    name: "Centro Metropolitano",
    coordinates: [-15.8189, -48.1034],
    lines: ["QNN 99", "QNN 101", "0.024"],
    description: "Centro comercial metropolitano",
    type: "main",
    passengers: 680,
    accessibility: true
  },
  // Paradas secundárias - Região Central
  {
    id: 6,
    name: "QNM 13 - Conjunto A",
    coordinates: [-15.8289, -48.1078],
    lines: ["QNM 21", "QNM 23"],
    description: "Quadra residencial QNM 13",
    type: "secondary",
    passengers: 180,
    accessibility: false
  },
  {
    id: 7,
    name: "QNM 15 - Comércio Local",
    coordinates: [-15.8234, -48.1098],
    lines: ["QNM 17", "0.030"],
    description: "Área comercial da QNM 15",
    type: "secondary",
    passengers: 220,
    accessibility: true
  },
  {
    id: 8,
    name: "QNM 17 - Escola Municipal",
    coordinates: [-15.8312, -48.1056],
    lines: ["QNM 17", "0.030"],
    description: "Próximo à escola municipal",
    type: "secondary",
    passengers: 195,
    accessibility: true
  },
  {
    id: 9,
    name: "QNM 19 - Posto de Saúde",
    coordinates: [-15.8201, -48.1123],
    lines: ["QNM 25", "0.029"],
    description: "Próximo ao posto de saúde",
    type: "secondary",
    passengers: 140,
    accessibility: true
  },
  {
    id: 10,
    name: "QNM 21 - Praça Central",
    coordinates: [-15.8278, -48.1156],
    lines: ["QNM 21", "QNM 23"],
    description: "Praça da quadra 21",
    type: "secondary",
    passengers: 125,
    accessibility: false
  },
  // Paradas secundárias - Região Norte
  {
    id: 11,
    name: "QNN 102 - Supermercado",
    coordinates: [-15.8156, -48.1089],
    lines: ["QNN 102", "0.033"],
    description: "Próximo ao supermercado",
    type: "secondary",
    passengers: 165,
    accessibility: false
  },
  {
    id: 12,
    name: "QNN 104 - Igreja Universal",
    coordinates: [-15.8134, -48.1067],
    lines: ["QNN 104", "0.025"],
    description: "Próximo à Igreja Universal",
    type: "secondary",
    passengers: 135,
    accessibility: false
  },
  {
    id: 13,
    name: "QNN 106 - Farmácia Popular",
    coordinates: [-15.8123, -48.1045],
    lines: ["QNN 106", "0.026"],
    description: "Próximo à farmácia popular",
    type: "secondary",
    passengers: 110,
    accessibility: true
  },
  {
    id: 14,
    name: "QNN 108 - Mercadinho do João",
    coordinates: [-15.8167, -48.1123],
    lines: ["QNN 108", "0.027"],
    description: "Próximo ao mercadinho",
    type: "secondary",
    passengers: 85,
    accessibility: false
  },
  {
    id: 15,
    name: "QNN 110 - Padaria Estrela",
    coordinates: [-15.8145, -48.1134],
    lines: ["QNN 110"],
    description: "Próximo à padaria",
    type: "secondary",
    passengers: 95,
    accessibility: false
  },
  // Paradas secundárias - Região Sul
  {
    id: 16,
    name: "QNO 15 - Condomínio Ville",
    coordinates: [-15.8345, -48.1145],
    lines: ["QNO 15", "0.035"],
    description: "Condomínio residencial",
    type: "secondary",
    passengers: 145,
    accessibility: false
  },
  {
    id: 17,
    name: "QNO 17 - Escola Técnica",
    coordinates: [-15.8378, -48.1167],
    lines: ["QNO 17", "0.036"],
    description: "Escola Técnica de Ceilândia",
    type: "secondary",
    passengers: 280,
    accessibility: true
  },
  {
    id: 18,
    name: "QNO 19 - Lotérica",
    coordinates: [-15.8412, -48.1189],
    lines: ["QNO 19", "0.037"],
    description: "Próximo à lotérica",
    type: "secondary",
    passengers: 90,
    accessibility: false
  },
  {
    id: 19,
    name: "QNO 21 - Centro Comunitário",
    coordinates: [-15.8434, -48.1201],
    lines: ["QNO 21"],
    description: "Centro comunitário local",
    type: "secondary",
    passengers: 75,
    accessibility: true
  },
  {
    id: 20,
    name: "QNO 03 - Colégio Estadual",
    coordinates: [-15.8389, -48.1134],
    lines: ["QNO 03", "0.034"],
    description: "Colégio Estadual Ceilândia",
    type: "secondary",
    passengers: 320,
    accessibility: true
  }
];

/**
 * Componente da página de paradas
 * @returns {JSX.Element} Página de paradas
 */
function ParadasPage() {
  // Estados para controle da página
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterAccessibility, setFilterAccessibility] = useState('all');
  const [sortBy, setSortBy] = useState('name');

  /**
   * Filtra e ordena as paradas baseado nos critérios selecionados
   */
  const filteredAndSortedStops = useMemo(() => {
    let filtered = mockBusStops.filter(stop => {
      // Filtro por termo de busca
      const matchesSearch = stop.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           stop.description.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Filtro por tipo
      const matchesType = filterType === 'all' || stop.type === filterType;
      
      // Filtro por acessibilidade
      const matchesAccessibility = filterAccessibility === 'all' ||
                                  (filterAccessibility === 'accessible' && stop.accessibility) ||
                                  (filterAccessibility === 'non-accessible' && !stop.accessibility);
      
      return matchesSearch && matchesType && matchesAccessibility;
    });

    // Ordenação
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'passengers':
          return b.passengers - a.passengers;
        case 'lines':
          return b.lines.length - a.lines.length;
        default:
          return 0;
      }
    });

    return filtered;
  }, [searchTerm, filterType, filterAccessibility, sortBy]);

  /**
   * Retorna o ícone baseado no tipo da parada
   * @param {string} type - Tipo da parada
   * @returns {string} Ícone correspondente
   */
  const getStopIcon = (type) => {
    switch (type) {
      case 'main': return '🚌';
      case 'secondary': return '🚏';
      default: return '📍';
    }
  };

  /**
   * Retorna a classe CSS baseada no tipo da parada
   * @param {string} type - Tipo da parada
   * @returns {string} Classe CSS correspondente
   */
  const getStopTypeClass = (type) => {
    switch (type) {
      case 'main': return 'stop-main';
      case 'secondary': return 'stop-secondary';
      default: return 'stop-default';
    }
  };

  /**
   * Formata o número de passageiros
   * @param {number} passengers - Número de passageiros
   * @returns {string} Número formatado
   */
  const formatPassengers = (passengers) => {
    if (passengers >= 1000) {
      return `${(passengers / 1000).toFixed(1)}k`;
    }
    return passengers.toString();
  };

  return (
    <div className="paradas-page">
      {/* Header da aplicação */}
      <Header showSearch={false} />
      
      {/* Conteúdo principal */}
      <div 
        className="page-content"
        style={{
          paddingTop: '90px',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, var(--color-tertiary-10) 0%, var(--color-tertiary-20) 100%)'
        }}
      >
        <div className="container">
          {/* Cabeçalho da página */}
          <div className="row mb-4">
            <div className="col-12">
                             <h1 
                 className="text-center mb-4"
                 style={{
                   color: 'var(--color-primary)',
                   fontSize: '2.5rem',
                   fontWeight: '700'
                 }}
               >
                 🚏 Paradas de Ônibus
               </h1>
              
              {/* Filtros e busca */}
              <Card 
                className="mb-4"
                style={{
                  background: 'var(--color-white)',
                  borderRadius: '16px',
                  border: 'none',
                  boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
                }}
              >
                <Card.Body className="p-4">
                  <Row className="g-3">
                    {/* Campo de busca */}
                    <Col md={6}>
                      <Form.Label 
                        style={{ 
                          color: 'var(--color-quaternary)', 
                          fontWeight: '600',
                          marginBottom: '8px'
                        }}
                      >
                        🔍 Buscar Parada
                      </Form.Label>
                      <InputGroup>
                        <Form.Control
                          type="text"
                          placeholder="Digite o nome da parada ou descrição..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          style={{
                            border: '2px solid var(--color-primary-30)',
                            borderRadius: '8px 0 0 8px'
                          }}
                        />
                        <Button 
                          variant="outline-primary"
                          onClick={() => setSearchTerm('')}
                          style={{
                            borderRadius: '0 8px 8px 0',
                            border: '2px solid var(--color-primary-30)',
                            borderLeft: 'none'
                          }}
                        >
                          ✕
                        </Button>
                      </InputGroup>
                    </Col>
                    
                    {/* Filtro por tipo */}
                    <Col md={2}>
                      <Form.Label 
                        style={{ 
                          color: 'var(--color-quaternary)', 
                          fontWeight: '600',
                          marginBottom: '8px'
                        }}
                      >
                        Tipo
                      </Form.Label>
                      <Form.Select
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value)}
                        style={{
                          border: '2px solid var(--color-primary-30)',
                          borderRadius: '8px'
                        }}
                      >
                        <option value="all">Todos</option>
                        <option value="main">Principal</option>
                        <option value="secondary">Secundária</option>
                      </Form.Select>
                    </Col>
                    
                    {/* Filtro por acessibilidade */}
                    <Col md={2}>
                      <Form.Label 
                        style={{ 
                          color: 'var(--color-quaternary)', 
                          fontWeight: '600',
                          marginBottom: '8px'
                        }}
                      >
                        Acessibilidade
                      </Form.Label>
                      <Form.Select
                        value={filterAccessibility}
                        onChange={(e) => setFilterAccessibility(e.target.value)}
                        style={{
                          border: '2px solid var(--color-primary-30)',
                          borderRadius: '8px'
                        }}
                      >
                        <option value="all">Todas</option>
                        <option value="accessible">Acessível</option>
                        <option value="non-accessible">Não Acessível</option>
                      </Form.Select>
                    </Col>
                    
                    {/* Ordenação */}
                    <Col md={2}>
                      <Form.Label 
                        style={{ 
                          color: 'var(--color-quaternary)', 
                          fontWeight: '600',
                          marginBottom: '8px'
                        }}
                      >
                        Ordenar por
                      </Form.Label>
                      <Form.Select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        style={{
                          border: '2px solid var(--color-primary-30)',
                          borderRadius: '8px'
                        }}
                      >
                        <option value="name">Nome</option>
                        <option value="passengers">Movimento</option>
                        <option value="lines">Nº de Linhas</option>
                      </Form.Select>
                    </Col>
                  </Row>
                  
                  {/* Estatísticas */}
                  <div 
                    className="mt-3 pt-3"
                    style={{ borderTop: '1px solid var(--color-primary-30)' }}
                  >
                    <small style={{ color: 'var(--color-quaternary-50)' }}>
                      Exibindo <strong>{filteredAndSortedStops.length}</strong> de <strong>{mockBusStops.length}</strong> paradas
                    </small>
                  </div>
                </Card.Body>
              </Card>
            </div>
          </div>
          
          {/* Lista de paradas */}
          <div className="row">
            {filteredAndSortedStops.length === 0 ? (
              <div className="col-12">
                <Card 
                  className="text-center py-5"
                  style={{
                    background: 'var(--color-white)',
                    borderRadius: '16px',
                    border: 'none'
                  }}
                >
                  <Card.Body>
                    <h3 style={{ color: 'var(--color-quaternary-50)' }}>
                      🔍 Nenhuma parada encontrada
                    </h3>
                    <p style={{ color: 'var(--color-quaternary-50)' }}>
                      Tente ajustar os filtros ou termo de busca.
                    </p>
                  </Card.Body>
                </Card>
              </div>
            ) : (
              filteredAndSortedStops.map((stop) => (
                <div key={stop.id} className="col-lg-6 col-xl-4 mb-4">
                  <Card 
                    className={`h-100 stop-card ${getStopTypeClass(stop.type)}`}
                    style={{
                      background: 'var(--color-white)',
                      borderRadius: '16px',
                      border: 'none',
                      boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
                      transition: 'all 0.3s ease',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)';
                      e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.15)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)';
                    }}
                  >
                    <Card.Body className="p-4">
                      {/* Cabeçalho da parada */}
                      <div className="d-flex align-items-start justify-content-between mb-3">
                        <div className="d-flex align-items-center">
                          <span 
                            className="stop-icon me-2"
                            style={{ fontSize: '1.5rem' }}
                          >
                            {getStopIcon(stop.type)}
                          </span>
                          <div>
                            <h5 
                              className="mb-1"
                              style={{
                                color: 'var(--color-quaternary)',
                                fontSize: '1.1rem',
                                fontWeight: '600',
                                lineHeight: '1.3'
                              }}
                            >
                              {stop.name}
                            </h5>
                            <Badge 
                              bg={stop.type === 'main' ? 'primary' : 'secondary'}
                              style={{
                                fontSize: '0.7rem',
                                fontWeight: '500'
                              }}
                            >
                              {stop.type === 'main' ? 'Principal' : 'Secundária'}
                            </Badge>
                          </div>
                        </div>
                        
                        {/* Indicador de acessibilidade */}
                        <div className="text-end">
                          <span 
                            title={stop.accessibility ? 'Parada acessível' : 'Parada não acessível'}
                            style={{
                              fontSize: '1.2rem',
                              opacity: stop.accessibility ? 1 : 0.3
                            }}
                          >
                            ♿
                          </span>
                        </div>
                      </div>
                      
                      {/* Descrição */}
                      <p 
                        className="mb-3"
                        style={{
                          color: 'var(--color-quaternary-50)',
                          fontSize: '0.9rem',
                          lineHeight: '1.4'
                        }}
                      >
                        {stop.description}
                      </p>
                      
                      {/* Estatísticas */}
                      <div className="row g-2 mb-3">
                        <div className="col-6">
                          <div 
                            className="text-center p-2"
                            style={{
                              background: 'var(--color-primary-10)',
                              borderRadius: '8px'
                            }}
                          >
                            <div 
                              style={{
                                color: 'var(--color-primary)',
                                fontSize: '1.2rem',
                                fontWeight: '700'
                              }}
                            >
                              {formatPassengers(stop.passengers)}
                            </div>
                            <small style={{ color: 'var(--color-quaternary-50)' }}>
                              Passageiros/dia
                            </small>
                          </div>
                        </div>
                        <div className="col-6">
                          <div 
                            className="text-center p-2"
                            style={{
                              background: 'var(--color-secondary-10)',
                              borderRadius: '8px'
                            }}
                          >
                            <div 
                              style={{
                                color: 'var(--color-secondary)',
                                fontSize: '1.2rem',
                                fontWeight: '700'
                              }}
                            >
                              {stop.lines.length}
                            </div>
                            <small style={{ color: 'var(--color-quaternary-50)' }}>
                              Linhas
                            </small>
                          </div>
                        </div>
                      </div>
                      
                      {/* Linhas de ônibus */}
                      <div>
                        <small 
                          className="d-block mb-2"
                          style={{ 
                            color: 'var(--color-quaternary)', 
                            fontWeight: '600' 
                          }}
                        >
                          Linhas que passam:
                        </small>
                        <div className="d-flex flex-wrap gap-1">
                          {stop.lines.slice(0, 4).map((line, index) => (
                            <Badge 
                              key={index}
                              bg="outline-primary"
                              style={{
                                color: 'var(--color-primary)',
                                background: 'var(--color-primary-10)',
                                border: '1px solid var(--color-primary-30)',
                                fontSize: '0.7rem'
                              }}
                            >
                              {line}
                            </Badge>
                          ))}
                          {stop.lines.length > 4 && (
                            <Badge 
                              bg="outline-secondary"
                              style={{
                                color: 'var(--color-quaternary-50)',
                                background: 'var(--color-quaternary-10)',
                                border: '1px solid var(--color-quaternary-30)',
                                fontSize: '0.7rem'
                              }}
                            >
                              +{stop.lines.length - 4}
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                      {/* Coordenadas (para desenvolvedores) */}
                      <div className="mt-3 pt-3" style={{ borderTop: '1px solid var(--color-quaternary-10)' }}>
                        <small style={{ color: 'var(--color-quaternary-30)', fontSize: '0.7rem' }}>
                          Coords: {stop.coordinates[0].toFixed(4)}, {stop.coordinates[1].toFixed(4)}
                        </small>
                      </div>
                    </Card.Body>
                  </Card>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ParadasPage; 
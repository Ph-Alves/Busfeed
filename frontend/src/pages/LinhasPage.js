/**
 * BusFeed - Página de Linhas
 * 
 * Interface para listagem e navegação das linhas de ônibus disponíveis.
 * Baseada no design fornecido com:
 * - Header com navegação e busca
 * - Lista de linhas com preços
 * - Estrelas para favoritos
 * - Design responsivo e acessível
 */

import React, { useState } from 'react';
import { Container, Card, Row, Col } from 'react-bootstrap';
import Header from '../components/common/Header';
import RouteDetails from '../components/map/RouteDetails';
import '../styles/LinhasPage.css';

/**
 * Dados mock das principais linhas de ônibus
 * Em produção, estes dados viriam de uma API
 */
const linhasDisponiveis = [
  {
    id: 1,
    numero: '0.092',
    preco: 3.80,
    favorita: true,
    destino: 'Estação Guará - Centro'
  },
  {
    id: 2,
    numero: '154.2',
    preco: 3.80,
    favorita: true,
    destino: 'Taguatinga - Plano Piloto'
  },
  {
    id: 3,
    numero: '162.1',
    preco: 3.80,
    favorita: false,
    destino: 'Ceilândia - Rodoviária'
  },
  {
    id: 4,
    numero: '86.1',
    preco: 3.80,
    favorita: false,
    destino: 'Sobradinho - Asa Norte'
  },
  {
    id: 5,
    numero: '153.2',
    preco: 3.80,
    favorita: false,
    destino: 'Samambaia - Centro'
  }
];

/**
 * Componente da página de linhas
 * @returns {JSX.Element} Interface da página de linhas
 */
function LinhasPage() {
  const [linhas, setLinhas] = useState(linhasDisponiveis);
  const [busca, setBusca] = useState('');
  const [linhaSelecionada, setLinhaSelecionada] = useState(null);

  /**
   * Manipula a busca de linhas
   * @param {string} termoBusca - Termo pesquisado
   */
  const handleBusca = (termoBusca) => {
    setBusca(termoBusca);
    console.log('Buscando linha:', termoBusca);
    // Aqui seria implementada a lógica de filtro/busca
  };

  /**
   * Alterna o status de favorita de uma linha
   * @param {number} linhaId - ID da linha
   */
  const toggleFavorita = (linhaId) => {
    setLinhas(linhas.map(linha => 
      linha.id === linhaId 
        ? { ...linha, favorita: !linha.favorita }
        : linha
    ));
  };

  /**
   * Exibe detalhes da linha selecionada
   * @param {Object} linha - Dados da linha selecionada
   */
  const handleLinhaClick = (linha) => {
    console.log('Exibindo detalhes da linha:', linha.numero);
    setLinhaSelecionada(linha.numero);
  };

  /**
   * Volta para a lista de linhas
   */
  const handleVoltarLista = () => {
    setLinhaSelecionada(null);
  };

  return (
    <div className="linhas-page">
      {/* Header com navegação e busca */}
      <Header 
        showSearch={false}
      />

      {/* Conteúdo principal */}
      <Container fluid className="linhas-content">
        <Row className="justify-content-center">
          <Col xs={12}>
            {/* Se há linha selecionada, mostra detalhes, senão mostra lista */}
            {linhaSelecionada ? (
              <RouteDetails 
                numeroLinha={linhaSelecionada}
                onClose={handleVoltarLista}
              />
            ) : (
              <Card className="linhas-card">
                <Card.Body className="p-0">
                  {/* Lista de linhas */}
                  <div className="linhas-lista">
                    {linhas.map((linha, index) => (
                      <div 
                        key={linha.id}
                        className={`linha-item ${index < linhas.length - 1 ? 'com-separador' : ''}`}
                        onClick={() => handleLinhaClick(linha)}
                        role="button"
                        tabIndex={0}
                        aria-label={`Linha ${linha.numero}, preço R$ ${linha.preco.toFixed(2)}`}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            handleLinhaClick(linha);
                          }
                        }}
                      >
                        <div className="linha-info">
                          <div className="linha-numero-container">
                            <span className="linha-numero">
                              Linha {linha.numero}
                            </span>
                            <button
                              className={`btn-estrela ${linha.favorita ? 'favorita' : ''}`}
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleFavorita(linha.id);
                              }}
                              aria-label={linha.favorita ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
                            >
                              ★
                            </button>
                          </div>
                        </div>
                        
                        <div className="linha-preco-container">
                          <span className="linha-preco">
                            R$ {linha.preco.toFixed(2).replace('.', ',')}
                          </span>
                          <div className="linha-seta">
                            ❯
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card.Body>
              </Card>
            )}
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default LinhasPage; 
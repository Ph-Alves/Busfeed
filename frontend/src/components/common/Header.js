/**
 * BusFeed - Componente Header
 * 
 * Header principal da aplicação com navegação e busca.
 * Segue as diretrizes de acessibilidade (A11y) e design responsivo.
 * 
 * Funcionalidades:
 * - Logo/título da aplicação
 * - Barra de busca de destino
 * - Navegação principal (Destino, Paradas, Linhas)
 * - Design responsivo e acessível
 */

import React, { useState } from 'react';
import { Navbar, Nav, Container, Form, FormControl } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';

/**
 * Componente Header da aplicação
 * @param {Object} props - Props do componente
 * @param {boolean} props.showSearch - Se deve exibir a barra de busca
 * @param {string} props.searchPlaceholder - Placeholder da busca
 * @param {Function} props.onSearch - Callback para busca
 * @returns {JSX.Element} Header da aplicação
 */
function Header({ 
  showSearch = true, 
  searchPlaceholder = "Pesquisar Destino...", 
  onSearch = null 
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  /**
   * Manipula a submissão da busca
   * @param {Event} e - Evento do formulário
   */
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (onSearch && searchTerm.trim()) {
      onSearch(searchTerm.trim());
    } else if (searchTerm.trim()) {
      // Navegação padrão para página de resultados (futura implementação)
      console.log('Buscando por:', searchTerm.trim());
    }
  };

  /**
   * Manipula mudanças no input de busca
   * @param {Event} e - Evento do input
   */
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  return (
    <Navbar 
      variant="dark" 
      expand="lg" 
      fixed="top"
      className="busfeed-header"
      role="banner"
      style={{ 
        backgroundColor: 'var(--color-quaternary)', // Cor quaternária para fundo escuro
        borderBottom: '2px solid var(--color-primary)', // Borda inferior com cor primária
        minHeight: '70px', // Altura mínima fixa
        padding: '0' // Remove padding extra que causa espaços em branco
      }}
    >
      <Container fluid>
        {/* Logo/Título da aplicação */}
        <Navbar.Brand 
          as={Link} 
          to="/" 
          className="fw-bold fs-3"
          aria-label="BusFeed - Página inicial"
          style={{ 
            color: 'var(--color-primary)', // Logo com cor primária para destaque
            textDecoration: 'none'
          }}
        >
          Busfeed
        </Navbar.Brand>

        {/* Barra de busca centralizada */}
        {showSearch && (
          <div className="d-flex flex-grow-1 justify-content-center mx-3">
            <Form 
              className="d-flex search-form" 
              onSubmit={handleSearchSubmit}
              role="search"
              style={{ width: '100%', maxWidth: '500px' }}
            >
              <FormControl
                type="search"
                placeholder={searchPlaceholder}
                className="search-input rounded-pill"
                aria-label="Campo de busca de destino"
                value={searchTerm}
                onChange={handleSearchChange}
                style={{
                  backgroundColor: 'var(--color-white)', // Fundo branco para melhor contraste
                  border: 'none', // Remove borda
                  fontSize: '1rem',
                  color: 'var(--color-quaternary)', // Texto escuro para contraste
                  '::placeholder': {
                    color: 'var(--color-quaternary-50)', // Placeholder mais visível
                    opacity: 1
                  }
                }}
                onFocus={(e) => {
                  e.target.style.border = 'none';
                  e.target.style.boxShadow = 'none'; // Remove borda ciano ao focar
                  e.target.style.outline = 'none'; // Remove outline padrão
                }}
                onBlur={(e) => {
                  e.target.style.border = 'none';
                  e.target.style.boxShadow = 'none';
                  e.target.style.outline = 'none';
                }}
              />
            </Form>
          </div>
        )}

        {/* Toggle para mobile */}
        <Navbar.Toggle 
          aria-controls="basic-navbar-nav"
          aria-label="Expandir menu de navegação"
          style={{ 
            borderColor: 'var(--color-primary)',
            color: 'var(--color-primary)'
          }}
        />
        
        {/* Menu de navegação */}
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto" role="navigation">
            <Nav.Link 
              as={Link} 
              to="/" 
              className="nav-link-custom"
              aria-label="Ir para página de destinos"
              style={{ 
                color: 'var(--color-tertiary)', // Cor terciária clara para contraste
                fontWeight: '500',
                padding: '8px 16px',
                borderRadius: '20px',
                margin: '0 4px',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = 'var(--color-primary-20)';
                e.target.style.color = 'var(--color-white)';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'transparent';
                e.target.style.color = 'var(--color-tertiary)';
              }}
            >
              Destino
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/mapa" 
              className="nav-link-custom"
              aria-label="Ir para página do mapa"
              style={{ 
                color: 'var(--color-tertiary)', // Cor terciária clara para contraste
                fontWeight: '500',
                padding: '8px 16px',
                borderRadius: '20px',
                margin: '0 4px',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = 'var(--color-primary-20)';
                e.target.style.color = 'var(--color-white)';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'transparent';
                e.target.style.color = 'var(--color-tertiary)';
              }}
                          >
                Mapa
              </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/paradas" 
              className="nav-link-custom"
              aria-label="Ir para página de paradas"
              style={{ 
                color: 'var(--color-tertiary)', // Cor terciária clara para contraste
                fontWeight: '500',
                padding: '8px 16px',
                borderRadius: '20px',
                margin: '0 4px',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = 'var(--color-primary-20)';
                e.target.style.color = 'var(--color-white)';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'transparent';
                e.target.style.color = 'var(--color-tertiary)';
              }}
            >
              Paradas
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/linhas" 
              className="nav-link-custom"
              aria-label="Ir para página de linhas"
              style={{ 
                color: 'var(--color-tertiary)', // Cor terciária clara para contraste
                fontWeight: '500',
                padding: '8px 16px',
                borderRadius: '20px',
                margin: '0 4px',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = 'var(--color-primary-20)';
                e.target.style.color = 'var(--color-white)';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'transparent';
                e.target.style.color = 'var(--color-tertiary)';
              }}
            >
              Linhas
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Header; 
# Componentes de Template do BusFeed

Este diretório contém componentes reutilizáveis para manter a consistência da interface.

## Componentes Disponíveis

### navbar.html
Menu de navegação principal padronizado para toda a aplicação.

**Características:**
- Menu responsivo
- Estado ativo automático
- Suporte a usuário autenticado/não autenticado
- Acessibilidade completa (ARIA labels, navegação por teclado)
- Design consistente com o protótipo UI/UX

### nav_item.html
Template para item individual de navegação (usado com template tag).

**Uso:**
```django
{% load navbar_tags %}
{% nav_item 'home' 'Início' 'bi-house' %}
{% nav_item 'routes_list' 'Rotas' 'bi-diagram-3' 'routes' %}
```

## Template Tags Relacionadas

### active_page
Retorna 'active' se a página atual corresponder ao URL fornecido.

### aria_current
Retorna 'page' para acessibilidade se a página for a atual.

### nav_item
Renderiza um item de navegação completo com estado ativo.

## Manutenção

Para adicionar novos itens ao menu:
1. Edite `templates/components/navbar.html`
2. Mantenha o padrão de estrutura HTML
3. Teste a responsividade
4. Verifique a acessibilidade 
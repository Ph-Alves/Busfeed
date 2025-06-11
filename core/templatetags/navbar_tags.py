"""
Template tags para auxiliar na navegação do BusFeed
Facilita a detecção do estado ativo dos itens do menu
"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_page(context, url_name, namespace=None):
    """
    Retorna 'active' se a página atual corresponder ao URL fornecido
    
    Uso:
    {% active_page 'home' %} 
    {% active_page 'routes_list' 'routes' %}
    """
    request = context['request']
    
    try:
        if namespace:
            # Verifica se está no namespace correto
            if hasattr(request.resolver_match, 'namespace') and namespace in str(request.resolver_match.namespace):
                return 'active'
            # Verifica se está no URL específico dentro do namespace
            if hasattr(request.resolver_match, 'url_name') and url_name in str(request.resolver_match.url_name):
                return 'active'
        else:
            # Verifica URL name direto
            if hasattr(request.resolver_match, 'url_name') and request.resolver_match.url_name == url_name:
                return 'active'
    except:
        pass
    
    return ''


@register.simple_tag(takes_context=True)
def aria_current(context, url_name, namespace=None):
    """
    Retorna 'page' para acessibilidade se a página atual corresponder ao URL fornecido
    
    Uso:
    {% aria_current 'home' %}
    {% aria_current 'routes_list' 'routes' %}
    """
    request = context['request']
    
    try:
        if namespace:
            if hasattr(request.resolver_match, 'namespace') and namespace in str(request.resolver_match.namespace):
                return 'page'
            if hasattr(request.resolver_match, 'url_name') and url_name in str(request.resolver_match.url_name):
                return 'page'
        else:
            if hasattr(request.resolver_match, 'url_name') and request.resolver_match.url_name == url_name:
                return 'page'
    except:
        pass
    
    return 'false'


@register.inclusion_tag('components/nav_item.html', takes_context=True)
def nav_item(context, url_name, label, icon_class, namespace=None):
    """
    Renderiza um item de navegação completo com estado ativo
    
    Uso:
    {% nav_item 'home' 'Início' 'bi-house' %}
    {% nav_item 'routes_list' 'Rotas' 'bi-diagram-3' 'routes' %}
    """
    return {
        'url_name': url_name,
        'label': label,
        'icon_class': icon_class,
        'namespace': namespace,
        'request': context['request'],
        'is_active': active_page(context, url_name, namespace),
        'aria_current': aria_current(context, url_name, namespace)
    } 
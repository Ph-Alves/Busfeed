"""
Context processors para o app core.
Fornece dados globais para todos os templates.
"""

from django.conf import settings


def app_settings(request):
    """
    Context processor que adiciona configurações do app aos templates.
    
    Returns:
        dict: Dicionário com configurações disponíveis nos templates
    """
    return {
        'DEBUG': settings.DEBUG,
        'BUSFEED_VERSION': '1.0.0',
        'SITE_NAME': 'BusFeed',
        'SITE_DESCRIPTION': 'Sistema de transporte público inteligente para Brasília',
        'CONTACT_EMAIL': 'contato@busfeed.df.gov.br',
        'SUPPORT_EMAIL': 'suporte@busfeed.df.gov.br',
        'GITHUB_URL': 'https://github.com/busfeed/busfeed',
        'TWITTER_URL': 'https://twitter.com/busfeed_df',
        'FACEBOOK_URL': 'https://facebook.com/busfeed.df',
        'INSTAGRAM_URL': 'https://instagram.com/busfeed_df',
    } 
"""
URLs do app core - Rotas centrais do BusFeed.

Define as URLs para as páginas básicas do sistema:
- Página inicial
- Páginas informativas 
- Endpoints de monitoramento
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Página inicial
    path('', views.HomeView.as_view(), name='home'),
    
    # Páginas informativas
    path('sobre/', views.AboutView.as_view(), name='about'),
    path('contato/', views.ContactView.as_view(), name='contact'),
    path('privacidade/', views.PrivacyView.as_view(), name='privacy'),
    path('acessibilidade/', views.AccessibilityView.as_view(), name='accessibility'),
    
    # Recursos e documentação
    path('ajuda/', views.HelpView.as_view(), name='help'),
    path('api/', views.APIView.as_view(), name='api'),
    
    # Monitoramento
    path('status/', views.StatusView.as_view(), name='status'),
    path('health/', views.health_check, name='health_check'),
] 
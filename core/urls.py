"""
URLs do app core - Rotas centrais do BusFeed.

Define as URLs para as páginas básicas do sistema:
- Página inicial
- Páginas informativas essenciais
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Página inicial
    path('', views.HomeView.as_view(), name='home'),
    
    # Páginas informativas essenciais
    path('sobre/', views.AboutView.as_view(), name='about'),
    path('contato/', views.ContactView.as_view(), name='contact'),
    path('ajuda/', views.HelpView.as_view(), name='help'),
    
    # Monitoramento básico
    path('health/', views.health_check, name='health_check'),
] 
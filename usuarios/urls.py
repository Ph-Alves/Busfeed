"""
BusFeed - URLs para Usuários

Este módulo define as rotas para autenticação e gerenciamento
de usuários no sistema.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'favoritos', views.LocalFavoritoViewSet, basename='favoritos')
router.register(r'historico', views.HistoricoBuscaViewSet, basename='historico')
router.register(r'avaliacoes', views.AvaliacaoRotaViewSet, basename='avaliacoes')

app_name = 'usuarios'

urlpatterns = [
    # Autenticação
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('verificar-username/', views.verificar_username, name='verificar-username'),
    
    # Perfil do usuário
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/atualizar/', views.atualizar_perfil, name='atualizar-perfil'),
    path('estatisticas/', views.estatisticas, name='estatisticas'),
    
    # Funcionalidades auxiliares
    path('registrar-busca/', views.registrar_busca, name='registrar-busca'),
    
    # ViewSets (favoritos, histórico, avaliações)
    path('', include(router.urls)),
] 
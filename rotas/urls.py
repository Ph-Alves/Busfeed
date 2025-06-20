"""
URLs do app de rotas
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.RotaViewSet, basename='rota')

urlpatterns = [
    path('calcular/', views.calcular_rotas, name='calcular-rotas'),
    path('salvar/', views.salvar_rota, name='salvar-rota'),
    path('salvas/', views.listar_rotas_salvas, name='listar-rotas-salvas'),
    path('', include(router.urls)),
] 
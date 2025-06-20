"""
BusFeed - URLs para Paradas

Configuração de URLs para a API de paradas de ônibus.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParadaViewSet

# Router para endpoints RESTful
router = DefaultRouter()
router.register(r'', ParadaViewSet, basename='parada')

app_name = 'paradas'

urlpatterns = [
    path('', include(router.urls)),
] 
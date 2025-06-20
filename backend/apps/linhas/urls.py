"""
BusFeed - URLs para Linhas

Configuração de URLs para a API de linhas de ônibus.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LinhaViewSet

# Router para endpoints RESTful
router = DefaultRouter()
router.register(r'', LinhaViewSet, basename='linha')

app_name = 'linhas'

urlpatterns = [
    path('', include(router.urls)),
] 
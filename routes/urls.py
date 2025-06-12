"""
URLs do app routes - Rotas de ônibus do BusFeed.

Define as URLs para funcionalidades relacionadas a rotas de ônibus:
- Listagem e busca de rotas
- Detalhes de rotas com mapas interativos
- APIs essenciais para dados de rotas
"""

from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    # Páginas principais de rotas
    path('', views.RouteListView.as_view(), name='list'),
    path('mapa/', views.RoutesMapView.as_view(), name='map'),
    path('mapa-avancado/', views.AdvancedMapView.as_view(), name='advanced_map'),
    path('<str:route_number>/', views.RouteDetailView.as_view(), name='detail'),
    
    # APIs essenciais
    path('api/search/', views.route_search_ajax, name='search_ajax'),
    path('api/map-data/', views.map_data_api, name='map_data_api'),
    path('api/<str:route_number>/stops/', views.route_stops_api, name='stops_api'),
] 
"""
URLs do app routes - Rotas de ônibus do BusFeed.

Define as URLs para funcionalidades relacionadas a rotas de ônibus:
- Listagem e busca de rotas
- Detalhes de rotas com mapas interativos
- APIs para dados de rotas e paradas
- Integração com mapas dinâmicos
"""

from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    # Páginas principais
    path('', views.RouteListView.as_view(), name='route_list'),
    path('mapa/', views.RoutesMapView.as_view(), name='routes_map'),
    path('<str:route_number>/', views.RouteDetailView.as_view(), name='route_detail'),
    
    # Redirecionamentos para compatibilidade
    path('lista/', views.routes_list, name='routes_list'),  # Redireciona para route_list
    path('paradas/', views.stops_list, name='stops_list'),  # Redireciona para stops app
    path('parada/<str:stop_code>/', views.stop_detail, name='stop_detail'),  # Redireciona para stops app
    
    # APIs para busca e mapas
    path('api/search/', views.route_search_ajax, name='route_search_ajax'),
    path('api/search/stops/', views.search_stops_api, name='search_stops_api'),
    path('api/nearby-stops/', views.nearby_stops_api, name='nearby_stops_api'),
    
    # APIs para dados de mapas
    path('api/map-data/', views.map_data_api, name='map_data_api'),
    path('api/routes/map-data/', views.all_routes_map_data, name='all_routes_map_data'),
    path('api/<str:route_number>/map-data/', views.route_map_data, name='route_map_data'),
    path('api/<str:route_number>/stops/', views.route_stops_api, name='route_stops_api'),
    path('api/stops/map-data/', views.stops_map_data, name='stops_map_data'),
    
    # APIs para estatísticas e monitoramento
    path('api/statistics/', views.routes_statistics_api, name='routes_statistics_api'),
    path('api/vehicles/', views.vehicle_locations_api, name='vehicle_locations_api'),
] 
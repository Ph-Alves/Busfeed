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
    path('', views.routes_list, name='routes_list'),
    path('mapa/', views.routes_map_view, name='routes_map'),
    path('rota/<str:route_number>/', views.RouteDetailView.as_view(), name='route_detail'),
    path('paradas/', views.stops_list, name='stops_list'),
    path('parada/<str:stop_code>/', views.stop_detail, name='stop_detail'),
    
    # APIs para mapas e busca
    path('api/search/routes/', views.route_search_ajax, name='route_search_ajax'),
    path('api/search/stops/', views.search_stops_api, name='search_stops_api'),
    path('api/nearby-stops/', views.nearby_stops_api, name='nearby_stops_api'),
    
    # APIs para dados de mapas
    path('api/routes/map-data/', views.all_routes_map_data, name='all_routes_map_data'),
    path('api/route/<str:route_number>/map-data/', views.route_map_data, name='route_map_data'),
    path('api/route/<str:route_number>/stops/', views.route_stops_api, name='route_stops_api'),
    path('api/stops/map-data/', views.stops_map_data, name='stops_map_data'),
    
    # Views de gerenciamento (para futura implementação)
    # path('criar/', views.create_route, name='create_route'),
    # path('<uuid:route_id>/editar/', views.edit_route, name='edit_route'),
    # path('<uuid:route_id>/paradas/', views.manage_route_stops, name='manage_route_stops'),
    # path('<uuid:route_id>/deletar/', views.delete_route, name='delete_route'),
] 
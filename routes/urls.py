"""
URLs do app routes - Rotas de ônibus do BusFeed.

Define as URLs para listagem, detalhes e funcionalidades das rotas.
"""
from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    # Listagem de rotas
    path('', views.RouteListView.as_view(), name='list'),
    
    # Detalhes de uma rota específica
    path('<str:route_number>/', views.RouteDetailView.as_view(), name='detail'),
    
    # AJAX endpoints
    path('ajax/search/', views.route_search_ajax, name='search_ajax'),
    path('ajax/<str:route_number>/map-data/', views.route_map_data, name='map_data'),
] 
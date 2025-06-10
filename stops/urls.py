"""
URLs do app stops - Paradas de ônibus do BusFeed.

Define as URLs para listagem, detalhes e funcionalidades das paradas.
"""
from django.urls import path
from . import views

app_name = 'stops'

urlpatterns = [
    # Listagem de paradas
    path('', views.StopListView.as_view(), name='list'),
    
    # Detalhes de uma parada específica
    path('<str:stop_code>/', views.StopDetailView.as_view(), name='detail'),
    
    # AJAX endpoints
    path('ajax/search/', views.stop_search_ajax, name='search_ajax'),
    path('ajax/<str:stop_code>/routes/', views.stop_routes_data, name='routes_data'),
    path('ajax/<str:stop_code>/map-data/', views.stop_map_data, name='map_data'),
] 
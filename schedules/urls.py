"""
URLs do app schedules - Gerenciamento de horários do BusFeed.

Define as URLs para funcionalidades relacionadas aos horários dos ônibus:
- Consulta de horários
- Programação de linhas
- Frequências
- APIs para dados de horários
"""

from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
    # Páginas principais
    path('', views.ScheduleListView.as_view(), name='list'),
    path('linha/<int:route_id>/', views.RouteScheduleView.as_view(), name='route_schedule'),
    
    # APIs para horários
    path('api/route/<str:route_number>/', views.route_schedule_api, name='route_schedule_api'),
    path('api/stop/<str:stop_code>/', views.schedules_by_stop_api, name='schedules_by_stop_api'),
] 
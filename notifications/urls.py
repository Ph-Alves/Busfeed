"""
URLs do app notifications - Sistema de avisos públicos do BusFeed.

Define as URLs para funcionalidades relacionadas aos avisos públicos:
- Lista de avisos e comunicados
- Status dos serviços de transporte
- Alertas de trânsito
"""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.PublicNoticesListView.as_view(), name='list'),
    path('status/', views.ServiceStatusView.as_view(), name='status'),
] 
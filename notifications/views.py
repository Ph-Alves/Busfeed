"""
Views do app notifications - Sistema de avisos públicos do BusFeed.

Handles para funcionalidades relacionadas aos avisos públicos de transporte.
"""

from django.shortcuts import render
from django.views.generic import TemplateView


class PublicNoticesListView(TemplateView):
    """
    View para listar avisos públicos sobre o transporte.
    """
    template_name = 'notifications/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Avisos e Comunicados'
        context['page_description'] = 'Acompanhe os avisos oficiais sobre o transporte público em Brasília'
        return context


class ServiceStatusView(TemplateView):
    """
    View para exibir status dos serviços de transporte.
    """
    template_name = 'notifications/status.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Status dos Serviços'
        context['page_description'] = 'Verifique o status atual dos serviços de transporte público'
        return context

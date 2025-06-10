"""
Views do app core - Funcionalidades centrais do BusFeed.

Implementa as views básicas do sistema seguindo os princípios de acessibilidade
e experiência do usuário centrada no cidadão brasiliense.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger('busfeed')


class HomeView(TemplateView):
    """
    Página inicial do BusFeed.
    
    Apresenta visão geral do sistema com acesso rápido às principais funcionalidades:
    - Busca de rotas
    - Paradas próximas
    - Horários em tempo real
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'BusFeed - Transporte Público Inteligente',
            'meta_description': 'Sistema inteligente de transporte público para Brasília. Encontre rotas, horários e paradas de ônibus em tempo real.',
        })
        return context


class AboutView(TemplateView):
    """
    Página sobre o BusFeed.
    
    Apresenta informações sobre o projeto, missão, visão e equipe.
    """
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Sobre o BusFeed',
            'meta_description': 'Conheça o BusFeed, sistema de transporte público inteligente desenvolvido para melhorar a mobilidade urbana em Brasília.',
        })
        return context


class ContactView(TemplateView):
    """
    Página de contato.
    
    Formulário para usuários enviarem feedback, sugestões e reportarem problemas.
    """
    template_name = 'core/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Contato - BusFeed',
            'meta_description': 'Entre em contato com a equipe do BusFeed. Envie sugestões, reporte problemas ou tire suas dúvidas.',
        })
        return context


class PrivacyView(TemplateView):
    """
    Página de política de privacidade.
    
    Informa como os dados dos usuários são coletados, armazenados e utilizados.
    """
    template_name = 'core/privacy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Política de Privacidade - BusFeed',
            'meta_description': 'Política de privacidade do BusFeed. Saiba como protegemos seus dados e respeitamos sua privacidade.',
        })
        return context


class AccessibilityView(TemplateView):
    """
    Página de acessibilidade.
    
    Informa sobre recursos de acessibilidade e conformidade com padrões WCAG.
    """
    template_name = 'core/accessibility.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Acessibilidade - BusFeed',
            'meta_description': 'Recursos de acessibilidade do BusFeed. Conheça as funcionalidades que tornam o sistema acessível para todos.',
        })
        return context


class HelpView(TemplateView):
    """
    Página de ajuda.
    
    FAQ e documentação para usuários.
    """
    template_name = 'core/help.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Ajuda - BusFeed',
            'meta_description': 'Central de ajuda do BusFeed. Encontre respostas para suas dúvidas e aprenda a usar o sistema.',
        })
        return context


class APIView(TemplateView):
    """
    Página de documentação da API.
    
    Documentação técnica para desenvolvedores.
    """
    template_name = 'core/api.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'API - BusFeed',
            'meta_description': 'Documentação da API do BusFeed. Integre dados de transporte público em suas aplicações.',
        })
        return context


class StatusView(TemplateView):
    """
    Página de status do sistema.
    
    Mostra o status dos serviços e métricas de performance.
    """
    template_name = 'core/status.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Simular dados de status do sistema
        system_status = {
            'database': {
                'status': 'online',
                'message': 'SQLite funcionando normalmente'
            },
            'cache': {
                'status': 'offline',
                'message': 'Redis não configurado'
            },
            'external_apis': {
                'status': 'offline',
                'message': 'APIs externas não configuradas'
            }
        }
        
        context.update({
            'page_title': 'Status do Sistema - BusFeed',
            'meta_description': 'Status em tempo real dos serviços do BusFeed.',
            'system_status': system_status,
        })
        return context


def health_check(request):
    """
    Endpoint de health check para monitoramento.
    
    Returns:
        JsonResponse: Status da aplicação
    """
    try:
        # Verificar conexão com banco de dados
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

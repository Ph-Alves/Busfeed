"""
Views refatoradas para gerenciamento de paradas do BusFeed.
Implementa Clean Architecture usando services para lógica de negócio.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from .models import BusStop, StopType
from .services import StopService, StopGeoService, StopStatisticsService
from routes.models import RouteStop

import json
import logging
from django.utils import timezone

logger = logging.getLogger('busfeed.stops.views')


class StopListView(ListView):
    """
    Lista todas as paradas com filtros e busca otimizada.
    """
    model = BusStop
    template_name = 'stops/stop_list.html'
    context_object_name = 'stops'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Utiliza StopService para busca otimizada.
        """
        search_term = self.request.GET.get('search', '').strip()
        filters = {
            'neighborhood': self.request.GET.get('neighborhood'),
            'wheelchair': self.request.GET.get('wheelchair'),
            'stop_type': self.request.GET.get('stop_type'),
        }
        
        # Remove filtros vazios
        filters = {k: v for k, v in filters.items() if v}
        
        logger.debug(f'Searching stops: term="{search_term}", filters={filters}')
        return StopService.search_stops(search_term, filters)
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados de filtros e estatísticas ao contexto.
        """
        context = super().get_context_data(**kwargs)
        
        context.update({
            'neighborhoods': StopService.get_neighborhoods_list(),
            'stop_types': cache.get_or_set(
                'stop_types_list',
                lambda: list(StopType.objects.filter(is_active=True)),
                3600
            ),
            'search_term': self.request.GET.get('search', ''),
            'selected_neighborhood': self.request.GET.get('neighborhood', ''),
            'wheelchair_filter': self.request.GET.get('wheelchair', ''),
            'selected_stop_type': self.request.GET.get('stop_type', ''),
            'statistics': StopStatisticsService.get_stop_statistics(),
        })
        
        logger.info(f'Stop list rendered: {len(context["stops"])} stops')
        return context


@method_decorator(cache_page(1800), name='dispatch')  # Cache por 30 minutos
class StopDetailView(DetailView):
    """
    Exibe detalhes completos de uma parada específica.
    """
    model = BusStop
    template_name = 'stops/stop_detail.html'
    context_object_name = 'stop'
    slug_field = 'code'
    slug_url_kwarg = 'stop_code'
    
    def get_object(self):
        """
        Usa StopService para obter dados com cache.
        """
        stop_code = self.kwargs['stop_code']
        stop = StopService.get_stop_detail(stop_code)
        
        if not stop:
            from django.http import Http404
            raise Http404(f"Parada {stop_code} não encontrada")
        
        return stop
    
    def get_context_data(self, **kwargs):
        """
        Adiciona informações sobre rotas que passam pela parada.
        """
        context = super().get_context_data(**kwargs)
        stop = self.object
        
        # Rotas que passam por esta parada
        route_stops = RouteStop.objects.select_related(
            'route', 'route__route_type', 'route__transport_company'
        ).filter(
            stop=stop, route__is_active=True
        ).order_by('route__number')
        
        # Paradas próximas
        if stop.latitude and stop.longitude:
            nearby_stops = StopGeoService.find_nearby_stops(
                stop.latitude, stop.longitude, 500  # 500m de raio
            )[:10]  # Máximo 10 paradas próximas
        else:
            nearby_stops = []
        
        context.update({
            'route_stops': route_stops,
            'routes_count': route_stops.count(),
            'nearby_stops': nearby_stops,
            'has_coordinates': bool(stop.latitude and stop.longitude),
        })
        
        logger.info(f'Stop detail rendered: {stop.code} - {stop.name}')
        return context


@method_decorator(cache_page(3600), name='dispatch')  # Cache por 1 hora
class StopsMapView(TemplateView):
    """
    View para mapa geral de todas as paradas.
    """
    template_name = 'stops/stops_map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Mapa de Paradas',
            'neighborhoods': StopService.get_neighborhoods_list(),
            'stop_types': StopType.objects.filter(is_active=True),
            'statistics': StopStatisticsService.get_stop_statistics(),
        })
        return context


@require_http_methods(["GET"])
def stop_search_ajax(request):
    """
    Busca de paradas via AJAX para autocomplete.
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    try:
        # Cache para buscas frequentes
        cache_key = f'stop_search_{query.lower()}_{limit}'
        results = cache.get(cache_key)
        
        if not results:
            stops = StopService.search_stops(query)[:limit]
            
            results = []
            for stop in stops:
                # Contar rotas da parada
                routes_count = RouteStop.objects.filter(
                    stop=stop, route__is_active=True
                ).values('route').distinct().count()
                
                results.append({
                    'id': str(stop.id),
                    'code': stop.code,
                    'name': stop.name,
                    'neighborhood': stop.neighborhood,
                    'type': stop.stop_type.name if stop.stop_type else 'Parada Comum',
                    'wheelchair_accessible': stop.wheelchair_accessible,
                    'has_shelter': stop.has_shelter,
                    'routes_count': routes_count,
                })
            
            cache.set(cache_key, results, 300)  # Cache por 5 minutos
        
        logger.debug(f'AJAX search completed: "{query}" -> {len(results)} results')
        return JsonResponse({'results': results})
        
    except Exception as e:
        logger.error(f'Error in stop search AJAX: {e}')
        return JsonResponse({'error': 'Search error'}, status=500)


@require_http_methods(["GET"])
@cache_page(1800)  # Cache por 30 minutos
def stops_map_data(request):
    """
    Retorna dados de paradas para exibição no mapa.
    """
    try:
        filters = {
            'neighborhood': request.GET.get('neighborhood'),
            'wheelchair': request.GET.get('wheelchair'),
            'stop_type': request.GET.get('stop_type'),
        }
        
        # Remove filtros vazios
        filters = {k: v for k, v in filters.items() if v}
        
        stops_data = StopGeoService.get_stops_map_data(filters)
        
        response_data = {
            'stops': stops_data,
            'total': len(stops_data),
            'filters_applied': filters,
            'updated_at': timezone.now().isoformat()
        }
        
        logger.info(f'Stops map data served: {len(stops_data)} stops')
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f'Error getting stops map data: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@require_http_methods(["GET"])
def nearby_stops_api(request):
    """
    API para buscar paradas próximas a uma coordenada.
    """
    try:
        lat = float(request.GET.get('lat', 0))
        lng = float(request.GET.get('lng', 0))
        radius = int(request.GET.get('radius', 1000))
        
        if not lat or not lng:
            return JsonResponse({'error': 'Coordenadas inválidas'}, status=400)
        
        nearby_stops = StopGeoService.find_nearby_stops(lat, lng, radius)
        
        response_data = {
            'stops': nearby_stops,
            'count': len(nearby_stops),
            'search_center': {'lat': lat, 'lng': lng},
            'radius_meters': radius,
            'updated_at': timezone.now().isoformat()
        }
        
        logger.debug(f'Nearby stops served: {len(nearby_stops)} stops within {radius}m')
        return JsonResponse(response_data)
        
    except (ValueError, TypeError) as e:
        logger.warning(f'Invalid parameters in nearby stops API: {e}')
        return JsonResponse({'error': 'Parâmetros inválidos'}, status=400)
    except Exception as e:
        logger.error(f'Error in nearby stops API: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@require_http_methods(["GET"])
def stops_statistics_api(request):
    """
    API para estatísticas do sistema de paradas.
    """
    try:
        statistics = StopStatisticsService.get_stop_statistics()
        
        logger.debug('Stop statistics served')
        return JsonResponse(statistics)
        
    except Exception as e:
        logger.error(f'Error getting stop statistics: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@require_http_methods(["GET"])
def accessibility_report_api(request):
    """
    API para relatório de acessibilidade das paradas.
    """
    try:
        report = StopStatisticsService.get_accessibility_report()
        
        logger.debug('Accessibility report served')
        return JsonResponse(report)
        
    except Exception as e:
        logger.error(f'Error generating accessibility report: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


# =============================================================================
# VIEWS LEGADAS (para compatibilidade) - Simplificadas
# =============================================================================

@require_http_methods(["GET"])
def stops_list(request):
    """
    View legada para lista de paradas (redirecionamento).
    """
    return redirect('stops:stop_list')


def home(request):
    """
    Página inicial do módulo de paradas.
    """
    try:
        context = {
            'statistics': StopStatisticsService.get_stop_statistics(),
            'recent_stops': StopService.get_active_stops_queryset()[:6],
            'neighborhoods': StopService.get_neighborhoods_list()[:10],
        }
        
        return render(request, 'stops/home.html', context)
        
    except Exception as e:
        logger.error(f'Error in stops home view: {e}')
        context = {'error': 'Erro ao carregar página inicial'}
        return render(request, 'stops/home.html', context)


# =============================================================================
# VIEWS DE ADMINISTRAÇÃO (placeholders)
# =============================================================================

def create_stop(request):
    """Placeholder para criação de paradas."""
    messages.info(request, 'Funcionalidade em desenvolvimento')
    return redirect('stops:stop_list')


def edit_stop(request, stop_id):
    """Placeholder para edição de paradas."""
    messages.info(request, 'Funcionalidade em desenvolvimento')
    return redirect('stops:stop_list')


def delete_stop(request, stop_id):
    """Placeholder para exclusão de paradas."""
    messages.info(request, 'Funcionalidade em desenvolvimento')
    return redirect('stops:stop_list')


# =============================================================================
# UTILITÁRIOS E VIEWS DE SUPORTE
# =============================================================================

@require_http_methods(["GET"])
def stop_routes_data(request, stop_code):
    """
    API para listar rotas que passam por uma parada específica.
    """
    try:
        stop = StopService.get_stop_detail(stop_code)
        if not stop:
            return JsonResponse({'error': 'Stop not found'}, status=404)
        
        route_stops = RouteStop.objects.select_related(
            'route', 'route__route_type', 'route__transport_company'
        ).filter(
            stop=stop, route__is_active=True
        ).order_by('route__number')
        
        routes_data = []
        for route_stop in route_stops:
            route = route_stop.route
            routes_data.append({
                'route_id': str(route.id),
                'route_number': route.number,
                'route_name': route.name,
                'direction': route_stop.direction,
                'sequence': route_stop.sequence,
                'company': route.transport_company.short_name,
                'type': route.route_type.name,
                'wheelchair_accessible': route.wheelchair_accessible,
            })
        
        response_data = {
            'stop': {
                'code': stop.code,
                'name': stop.name,
                'neighborhood': stop.neighborhood,
            },
            'routes': routes_data,
            'total_routes': len(routes_data),
        }
        
        logger.debug(f'Routes for stop {stop_code}: {len(routes_data)} routes')
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f'Error getting routes for stop {stop_code}: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@require_http_methods(["GET"])
def stop_map_data(request, stop_code):
    """
    API para dados de mapa de uma parada específica.
    """
    try:
        stop = StopService.get_stop_detail(stop_code)
        if not stop:
            return JsonResponse({'error': 'Stop not found'}, status=404)
        
        if not stop.latitude or not stop.longitude:
            return JsonResponse({'error': 'Stop coordinates not available'}, status=404)
        
        # Dados da parada para o mapa
        stop_data = {
            'id': str(stop.id),
            'code': stop.code,
            'name': stop.name,
            'neighborhood': stop.neighborhood,
            'coordinates': {
                'lat': float(stop.latitude),
                'lng': float(stop.longitude),
            },
            'wheelchair_accessible': stop.wheelchair_accessible,
            'has_shelter': stop.has_shelter,
            'has_bench': stop.has_bench,
            'address': stop.get_full_address(),
        }
        
        # Paradas próximas
        nearby_stops = StopGeoService.find_nearby_stops(
            float(stop.latitude), 
            float(stop.longitude), 
            500  # 500 metros
        )[:5]  # Máximo 5 paradas próximas
        
        nearby_data = []
        for nearby_stop in nearby_stops:
            if nearby_stop.id != stop.id:  # Excluir a própria parada
                nearby_data.append({
                    'id': str(nearby_stop.id),
                    'code': nearby_stop.code,
                    'name': nearby_stop.name,
                    'distance': getattr(nearby_stop, 'distance', None),
                })
        
        response_data = {
            'stop': stop_data,
            'nearby_stops': nearby_data,
            'metadata': {
                'nearby_count': len(nearby_data),
                'search_radius': 500,
            }
        }
        
        logger.debug(f'Map data for stop {stop_code}: {len(nearby_data)} nearby stops')
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f'Error getting map data for stop {stop_code}: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)

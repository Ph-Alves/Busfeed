"""
Views refatoradas para gerenciamento de rotas do BusFeed.
Implementa Clean Architecture usando services para lógica de negócio.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from .models import BusRoute, RouteType, TransportCompany, Vehicle, RouteStop
from .services import (
    RouteService, 
    RouteMapService, 
    VehicleTrackingService, 
    RouteStatisticsService
)
from stops.models import BusStop

import json
import logging
from django.utils import timezone

logger = logging.getLogger('busfeed.routes.views')


class RouteListView(ListView):
    """
    Lista todas as rotas de ônibus com filtros e busca otimizada.
    Usa RouteService para lógica de negócio e cache inteligente.
    """
    model = BusRoute
    template_name = 'routes/route_list.html'
    context_object_name = 'routes'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Utiliza RouteService para busca otimizada com cache.
        """
        search_term = self.request.GET.get('search', '').strip()
        filters = {
            'route_type': self.request.GET.get('type'),
            'company': self.request.GET.get('company'),
            'wheelchair': self.request.GET.get('wheelchair'),
        }
        
        # Remove filtros vazios
        filters = {k: v for k, v in filters.items() if v}
        
        logger.debug(f'Searching routes: term="{search_term}", filters={filters}')
        return RouteService.search_routes(search_term, filters)
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados de filtros e estatísticas ao contexto.
        """
        context = super().get_context_data(**kwargs)
        
        # Dados para filtros (com cache)
        context.update({
            'route_types': cache.get_or_set(
                'route_types_list', 
                lambda: list(RouteType.objects.filter(is_active=True)), 
                3600
            ),
            'companies': cache.get_or_set(
                'companies_list',
                lambda: list(TransportCompany.objects.filter(is_active=True)),
                3600
            ),
            'search_term': self.request.GET.get('search', ''),
            'selected_type': self.request.GET.get('type', ''),
            'selected_company': self.request.GET.get('company', ''),
            'wheelchair_filter': self.request.GET.get('wheelchair', ''),
            'statistics': RouteStatisticsService.get_route_statistics(),
        })
        
        logger.info(f'Route list rendered: {len(context["routes"])} routes')
        return context


@method_decorator(cache_page(1800), name='dispatch')  # Cache por 30 minutos
class RouteDetailView(DetailView):
    """
    Exibe detalhes completos de uma rota específica com otimizações.
    """
    model = BusRoute
    template_name = 'routes/route_detail.html'
    context_object_name = 'route'
    slug_field = 'number'
    slug_url_kwarg = 'route_number'
    
    def get_object(self):
        """
        Usa RouteService para obter dados com cache.
        """
        route_number = self.kwargs['route_number']
        route = RouteService.get_route_detail(route_number)
        
        if not route:
            from django.http import Http404
            raise Http404(f"Rota {route_number} não encontrada")
        
        return route
    
    def get_context_data(self, **kwargs):
        """
        Adiciona informações organizadas sobre a rota.
        """
        context = super().get_context_data(**kwargs)
        route = self.object
        
        # Organizar paradas por direção usando service
        stops_data = RouteService.get_route_stops_data(route)
        
        # Dados de veículos em tempo real
        vehicle_locations = VehicleTrackingService.get_vehicle_locations(route.number)
        
        context.update({
            'ida_stops': stops_data['ida'],
            'volta_stops': stops_data['volta'],
            'circular_stops': stops_data['circular'],
            'total_stops': sum(len(stops) for stops in stops_data.values()),
            'is_operational': route.is_operational_today(),
            'current_fare': route.get_current_fare(),
            'vehicle_locations': vehicle_locations,
            'vehicles_count': len(vehicle_locations),
        })
        
        logger.info(f'Route detail rendered: {route.number} - {route.name}')
        return context


@require_http_methods(["GET"])
def route_search_ajax(request):
    """
    Busca de rotas via AJAX para autocomplete otimizada.
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    try:
        # Usar cache para buscas frequentes
        cache_key = f'route_search_{query.lower()}'
        results = cache.get(cache_key)
        
        if not results:
            routes = RouteService.search_routes(query)[:10]
            
            results = []
            for route in routes:
                results.append({
                    'id': str(route.id),
                    'number': route.number,
                    'name': route.name,
                    'full_name': route.get_full_name(),
                    'type': route.route_type.name,
                    'company': route.transport_company.short_name,
                    'fare': str(route.get_current_fare()) if route.get_current_fare() else 'N/A',
                    'wheelchair': route.wheelchair_accessible,
                })
            
            cache.set(cache_key, results, 300)  # Cache por 5 minutos
            
        logger.debug(f'AJAX search completed: "{query}" -> {len(results)} results')
        return JsonResponse({'results': results})
        
    except Exception as e:
        logger.error(f'Error in route search AJAX: {e}')
        return JsonResponse({'error': 'Search error'}, status=500)


@require_http_methods(["GET"])
def route_map_data(request, route_number):
    """
    Retorna dados da rota para exibição no mapa usando MapService.
    """
    try:
        map_data = RouteMapService.get_route_map_data(route_number)
        
        if not map_data:
            return JsonResponse({
                'error': f'Rota {route_number} não encontrada'
            }, status=404)
        
        logger.debug(f'Map data served for route {route_number}')
        return JsonResponse(map_data)
        
    except Exception as e:
        logger.error(f'Error getting map data for route {route_number}: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@require_http_methods(["GET"])
@cache_page(1800)  # Cache por 30 minutos
def all_routes_map_data(request):
    """
    Retorna dados de todas as rotas para mapa geral.
    """
    try:
        routes_data = RouteMapService.get_all_routes_map_data()
        
        response_data = {
            'routes': routes_data,
            'total': len(routes_data),
            'updated_at': timezone.now().isoformat()
        }
        
        logger.info(f'All routes map data served: {len(routes_data)} routes')
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f'Error getting all routes map data: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@require_http_methods(["GET"])
def vehicle_locations_api(request):
    """
    API para localizações em tempo real dos veículos.
    """
    route_number = request.GET.get('route')
    
    try:
        locations = VehicleTrackingService.get_vehicle_locations(route_number)
        
        response_data = {
            'vehicles': locations,
            'count': len(locations),
            'route_filter': route_number,
            'updated_at': timezone.now().isoformat()
        }
        
        logger.debug(f'Vehicle locations served: {len(locations)} vehicles')
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f'Error getting vehicle locations: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@method_decorator(cache_page(3600), name='dispatch')  # Cache por 1 hora
class RoutesMapView(TemplateView):
    """
    View para mapa geral de todas as rotas.
    """
    template_name = 'routes/routes_map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Mapa de Rotas',
            'statistics': RouteStatisticsService.get_route_statistics(),
        })
        return context


@require_http_methods(["GET"])
def routes_statistics_api(request):
    """
    API para estatísticas do sistema de rotas.
    """
    try:
        statistics = RouteStatisticsService.get_route_statistics()
        
        logger.debug('Route statistics served')
        return JsonResponse(statistics)
        
    except Exception as e:
        logger.error(f'Error getting route statistics: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


# =============================================================================
# VIEWS LEGADAS (para compatibilidade) - Simplificadas
# =============================================================================

@require_http_methods(["GET"])
def routes_list(request):
    """
    View legada para lista de rotas (redirecionamento).
    """
    return redirect('routes:route_list')


# View removida - usar RoutesMapView diretamente nas URLs


@require_http_methods(["GET"])
def stops_list(request):
    """
    View legada para lista de paradas (redirecionamento para stops app).
    """
    from django.urls import reverse
    return redirect(reverse('stops:list'))


@require_http_methods(["GET"])
def search_stops_api(request):
    """
    API legada para busca de paradas (redirecionamento para stops app).
    """
    try:
        from stops.services import StopService
        
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        stops = StopService.search_stops(query)[:10]
        
        results = []
        for stop in stops:
            results.append({
                'id': str(stop.id),
                'code': stop.code,
                'name': stop.name,
                'neighborhood': stop.neighborhood,
                'full_address': stop.get_full_address(),
                'wheelchair_accessible': stop.wheelchair_accessible,
            })
        
        return JsonResponse({'results': results})
        
    except Exception as e:
        logger.error(f'Error in search_stops_api: {e}')
        return JsonResponse({'error': 'Search error'}, status=500)


@require_http_methods(["GET"])
def nearby_stops_api(request):
    """
    API para buscar paradas próximas usando coordenadas.
    """
    try:
        from stops.services import StopGeoService
        
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius = request.GET.get('radius', 1000)  # metros
        
        if not lat or not lng:
            return JsonResponse({'error': 'Coordinates required'}, status=400)
        
        try:
            lat = float(lat)
            lng = float(lng)
            radius = int(radius)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid coordinates'}, status=400)
        
        stops = StopGeoService.find_nearby_stops(lat, lng, radius)
        
        results = []
        for stop in stops:
            results.append({
                'id': str(stop.id),
                'code': stop.code,
                'name': stop.name,
                'neighborhood': stop.neighborhood,
                'distance': getattr(stop, 'distance', None),
                'coordinates': {
                    'lat': float(stop.latitude) if stop.latitude else None,
                    'lng': float(stop.longitude) if stop.longitude else None,
                }
            })
        
        return JsonResponse({
            'stops': results,
            'total': len(results),
            'center': {'lat': lat, 'lng': lng},
            'radius': radius
        })
        
    except Exception as e:
        logger.error(f'Error in nearby_stops_api: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@require_http_methods(["GET"])
def map_data_api(request):
    """
    API geral para dados de mapa (rotas e paradas).
    """
    try:
        routes_data = RouteMapService.get_all_routes_map_data()
        
        # Dados simplificados de paradas
        from stops.services import StopService
        stops_data = StopService.get_map_data()
        
        response_data = {
            'routes': routes_data,
            'stops': stops_data,
            'metadata': {
                'routes_count': len(routes_data),
                'stops_count': len(stops_data),
                'updated_at': timezone.now().isoformat()
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f'Error in map_data_api: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@require_http_methods(["GET"])
def route_stops_api(request, route_number):
    """
    API para obter paradas de uma rota específica.
    """
    try:
        route = RouteService.get_route_detail(route_number)
        if not route:
            return JsonResponse({'error': 'Route not found'}, status=404)
        
        stops_data = RouteService.get_route_stops_data(route)
        
        response_data = {
            'route': {
                'number': route.number,
                'name': route.name,
                'company': route.transport_company.short_name,
            },
            'stops': stops_data,
            'metadata': {
                'total_stops': sum(len(stops) for stops in stops_data.values()),
                'has_return': bool(stops_data.get('volta')),
                'is_circular': route.is_circular,
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f'Error in route_stops_api for route {route_number}: {e}')
        return JsonResponse({'error': 'Server error'}, status=500)


@require_http_methods(["GET"])
def stop_detail(request, stop_code):
    """
    Detalhes de uma parada específica (simplificada).
    """
    try:
        stop = get_object_or_404(BusStop, code=stop_code, is_active=True)
        
        # Rotas que passam por esta parada
        route_stops = RouteStop.objects.select_related(
            'route', 'route__route_type', 'route__transport_company'
        ).filter(
            stop=stop, route__is_active=True
        ).order_by('route__number')
        
        context = {
            'stop': stop,
            'route_stops': route_stops,
            'routes_count': route_stops.count(),
        }
        
        return render(request, 'stops/stop_detail.html', context)
        
    except Exception as e:
        logger.error(f'Error in stop detail view: {e}')
        messages.error(request, 'Erro ao carregar detalhes da parada')
        return redirect('routes:route_list')


@require_http_methods(["GET"])
def home(request):
    """
    Página inicial do sistema (simplificada).
    """
    try:
        context = {
            'statistics': RouteStatisticsService.get_route_statistics(),
            'featured_routes': RouteService.get_active_routes_queryset()[:6],
        }
        
        return render(request, 'routes/home.html', context)
        
    except Exception as e:
        logger.error(f'Error in home view: {e}')
        context = {'error': 'Erro ao carregar página inicial'}
        return render(request, 'routes/home.html', context)


# =============================================================================
# VIEWS DE ADMINISTRAÇÃO (simplificadas para futuro desenvolvimento)
# =============================================================================

def create_route(request):
    """Placeholder para criação de rotas."""
    messages.info(request, 'Funcionalidade em desenvolvimento')
    return redirect('routes:route_list')


def edit_route(request, route_id):
    """Placeholder para edição de rotas."""
    messages.info(request, 'Funcionalidade em desenvolvimento')
    return redirect('routes:route_list')


def delete_route(request, route_id):
    """Placeholder para exclusão de rotas."""
    messages.info(request, 'Funcionalidade em desenvolvimento')
    return redirect('routes:route_list')


def manage_route_stops(request, route_id):
    """Placeholder para gerenciamento de paradas da rota."""
    messages.info(request, 'Funcionalidade em desenvolvimento')
    return redirect('routes:route_list')


# =============================================================================
# APIs DE COMPATIBILIDADE (simplificadas)
# =============================================================================

@require_http_methods(["GET"])
def stops_map_data(request):
    """Dados de paradas para mapa (compatibilidade)."""
    return JsonResponse({'stops': [], 'message': 'Use stops app API'})

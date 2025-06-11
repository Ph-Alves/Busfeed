"""
Views para gerenciamento de rotas do BusFeed.
Implementa as páginas de listagem, detalhes e busca de rotas com mapas interativos.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from .models import BusRoute, RouteType, TransportCompany, Vehicle, RouteStop
from django.views.decorators.http import require_http_methods
from stops.models import BusStop
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from django.utils import timezone
from django.db import models

logger = logging.getLogger('busfeed')


class RouteListView(ListView):
    """
    Lista todas as rotas de ônibus com filtros e busca.
    """
    model = BusRoute
    template_name = 'routes/route_list.html'
    context_object_name = 'routes'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Retorna queryset filtrado e otimizado.
        """
        queryset = BusRoute.objects.select_related(
            'route_type', 'transport_company'
        ).prefetch_related(
            'route_stops__stop'
        ).filter(is_active=True)
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(name__icontains=search) |
                Q(origin_terminal__icontains=search) |
                Q(destination_terminal__icontains=search)
            )
        
        # Filtro por tipo
        route_type = self.request.GET.get('type')
        if route_type:
            queryset = queryset.filter(route_type_id=route_type)
        
        # Filtro por empresa
        company = self.request.GET.get('company')
        if company:
            queryset = queryset.filter(transport_company_id=company)
        
        # Filtro por acessibilidade
        wheelchair = self.request.GET.get('wheelchair')
        if wheelchair == 'true':
            queryset = queryset.filter(wheelchair_accessible=True)
        
        return queryset.order_by('number', 'name')
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados extras ao contexto.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'route_types': RouteType.objects.all(),
            'companies': TransportCompany.objects.all(),
            'search_term': self.request.GET.get('search', ''),
            'selected_type': self.request.GET.get('type', ''),
            'selected_company': self.request.GET.get('company', ''),
            'wheelchair_filter': self.request.GET.get('wheelchair', ''),
        })
        return context


class RouteDetailView(DetailView):
    """
    Exibe detalhes completos de uma rota específica com mapa interativo.
    """
    model = BusRoute
    template_name = 'routes/route_detail.html'
    context_object_name = 'route'
    slug_field = 'number'
    slug_url_kwarg = 'route_number'
    
    def get_queryset(self):
        """
        Otimiza consulta com dados relacionados.
        """
        return BusRoute.objects.select_related(
            'route_type', 'transport_company'
        ).prefetch_related(
            Prefetch(
                'route_stops',
                queryset=RouteStop.objects.select_related('stop').order_by('direction', 'sequence'),
                to_attr='ordered_stops'
            )
        )
    
    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras sobre a rota.
        """
        context = super().get_context_data(**kwargs)
        route = self.object
        
        # Paradas organizadas por direção
        ida_stops = route.route_stops.filter(direction='ida').order_by('sequence')
        volta_stops = route.route_stops.filter(direction='volta').order_by('sequence')
        circular_stops = route.route_stops.filter(direction='circular').order_by('sequence')
        
        context.update({
            'ida_stops': ida_stops,
            'volta_stops': volta_stops,
            'circular_stops': circular_stops,
            'total_stops': ida_stops.count() + volta_stops.count() + circular_stops.count(),
            'is_operational': route.is_operational_today(),
            'current_fare': route.get_current_fare(),
        })
        return context


def route_search_ajax(request):
    """
    Busca de rotas via AJAX para autocomplete.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '')
        if len(query) >= 2:
            routes = BusRoute.objects.filter(
                Q(number__icontains=query) |
                Q(name__icontains=query) |
                Q(origin_terminal__icontains=query) |
                Q(destination_terminal__icontains=query),
                is_active=True
            ).select_related('route_type', 'transport_company')[:10]
            
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
            
            return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})


@require_http_methods(["GET"])
def route_map_data(request, route_number):
    """
    Retorna dados da rota para exibição no mapa.
    """
    try:
        route = get_object_or_404(BusRoute, number=route_number, is_active=True)
        
        # Dados das paradas organizados por direção
        stops_data = {
            'ida': [],
            'volta': [],
            'circular': []
        }
        
        for route_stop in route.route_stops.select_related('stop').all():
            stop = route_stop.stop
            stop_data = {
                'id': str(stop.id),
                'code': stop.code,
                'name': stop.name,
                'sequence': route_stop.sequence,
                'lat': float(stop.latitude) if stop.latitude else None,
                'lng': float(stop.longitude) if stop.longitude else None,
                'wheelchair_accessible': stop.wheelchair_accessible,
                'has_shelter': stop.has_shelter,
                'has_seating': stop.has_seating,
                'neighborhood': stop.neighborhood,
                'distance_from_origin': route_stop.distance_from_origin,
                'estimated_time_from_origin': route_stop.estimated_time_from_origin
            }
            
            if stop_data['lat'] and stop_data['lng']:
                stops_data[route_stop.direction].append(stop_data)
        
        # Dados da rota
        route_data = {
            'id': str(route.id),
            'number': route.number,
            'name': route.name,
            'type': route.route_type.name,
            'company': route.transport_company.short_name,
            'fare': float(route.get_current_fare()) if route.get_current_fare() else None,
            'wheelchair_accessible': route.wheelchair_accessible,
            'is_circular': route.is_circular,
            'color': route.route_type.color,
            'stops': stops_data
        }
        
        return JsonResponse({
            'status': 'success',
            'route': route_data
        })
        
    except Exception as e:
        logger.error(f'Erro ao buscar dados da rota {route_number}: {e}')
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao carregar dados da rota: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def all_routes_map_data(request):
    """
    Retorna dados de todas as rotas para exibição no mapa.
    """
    try:
        # Filtros opcionais
        route_type_filter = request.GET.get('type')
        company_filter = request.GET.get('company')
        wheelchair_filter = request.GET.get('wheelchair') == 'true'
        
        # Query otimizada para buscar rotas com dados relacionados
        routes_query = BusRoute.objects.select_related(
            'route_type', 'transport_company'
        ).prefetch_related(
            Prefetch(
                'route_stops',
                queryset=RouteStop.objects.select_related('stop').order_by('direction', 'sequence')
            )
        ).filter(is_active=True)
        
        # Aplicar filtros se fornecidos
        if route_type_filter:
            routes_query = routes_query.filter(route_type_id=route_type_filter)
        
        if company_filter:
            routes_query = routes_query.filter(transport_company_id=company_filter)
        
        if wheelchair_filter:
            routes_query = routes_query.filter(wheelchair_accessible=True)
        
        routes_data = []
        
        for route in routes_query:
            # Organiza paradas por direção
            stops_by_direction = {
                'ida': [],
                'volta': [],
                'circular': []
            }
            
            for route_stop in route.route_stops.all():
                stop = route_stop.stop
                if stop.latitude and stop.longitude:  # Só inclui paradas com coordenadas
                    stop_data = {
                        'id': str(stop.id),
                        'code': stop.code,
                        'name': stop.name,
                        'sequence': route_stop.sequence,
                        'direction': route_stop.direction,
                        'lat': float(stop.latitude),
                        'lng': float(stop.longitude),
                        'wheelchair_accessible': stop.wheelchair_accessible,
                        'has_shelter': stop.has_shelter,
                        'has_seating': stop.has_seating,
                        'neighborhood': stop.neighborhood,
                        'distance_from_origin': route_stop.distance_from_origin,
                        'estimated_time_from_origin': route_stop.estimated_time_from_origin
                    }
                    stops_by_direction[route_stop.direction].append(stop_data)
            
            # Só inclui rotas que têm pelo menos uma parada com coordenadas
            total_stops = sum(len(stops) for stops in stops_by_direction.values())
            if total_stops > 0:
                # Combina todas as paradas para compatibilidade com o frontend
                all_stops = []
                for direction, stops in stops_by_direction.items():
                    all_stops.extend(stops)
                
                route_data = {
                    'id': str(route.id),
                    'number': route.number,
                    'name': route.name,
                    'full_name': route.get_full_name(),
                    'type': route.route_type.name,
                    'company': route.transport_company.short_name,
                    'color': route.route_type.color,
                    'wheelchair_accessible': route.wheelchair_accessible,
                    'fare': float(route.base_fare) if route.base_fare else None,
                    'stops': all_stops,  # Para compatibilidade com o frontend atual
                    'stops_by_direction': stops_by_direction,  # Dados organizados por direção
                    'is_circular': route.is_circular,
                    'operates_weekdays': route.operates_weekdays,
                    'operates_saturdays': route.operates_saturdays,
                    'operates_sundays': route.operates_sundays,
                }
                routes_data.append(route_data)
        
        return JsonResponse({
            'status': 'success',
            'routes': routes_data,
            'total': len(routes_data)
        })
        
    except Exception as e:
        logger.error(f'Erro ao buscar dados de todas as rotas: {e}')
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao carregar dados das rotas: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def routes_list(request):
    """
    Lista de rotas com mapa interativo.
    """
    # Filtros
    search = request.GET.get('search', '')
    route_type_id = request.GET.get('type', '')
    company_id = request.GET.get('company', '')
    wheelchair_only = request.GET.get('wheelchair') == 'true'
    
    # Query base
    routes = BusRoute.objects.select_related(
        'route_type', 'transport_company'
    ).filter(is_active=True)
    
    # Aplicar filtros
    if search:
        routes = routes.filter(
            Q(number__icontains=search) |
            Q(name__icontains=search) |
            Q(origin_terminal__icontains=search) |
            Q(destination_terminal__icontains=search)
        )
    
    if route_type_id:
        routes = routes.filter(route_type_id=route_type_id)
    
    if company_id:
        routes = routes.filter(transport_company_id=company_id)
    
    if wheelchair_only:
        routes = routes.filter(wheelchair_accessible=True)
    
    # Paginação
    paginator = Paginator(routes.order_by('number'), 20)
    page_number = request.GET.get('page')
    page_routes = paginator.get_page(page_number)
    
    context = {
        'routes': page_routes,
        'route_types': RouteType.objects.all(),
        'companies': TransportCompany.objects.all(),
        'search_term': search,
        'selected_type': route_type_id,
        'selected_company': company_id,
        'wheelchair_filter': wheelchair_only,
        'total_routes': routes.count()
    }
    
    return render(request, 'routes/routes_list.html', context)


@require_http_methods(["GET"])
def routes_map_view(request):
    """
    Página dedicada ao mapa com todas as rotas.
    """
    context = {
        'route_types': RouteType.objects.all(),
        'companies': TransportCompany.objects.all(),
        'total_routes': BusRoute.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'routes/routes_map.html', context)


@require_http_methods(["GET"])
def stops_list(request):
    """
    Lista de paradas com mapa interativo.
    """
    # Filtros
    search = request.GET.get('search', '')
    neighborhood = request.GET.get('neighborhood', '')
    wheelchair_only = request.GET.get('wheelchair') == 'true'
    
    # Query base
    stops = BusStop.objects.select_related('stop_type').filter(is_active=True)
    
    # Aplicar filtros
    if search:
        stops = stops.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(neighborhood__icontains=search) |
            Q(reference_point__icontains=search)
        )
    
    if neighborhood:
        stops = stops.filter(neighborhood__icontains=neighborhood)
    
    if wheelchair_only:
        stops = stops.filter(wheelchair_accessible=True)
    
    # Paginação
    paginator = Paginator(stops.order_by('name'), 20)
    page_number = request.GET.get('page')
    page_stops = paginator.get_page(page_number)
    
    # Bairros para filtro
    neighborhoods = BusStop.objects.filter(
        is_active=True, 
        neighborhood__isnull=False
    ).values_list('neighborhood', flat=True).distinct().order_by('neighborhood')
    
    context = {
        'stops': page_stops,
        'neighborhoods': neighborhoods,
        'search_term': search,
        'selected_neighborhood': neighborhood,
        'wheelchair_filter': wheelchair_only,
        'total_stops': stops.count()
    }
    
    return render(request, 'stops/stops_list.html', context)


@require_http_methods(["GET"])
def stop_detail(request, stop_code):
    """
    Detalhes de uma parada específica.
    """
    stop = get_object_or_404(BusStop, code=stop_code, is_active=True)
    
    # Rotas que passam por esta parada
    route_stops = RouteStop.objects.filter(
        stop=stop
    ).select_related('route', 'route__route_type', 'route__transport_company').order_by('route__number')
    
    context = {
        'stop': stop,
        'route_stops': route_stops,
        'total_routes': route_stops.count()
    }
    
    return render(request, 'stops/stop_detail.html', context)


@require_http_methods(["GET"])
def stops_map_data(request):
    """
    Retorna dados de todas as paradas para o mapa.
    """
    try:
        # Filtros
        neighborhood = request.GET.get('neighborhood', '')
        wheelchair_only = request.GET.get('wheelchair') == 'true'
        
        stops = BusStop.objects.filter(
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False
        ).select_related('stop_type')
        
        if neighborhood:
            stops = stops.filter(neighborhood__icontains=neighborhood)
        
        if wheelchair_only:
            stops = stops.filter(wheelchair_accessible=True)
        
        stops_data = []
        for stop in stops[:200]:  # Limitar para performance
            stops_data.append({
                'id': str(stop.id),
                'code': stop.code,
                'name': stop.name,
                'lat': float(stop.latitude),
                'lng': float(stop.longitude),
                'type': stop.stop_type.name,
                'type_icon': stop.stop_type.icon,
                'type_color': stop.stop_type.color,
                'wheelchair_accessible': stop.wheelchair_accessible,
                'has_shelter': stop.has_shelter,
                'has_seating': stop.has_seating,
                'neighborhood': stop.neighborhood,
                'routes_count': stop.route_stops.count()
            })
        
        return JsonResponse({
            'status': 'success',
            'stops': stops_data,
            'total': len(stops_data)
        })
        
    except Exception as e:
        logger.error(f'Erro ao buscar dados das paradas: {e}')
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao carregar dados das paradas: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def search_stops_api(request):
    """
    API para busca de paradas.
    """
    query = request.GET.get('q', '')
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    stops = BusStop.objects.filter(
        Q(name__icontains=query) |
        Q(code__icontains=query) |
        Q(neighborhood__icontains=query),
        is_active=True
    ).select_related('stop_type')[:limit]
    
    results = []
    for stop in stops:
        results.append({
            'id': str(stop.id),
            'code': stop.code,
            'name': stop.name,
            'neighborhood': stop.neighborhood,
            'type': stop.stop_type.name,
            'wheelchair_accessible': stop.wheelchair_accessible,
            'routes_count': stop.route_stops.count()
        })
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def nearby_stops_api(request):
    """
    API para buscar paradas próximas a uma coordenada.
    """
    try:
        lat = float(request.GET.get('lat', 0))
        lng = float(request.GET.get('lng', 0))
        radius = min(float(request.GET.get('radius', 1000)), 5000)  # Max 5km
        
        if not lat or not lng:
            return JsonResponse({'error': 'Coordenadas inválidas'}, status=400)
        
        # Busca simples por bounding box (sem PostGIS)
        lat_delta = radius / 111000  # Aproximadamente 1 grau = 111km
        lng_delta = radius / (111000 * abs(lat))
        
        stops = BusStop.objects.filter(
            latitude__gte=lat - lat_delta,
            latitude__lte=lat + lat_delta,
            longitude__gte=lng - lng_delta,
            longitude__lte=lng + lng_delta,
            is_active=True
        ).select_related('stop_type')[:20]
        
        results = []
        for stop in stops:
            # Calcular distância aproximada
            lat_diff = abs(stop.latitude - lat)
            lng_diff = abs(stop.longitude - lng)
            distance = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111000
            
            if distance <= radius:
                results.append({
                    'id': str(stop.id),
                    'code': stop.code,
                    'name': stop.name,
                    'lat': stop.latitude,
                    'lng': stop.longitude,
                    'distance': round(distance),
                    'type': stop.stop_type.name,
                    'wheelchair_accessible': stop.wheelchair_accessible,
                    'routes_count': stop.route_stops.count()
                })
        
        # Ordenar por distância
        results.sort(key=lambda x: x['distance'])
        
        return JsonResponse({'results': results})
        
    except (ValueError, TypeError) as e:
        return JsonResponse({'error': 'Parâmetros inválidos'}, status=400)
    except Exception as e:
        logger.error(f'Erro na busca de paradas próximas: {e}')
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@require_http_methods(["GET"])
def route_stops_api(request, route_number):
    """
    API para obter paradas de uma rota específica.
    """
    try:
        route = get_object_or_404(BusRoute, number=route_number, is_active=True)
        
        route_stops = RouteStop.objects.filter(
            route=route
        ).select_related('stop').order_by('direction', 'sequence')
        
        stops_by_direction = {
            'ida': [],
            'volta': [],
            'circular': []
        }
        
        for route_stop in route_stops:
            stop = route_stop.stop
            stop_data = {
                'id': str(stop.id),
                'code': stop.code,
                'name': stop.name,
                'sequence': route_stop.sequence,
                'lat': stop.latitude,
                'lng': stop.longitude,
                'wheelchair_accessible': stop.wheelchair_accessible,
                'distance_from_origin': route_stop.distance_from_origin,
                'estimated_time_from_origin': route_stop.estimated_time_from_origin
            }
            
            stops_by_direction[route_stop.direction].append(stop_data)
        
        return JsonResponse({
            'route_number': route.number,
            'route_name': route.name,
            'stops': stops_by_direction
        })
        
    except Exception as e:
        logger.error(f'Erro ao buscar paradas da rota {route_number}: {e}')
        return JsonResponse({'error': 'Erro ao carregar paradas da rota'}, status=500)


def home(request):
    """
    Página inicial com busca e mapas interativos.
    """
    context = {
        'total_routes': BusRoute.objects.filter(is_active=True).count(),
        'total_stops': BusStop.objects.filter(is_active=True).count(),
        'route_types': RouteType.objects.all(),
        'companies': TransportCompany.objects.all()
    }
    
    # Se há uma busca por destino, mostrar resultados
    destination = request.GET.get('destino', '')
    if destination:
        routes = BusRoute.objects.filter(
            Q(name__icontains=destination) |
            Q(destination_terminal__icontains=destination) |
            Q(origin_terminal__icontains=destination),
            is_active=True
        ).select_related('route_type', 'transport_company')[:10]
        
        context['search_results'] = routes
        context['search_term'] = destination
    
    return render(request, 'core/home.html', context)


# Views adicionais para gerenciamento de rotas
def create_route(request):
    """Criar nova rota (placeholder)."""
    messages.info(request, 'Funcionalidade de criação de rotas em desenvolvimento.')
    return redirect('routes:routes_list')


def edit_route(request, route_id):
    """Editar rota existente (placeholder)."""
    route = get_object_or_404(BusRoute, pk=route_id)
    messages.info(request, f'Funcionalidade de edição da rota {route.number} em desenvolvimento.')
    return redirect('routes:route_detail', route_id=route_id)


def manage_route_stops(request, route_id):
    """Gerenciar paradas da rota (placeholder)."""
    route = get_object_or_404(BusRoute, pk=route_id)
    messages.info(request, f'Funcionalidade de gerenciamento de paradas da rota {route.number} em desenvolvimento.')
    return redirect('routes:route_detail', route_id=route_id)


def delete_route(request, route_id):
    """Deletar rota (placeholder)."""
    route = get_object_or_404(BusRoute, pk=route_id)
    if request.method == 'POST':
        messages.warning(request, f'Funcionalidade de exclusão da rota {route.number} em desenvolvimento.')
        return redirect('routes:routes_list')
    return redirect('routes:route_detail', route_id=route_id)


def map_data_api(request):
    """
    API para dados do mapa - VERSÃO APRIMORADA
    Retorna todas as rotas e paradas com suporte a múltiplos tipos de transporte
    """
    try:
        # Buscar todas as rotas ativas com informações relacionadas
        routes = BusRoute.objects.filter(is_active=True).select_related(
            'route_type', 
            'transport_company'
        ).prefetch_related(
            Prefetch(
                'route_stops',
                queryset=RouteStop.objects.select_related('stop__stop_type').order_by('direction', 'sequence'),
                to_attr='ordered_stops'
            )
        )
        
        # Buscar todas as paradas ativas
        stops = BusStop.objects.filter(is_active=True).select_related('stop_type')
        
        routes_data = []
        for route in routes:
            # Organizar paradas por direção
            ida_stops = [rs for rs in route.ordered_stops if rs.direction == 'ida']
            volta_stops = [rs for rs in route.ordered_stops if rs.direction == 'volta']
            
            # Definir cor baseada no tipo de transporte
            route_color = route.route_type.color if route.route_type.color else '#007bff'
            
            # Determinar ícone baseado no tipo
            if route.route_type.name == 'Metrô':
                route_icon = 'subway'
                route_weight = 6
            elif route.route_type.name == 'BRT':
                route_icon = 'train'
                route_weight = 5
            elif 'Expresso' in route.route_type.name:
                route_icon = 'lightning'
                route_weight = 4
            elif 'Circular' in route.route_type.name:
                route_icon = 'arrow-repeat'
                route_weight = 3
            else:
                route_icon = 'bus'
                route_weight = 3
            
            route_info = {
                'id': route.id,
                'number': route.number,
                'name': route.name,
                'full_name': route.get_full_name(),
                'type': route.route_type.name,
                'type_icon': route_icon,
                'company': route.transport_company.short_name,
                'color': route_color,
                'weight': route_weight,
                'fare': float(route.base_fare) if route.base_fare else 0,
                'frequency': route.average_frequency,
                'duration': route.estimated_duration,
                'is_circular': route.is_circular,
                'wheelchair_accessible': route.wheelchair_accessible,
                'operates': {
                    'weekdays': route.operates_weekdays,
                    'saturdays': route.operates_saturdays,
                    'sundays': route.operates_sundays,
                },
                'stops': {
                    'ida': [{
                        'id': rs.stop.id,
                        'code': rs.stop.code,
                        'name': rs.stop.name,
                        'lat': float(rs.stop.latitude),
                        'lng': float(rs.stop.longitude),
                        'sequence': rs.sequence,
                        'distance': float(rs.distance_from_origin) if rs.distance_from_origin else 0,
                        'time': rs.estimated_time_from_origin if rs.estimated_time_from_origin else 0,
                    } for rs in ida_stops],
                    'volta': [{
                        'id': rs.stop.id,
                        'code': rs.stop.code,
                        'name': rs.stop.name,
                        'lat': float(rs.stop.latitude),
                        'lng': float(rs.stop.longitude),
                        'sequence': rs.sequence,
                        'distance': float(rs.distance_from_origin) if rs.distance_from_origin else 0,
                        'time': rs.estimated_time_from_origin if rs.estimated_time_from_origin else 0,
                    } for rs in volta_stops]
                }
            }
            routes_data.append(route_info)
        
        # Dados das paradas organizados por tipo
        stops_by_type = {}
        for stop in stops:
            stop_type = stop.stop_type.name if stop.stop_type else 'Parada Comum'
            
            if stop_type not in stops_by_type:
                stops_by_type[stop_type] = {
                    'type_info': {
                        'name': stop_type,
                        'icon': stop.stop_type.icon if stop.stop_type else 'bus',
                        'color': stop.stop_type.color if stop.stop_type else '#007bff',
                    },
                    'stops': []
                }
            
            # Contar quantas rotas passam nesta parada
            routes_count = RouteStop.objects.filter(stop=stop).values('route').distinct().count()
            
            stop_info = {
                'id': stop.id,
                'code': stop.code,
                'name': stop.name,
                'lat': float(stop.latitude),
                'lng': float(stop.longitude),
                'neighborhood': stop.neighborhood,
                'routes_count': routes_count,
                'accessibility': {
                    'wheelchair': stop.wheelchair_accessible,
                    'shelter': stop.has_shelter,
                    'seating': stop.has_seating,
                    'lighting': stop.has_lighting,
                    'security': stop.has_security,
                }
            }
            stops_by_type[stop_type]['stops'].append(stop_info)
        
        # Estatísticas do sistema
        stats = {
            'total_routes': routes.count(),
            'total_stops': stops.count(),
            'route_types': {
                'bus': routes.filter(route_type__name='Ônibus Convencional').count(),
                'metro': routes.filter(route_type__name='Metrô').count(),
                'brt': routes.filter(route_type__name='BRT').count(),
                'express': routes.filter(route_type__name='Expresso').count(),
                'circular': routes.filter(route_type__name='Circular').count(),
            },
            'coverage_area': {
                'center': {'lat': -15.7942, 'lng': -47.8822},  # Rodoviária
                'bounds': {
                    'north': -15.6000,
                    'south': -16.1000,
                    'east': -47.6000,
                    'west': -48.3000,
                }
            }
        }
        
        return JsonResponse({
            'success': True,
            'routes': routes_data,
            'stops_by_type': stops_by_type,
            'statistics': stats,
            'last_updated': timezone.now().isoformat(),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def route_map_data_api(request, route_number):
    """
    API para dados de uma rota específica no mapa - VERSÃO APRIMORADA
    """
    try:
        route = get_object_or_404(
            BusRoute.objects.select_related('route_type', 'transport_company'),
            number=route_number,
            is_active=True
        )
        
        # Buscar paradas da rota organizadas
        route_stops_ida = RouteStop.objects.filter(
            route=route,
            direction='ida'
        ).select_related('stop__stop_type').order_by('sequence')
        
        route_stops_volta = RouteStop.objects.filter(
            route=route,
            direction='volta'
        ).select_related('stop__stop_type').order_by('sequence')
        
        # Definir características visuais baseadas no tipo
        if route.route_type.name == 'Metrô':
            route_color = '#6f42c1'
            route_weight = 8
            route_opacity = 0.9
            route_icon = 'subway'
        elif route.route_type.name == 'BRT':
            route_color = '#dc3545'
            route_weight = 6
            route_opacity = 0.8
            route_icon = 'train'
        elif 'Expresso' in route.route_type.name:
            route_color = '#28a745'
            route_weight = 5
            route_opacity = 0.8
            route_icon = 'lightning'
        elif 'Circular' in route.route_type.name:
            route_color = '#ffc107'
            route_weight = 4
            route_opacity = 0.7
            route_icon = 'arrow-repeat'
        else:
            route_color = route.route_type.color or '#007bff'
            route_weight = 4
            route_opacity = 0.7
            route_icon = 'bus'
        
        def format_stops(route_stops_qs):
            return [{
                'id': rs.stop.id,
                'code': rs.stop.code,
                'name': rs.stop.name,
                'lat': float(rs.stop.latitude),
                'lng': float(rs.stop.longitude),
                'neighborhood': rs.stop.neighborhood,
                'sequence': rs.sequence,
                'distance_km': float(rs.distance_from_origin) if rs.distance_from_origin else 0,
                'time_minutes': rs.estimated_time_from_origin if rs.estimated_time_from_origin else 0,
                'stop_type': {
                    'name': rs.stop.stop_type.name if rs.stop.stop_type else 'Parada Comum',
                    'icon': rs.stop.stop_type.icon if rs.stop.stop_type else 'bus',
                    'color': rs.stop.stop_type.color if rs.stop.stop_type else '#007bff',
                },
                'accessibility': {
                    'wheelchair': rs.stop.wheelchair_accessible,
                    'shelter': rs.stop.has_shelter,
                    'seating': rs.stop.has_seating,
                    'lighting': rs.stop.has_lighting,
                    'security': rs.stop.has_security,
                }
            } for rs in route_stops_qs]
        
        return JsonResponse({
            'success': True,
            'route': {
                'id': route.id,
                'number': route.number,
                'name': route.name,
                'full_name': route.get_full_name(),
                'origin': route.origin_terminal,
                'destination': route.destination_terminal,
                'type': {
                    'name': route.route_type.name,
                    'icon': route_icon,
                    'color': route_color,
                },
                'company': {
                    'name': route.transport_company.name,
                    'short_name': route.transport_company.short_name,
                },
                'fare': float(route.base_fare) if route.base_fare else 0,
                'frequency_minutes': route.average_frequency,
                'duration_minutes': route.estimated_duration,
                'is_circular': route.is_circular,
                'wheelchair_accessible': route.wheelchair_accessible,
                'operates': {
                    'weekdays': route.operates_weekdays,
                    'saturdays': route.operates_saturdays,
                    'sundays': route.operates_sundays,
                },
                'visual': {
                    'color': route_color,
                    'weight': route_weight,
                    'opacity': route_opacity,
                }
            },
            'stops': {
                'ida': format_stops(route_stops_ida),
                'volta': format_stops(route_stops_volta) if not route.is_circular else [],
            },
            'statistics': {
                'total_stops': {
                    'ida': route_stops_ida.count(),
                    'volta': route_stops_volta.count() if not route.is_circular else 0,
                },
                'total_distance': {
                    'ida': route_stops_ida.aggregate(
                        total=models.Max('distance_from_origin')
                    )['total'] or 0,
                    'volta': route_stops_volta.aggregate(
                        total=models.Max('distance_from_origin')
                    )['total'] or 0 if not route.is_circular else 0,
                },
                'total_time': {
                    'ida': route_stops_ida.aggregate(
                        total=models.Max('estimated_time_from_origin')
                    )['total'] or 0,
                    'volta': route_stops_volta.aggregate(
                        total=models.Max('estimated_time_from_origin')
                    )['total'] or 0 if not route.is_circular else 0,
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

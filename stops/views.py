"""
Views para gerenciamento de paradas do BusFeed.
Implementa as páginas de listagem, detalhes e busca de paradas.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.contrib import messages
from .models import BusStop, StopType, StopAmenity


class StopListView(ListView):
    """
    Lista todas as paradas de ônibus com filtros e busca.
    """
    model = BusStop
    template_name = 'stops/stop_list.html'
    context_object_name = 'stops'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Retorna queryset filtrado e otimizado.
        """
        queryset = BusStop.objects.select_related(
            'stop_type'
        ).prefetch_related(
            'route_stops__route',
            'amenity_mappings__amenity'
        ).filter(is_active=True)
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search) |
                Q(nickname__icontains=search) |
                Q(neighborhood__icontains=search) |
                Q(reference_point__icontains=search)
            )
        
        # Filtro por tipo
        stop_type = self.request.GET.get('type')
        if stop_type:
            queryset = queryset.filter(stop_type_id=stop_type)
        
        # Filtro por bairro
        neighborhood = self.request.GET.get('neighborhood')
        if neighborhood:
            queryset = queryset.filter(neighborhood__icontains=neighborhood)
        
        # Filtro por acessibilidade
        wheelchair = self.request.GET.get('wheelchair')
        if wheelchair == 'true':
            queryset = queryset.filter(wheelchair_accessible=True)
        
        # Filtro por facilidades
        has_shelter = self.request.GET.get('shelter')
        if has_shelter == 'true':
            queryset = queryset.filter(has_shelter=True)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados extras ao contexto.
        """
        context = super().get_context_data(**kwargs)
        
        # Bairros únicos
        neighborhoods = BusStop.objects.filter(
            is_active=True,
            neighborhood__isnull=False
        ).exclude(neighborhood='').values_list(
            'neighborhood', flat=True
        ).distinct().order_by('neighborhood')
        
        context.update({
            'stop_types': StopType.objects.all(),
            'neighborhoods': neighborhoods,
            'search_term': self.request.GET.get('search', ''),
            'selected_type': self.request.GET.get('type', ''),
            'selected_neighborhood': self.request.GET.get('neighborhood', ''),
            'wheelchair_filter': self.request.GET.get('wheelchair', ''),
            'shelter_filter': self.request.GET.get('shelter', ''),
        })
        return context


class StopDetailView(DetailView):
    """
    Exibe detalhes completos de uma parada específica.
    """
    model = BusStop
    template_name = 'stops/stop_detail.html'
    context_object_name = 'stop'
    slug_field = 'code'
    slug_url_kwarg = 'stop_code'
    
    def get_queryset(self):
        """
        Otimiza consulta com dados relacionados.
        """
        return BusStop.objects.select_related(
            'stop_type'
        ).prefetch_related(
            Prefetch(
                'route_stops',
                queryset=None,  # Buscar todas as rotas da parada
                to_attr='ordered_routes'
            ),
            'amenity_mappings__amenity',
            'user_reports'
        )
    
    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras sobre a parada.
        """
        context = super().get_context_data(**kwargs)
        stop = self.object
        
        # Rotas que passam na parada
        routes_ida = stop.route_stops.filter(direction='ida').select_related('route__route_type', 'route__transport_company').order_by('sequence')
        routes_volta = stop.route_stops.filter(direction='volta').select_related('route__route_type', 'route__transport_company').order_by('sequence')
        routes_circular = stop.route_stops.filter(direction='circular').select_related('route__route_type', 'route__transport_company').order_by('sequence')
        
        # Facilidades disponíveis
        amenities = stop.amenity_mappings.filter(
            is_working=True
        ).select_related('amenity').order_by('amenity__category', 'amenity__name')
        
        # Relatórios recentes
        recent_reports = stop.user_reports.filter(
            status__in=['pending', 'investigating', 'confirmed']
        ).order_by('-created_at')[:5]
        
        context.update({
            'routes_ida': routes_ida,
            'routes_volta': routes_volta,
            'routes_circular': routes_circular,
            'total_routes': routes_ida.count() + routes_volta.count() + routes_circular.count(),
            'amenities': amenities,
            'recent_reports': recent_reports,
            'accessibility_score': stop.get_accessibility_score(),
            'comfort_score': stop.get_comfort_score(),
            'is_operational': stop.is_operational(),
        })
        return context


def stop_search_ajax(request):
    """
    Busca de paradas via AJAX para autocomplete.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '')
        if len(query) >= 2:
            stops = BusStop.objects.filter(
                Q(code__icontains=query) |
                Q(name__icontains=query) |
                Q(nickname__icontains=query) |
                Q(neighborhood__icontains=query),
                is_active=True
            ).select_related('stop_type')[:10]
            
            results = []
            for stop in stops:
                results.append({
                    'id': stop.id,
                    'code': stop.code,
                    'name': stop.name,
                    'nickname': stop.nickname,
                    'neighborhood': stop.neighborhood,
                    'type': stop.stop_type.name,
                    'wheelchair_accessible': stop.wheelchair_accessible,
                    'has_shelter': stop.has_shelter,
                    'reference_point': stop.reference_point,
                })
            
            return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})


def stop_routes_data(request, stop_code):
    """
    Retorna dados das rotas que passam na parada.
    """
    stop = get_object_or_404(BusStop, code=stop_code, is_active=True)
    
    # Organizar rotas por direção
    routes_data = {
        'ida': [],
        'volta': [],
        'circular': []
    }
    
    for route_stop in stop.route_stops.select_related('route__route_type', 'route__transport_company').all():
        route = route_stop.route
        route_info = {
            'id': route.id,
            'number': route.number,
            'name': route.name,
            'type': route.route_type.name,
            'type_color': route.route_type.color,
            'company': route.transport_company.short_name,
            'sequence': route_stop.sequence,
            'wheelchair_accessible': route.wheelchair_accessible,
            'fare': str(route.get_current_fare()) if route.get_current_fare() else None,
            'is_operational': route.is_operational_today(),
        }
        
        routes_data[route_stop.direction].append(route_info)
    
    # Ordenar por sequência
    for direction in routes_data:
        routes_data[direction].sort(key=lambda x: x['sequence'])
    
    data = {
        'stop': {
            'id': stop.id,
            'code': stop.code,
            'name': stop.name,
            'neighborhood': stop.neighborhood,
            'type': stop.stop_type.name,
        },
        'routes': routes_data,
        'total_routes': sum(len(routes) for routes in routes_data.values()),
    }
    
    return JsonResponse(data)


def stop_map_data(request, stop_code):
    """
    Retorna dados da parada para exibição no mapa.
    """
    stop = get_object_or_404(BusStop, code=stop_code, is_active=True)
    
    data = {
        'stop': {
            'id': stop.id,
            'code': stop.code,
            'name': stop.name,
            'type': stop.stop_type.name,
            'neighborhood': stop.neighborhood,
            'reference_point': stop.reference_point,
            'wheelchair_accessible': stop.wheelchair_accessible,
            'has_shelter': stop.has_shelter,
            'has_seating': stop.has_seating,
            'has_lighting': stop.has_lighting,
        },
        'location': None,  # Será preenchido quando houver dados de geolocalização
        'nearby_stops': [],  # Paradas próximas
    }
    
    # Adicionar coordenadas se disponíveis
    if stop.location:
        data['location'] = {
            'lat': stop.location.y,
            'lng': stop.location.x,
        }
    
    return JsonResponse(data)

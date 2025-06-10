"""
Views para gerenciamento de rotas do BusFeed.
Implementa as páginas de listagem, detalhes e busca de rotas.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from .models import BusRoute, RouteType, TransportCompany, Vehicle


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
    Exibe detalhes completos de uma rota específica.
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
                queryset=None,  # Buscar todas as paradas da rota
                to_attr='ordered_stops'
            ),
            'vehicle_locations__vehicle'
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
        
        # Veículos ativos na rota
        active_vehicles = Vehicle.objects.filter(
            locations__route=route,
            is_operational=True
        ).distinct()[:5]
        
        context.update({
            'ida_stops': ida_stops,
            'volta_stops': volta_stops,
            'active_vehicles': active_vehicles,
            'total_stops': ida_stops.count() + volta_stops.count(),
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
                    'id': route.id,
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


def route_map_data(request, route_number):
    """
    Retorna dados da rota para exibição no mapa.
    """
    route = get_object_or_404(BusRoute, number=route_number, is_active=True)
    
    # Dados das paradas
    stops_data = []
    for route_stop in route.route_stops.select_related('stop').all():
        if route_stop.stop.location:
            stops_data.append({
                'id': route_stop.stop.id,
                'name': route_stop.stop.name,
                'code': route_stop.stop.code,
                'direction': route_stop.direction,
                'sequence': route_stop.sequence,
                'lat': route_stop.stop.location.y,
                'lng': route_stop.stop.location.x,
                'wheelchair_accessible': route_stop.stop.wheelchair_accessible,
                'has_shelter': route_stop.stop.has_shelter,
            })
    
    # Dados dos veículos ativos
    vehicles_data = []
    for location in route.vehicle_locations.select_related('vehicle').filter(
        vehicle__is_operational=True
    )[:10]:  # Últimas 10 localizações
        if location.location:
            vehicles_data.append({
                'vehicle_id': location.vehicle.id,
                'fleet_number': location.vehicle.fleet_number,
                'lat': location.location.y,
                'lng': location.location.x,
                'speed': location.speed,
                'heading': location.heading,
                'timestamp': location.created_at.isoformat(),
            })
    
    data = {
        'route': {
            'id': route.id,
            'number': route.number,
            'name': route.name,
            'origin': route.origin_terminal,
            'destination': route.destination_terminal,
            'color': route.route_type.color,
        },
        'stops': stops_data,
        'vehicles': vehicles_data,
    }
    
    return JsonResponse(data)

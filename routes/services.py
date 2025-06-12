"""
Serviços para gerenciamento de rotas do BusFeed.
Implementa a lógica de negócio separada das views, seguindo Clean Architecture.
"""
from typing import List, Dict, Optional, Tuple
from django.db.models import QuerySet, Q, Count, Prefetch
from django.core.cache import cache
from django.utils import timezone
from .models import BusRoute, RouteType, TransportCompany, RouteStop, Vehicle, VehicleLocation
from stops.models import BusStop
import logging

logger = logging.getLogger('busfeed.routes')


class RouteService:
    """
    Serviço principal para operações relacionadas a rotas.
    Centraliza a lógica de negócio e otimizações de performance.
    """
    
    CACHE_TIMEOUT = 3600  # 1 hora para dados de rota
    
    @staticmethod
    def get_active_routes_queryset() -> QuerySet:
        """
        Retorna queryset otimizado para rotas ativas.
        Aplica select_related e prefetch_related para evitar N+1 queries.
        """
        return BusRoute.objects.select_related(
            'route_type', 'transport_company'
        ).prefetch_related(
            Prefetch(
                'route_stops',
                queryset=RouteStop.objects.select_related('stop').order_by('direction', 'sequence'),
                to_attr='ordered_stops'
            )
        ).filter(is_active=True)
    
    @classmethod
    def search_routes(cls, search_term: str, filters: Dict = None) -> QuerySet:
        """
        Busca rotas por termo de pesquisa e aplica filtros.
        
        Args:
            search_term: Termo para busca textual
            filters: Dicionário com filtros opcionais (type, company, wheelchair)
            
        Returns:
            QuerySet filtrado e otimizado
        """
        filters = filters or {}
        queryset = cls.get_active_routes_queryset()
        
        # Aplicar busca textual
        if search_term:
            queryset = queryset.filter(
                Q(number__icontains=search_term) |
                Q(name__icontains=search_term) |
                Q(origin_terminal__icontains=search_term) |
                Q(destination_terminal__icontains=search_term)
            )
        
        # Aplicar filtros específicos
        if filters.get('route_type'):
            queryset = queryset.filter(route_type_id=filters['route_type'])
            
        if filters.get('company'):
            queryset = queryset.filter(transport_company_id=filters['company'])
            
        if filters.get('wheelchair') == 'true':
            queryset = queryset.filter(wheelchair_accessible=True)
        
        return queryset.order_by('number', 'name')
    
    @classmethod
    def get_route_detail(cls, route_number: str) -> Optional[BusRoute]:
        """
        Retorna detalhes completos de uma rota específica.
        Implementa cache para otimizar performance.
        
        Args:
            route_number: Número da rota
            
        Returns:
            Instância da rota ou None se não encontrada
        """
        cache_key = f'route_detail_{route_number}'
        route = cache.get(cache_key)
        
        if not route:
            try:
                route = cls.get_active_routes_queryset().get(number=route_number)
                cache.set(cache_key, route, cls.CACHE_TIMEOUT)
                logger.info(f'Route {route_number} cached for {cls.CACHE_TIMEOUT}s')
            except BusRoute.DoesNotExist:
                logger.warning(f'Route {route_number} not found')
                return None
        
        return route
    
    @staticmethod
    def get_route_stops_data(route: BusRoute) -> Dict:
        """
        Organiza dados das paradas de uma rota por direção.
        
        Args:
            route: Instância da rota
            
        Returns:
            Dicionário com paradas organizadas por direção
        """
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
        
        return stops_data


class RouteMapService:
    """
    Serviço especializado para dados de mapas e geolocalização.
    """
    
    CACHE_TIMEOUT = 1800  # 30 minutos para dados de mapa
    
    @classmethod
    def get_route_map_data(cls, route_number: str) -> Dict:
        """
        Prepara dados completos da rota para exibição em mapa.
        
        Args:
            route_number: Número da rota
            
        Returns:
            Dicionário com dados formatados para o mapa
        """
        cache_key = f'route_map_data_{route_number}'
        map_data = cache.get(cache_key)
        
        if not map_data:
            route = RouteService.get_route_detail(route_number)
            if not route:
                return {}
            
            stops_data = RouteService.get_route_stops_data(route)
            
            map_data = {
                'route': {
                    'id': str(route.id),
                    'number': route.number,
                    'name': route.name,
                    'full_name': route.get_full_name(),
                    'type': route.route_type.name,
                    'type_color': route.route_type.color,
                    'company': route.transport_company.name,
                    'wheelchair_accessible': route.wheelchair_accessible,
                    'fare': str(route.get_current_fare()) if route.get_current_fare() else None,
                    'is_circular': route.is_circular,
                    'is_bidirectional': route.is_bidirectional,
                },
                'stops': stops_data,
                'metadata': {
                    'total_stops': sum(len(stops) for stops in stops_data.values()),
                    'has_wheelchair_stops': any(
                        stop['wheelchair_accessible'] for direction_stops in stops_data.values()
                        for stop in direction_stops
                    ),
                    'updated_at': timezone.now().isoformat()
                }
            }
            
            cache.set(cache_key, map_data, cls.CACHE_TIMEOUT)
            logger.info(f'Map data for route {route_number} cached')
        
        return map_data
    
    @classmethod
    def get_all_routes_map_data(cls) -> List[Dict]:
        """
        Retorna dados simplificados de todas as rotas para mapa geral.
        
        Returns:
            Lista com dados básicos de todas as rotas
        """
        cache_key = 'all_routes_map_data'
        routes_data = cache.get(cache_key)
        
        if not routes_data:
            routes = RouteService.get_active_routes_queryset().only(
                'id', 'number', 'name', 'route_type__name', 'route_type__color',
                'transport_company__short_name', 'wheelchair_accessible'
            )
            
            routes_data = []
            for route in routes:
                routes_data.append({
                    'id': str(route.id),
                    'number': route.number,
                    'name': route.name,
                    'type': route.route_type.name,
                    'type_color': route.route_type.color,
                    'company': route.transport_company.short_name,
                    'wheelchair_accessible': route.wheelchair_accessible,
                })
            
            cache.set(cache_key, routes_data, cls.CACHE_TIMEOUT)
            logger.info(f'All routes map data cached ({len(routes_data)} routes)')
        
        return routes_data


class VehicleTrackingService:
    """
    Serviço para rastreamento de veículos em tempo real.
    """
    
    CACHE_TIMEOUT = 30  # 30 segundos para dados em tempo real
    
    @classmethod
    def get_vehicle_locations(cls, route_number: str = None) -> List[Dict]:
        """
        Retorna localizações atuais dos veículos.
        
        Args:
            route_number: Filtrar por rota específica (opcional)
            
        Returns:
            Lista com dados de localização dos veículos
        """
        cache_key = f'vehicle_locations_{route_number or "all"}'
        locations = cache.get(cache_key)
        
        if not locations:
            queryset = VehicleLocation.objects.select_related(
                'vehicle', 'route'
            ).filter(
                created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
            )
            
            if route_number:
                queryset = queryset.filter(route__number=route_number)
            
            locations = []
            for location in queryset:
                if location.latitude and location.longitude:
                    locations.append({
                        'vehicle_id': str(location.vehicle.id),
                        'fleet_number': location.vehicle.fleet_number,
                        'route_number': location.route.number if location.route else None,
                        'lat': float(location.latitude),
                        'lng': float(location.longitude),
                        'speed': location.speed,
                        'heading': location.heading,
                        'passenger_count': location.passenger_count,
                        'updated_at': location.created_at.isoformat(),
                    })
            
            cache.set(cache_key, locations, cls.CACHE_TIMEOUT)
            logger.debug(f'Vehicle locations cached: {len(locations)} vehicles')
        
        return locations


class RouteStatisticsService:
    """
    Serviço para estatísticas e analytics de rotas.
    """
    
    @staticmethod
    def get_route_statistics() -> Dict:
        """
        Calcula estatísticas gerais do sistema de rotas.
        
        Returns:
            Dicionário com estatísticas consolidadas
        """
        cache_key = 'route_statistics'
        stats = cache.get(cache_key)
        
        if not stats:
            total_routes = BusRoute.objects.filter(is_active=True).count()
            total_companies = TransportCompany.objects.filter(is_active=True).count()
            total_stops = BusStop.objects.filter(is_active=True).count()
            wheelchair_routes = BusRoute.objects.filter(
                is_active=True, wheelchair_accessible=True
            ).count()
            
            stats = {
                'total_routes': total_routes,
                'total_companies': total_companies,
                'total_stops': total_stops,
                'wheelchair_routes': wheelchair_routes,
                'wheelchair_percentage': round((wheelchair_routes / total_routes * 100), 1) if total_routes else 0,
                'updated_at': timezone.now().isoformat()
            }
            
            cache.set(cache_key, stats, 3600)  # Cache por 1 hora
            logger.info('Route statistics calculated and cached')
        
        return stats 
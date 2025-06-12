"""
Serviços para gerenciamento de paradas do BusFeed.
Implementa a lógica de negócio para operações com paradas de ônibus.
"""
from typing import List, Dict, Optional, Tuple
from django.db.models import QuerySet, Q, Count
from django.core.cache import cache
from django.utils import timezone
from .models import BusStop, StopType
import logging
import math

logger = logging.getLogger('busfeed.stops')


class StopService:
    """
    Serviço principal para operações relacionadas a paradas.
    """
    
    CACHE_TIMEOUT = 7200  # 2 horas para dados de parada (mudança rara)
    
    @staticmethod
    def get_active_stops_queryset() -> QuerySet:
        """
        Retorna queryset otimizado para paradas ativas.
        """
        return BusStop.objects.select_related('stop_type').filter(is_active=True)
    
    @classmethod
    def search_stops(cls, search_term: str, filters: Dict = None) -> QuerySet:
        """
        Busca paradas por termo e aplica filtros.
        
        Args:
            search_term: Termo para busca textual
            filters: Filtros opcionais (neighborhood, wheelchair, stop_type)
            
        Returns:
            QuerySet filtrado e otimizado
        """
        filters = filters or {}
        queryset = cls.get_active_stops_queryset()
        
        # Busca textual
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(code__icontains=search_term) |
                Q(neighborhood__icontains=search_term) |
                Q(reference_point__icontains=search_term) |
                Q(address__icontains=search_term)
            )
        
        # Filtros específicos
        if filters.get('neighborhood'):
            queryset = queryset.filter(neighborhood__icontains=filters['neighborhood'])
            
        if filters.get('wheelchair') == 'true':
            queryset = queryset.filter(wheelchair_accessible=True)
            
        if filters.get('stop_type'):
            queryset = queryset.filter(stop_type_id=filters['stop_type'])
        
        return queryset.order_by('name')
    
    @classmethod
    def get_stop_detail(cls, stop_code: str) -> Optional[BusStop]:
        """
        Retorna detalhes de uma parada específica com cache.
        
        Args:
            stop_code: Código da parada
            
        Returns:
            Instância da parada ou None se não encontrada
        """
        cache_key = f'stop_detail_{stop_code}'
        stop = cache.get(cache_key)
        
        if not stop:
            try:
                stop = cls.get_active_stops_queryset().get(code=stop_code)
                cache.set(cache_key, stop, cls.CACHE_TIMEOUT)
                logger.info(f'Stop {stop_code} cached for {cls.CACHE_TIMEOUT}s')
            except BusStop.DoesNotExist:
                logger.warning(f'Stop {stop_code} not found')
                return None
        
        return stop
    
    @staticmethod
    def get_neighborhoods_list() -> List[str]:
        """
        Retorna lista de bairros únicos das paradas.
        
        Returns:
            Lista de nomes de bairros
        """
        cache_key = 'neighborhoods_list'
        neighborhoods = cache.get(cache_key)
        
        if not neighborhoods:
            neighborhoods = list(
                BusStop.objects.filter(is_active=True)
                .exclude(neighborhood__isnull=True)
                .exclude(neighborhood__exact='')
                .values_list('neighborhood', flat=True)
                .distinct()
                .order_by('neighborhood')
            )
            
            cache.set(cache_key, neighborhoods, 3600)
            logger.info(f'Neighborhoods list cached ({len(neighborhoods)} neighborhoods)')
        
        return neighborhoods

    @classmethod
    def get_map_data(cls) -> List[Dict]:
        """
        Retorna dados simplificados de todas as paradas para mapa.
        
        Returns:
            Lista com dados básicos de todas as paradas
        """
        cache_key = 'all_stops_map_data'
        stops_data = cache.get(cache_key)
        
        if not stops_data:
            stops = BusStop.objects.filter(is_active=True).only(
                'id', 'code', 'name', 'neighborhood', 'latitude', 'longitude',
                'wheelchair_accessible', 'has_shelter', 'has_seating'
            )
            
            stops_data = []
            for stop in stops:
                if stop.latitude and stop.longitude:
                    stops_data.append({
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
                        'has_seating': stop.has_seating,
                    })
            
            cache.set(cache_key, stops_data, 1800)  # 30 minutos
            logger.info(f'All stops map data cached ({len(stops_data)} stops)')
        
        return stops_data


class StopGeoService:
    """
    Serviço especializado para operações geográficas com paradas.
    """
    
    CACHE_TIMEOUT = 1800  # 30 minutos para dados geográficos
    
    @classmethod
    def find_nearby_stops(cls, latitude: float, longitude: float, radius_meters: int = 1000) -> List[Dict]:
        """
        Encontra paradas próximas a uma coordenada.
        Implementa busca simples por bounding box (sem PostGIS).
        
        Args:
            latitude: Latitude de referência
            longitude: Longitude de referência
            radius_meters: Raio de busca em metros (máximo 5000m)
            
        Returns:
            Lista de paradas próximas com distâncias
        """
        # Validação de parâmetros
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.warning(f'Invalid coordinates: lat={latitude}, lng={longitude}')
            return []
        
        radius_meters = min(radius_meters, 5000)  # Máximo 5km
        
        # Cache baseado em coordenadas arredondadas
        lat_rounded = round(latitude, 4)
        lng_rounded = round(longitude, 4)
        cache_key = f'nearby_stops_{lat_rounded}_{lng_rounded}_{radius_meters}'
        
        nearby_stops = cache.get(cache_key)
        
        if not nearby_stops:
            # Cálculo do bounding box
            lat_delta = radius_meters / 111000  # Aproximadamente 1 grau = 111km
            lng_delta = radius_meters / (111000 * math.cos(math.radians(latitude)))
            
            # Busca por bounding box
            stops = StopService.get_active_stops_queryset().filter(
                latitude__gte=latitude - lat_delta,
                latitude__lte=latitude + lat_delta,
                longitude__gte=longitude - lng_delta,
                longitude__lte=longitude + lng_delta,
                latitude__isnull=False,
                longitude__isnull=False
            )
            
            nearby_stops = []
            for stop in stops:
                # Calcular distância usando fórmula de Haversine simplificada
                distance = cls._calculate_distance(
                    latitude, longitude, 
                    stop.latitude, stop.longitude
                )
                
                if distance <= radius_meters:
                    nearby_stops.append({
                        'id': str(stop.id),
                        'code': stop.code,
                        'name': stop.name,
                        'lat': stop.latitude,
                        'lng': stop.longitude,
                        'distance': round(distance),
                        'neighborhood': stop.neighborhood,
                        'type': stop.stop_type.name if stop.stop_type else 'Parada Comum',
                        'wheelchair_accessible': stop.wheelchair_accessible,
                        'has_shelter': stop.has_shelter,
                        'has_seating': stop.has_seating,
                        'routes_count': getattr(stop, 'routes_count', 0)
                    })
            
            # Ordenar por distância
            nearby_stops.sort(key=lambda x: x['distance'])
            
            cache.set(cache_key, nearby_stops, cls.CACHE_TIMEOUT)
            logger.debug(f'Found {len(nearby_stops)} stops within {radius_meters}m')
        
        return nearby_stops
    
    @staticmethod
    def _calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calcula distância entre duas coordenadas usando fórmula de Haversine.
        
        Args:
            lat1, lng1: Coordenadas do ponto 1
            lat2, lng2: Coordenadas do ponto 2
            
        Returns:
            Distância em metros
        """
        # Raio da Terra em metros
        R = 6371000
        
        # Converter para radianos
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        # Fórmula de Haversine
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @classmethod
    def get_stops_map_data(cls, filters: Dict = None) -> List[Dict]:
        """
        Retorna dados de paradas formatados para mapa.
        
        Args:
            filters: Filtros opcionais para as paradas
            
        Returns:
            Lista com dados das paradas para mapa
        """
        filters = filters or {}
        cache_key = f'stops_map_data_{hash(str(sorted(filters.items())))}'
        
        map_data = cache.get(cache_key)
        
        if not map_data:
            queryset = StopService.get_active_stops_queryset().filter(
                latitude__isnull=False,
                longitude__isnull=False
            )
            
            # Aplicar filtros
            if filters.get('neighborhood'):
                queryset = queryset.filter(neighborhood__icontains=filters['neighborhood'])
                
            if filters.get('wheelchair') == 'true':
                queryset = queryset.filter(wheelchair_accessible=True)
                
            if filters.get('stop_type'):
                queryset = queryset.filter(stop_type_id=filters['stop_type'])
            
            # Limitar para performance (máximo 500 paradas no mapa)
            stops = queryset[:500]
            
            map_data = []
            for stop in stops:
                map_data.append({
                    'id': str(stop.id),
                    'code': stop.code,
                    'name': stop.name,
                    'lat': float(stop.latitude),
                    'lng': float(stop.longitude),
                    'neighborhood': stop.neighborhood,
                    'type': stop.stop_type.name if stop.stop_type else 'Parada Comum',
                    'type_icon': stop.stop_type.icon if stop.stop_type else 'bus',
                    'type_color': stop.stop_type.color if stop.stop_type else '#007bff',
                    'wheelchair_accessible': stop.wheelchair_accessible,
                    'has_shelter': stop.has_shelter,
                    'has_seating': stop.has_seating,
                    'has_lighting': stop.has_lighting,
                    'has_security': stop.has_security,
                })
            
            cache.set(cache_key, map_data, cls.CACHE_TIMEOUT)
            logger.info(f'Map data cached: {len(map_data)} stops')
        
        return map_data


class StopStatisticsService:
    """
    Serviço para estatísticas e analytics de paradas.
    """
    
    @staticmethod
    def get_stop_statistics() -> Dict:
        """
        Calcula estatísticas gerais do sistema de paradas.
        
        Returns:
            Dicionário com estatísticas consolidadas
        """
        cache_key = 'stop_statistics'
        stats = cache.get(cache_key)
        
        if not stats:
            total_stops = BusStop.objects.filter(is_active=True).count()
            wheelchair_stops = BusStop.objects.filter(
                is_active=True, wheelchair_accessible=True
            ).count()
            stops_with_shelter = BusStop.objects.filter(
                is_active=True, has_shelter=True
            ).count()
            stops_with_seating = BusStop.objects.filter(
                is_active=True, has_seating=True
            ).count()
            neighborhoods_count = BusStop.objects.filter(
                is_active=True, neighborhood__isnull=False
            ).values('neighborhood').distinct().count()
            
            stats = {
                'total_stops': total_stops,
                'wheelchair_stops': wheelchair_stops,
                'wheelchair_percentage': round((wheelchair_stops / total_stops * 100), 1) if total_stops else 0,
                'stops_with_shelter': stops_with_shelter,
                'shelter_percentage': round((stops_with_shelter / total_stops * 100), 1) if total_stops else 0,
                'stops_with_seating': stops_with_seating,
                'seating_percentage': round((stops_with_seating / total_stops * 100), 1) if total_stops else 0,
                'neighborhoods_covered': neighborhoods_count,
                'updated_at': timezone.now().isoformat()
            }
            
            cache.set(cache_key, stats, 3600)  # Cache por 1 hora
            logger.info('Stop statistics calculated and cached')
        
        return stats
    
    @staticmethod
    def get_accessibility_report() -> Dict:
        """
        Gera relatório detalhado de acessibilidade das paradas.
        
        Returns:
            Relatório de acessibilidade por bairro
        """
        cache_key = 'accessibility_report'
        report = cache.get(cache_key)
        
        if not report:
            from django.db.models import Count, Q
            
            # Agregação por bairro
            neighborhood_stats = BusStop.objects.filter(
                is_active=True,
                neighborhood__isnull=False
            ).values('neighborhood').annotate(
                total_stops=Count('id'),
                wheelchair_stops=Count('id', filter=Q(wheelchair_accessible=True)),
                shelter_stops=Count('id', filter=Q(has_shelter=True)),
                seating_stops=Count('id', filter=Q(has_seating=True)),
                lighting_stops=Count('id', filter=Q(has_lighting=True)),
                security_stops=Count('id', filter=Q(has_security=True))
            ).order_by('neighborhood')
            
            neighborhoods = []
            for stats in neighborhood_stats:
                total = stats['total_stops']
                neighborhoods.append({
                    'name': stats['neighborhood'],
                    'total_stops': total,
                    'accessibility': {
                        'wheelchair': {
                            'count': stats['wheelchair_stops'],
                            'percentage': round((stats['wheelchair_stops'] / total * 100), 1) if total else 0
                        },
                        'shelter': {
                            'count': stats['shelter_stops'],
                            'percentage': round((stats['shelter_stops'] / total * 100), 1) if total else 0
                        },
                        'seating': {
                            'count': stats['seating_stops'],
                            'percentage': round((stats['seating_stops'] / total * 100), 1) if total else 0
                        },
                        'lighting': {
                            'count': stats['lighting_stops'],
                            'percentage': round((stats['lighting_stops'] / total * 100), 1) if total else 0
                        },
                        'security': {
                            'count': stats['security_stops'],
                            'percentage': round((stats['security_stops'] / total * 100), 1) if total else 0
                        }
                    }
                })
            
            report = {
                'neighborhoods': neighborhoods,
                'summary': StopStatisticsService.get_stop_statistics(),
                'generated_at': timezone.now().isoformat()
            }
            
            cache.set(cache_key, report, 1800)  # Cache por 30 minutos
            logger.info('Accessibility report generated and cached')
        
        return report 
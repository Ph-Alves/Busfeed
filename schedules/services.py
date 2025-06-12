"""
Serviços para gerenciamento de horários do BusFeed.
Implementa a lógica de negócio para horários, previsões e cronogramas.
"""
from typing import List, Dict, Optional, Tuple
from django.db.models import QuerySet, Q, Count, Avg
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import ScheduleEntry, ScheduleTemplate, RealTimeUpdate, ServiceAlert
from routes.models import BusRoute
import logging

logger = logging.getLogger('busfeed.schedules')


class ScheduleService:
    """
    Serviço principal para operações relacionadas a horários.
    """
    
    CACHE_TIMEOUT = 300  # 5 minutos para dados de horário
    
    @staticmethod
    def get_active_schedules_queryset() -> QuerySet:
        """
        Retorna queryset otimizado para horários ativos.
        """
        return ScheduleEntry.objects.select_related(
            'route', 'route__route_type', 'route__transport_company'
        ).filter(is_active=True)
    
    @classmethod
    def get_route_schedules(cls, route_number: str, direction: str = None, 
                           day_type: str = None) -> QuerySet:
        """
        Obtém horários de uma rota específica com filtros.
        
        Args:
            route_number: Número da rota
            direction: Direção (ida, volta, circular)
            day_type: Tipo de dia (weekday, saturday, sunday)
            
        Returns:
            QuerySet com horários filtrados
        """
        cache_key = f'schedule_{route_number}_{direction}_{day_type}'
        schedules = cache.get(cache_key)
        
        if not schedules:
            queryset = cls.get_active_schedules_queryset().filter(
                route__number=route_number
            )
            
            if direction:
                queryset = queryset.filter(direction=direction)
                
            if day_type:
                queryset = queryset.filter(day_type=day_type)
            
            schedules = list(queryset.order_by('departure_time'))
            cache.set(cache_key, schedules, cls.CACHE_TIMEOUT)
            logger.debug(f'Schedules cached for route {route_number}')
        
        return schedules
    
    @classmethod
    def get_next_departures(cls, route_number: str, direction: str = None, 
                           limit: int = 5) -> List[Dict]:
        """
        Obtém próximas partidas de uma rota.
        
        Args:
            route_number: Número da rota
            direction: Direção específica (opcional)
            limit: Número máximo de partidas
            
        Returns:
            Lista com próximas partidas e estimativas
        """
        current_time = timezone.now()
        current_day_type = cls._get_day_type(current_time)
        
        cache_key = f'next_departures_{route_number}_{direction}_{current_day_type}_{current_time.hour}'
        next_departures = cache.get(cache_key)
        
        if not next_departures:
            schedules = cls.get_route_schedules(route_number, direction, current_day_type)
            
            # Filtrar horários futuros
            current_time_only = current_time.time()
            future_schedules = [
                s for s in schedules 
                if s.departure_time >= current_time_only
            ]
            
            # Se não há mais horários hoje, buscar primeiros de amanhã
            if not future_schedules:
                tomorrow_type = cls._get_day_type(current_time + timedelta(days=1))
                tomorrow_schedules = cls.get_route_schedules(
                    route_number, direction, tomorrow_type
                )
                future_schedules = tomorrow_schedules[:limit]
                next_day = True
            else:
                next_day = False
            
            next_departures = []
            for schedule in future_schedules[:limit]:
                # Buscar atualizações em tempo real
                real_time_data = cls._get_real_time_update(schedule)
                
                departure_data = {
                    'id': str(schedule.id),
                    'scheduled_time': schedule.departure_time.strftime('%H:%M'),
                    'direction': schedule.direction,
                    'day_type': schedule.day_type,
                    'is_next_day': next_day,
                    'real_time': real_time_data,
                    'estimated_time': cls._calculate_estimated_time(schedule, real_time_data),
                    'delay_minutes': real_time_data.get('delay_minutes', 0) if real_time_data else 0,
                }
                
                next_departures.append(departure_data)
            
            cache.set(cache_key, next_departures, 60)  # Cache por 1 minuto
            logger.debug(f'Next departures calculated for route {route_number}')
        
        return next_departures
    
    @staticmethod
    def _get_day_type(date_time: datetime) -> str:
        """
        Determina o tipo de dia baseado na data.
        
        Args:
            date_time: Data/hora para análise
            
        Returns:
            Tipo de dia (weekday, saturday, sunday)
        """
        weekday = date_time.weekday()
        
        if weekday < 5:  # Segunda a sexta
            return 'weekday'
        elif weekday == 5:  # Sábado
            return 'saturday'
        else:  # Domingo
            return 'sunday'
    
    @staticmethod
    def _get_real_time_update(schedule: ScheduleEntry) -> Optional[Dict]:
        """
        Busca atualização em tempo real para um horário.
        
        Args:
            schedule: Entrada de horário
            
        Returns:
            Dados de tempo real ou None
        """
        try:
            update = RealTimeUpdate.objects.filter(
                route=schedule.route,
                direction=schedule.direction,
                created_at__gte=timezone.now() - timedelta(minutes=10)
            ).first()
            
            if update:
                return {
                    'delay_minutes': update.delay_minutes,
                    'updated_at': update.created_at.isoformat(),
                    'confidence': update.confidence_level,
                }
        except Exception as e:
            logger.warning(f'Error getting real-time update: {e}')
        
        return None
    
    @staticmethod
    def _calculate_estimated_time(schedule: ScheduleEntry, real_time_data: Dict = None) -> str:
        """
        Calcula horário estimado considerando atrasos.
        
        Args:
            schedule: Horário programado
            real_time_data: Dados em tempo real
            
        Returns:
            Horário estimado formatado
        """
        scheduled_datetime = datetime.combine(
            timezone.now().date(), 
            schedule.departure_time
        )
        
        if real_time_data and real_time_data.get('delay_minutes'):
            estimated_datetime = scheduled_datetime + timedelta(
                minutes=real_time_data['delay_minutes']
            )
        else:
            estimated_datetime = scheduled_datetime
        
        return estimated_datetime.strftime('%H:%M')


class RealTimeService:
    """
    Serviço para dados em tempo real e previsões.
    """
    
    CACHE_TIMEOUT = 30  # 30 segundos para dados em tempo real
    
    @classmethod
    def get_live_updates(cls, route_number: str = None) -> List[Dict]:
        """
        Obtém atualizações em tempo real das rotas.
        
        Args:
            route_number: Filtrar por rota específica
            
        Returns:
            Lista com atualizações recentes
        """
        cache_key = f'live_updates_{route_number or "all"}'
        updates = cache.get(cache_key)
        
        if not updates:
            queryset = RealTimeUpdate.objects.select_related('route').filter(
                created_at__gte=timezone.now() - timedelta(minutes=15)
            ).order_by('-created_at')
            
            if route_number:
                queryset = queryset.filter(route__number=route_number)
            
            updates = []
            for update in queryset[:50]:  # Limitar para performance
                updates.append({
                    'id': str(update.id),
                    'route_number': update.route.number,
                    'route_name': update.route.name,
                    'direction': update.direction,
                    'delay_minutes': update.delay_minutes,
                    'vehicle_position': update.vehicle_position,
                    'passenger_load': update.passenger_load,
                    'confidence_level': update.confidence_level,
                    'updated_at': update.created_at.isoformat(),
                })
            
            cache.set(cache_key, updates, cls.CACHE_TIMEOUT)
            logger.debug(f'Live updates cached: {len(updates)} updates')
        
        return updates
    
    @classmethod
    def create_update(cls, route_id: str, direction: str, 
                     delay_minutes: int, **kwargs) -> RealTimeUpdate:
        """
        Cria nova atualização em tempo real.
        
        Args:
            route_id: ID da rota
            direction: Direção
            delay_minutes: Atraso em minutos
            **kwargs: Dados adicionais
            
        Returns:
            Instância da atualização criada
        """
        try:
            route = BusRoute.objects.get(id=route_id, is_active=True)
            
            update = RealTimeUpdate.objects.create(
                route=route,
                direction=direction,
                delay_minutes=delay_minutes,
                vehicle_position=kwargs.get('vehicle_position'),
                passenger_load=kwargs.get('passenger_load', 'unknown'),
                confidence_level=kwargs.get('confidence_level', 'medium'),
                data_source=kwargs.get('data_source', 'system'),
            )
            
            # Invalidar cache relacionado
            cache_keys = [
                f'live_updates_{route.number}',
                f'live_updates_all',
                f'next_departures_{route.number}_*',
            ]
            
            for pattern in cache_keys:
                if '*' in pattern:
                    # Invalidar múltiplas chaves (implementação simplificada)
                    continue
                cache.delete(pattern)
            
            logger.info(f'Real-time update created for route {route.number}')
            return update
            
        except BusRoute.DoesNotExist:
            logger.error(f'Route {route_id} not found for real-time update')
            raise
        except Exception as e:
            logger.error(f'Error creating real-time update: {e}')
            raise


class ServiceAlertService:
    """
    Serviço para alertas de serviço e interrupções.
    """
    
    CACHE_TIMEOUT = 900  # 15 minutos para alertas
    
    @classmethod
    def get_active_alerts(cls, route_number: str = None, 
                         alert_type: str = None) -> List[Dict]:
        """
        Obtém alertas ativos do sistema.
        
        Args:
            route_number: Filtrar por rota específica
            alert_type: Filtrar por tipo de alerta
            
        Returns:
            Lista com alertas ativos
        """
        cache_key = f'active_alerts_{route_number}_{alert_type}'
        alerts = cache.get(cache_key)
        
        if not alerts:
            queryset = ServiceAlert.objects.filter(
                is_active=True,
                start_time__lte=timezone.now()
            ).filter(
                Q(end_time__isnull=True) | Q(end_time__gte=timezone.now())
            ).select_related('route').order_by('-priority', '-created_at')
            
            if route_number:
                queryset = queryset.filter(route__number=route_number)
                
            if alert_type:
                queryset = queryset.filter(alert_type=alert_type)
            
            alerts = []
            for alert in queryset:
                alerts.append({
                    'id': str(alert.id),
                    'title': alert.title,
                    'message': alert.message,
                    'alert_type': alert.alert_type,
                    'priority': alert.priority,
                    'route_number': alert.route.number if alert.route else None,
                    'route_name': alert.route.name if alert.route else None,
                    'affected_directions': alert.affected_directions,
                    'start_time': alert.start_time.isoformat(),
                    'end_time': alert.end_time.isoformat() if alert.end_time else None,
                    'created_at': alert.created_at.isoformat(),
                })
            
            cache.set(cache_key, alerts, cls.CACHE_TIMEOUT)
            logger.debug(f'Active alerts cached: {len(alerts)} alerts')
        
        return alerts
    
    @classmethod
    def create_alert(cls, title: str, message: str, alert_type: str,
                    route_id: str = None, **kwargs) -> ServiceAlert:
        """
        Cria novo alerta de serviço.
        
        Args:
            title: Título do alerta
            message: Mensagem do alerta
            alert_type: Tipo do alerta
            route_id: ID da rota afetada (opcional)
            **kwargs: Dados adicionais
            
        Returns:
            Instância do alerta criado
        """
        try:
            route = None
            if route_id:
                route = BusRoute.objects.get(id=route_id, is_active=True)
            
            alert = ServiceAlert.objects.create(
                title=title,
                message=message,
                alert_type=alert_type,
                route=route,
                priority=kwargs.get('priority', 'medium'),
                affected_directions=kwargs.get('affected_directions', []),
                start_time=kwargs.get('start_time', timezone.now()),
                end_time=kwargs.get('end_time'),
                data_source=kwargs.get('data_source', 'system'),
            )
            
            # Invalidar cache de alertas
            cache.delete(f'active_alerts_{route.number if route else None}_None')
            cache.delete('active_alerts_None_None')
            
            logger.info(f'Service alert created: {title}')
            return alert
            
        except Exception as e:
            logger.error(f'Error creating service alert: {e}')
            raise


class ScheduleStatisticsService:
    """
    Serviço para estatísticas e analytics de horários.
    """
    
    @staticmethod
    def get_schedule_statistics() -> Dict:
        """
        Calcula estatísticas gerais do sistema de horários.
        
        Returns:
            Dicionário com estatísticas consolidadas
        """
        cache_key = 'schedule_statistics'
        stats = cache.get(cache_key)
        
        if not stats:
            total_schedules = ScheduleEntry.objects.filter(is_active=True).count()
            routes_with_schedules = ScheduleEntry.objects.filter(
                is_active=True
            ).values('route').distinct().count()
            
            active_alerts = ServiceAlert.objects.filter(
                is_active=True,
                start_time__lte=timezone.now()
            ).filter(
                Q(end_time__isnull=True) | Q(end_time__gte=timezone.now())
            ).count()
            
            recent_updates = RealTimeUpdate.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            # Calcular atraso médio
            avg_delay = RealTimeUpdate.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).aggregate(Avg('delay_minutes'))['delay_minutes__avg'] or 0
            
            stats = {
                'total_schedules': total_schedules,
                'routes_with_schedules': routes_with_schedules,
                'active_alerts': active_alerts,
                'recent_updates': recent_updates,
                'average_delay_minutes': round(avg_delay, 1),
                'system_status': cls._determine_system_status(avg_delay, active_alerts),
                'updated_at': timezone.now().isoformat()
            }
            
            cache.set(cache_key, stats, 300)  # Cache por 5 minutos
            logger.info('Schedule statistics calculated and cached')
        
        return stats
    
    @staticmethod
    def _determine_system_status(avg_delay: float, active_alerts: int) -> str:
        """
        Determina status geral do sistema baseado em métricas.
        
        Args:
            avg_delay: Atraso médio em minutos
            active_alerts: Número de alertas ativos
            
        Returns:
            Status do sistema (good, warning, critical)
        """
        if active_alerts > 5 or avg_delay > 15:
            return 'critical'
        elif active_alerts > 2 or avg_delay > 8:
            return 'warning'
        else:
            return 'good'
    
    @staticmethod
    def get_punctuality_report(route_number: str = None, 
                              days: int = 7) -> Dict:
        """
        Gera relatório de pontualidade das rotas.
        
        Args:
            route_number: Rota específica (opcional)
            days: Número de dias para análise
            
        Returns:
            Relatório de pontualidade
        """
        cache_key = f'punctuality_report_{route_number}_{days}'
        report = cache.get(cache_key)
        
        if not report:
            since_date = timezone.now() - timedelta(days=days)
            
            queryset = RealTimeUpdate.objects.filter(
                created_at__gte=since_date
            ).select_related('route')
            
            if route_number:
                queryset = queryset.filter(route__number=route_number)
            
            # Análise por rota
            route_analysis = {}
            for update in queryset:
                route_num = update.route.number
                
                if route_num not in route_analysis:
                    route_analysis[route_num] = {
                        'route_name': update.route.name,
                        'total_updates': 0,
                        'on_time': 0,
                        'delays': [],
                        'avg_delay': 0,
                    }
                
                analysis = route_analysis[route_num]
                analysis['total_updates'] += 1
                analysis['delays'].append(update.delay_minutes)
                
                if abs(update.delay_minutes) <= 2:  # Considerado pontual
                    analysis['on_time'] += 1
            
            # Calcular métricas finais
            for route_num, analysis in route_analysis.items():
                if analysis['delays']:
                    analysis['avg_delay'] = round(
                        sum(analysis['delays']) / len(analysis['delays']), 1
                    )
                    analysis['punctuality_rate'] = round(
                        (analysis['on_time'] / analysis['total_updates']) * 100, 1
                    )
                
                # Remover lista de atrasos (não precisamos mais)
                del analysis['delays']
            
            report = {
                'period_days': days,
                'routes': route_analysis,
                'summary': {
                    'total_routes_analyzed': len(route_analysis),
                    'total_updates': sum(r['total_updates'] for r in route_analysis.values()),
                    'overall_punctuality': round(
                        sum(r['on_time'] for r in route_analysis.values()) / 
                        max(sum(r['total_updates'] for r in route_analysis.values()), 1) * 100, 1
                    ) if route_analysis else 0,
                },
                'generated_at': timezone.now().isoformat()
            }
            
            cache.set(cache_key, report, 1800)  # Cache por 30 minutos
            logger.info('Punctuality report generated and cached')
        
        return report 
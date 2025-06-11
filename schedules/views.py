"""
Views do app schedules - Gerenciamento de horários do BusFeed.

Handles para funcionalidades relacionadas aos horários dos ônibus.
"""

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.utils import timezone
from .models import Schedule, SpecialSchedule
from routes.models import BusRoute
from datetime import datetime, timedelta


class ScheduleListView(ListView):
    """
    View para listar horários disponíveis com busca e filtros.
    """
    model = Schedule
    template_name = 'schedules/list.html'
    context_object_name = 'schedules'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Retorna queryset filtrado e otimizado.
        """
        queryset = Schedule.objects.select_related(
            'route__route_type', 
            'route__transport_company'
        ).filter(is_active=True)
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(route__number__icontains=search) |
                Q(route__name__icontains=search) |
                Q(route__origin_terminal__icontains=search) |
                Q(route__destination_terminal__icontains=search)
            )
        
        # Filtro por tipo de dia
        day_type = self.request.GET.get('day_type')
        if day_type:
            queryset = queryset.filter(day_type=day_type)
        
        # Filtro por direção
        direction = self.request.GET.get('direction')
        if direction:
            queryset = queryset.filter(direction=direction)
        
        # Filtro por rota
        route_number = self.request.GET.get('route')
        if route_number:
            queryset = queryset.filter(route__number__icontains=route_number)
        
        return queryset.order_by('route__number', 'day_type', 'direction', 'start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Opções para filtros
        day_types = Schedule.DAY_TYPE_CHOICES
        directions = Schedule.DIRECTION_CHOICES
        
        # Rotas disponíveis
        routes = BusRoute.objects.filter(
            is_active=True,
            schedules__isnull=False
        ).distinct().order_by('number')
        
        context.update({
            'title': 'Horários de Ônibus',
            'description': 'Consulte os horários dos ônibus do Distrito Federal',
            'day_types': day_types,
            'directions': directions,
            'routes': routes,
            'search_term': self.request.GET.get('search', ''),
            'selected_day_type': self.request.GET.get('day_type', ''),
            'selected_direction': self.request.GET.get('direction', ''),
            'selected_route': self.request.GET.get('route', ''),
            'current_time': timezone.now(),
        })
        return context


class RouteScheduleView(TemplateView):
    """
    View para mostrar horários detalhados de uma linha específica.
    """
    template_name = 'schedules/route_schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_id = kwargs.get('route_id')
        
        # Buscar rota
        route = get_object_or_404(BusRoute, id=route_id, is_active=True)
        
        # Horários organizados por tipo de dia e direção
        schedules = Schedule.objects.filter(
            route=route,
            is_active=True
        ).order_by('day_type', 'direction', 'start_time')
        
        # Organizar horários em estrutura aninhada
        organized_schedules = {}
        for schedule in schedules:
            day_type = schedule.get_day_type_display()
            direction = schedule.get_direction_display()
            
            if day_type not in organized_schedules:
                organized_schedules[day_type] = {}
            
            if direction not in organized_schedules[day_type]:
                organized_schedules[day_type][direction] = []
            
            # Adicionar próximas partidas
            next_departures = schedule.get_next_departures(10)
            schedule.next_departures = next_departures
            schedule.is_operational = schedule.is_operational_now()
            
            organized_schedules[day_type][direction].append(schedule)
        
        # Horários especiais
        today = timezone.now().date()
        special_schedules = SpecialSchedule.objects.filter(
            route=route,
            date__gte=today
        ).order_by('date')
        
        context.update({
            'title': f'Horários da Linha {route.number}',
            'route': route,
            'organized_schedules': organized_schedules,
            'special_schedules': special_schedules,
            'current_time': timezone.now(),
        })
        return context


def route_schedule_api(request, route_number):
    """
    API para obter horários de uma rota específica.
    """
    try:
        route = get_object_or_404(BusRoute, number=route_number, is_active=True)
        
        # Pegar tipo de dia atual
        now = timezone.now()
        current_weekday = now.weekday()
        
        if current_weekday < 5:  # Segunda a sexta
            day_type = Schedule.WEEKDAY
        elif current_weekday == 5:  # Sábado
            day_type = Schedule.SATURDAY
        else:  # Domingo
            day_type = Schedule.SUNDAY
        
        # Buscar horários do dia atual
        schedules = Schedule.objects.filter(
            route=route,
            day_type=day_type,
            is_active=True
        ).order_by('direction', 'start_time')
        
        # Verificar horários especiais para hoje
        special_schedule = SpecialSchedule.objects.filter(
            route=route,
            date=now.date()
        ).first()
        
        schedules_data = []
        for schedule in schedules:
            # Se há horário especial, usar ele
            if special_schedule:
                if special_schedule.is_suspended:
                    continue
                    
                schedule_info = {
                    'id': schedule.id,
                    'direction': schedule.get_direction_display(),
                    'start_time': special_schedule.start_time.strftime('%H:%M') if special_schedule.start_time else 'N/A',
                    'end_time': special_schedule.end_time.strftime('%H:%M') if special_schedule.end_time else 'N/A',
                    'frequency': special_schedule.frequency_minutes or schedule.frequency_minutes,
                    'next_departures': [],
                    'is_operational': False,
                    'is_special': True,
                    'special_description': special_schedule.description
                }
            else:
                schedule_info = {
                    'id': schedule.id,
                    'direction': schedule.get_direction_display(),
                    'start_time': schedule.start_time.strftime('%H:%M'),
                    'end_time': schedule.end_time.strftime('%H:%M'),
                    'frequency': schedule.get_current_frequency(),
                    'next_departures': [t.strftime('%H:%M') for t in schedule.get_next_departures()],
                    'is_operational': schedule.is_operational_now(),
                    'is_special': False,
                    'peak_frequency': schedule.peak_frequency_minutes,
                    'peak_start': schedule.peak_start_time.strftime('%H:%M') if schedule.peak_start_time else None,
                    'peak_end': schedule.peak_end_time.strftime('%H:%M') if schedule.peak_end_time else None,
                    'notes': schedule.notes
                }
            
            schedules_data.append(schedule_info)
        
        return JsonResponse({
            'success': True,
            'route': {
                'number': route.number,
                'name': route.name,
                'full_name': route.get_full_name()
            },
            'day_type': day_type,
            'day_type_display': dict(Schedule.DAY_TYPE_CHOICES)[day_type],
            'schedules': schedules_data,
            'current_time': now.strftime('%H:%M'),
            'has_special_schedule': special_schedule is not None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def schedules_by_stop_api(request, stop_code):
    """
    API para obter horários de todas as rotas que passam em uma parada.
    """
    try:
        from stops.models import BusStop
        
        stop = get_object_or_404(BusStop, code=stop_code, is_active=True)
        
        # Buscar todas as rotas que passam na parada
        route_stops = stop.route_stops.select_related('route').all()
        
        routes_schedules = []
        for route_stop in route_stops:
            route = route_stop.route
            
            # Pegar horários da rota na direção específica
            schedules = Schedule.objects.filter(
                route=route,
                direction=route_stop.direction,
                is_active=True
            ).order_by('day_type', 'start_time')
            
            if schedules.exists():
                route_data = {
                    'route': {
                        'number': route.number,
                        'name': route.name,
                        'direction': route_stop.get_direction_display(),
                        'sequence': route_stop.sequence,
                        'estimated_time_from_origin': route_stop.estimated_time_from_origin
                    },
                    'schedules': []
                }
                
                for schedule in schedules:
                    route_data['schedules'].append({
                        'day_type': schedule.get_day_type_display(),
                        'start_time': schedule.start_time.strftime('%H:%M'),
                        'end_time': schedule.end_time.strftime('%H:%M'),
                        'frequency': schedule.get_current_frequency(),
                        'next_departures': [t.strftime('%H:%M') for t in schedule.get_next_departures()],
                        'is_operational': schedule.is_operational_now()
                    })
                
                routes_schedules.append(route_data)
        
        return JsonResponse({
            'success': True,
            'stop': {
                'code': stop.code,
                'name': stop.name
            },
            'routes': routes_schedules,
            'current_time': timezone.now().strftime('%H:%M')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

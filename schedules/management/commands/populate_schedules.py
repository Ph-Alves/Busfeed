"""
Comando para popular dados de horários de exemplo do BusFeed.
Execução: python manage.py populate_schedules
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from schedules.models import Schedule, SpecialSchedule
from routes.models import BusRoute
from datetime import time, date, timedelta


class Command(BaseCommand):
    help = 'Popula dados de horários de exemplo para as rotas do BusFeed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os horários existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Removendo horários existentes...')
            Schedule.objects.all().delete()
            SpecialSchedule.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Horários removidos'))

        self.stdout.write('🕒 Criando horários de exemplo...')
        
        # Buscar todas as rotas ativas
        routes = BusRoute.objects.filter(is_active=True)
        
        if not routes.exists():
            self.stdout.write(
                self.style.ERROR('❌ Nenhuma rota encontrada. Execute primeiro: python populate_data.py')
            )
            return

        created_count = 0
        special_count = 0

        for route in routes:
            created_count += self.create_route_schedules(route)
            special_count += self.create_special_schedules(route)

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Criados {created_count} horários e {special_count} horários especiais!'
            )
        )

    def create_route_schedules(self, route):
        """Cria horários padrão para uma rota"""
        created = 0
        
        # Horários base para diferentes tipos de linha
        schedules_config = [
            # Dias úteis
            {
                'day_type': Schedule.WEEKDAY,
                'direction': Schedule.IDA,
                'start_time': time(5, 30),
                'end_time': time(23, 30),
                'frequency': 15,
                'peak_frequency': 8,
                'peak_start': time(6, 30),
                'peak_end': time(9, 0),
            },
            {
                'day_type': Schedule.WEEKDAY,
                'direction': Schedule.VOLTA,
                'start_time': time(5, 45),
                'end_time': time(23, 45),
                'frequency': 15,
                'peak_frequency': 8,
                'peak_start': time(17, 30),
                'peak_end': time(20, 0),
            },
            
            # Sábados
            {
                'day_type': Schedule.SATURDAY,
                'direction': Schedule.IDA,
                'start_time': time(6, 0),
                'end_time': time(23, 0),
                'frequency': 20,
                'peak_frequency': None,
                'peak_start': None,
                'peak_end': None,
            },
            {
                'day_type': Schedule.SATURDAY,
                'direction': Schedule.VOLTA,
                'start_time': time(6, 15),
                'end_time': time(23, 15),
                'frequency': 20,
                'peak_frequency': None,
                'peak_start': None,
                'peak_end': None,
            },
            
            # Domingos
            {
                'day_type': Schedule.SUNDAY,
                'direction': Schedule.IDA,
                'start_time': time(7, 0),
                'end_time': time(22, 0),
                'frequency': 30,
                'peak_frequency': None,
                'peak_start': None,
                'peak_end': None,
            },
            {
                'day_type': Schedule.SUNDAY,
                'direction': Schedule.VOLTA,
                'start_time': time(7, 15),
                'end_time': time(22, 15),
                'frequency': 30,
                'peak_frequency': None,
                'peak_start': None,
                'peak_end': None,
            },
        ]

        for config in schedules_config:
            schedule, created_schedule = Schedule.objects.get_or_create(
                route=route,
                day_type=config['day_type'],
                direction=config['direction'],
                start_time=config['start_time'],
                end_time=config['end_time'],
                defaults={
                    'frequency_minutes': config['frequency'],
                    'peak_frequency_minutes': config['peak_frequency'],
                    'peak_start_time': config['peak_start'],
                    'peak_end_time': config['peak_end'],
                    'is_active': True,
                    'notes': f'Horário padrão para {route.get_full_name()}'
                }
            )
            
            if created_schedule:
                created += 1
                self.stdout.write(
                    f'  ✓ {route.number} - {schedule.get_day_type_display()} - {schedule.get_direction_display()}'
                )

        return created

    def create_special_schedules(self, route):
        """Cria alguns horários especiais de exemplo"""
        created = 0
        today = timezone.now().date()
        
        # Horários especiais para feriados próximos
        special_dates = [
            {
                'date': today + timedelta(days=30),  # Próximo mês
                'description': 'Natal',
                'start_time': time(8, 0),
                'end_time': time(18, 0),
                'frequency': 60,
                'is_suspended': False,
            },
            {
                'date': today + timedelta(days=37),  # Próximo mês + 7 dias
                'description': 'Ano Novo',
                'start_time': None,
                'end_time': None,
                'frequency': None,
                'is_suspended': True,
            },
        ]

        for special_config in special_dates:
            for direction in [Schedule.IDA, Schedule.VOLTA]:
                special_schedule, created_special = SpecialSchedule.objects.get_or_create(
                    route=route,
                    date=special_config['date'],
                    direction=direction,
                    defaults={
                        'description': special_config['description'],
                        'start_time': special_config['start_time'],
                        'end_time': special_config['end_time'],
                        'frequency_minutes': special_config['frequency'],
                        'is_suspended': special_config['is_suspended'],
                    }
                )
                
                if created_special:
                    created += 1

        return created 
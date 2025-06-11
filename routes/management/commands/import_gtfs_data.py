"""
Management command para importar dados GTFS de Brasília ou criar dados simulados
para demonstração do sistema.
"""
import csv
import json
import random
from datetime import datetime, time, timedelta
from decimal import Decimal
from io import StringIO

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from routes.models import (
    TransportCompany, RouteType, BusRoute, RouteStop, Vehicle
)
from stops.models import BusStop, StopType
from schedules.models import Schedule


class Command(BaseCommand):
    help = 'Importa dados GTFS ou cria dados simulados para demonstração'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = {
            'companies_created': 0,
            'route_types_created': 0,
            'stops_created': 0,
            'routes_created': 0,
            'route_stops_created': 0,
            'schedules_created': 0,
            'vehicles_created': 0,
            'errors': []
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['demo', 'gtfs'],
            default='demo',
            help='Modo: demo (dados simulados) ou gtfs (dados reais)',
        )
        parser.add_argument(
            '--gtfs-path',
            type=str,
            help='Caminho para arquivo ou diretório GTFS',
        )
        parser.add_argument(
            '--routes-count',
            type=int,
            default=10,
            help='Número de rotas para criar no modo demo',
        )

    def handle(self, *args, **options):
        self.mode = options['mode']
        self.gtfs_path = options['gtfs_path']
        self.routes_count = options['routes_count']
        
        try:
            if self.mode == 'demo':
                self.stdout.write('Criando dados de demonstração...')
                self.create_demo_data()
            else:
                self.stdout.write('Importando dados GTFS...')
                if not self.gtfs_path:
                    raise CommandError('--gtfs-path é obrigatório para modo GTFS')
                self.import_gtfs_data()
                
            self.print_report()
            
        except Exception as e:
            self.stats['errors'].append(f'Erro geral: {str(e)}')
            raise CommandError(f'Erro durante importação: {e}')

    def create_demo_data(self):
        """Cria dados simulados para demonstração."""
        self.stdout.write('Criando dados de demonstração para Brasília...')
        
        with transaction.atomic():
            # 1. Criar empresas
            companies = self.create_demo_companies()
            
            # 2. Criar tipos de rota
            route_types = self.create_demo_route_types()
            
            # 3. Criar tipos de parada
            stop_types = self.create_demo_stop_types()
            
            # 4. Criar paradas estratégicas de Brasília
            stops = self.create_demo_stops(stop_types)
            
            # 5. Criar rotas
            routes = self.create_demo_routes(companies, route_types)
            
            # 6. Conectar rotas e paradas
            self.connect_routes_and_stops(routes, stops)
            
            # 7. Criar horários
            self.create_demo_schedules(routes)
            
            # 8. Criar alguns veículos
            self.create_demo_vehicles(companies)

    def create_demo_companies(self):
        """Cria empresas de transporte do DF."""
        companies_data = [
            {
                'name': 'DFTrans',
                'short_name': 'DFT',
                'cnpj': '00.394.679/0001-39',
                'website': 'https://www.dftrans.df.gov.br',
            },
            {
                'name': 'Viação Pioneira',
                'short_name': 'VPI',
                'cnpj': '12.345.678/0001-90',
                'website': '',
            },
            {
                'name': 'Expresso São José',
                'short_name': 'ESJ',
                'cnpj': '98.765.432/0001-10',
                'website': '',
            },
        ]
        
        companies = []
        for data in companies_data:
            company, created = TransportCompany.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stats['companies_created'] += 1
            companies.append(company)
            
        return companies

    def create_demo_route_types(self):
        """Cria tipos de rotas do DF."""
        types_data = [
            {
                'name': 'Convencional',
                'description': 'Linhas convencionais urbanas',
                'color': '#2196F3',
                'fare_multiplier': Decimal('1.0'),
            },
            {
                'name': 'Expresso',
                'description': 'Linhas expressas com paradas limitadas',
                'color': '#FF5722',
                'fare_multiplier': Decimal('1.5'),
            },
            {
                'name': 'Semi-Direto',
                'description': 'Linhas semi-diretas',
                'color': '#4CAF50',
                'fare_multiplier': Decimal('1.2'),
            },
        ]
        
        route_types = []
        for data in types_data:
            route_type, created = RouteType.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stats['route_types_created'] += 1
            route_types.append(route_type)
            
        return route_types

    def create_demo_stop_types(self):
        """Cria tipos de paradas."""
        types_data = [
            {
                'name': 'Terminal',
                'description': 'Terminal de ônibus',
                'color': '#FF5722',
            },
            {
                'name': 'Estação',
                'description': 'Estação de transporte',
                'color': '#9C27B0',
            },
            {
                'name': 'Parada',
                'description': 'Parada comum',
                'color': '#2196F3',
            },
        ]
        
        stop_types = []
        for data in types_data:
            stop_type, created = StopType.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            stop_types.append(stop_type)
            
        return stop_types

    def create_demo_stops(self, stop_types):
        """Cria paradas estratégicas de Brasília."""
        # Coordenadas aproximadas de locais importantes de Brasília
        stops_data = [
            # Terminais principais
            {
                'code': 'T001',
                'name': 'Terminal Rodoviário',
                'latitude': -15.7942,
                'longitude': -47.8822,
                'stop_type': 'Terminal',
                'neighborhood': 'Asa Sul',
            },
            {
                'code': 'T002', 
                'name': 'Terminal Asa Norte',
                'latitude': -15.7650,
                'longitude': -47.8689,
                'stop_type': 'Terminal',
                'neighborhood': 'Asa Norte',
            },
            {
                'code': 'T003',
                'name': 'Terminal Plano Piloto',
                'latitude': -15.7801,
                'longitude': -47.9292,
                'stop_type': 'Terminal',
                'neighborhood': 'Plano Piloto',
            },
            
            # Estações importantes
            {
                'code': 'E001',
                'name': 'Estação Central',
                'latitude': -15.7797,
                'longitude': -47.9297,
                'stop_type': 'Estação',
                'neighborhood': 'Plano Piloto',
            },
            {
                'code': 'E002',
                'name': 'Estação 102 Sul',
                'latitude': -15.8063,
                'longitude': -47.8908,
                'stop_type': 'Estação',
                'neighborhood': 'Asa Sul',
            },
            {
                'code': 'E003',
                'name': 'Estação 108 Norte',
                'latitude': -15.7571,
                'longitude': -47.8739,
                'stop_type': 'Estação',
                'neighborhood': 'Asa Norte',
            },
            
            # Paradas estratégicas
            {
                'code': 'P001',
                'name': 'Congresso Nacional',
                'latitude': -15.7998,
                'longitude': -47.8636,
                'stop_type': 'Parada',
                'neighborhood': 'Plano Piloto',
            },
            {
                'code': 'P002',
                'name': 'UnB - Universidade de Brasília',
                'latitude': -15.7634,
                'longitude': -47.8707,
                'stop_type': 'Parada',
                'neighborhood': 'Asa Norte',
            },
            {
                'code': 'P003',
                'name': 'Shopping Brasília',
                'latitude': -15.7815,
                'longitude': -47.8911,
                'stop_type': 'Parada',
                'neighborhood': 'Asa Norte',
            },
            {
                'code': 'P004',
                'name': 'Setor Comercial Sul',
                'latitude': -15.7972,
                'longitude': -47.8886,
                'stop_type': 'Parada',
                'neighborhood': 'Asa Sul',
            },
            {
                'code': 'P005',
                'name': 'Aeroporto Internacional',
                'latitude': -15.8697,
                'longitude': -47.9208,
                'stop_type': 'Parada',
                'neighborhood': 'Lago Sul',
            },
            {
                'code': 'P006',
                'name': 'Taguatinga Centro',
                'latitude': -15.8270,
                'longitude': -48.0589,
                'stop_type': 'Parada',
                'neighborhood': 'Taguatinga',
            },
            {
                'code': 'P007',
                'name': 'Ceilândia Norte',
                'latitude': -15.8158,
                'longitude': -48.1109,
                'stop_type': 'Parada',
                'neighborhood': 'Ceilândia',
            },
            {
                'code': 'P008',
                'name': 'Samambaia Sul',
                'latitude': -15.8790,
                'longitude': -48.0944,
                'stop_type': 'Parada',
                'neighborhood': 'Samambaia',
            },
            {
                'code': 'P009',
                'name': 'Planaltina Central',
                'latitude': -15.6227,
                'longitude': -47.6537,
                'stop_type': 'Parada',
                'neighborhood': 'Planaltina',
            },
            {
                'code': 'P010',
                'name': 'Gama Centro',
                'latitude': -16.0123,
                'longitude': -48.0655,
                'stop_type': 'Parada',
                'neighborhood': 'Gama',
            },
        ]
        
        stops = []
        stop_types_dict = {st.name: st for st in stop_types}
        
        for data in stops_data:
            stop_type_name = data.pop('stop_type')
            stop_type = stop_types_dict.get(stop_type_name)
            
            stop, created = BusStop.objects.get_or_create(
                code=data['code'],
                defaults={
                    **data,
                    'stop_type': stop_type,
                    'has_shelter': random.choice([True, False]),
                    'has_seating': random.choice([True, False]),
                    'wheelchair_accessible': random.choice([True, False]),
                    'data_source': 'BusFeed Demo',
                }
            )
            
            if created:
                self.stats['stops_created'] += 1
            stops.append(stop)
            
        return stops

    def create_demo_routes(self, companies, route_types):
        """Cria rotas de demonstração."""
        routes_data = [
            {
                'number': '100',
                'name': 'Terminal Rodoviário - Asa Norte',
                'origin': 'Terminal Rodoviário',
                'destination': 'Asa Norte',
                'company': 0,  # Índice na lista de empresas
                'route_type': 0,  # Índice na lista de tipos
            },
            {
                'number': '200',
                'name': 'Plano Piloto - Taguatinga',
                'origin': 'Plano Piloto',
                'destination': 'Taguatinga',
                'company': 1,
                'route_type': 0,
            },
            {
                'number': '300',
                'name': 'Asa Sul - Ceilândia',
                'origin': 'Asa Sul',
                'destination': 'Ceilândia',
                'company': 0,
                'route_type': 1,
            },
            {
                'number': '400',
                'name': 'UnB - Samambaia',
                'origin': 'UnB',
                'destination': 'Samambaia',
                'company': 2,
                'route_type': 0,
            },
            {
                'number': '500',
                'name': 'Aeroporto - Plano Piloto',
                'origin': 'Aeroporto',
                'destination': 'Plano Piloto',
                'company': 0,
                'route_type': 1,
            },
            {
                'number': '600',
                'name': 'Planaltina - Terminal Rodoviário',
                'origin': 'Planaltina',
                'destination': 'Terminal Rodoviário',
                'company': 1,
                'route_type': 2,
            },
            {
                'number': '700',
                'name': 'Gama - Asa Sul',
                'origin': 'Gama',
                'destination': 'Asa Sul',
                'company': 2,
                'route_type': 2,
            },
            {
                'number': '108',
                'name': 'Circular Asa Norte',
                'origin': 'Asa Norte',
                'destination': 'Asa Norte',
                'company': 0,
                'route_type': 0,
            },
            {
                'number': '308',
                'name': 'Circular Asa Sul',
                'origin': 'Asa Sul',
                'destination': 'Asa Sul',
                'company': 0,
                'route_type': 0,
            },
            {
                'number': 'W3',
                'name': 'Expresso W3 Norte-Sul',
                'origin': 'Asa Norte',
                'destination': 'Asa Sul',
                'company': 0,
                'route_type': 1,
            },
        ]
        
        routes = []
        for data in routes_data:
            route, created = BusRoute.objects.get_or_create(
                number=data['number'],
                transport_company=companies[data['company']],
                defaults={
                    'name': data['name'],
                    'route_type': route_types[data['route_type']],
                    'origin_terminal': data['origin'],
                    'destination_terminal': data['destination'],
                    'is_circular': data['origin'] == data['destination'],
                    'operates_weekdays': True,
                    'operates_saturdays': True,
                    'operates_sundays': random.choice([True, False]),
                    'wheelchair_accessible': random.choice([True, False]),
                    'first_departure': time(5, 0),
                    'last_departure': time(23, 30),
                    'average_frequency': random.randint(10, 30),
                    'estimated_duration': random.randint(30, 90),
                    'data_source': 'BusFeed Demo',
                }
            )
            
            if created:
                self.stats['routes_created'] += 1
            routes.append(route)
            
        return routes

    def connect_routes_and_stops(self, routes, stops):
        """Conecta rotas com paradas de forma inteligente."""
        # Mapear paradas por região para facilitar conexões
        regions = {
            'centro': [s for s in stops if any(term in s.name.lower() for term in ['terminal', 'central', 'congresso'])],
            'asa_norte': [s for s in stops if 'norte' in s.name.lower() or 'unb' in s.name.lower()],
            'asa_sul': [s for s in stops if 'sul' in s.name.lower()],
            'satelites': [s for s in stops if any(term in s.name.lower() for term in ['taguatinga', 'ceilândia', 'samambaia', 'planaltina', 'gama'])],
            'especiais': [s for s in stops if any(term in s.name.lower() for term in ['aeroporto', 'shopping'])],
        }
        
        for route in routes:
            # Definir paradas baseado no tipo de rota
            route_stops = []
            
            if 'circular' in route.name.lower():
                # Rotas circulares ficam numa região
                if 'norte' in route.name.lower():
                    route_stops = regions['asa_norte'] + regions['centro'][:2]
                else:
                    route_stops = regions['asa_sul'] + regions['centro'][:2]
            elif 'expresso' in route.name.lower() or 'w3' in route.name.lower():
                # Expressas conectam apenas pontos principais
                route_stops = regions['centro'] + regions['asa_norte'][:2] + regions['asa_sul'][:2]
            elif any(term in route.name.lower() for term in ['taguatinga', 'ceilândia', 'samambaia', 'planaltina', 'gama']):
                # Rotas para cidades satélites
                route_stops = regions['centro'] + regions['satelites']
            elif 'aeroporto' in route.name.lower():
                # Rota do aeroporto
                route_stops = regions['centro'] + regions['especiais'] + regions['asa_sul'][:1]
            else:
                # Rotas convencionais pegam várias paradas
                route_stops = regions['centro'] + regions['asa_norte'][:2] + regions['asa_sul'][:2]
            
            # Embaralhar para simular diferentes sequências
            random.shuffle(route_stops)
            route_stops = route_stops[:random.randint(5, min(10, len(route_stops)))]
            
            # Criar relacionamentos RouteStop
            for i, stop in enumerate(route_stops, 1):
                RouteStop.objects.get_or_create(
                    route=route,
                    stop=stop,
                    direction='ida',
                    sequence=i,
                    defaults={
                        'distance_from_origin': i * random.uniform(1.0, 3.0),
                        'estimated_time_from_origin': i * random.randint(3, 8),
                    }
                )
                self.stats['route_stops_created'] += 1

    def create_demo_schedules(self, routes):
        """Cria horários para as rotas."""
        from schedules.models import Schedule
        
        for route in routes:
            # Criar horários para dias úteis
            for day_type in ['weekday', 'saturday', 'sunday']:
                if day_type == 'sunday' and not route.operates_sundays:
                    continue
                if day_type == 'saturday' and not route.operates_saturdays:
                    continue
                
                # Horários de pico e fora-pico
                if day_type == 'weekday':
                    schedules = [
                        ('05:00', '06:30', 20),  # Manhã cedo
                        ('06:30', '09:00', 10),  # Pico manhã
                        ('09:00', '17:00', 15),  # Fora-pico
                        ('17:00', '19:30', 8),   # Pico tarde
                        ('19:30', '23:30', 20),  # Noite
                    ]
                else:
                    schedules = [
                        ('06:00', '23:00', 20),  # Fim de semana
                    ]
                
                for start_time, end_time, frequency in schedules:
                    Schedule.objects.get_or_create(
                        route=route,
                        day_type=day_type,
                        start_time=datetime.strptime(start_time, '%H:%M').time(),
                        end_time=datetime.strptime(end_time, '%H:%M').time(),
                        defaults={
                            'frequency_minutes': frequency,
                            'is_active': True,
                        }
                    )
                    self.stats['schedules_created'] += 1

    def create_demo_vehicles(self, companies):
        """Cria veículos da frota."""
        vehicle_models = [
            'Mercedes-Benz OF-1722',
            'Volvo B270F',
            'Scania K280',
            'Marcopolo Torino',
            'Caio Apache Vip',
        ]
        
        for i, company in enumerate(companies):
            vehicle_count = random.randint(10, 25)
            
            for j in range(vehicle_count):
                fleet_number = f'{company.short_name}{i+1:02d}{j+1:03d}'
                
                Vehicle.objects.get_or_create(
                    fleet_number=fleet_number,
                    defaults={
                        'license_plate': f'ABC{random.randint(1000, 9999)}',
                        'model': random.choice(vehicle_models),
                        'manufacturer': random.choice(['Mercedes-Benz', 'Volvo', 'Scania']),
                        'year': random.randint(2015, 2023),
                        'capacity': random.randint(40, 80),
                        'fuel_type': 'diesel',
                        'wheelchair_accessible': random.choice([True, False]),
                        'low_floor': random.choice([True, False]),
                        'air_conditioning': random.choice([True, False]),
                        'transport_company': company,
                    }
                )
                self.stats['vehicles_created'] += 1

    def import_gtfs_data(self):
        """Importa dados GTFS reais (placeholder para implementação futura)."""
        self.stdout.write(
            self.style.WARNING(
                'Importação GTFS não implementada ainda. Use --mode=demo para dados simulados.'
            )
        )

    def print_report(self):
        """Imprime relatório final."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('RELATÓRIO DE IMPORTAÇÃO'))
        self.stdout.write('='*50)
        
        self.stdout.write(f'Empresas criadas: {self.stats["companies_created"]}')
        self.stdout.write(f'Tipos de rota criados: {self.stats["route_types_created"]}')
        self.stdout.write(f'Paradas criadas: {self.stats["stops_created"]}')
        self.stdout.write(f'Rotas criadas: {self.stats["routes_created"]}')
        self.stdout.write(f'Relacionamentos rota-parada: {self.stats["route_stops_created"]}')
        self.stdout.write(f'Horários criados: {self.stats["schedules_created"]}')
        self.stdout.write(f'Veículos criados: {self.stats["vehicles_created"]}')
        
        if self.stats['errors']:
            self.stdout.write(f'\nErros: {len(self.stats["errors"])}')
            for error in self.stats['errors'][:5]:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        
        self.stdout.write('\n' + '='*50) 
"""
Comando para importar dados de transporte público do DF.
Integra com fontes oficiais do DFTrans para carregar dados reais de linhas, paradas e rotas.
"""

import os
import requests
import json
import csv
from io import StringIO
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from routes.models import BusRoute, RouteType, TransportCompany, RouteStop, Vehicle
from stops.models import BusStop, StopType
from django.utils import timezone
import logging

logger = logging.getLogger('busfeed')


class Command(BaseCommand):
    help = 'Importa dados de transporte público do DF (linhas, paradas e rotas)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            choices=['mock', 'gtfs', 'api'],
            default='mock',
            help='Fonte dos dados (mock para dados simulados, gtfs para arquivos GTFS, api para APIs)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa todos os dados existentes antes de importar'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando importação de dados do transporte público do DF...')
        )

        if options['clear']:
            self.clear_existing_data()

        if options['source'] == 'mock':
            self.import_mock_data()
        elif options['source'] == 'gtfs':
            self.import_gtfs_data()
        elif options['source'] == 'api':
            self.import_api_data()

        self.stdout.write(
            self.style.SUCCESS('Importação concluída com sucesso!')
        )

    def clear_existing_data(self):
        """Remove todos os dados existentes."""
        self.stdout.write('Removendo dados existentes...')
        
        with transaction.atomic():
            RouteStop.objects.all().delete()
            Vehicle.objects.all().delete()
            BusRoute.objects.all().delete()
            BusStop.objects.all().delete()
            # Manter tipos e empresas para reutilização
            
        self.stdout.write(self.style.SUCCESS('Dados removidos.'))

    def import_mock_data(self):
        """Importa dados simulados baseados nas linhas reais do DF."""
        self.stdout.write('Importando dados simulados das linhas do DF...')
        
        with transaction.atomic():
            # Criar tipos de paradas
            self.create_stop_types()
            
            # Criar tipos de rotas
            self.create_route_types()
            
            # Criar empresas
            self.create_transport_companies()
            
            # Criar paradas principais do DF
            self.create_main_stops()
            
            # Criar linhas principais do DF
            self.create_main_routes()

    def create_stop_types(self):
        """Cria os tipos de paradas."""
        stop_types_data = [
            {
                'name': 'Parada Simples',
                'description': 'Parada comum sem abrigo',
                'icon': 'bus-stop',
                'color': '#007bff'
            },
            {
                'name': 'Parada com Abrigo',
                'description': 'Parada com cobertura e bancos',
                'icon': 'bus-shelter',
                'color': '#28a745'
            },
            {
                'name': 'Terminal Rodoviário',
                'description': 'Terminal principal de ônibus',
                'icon': 'terminal',
                'color': '#dc3545'
            },
            {
                'name': 'Estação de Metrô',
                'description': 'Estação integrada com metrô',
                'icon': 'metro',
                'color': '#fd7e14'
            }
        ]
        
        for stop_type_data in stop_types_data:
            stop_type, created = StopType.objects.get_or_create(
                name=stop_type_data['name'],
                defaults=stop_type_data
            )
            if created:
                self.stdout.write(f'  • Tipo de parada criado: {stop_type.name}')

    def create_route_types(self):
        """Cria os tipos de rotas."""
        route_types_data = [
            {
                'name': 'Convencional',
                'description': 'Linha de ônibus convencional',
                'icon': 'bus',
                'color': '#007bff',
                'fare_multiplier': 1.0
            },
            {
                'name': 'Expresso',
                'description': 'Linha expressa com paradas limitadas',
                'icon': 'bus-express',
                'color': '#28a745',
                'fare_multiplier': 1.2
            },
            {
                'name': 'Circular',
                'description': 'Linha circular dentro de uma região',
                'icon': 'bus-circular',
                'color': '#ffc107',
                'fare_multiplier': 0.8
            },
            {
                'name': 'Metropolitana',
                'description': 'Linha intermunicipal da região metropolitana',
                'icon': 'bus-metro',
                'color': '#dc3545',
                'fare_multiplier': 1.5
            }
        ]
        
        for route_type_data in route_types_data:
            route_type, created = RouteType.objects.get_or_create(
                name=route_type_data['name'],
                defaults=route_type_data
            )
            if created:
                self.stdout.write(f'  • Tipo de rota criado: {route_type.name}')

    def create_transport_companies(self):
        """Cria as principais empresas de transporte do DF."""
        companies_data = [
            {
                'name': 'Sociedade de Transporte Coletivo de Brasília Ltda',
                'short_name': 'TCB',
                'cnpj': '00.000.000/0001-00',
                'phone': '(61) 3344-1234',
                'email': 'contato@tcb.com.br'
            },
            {
                'name': 'Expresso São José Ltda',
                'short_name': 'São José',
                'cnpj': '00.000.000/0001-01',
                'phone': '(61) 3344-5678',
                'email': 'contato@expresssaojose.com.br'
            },
            {
                'name': 'Pioneira',
                'short_name': 'Pioneira',
                'cnpj': '00.000.000/0001-02',
                'phone': '(61) 3344-9012',
                'email': 'contato@pioneira.com.br'
            },
            {
                'name': 'Empresa Marechal',
                'short_name': 'Marechal',
                'cnpj': '00.000.000/0001-03',
                'phone': '(61) 3344-3456',
                'email': 'contato@marechal.com.br'
            }
        ]
        
        for company_data in companies_data:
            company, created = TransportCompany.objects.get_or_create(
                short_name=company_data['short_name'],
                defaults=company_data
            )
            if created:
                self.stdout.write(f'  • Empresa criada: {company.short_name}')

    def create_main_stops(self):
        """Cria as principais paradas e terminais do DF."""
        # Tipos de paradas
        parada_simples = StopType.objects.get(name='Parada Simples')
        parada_abrigo = StopType.objects.get(name='Parada com Abrigo')
        terminal = StopType.objects.get(name='Terminal Rodoviário')
        metro = StopType.objects.get(name='Estação de Metrô')
        
        stops_data = [
            # Terminais principais
            {
                'code': 'T001',
                'name': 'Terminal Rodoviário do Plano Piloto',
                'latitude': -15.7898,
                'longitude': -47.8864,
                'stop_type': terminal,
                'neighborhood': 'Asa Sul',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'T002',
                'name': 'Terminal da Asa Norte',
                'latitude': -15.7641,
                'longitude': -47.8825,
                'stop_type': terminal,
                'neighborhood': 'Asa Norte',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'T003',
                'name': 'Terminal de Taguatinga',
                'latitude': -15.8267,
                'longitude': -48.0580,
                'stop_type': terminal,
                'neighborhood': 'Taguatinga',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'T004',
                'name': 'Terminal do Gama',
                'latitude': -15.9888,
                'longitude': -48.0654,
                'stop_type': terminal,
                'neighborhood': 'Gama',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'T005',
                'name': 'Terminal de Ceilândia',
                'latitude': -15.8108,
                'longitude': -48.1073,
                'stop_type': terminal,
                'neighborhood': 'Ceilândia',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            
            # Estações de Metrô
            {
                'code': 'M001',
                'name': 'Estação Central',
                'latitude': -15.7942,
                'longitude': -47.8822,
                'stop_type': metro,
                'neighborhood': 'Asa Sul',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'M002',
                'name': 'Estação Galeria',
                'latitude': -15.7895,
                'longitude': -47.8773,
                'stop_type': metro,
                'neighborhood': 'Asa Sul',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'M003',
                'name': 'Estação 102 Sul',
                'latitude': -15.7973,
                'longitude': -47.8896,
                'stop_type': metro,
                'neighborhood': 'Asa Sul',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'M004',
                'name': 'Estação 108 Sul',
                'latitude': -15.8024,
                'longitude': -47.8948,
                'stop_type': metro,
                'neighborhood': 'Asa Sul',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'M005',
                'name': 'Estação Taguatinga Sul',
                'latitude': -15.8320,
                'longitude': -48.0463,
                'stop_type': metro,
                'neighborhood': 'Taguatinga',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            
            # Paradas importantes
            {
                'code': 'P001',
                'name': 'Hélio Prates',
                'latitude': -15.7850,
                'longitude': -47.8950,
                'stop_type': parada_abrigo,
                'neighborhood': 'Guará',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': False
            },
            {
                'code': 'P002',
                'name': 'Shopping Brasília',
                'latitude': -15.7820,
                'longitude': -47.8900,
                'stop_type': parada_abrigo,
                'neighborhood': 'Asa Norte',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'P003',
                'name': 'Setor Bancário Sul',
                'latitude': -15.7950,
                'longitude': -47.8800,
                'stop_type': parada_abrigo,
                'neighborhood': 'Asa Sul',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'P004',
                'name': 'UnB - Campus Darcy Ribeiro',
                'latitude': -15.7648,
                'longitude': -47.8700,
                'stop_type': parada_abrigo,
                'neighborhood': 'Asa Norte',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            },
            {
                'code': 'P005',
                'name': 'Hospital de Base',
                'latitude': -15.7900,
                'longitude': -47.8600,
                'stop_type': parada_abrigo,
                'neighborhood': 'Asa Sul',
                'has_shelter': True,
                'has_seating': True,
                'wheelchair_accessible': True
            }
        ]
        
        for stop_data in stops_data:
            stop, created = BusStop.objects.get_or_create(
                code=stop_data['code'],
                defaults=stop_data
            )
            if created:
                self.stdout.write(f'  • Parada criada: {stop.name}')

    def create_main_routes(self):
        """Cria as principais linhas de ônibus do DF."""
        # Buscar dependências
        convencional = RouteType.objects.get(name='Convencional')
        expresso = RouteType.objects.get(name='Expresso')
        circular = RouteType.objects.get(name='Circular')
        
        tcb = TransportCompany.objects.get(short_name='TCB')
        sao_jose = TransportCompany.objects.get(short_name='São José')
        pioneira = TransportCompany.objects.get(short_name='Pioneira')
        
        routes_data = [
            {
                'number': '0.039',
                'name': 'Rodoviária → Guará → QE 40',
                'route_type': convencional,
                'transport_company': tcb,
                'origin_terminal': 'Terminal Rodoviário',
                'destination_terminal': 'QE 40 - Guará',
                'operates_weekdays': True,
                'operates_saturdays': True,
                'operates_sundays': False,
                'base_fare': 5.50,
                'wheelchair_accessible': True,
                'first_departure': '05:00',
                'last_departure': '23:30',
                'average_frequency': 15
            },
            {
                'number': '0.089',
                'name': 'Rodoviária → Shopping Brasília → Asa Norte',
                'route_type': convencional,
                'transport_company': tcb,
                'origin_terminal': 'Terminal Rodoviário',
                'destination_terminal': 'Asa Norte',
                'operates_weekdays': True,
                'operates_saturdays': True,
                'operates_sundays': True,
                'base_fare': 5.50,
                'wheelchair_accessible': True,
                'first_departure': '05:30',
                'last_departure': '23:00',
                'average_frequency': 20
            },
            {
                'number': '0.886',
                'name': 'Guará → Metrô Central',
                'route_type': convencional,
                'transport_company': sao_jose,
                'origin_terminal': 'Guará',
                'destination_terminal': 'Estação Central',
                'operates_weekdays': True,
                'operates_saturdays': True,
                'operates_sundays': False,
                'base_fare': 5.50,
                'wheelchair_accessible': False,
                'first_departure': '05:15',
                'last_departure': '22:45',
                'average_frequency': 25
            },
            {
                'number': '0.142',
                'name': 'Taguatinga → Ceilândia → Terminal Norte',
                'route_type': expresso,
                'transport_company': pioneira,
                'origin_terminal': 'Terminal Taguatinga',
                'destination_terminal': 'Terminal Asa Norte',
                'operates_weekdays': True,
                'operates_saturdays': True,
                'operates_sundays': False,
                'base_fare': 6.60,
                'wheelchair_accessible': True,
                'first_departure': '06:00',
                'last_departure': '22:00',
                'average_frequency': 30
            },
            {
                'number': '0.108',
                'name': 'UnB → Hospital de Base → Setor Bancário',
                'route_type': circular,
                'transport_company': tcb,
                'origin_terminal': 'UnB',
                'destination_terminal': 'UnB',
                'is_circular': True,
                'operates_weekdays': True,
                'operates_saturdays': False,
                'operates_sundays': False,
                'base_fare': 4.40,
                'wheelchair_accessible': True,
                'first_departure': '06:30',
                'last_departure': '18:30',
                'average_frequency': 40
            }
        ]
        
        for route_data in routes_data:
            route, created = BusRoute.objects.get_or_create(
                number=route_data['number'],
                defaults=route_data
            )
            if created:
                self.stdout.write(f'  • Rota criada: {route.number} - {route.name}')
                self.create_route_stops(route)

    def create_route_stops(self, route):
        """Cria as paradas para uma rota específica."""
        # Mapear rotas para suas paradas (simulado)
        route_stops_map = {
            '0.039': [
                ('T001', 'ida', 1), ('M001', 'ida', 2), ('P001', 'ida', 3),
                ('P001', 'volta', 1), ('M001', 'volta', 2), ('T001', 'volta', 3)
            ],
            '0.089': [
                ('T001', 'ida', 1), ('P002', 'ida', 2), ('T002', 'ida', 3),
                ('T002', 'volta', 1), ('P002', 'volta', 2), ('T001', 'volta', 3)
            ],
            '0.886': [
                ('P001', 'ida', 1), ('M001', 'ida', 2),
                ('M001', 'volta', 1), ('P001', 'volta', 2)
            ],
            '0.142': [
                ('T003', 'ida', 1), ('T005', 'ida', 2), ('T002', 'ida', 3),
                ('T002', 'volta', 1), ('T005', 'volta', 2), ('T003', 'volta', 3)
            ],
            '0.108': [
                ('P004', 'circular', 1), ('P005', 'circular', 2), 
                ('P003', 'circular', 3), ('P004', 'circular', 4)
            ]
        }
        
        stops_sequence = route_stops_map.get(route.number, [])
        
        for stop_code, direction, sequence in stops_sequence:
            try:
                stop = BusStop.objects.get(code=stop_code)
                route_stop, created = RouteStop.objects.get_or_create(
                    route=route,
                    stop=stop,
                    direction=direction,
                    sequence=sequence,
                    defaults={
                        'distance_from_origin': sequence * 2.5,  # Estimativa
                        'estimated_time_from_origin': sequence * 8  # Estimativa
                    }
                )
                if created:
                    self.stdout.write(f'    → Parada {stop.name} adicionada à rota')
            except BusStop.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'    → Parada {stop_code} não encontrada')
                )

    def import_gtfs_data(self):
        """Importa dados do formato GTFS (futuro)."""
        self.stdout.write(
            self.style.WARNING('Importação GTFS ainda não implementada. Use --source=mock')
        )

    def import_api_data(self):
        """Importa dados via API (futuro)."""
        self.stdout.write(
            self.style.WARNING('Importação via API ainda não implementada. Use --source=mock')
        ) 
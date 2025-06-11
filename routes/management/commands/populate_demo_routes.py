"""
Comando para popular dados de demonstração das rotas de ônibus de Brasília.
Cria rotas, paradas e empresas de exemplo para testar o sistema.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from routes.models import BusRoute, RouteType, TransportCompany, RouteStop
from stops.models import BusStop, StopType
import random


class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração das rotas de Brasília'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa dados existentes antes de popular',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Limpando dados existentes...')
            BusRoute.objects.all().delete()
            RouteType.objects.all().delete()
            TransportCompany.objects.all().delete()
            BusStop.objects.all().delete()
            StopType.objects.all().delete()

        with transaction.atomic():
            self.create_stop_types()
            self.create_route_types()
            self.create_companies()
            self.create_stops()
            self.create_routes()
            self.create_route_stops()

        self.stdout.write(
            self.style.SUCCESS('Dados de demonstração criados com sucesso!')
        )

    def create_stop_types(self):
        """Cria tipos de paradas"""
        stop_types = [
            {'name': 'Parada Comum', 'icon': 'bus', 'color': '#007bff'},
            {'name': 'Terminal', 'icon': 'building', 'color': '#28a745'},
            {'name': 'Estação BRT', 'icon': 'train', 'color': '#dc3545'},
        ]
        
        for data in stop_types:
            StopType.objects.get_or_create(
                name=data['name'],
                defaults={
                    'icon': data['icon'],
                    'color': data['color']
                }
            )
        
        self.stdout.write('Tipos de paradas criados')

    def create_route_types(self):
        """Cria tipos de rotas"""
        route_types = [
            {'name': 'Convencional', 'color': '#007bff', 'icon': 'bus'},
            {'name': 'BRT', 'color': '#dc3545', 'icon': 'train'},
            {'name': 'Expresso', 'color': '#28a745', 'icon': 'lightning'},
            {'name': 'Circular', 'color': '#ffc107', 'icon': 'arrow-repeat'},
        ]
        
        for data in route_types:
            RouteType.objects.get_or_create(
                name=data['name'],
                defaults={
                    'color': data['color'],
                    'icon': data['icon'],
                    'fare_multiplier': 1.0
                }
            )
        
        self.stdout.write('Tipos de rotas criados')

    def create_companies(self):
        """Cria empresas de transporte"""
        companies = [
            {
                'name': 'Viação Pioneira',
                'short_name': 'Pioneira',
                'cnpj': '12.345.678/0001-90'
            },
            {
                'name': 'Expresso Brasiliense',
                'short_name': 'Brasiliense',
                'cnpj': '98.765.432/0001-10'
            },
            {
                'name': 'Transportes Planalto',
                'short_name': 'Planalto',
                'cnpj': '11.222.333/0001-44'
            },
        ]
        
        for data in companies:
            TransportCompany.objects.get_or_create(
                cnpj=data['cnpj'],
                defaults=data
            )
        
        self.stdout.write('Empresas de transporte criadas')

    def create_stops(self):
        """Cria paradas de exemplo em Brasília"""
        # Coordenadas aproximadas de pontos importantes de Brasília
        stops_data = [
            # Plano Piloto
            {'name': 'Rodoviária do Plano Piloto', 'code': 'ROD001', 'lat': -15.7942, 'lng': -47.8822, 'neighborhood': 'Asa Norte'},
            {'name': 'Esplanada dos Ministérios', 'code': 'ESP001', 'lat': -15.7998, 'lng': -47.8645, 'neighborhood': 'Zona Cívico-Administrativa'},
            {'name': 'Shopping Brasília', 'code': 'SHB001', 'lat': -15.7817, 'lng': -47.8906, 'neighborhood': 'Asa Norte'},
            {'name': 'UnB - Universidade de Brasília', 'code': 'UNB001', 'lat': -15.7633, 'lng': -47.8707, 'neighborhood': 'Asa Norte'},
            {'name': 'Hospital de Base', 'code': 'HBB001', 'lat': -15.7808, 'lng': -47.9267, 'neighborhood': 'Asa Sul'},
            
            # Taguatinga
            {'name': 'Centro de Taguatinga', 'code': 'TAG001', 'lat': -15.8267, 'lng': -48.0583, 'neighborhood': 'Taguatinga Centro'},
            {'name': 'Shopping Taguatinga', 'code': 'SHT001', 'lat': -15.8389, 'lng': -48.0506, 'neighborhood': 'Taguatinga Norte'},
            {'name': 'Terminal Taguatinga', 'code': 'TER001', 'lat': -15.8333, 'lng': -48.0500, 'neighborhood': 'Taguatinga Centro'},
            
            # Ceilândia
            {'name': 'Centro de Ceilândia', 'code': 'CEI001', 'lat': -15.8167, 'lng': -48.1067, 'neighborhood': 'Ceilândia Centro'},
            {'name': 'Terminal Ceilândia', 'code': 'TER002', 'lat': -15.8200, 'lng': -48.1100, 'neighborhood': 'Ceilândia Centro'},
            
            # Samambaia
            {'name': 'Centro de Samambaia', 'code': 'SAM001', 'lat': -15.8783, 'lng': -48.0944, 'neighborhood': 'Samambaia Norte'},
            {'name': 'Terminal Samambaia', 'code': 'TER003', 'lat': -15.8800, 'lng': -48.0950, 'neighborhood': 'Samambaia Norte'},
            
            # Águas Claras
            {'name': 'Centro de Águas Claras', 'code': 'AGC001', 'lat': -15.8344, 'lng': -48.0267, 'neighborhood': 'Águas Claras'},
            {'name': 'Shopping Águas Claras', 'code': 'SHA001', 'lat': -15.8356, 'lng': -48.0289, 'neighborhood': 'Águas Claras'},
            
            # Guará
            {'name': 'Centro do Guará', 'code': 'GUA001', 'lat': -15.8267, 'lng': -47.9667, 'neighborhood': 'Guará I'},
            {'name': 'Shopping Guará', 'code': 'SHG001', 'lat': -15.8300, 'lng': -47.9700, 'neighborhood': 'Guará II'},
        ]
        
        stop_type = StopType.objects.first()
        
        for data in stops_data:
            BusStop.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'latitude': data['lat'],
                    'longitude': data['lng'],
                    'neighborhood': data['neighborhood'],
                    'stop_type': stop_type,
                    'wheelchair_accessible': random.choice([True, False]),
                    'has_shelter': random.choice([True, False]),
                    'has_seating': random.choice([True, False]),
                }
            )
        
        self.stdout.write('Paradas criadas')

    def create_routes(self):
        """Cria rotas de exemplo"""
        route_type = RouteType.objects.first()
        company = TransportCompany.objects.first()
        
        routes_data = [
            {
                'number': '0.101',
                'name': 'Rodoviária - Taguatinga',
                'origin_terminal': 'Rodoviária do Plano Piloto',
                'destination_terminal': 'Terminal Taguatinga',
                'base_fare': 5.50,
            },
            {
                'number': '0.102',
                'name': 'Rodoviária - Ceilândia',
                'origin_terminal': 'Rodoviária do Plano Piloto',
                'destination_terminal': 'Terminal Ceilândia',
                'base_fare': 5.50,
            },
            {
                'number': '0.103',
                'name': 'Rodoviária - Samambaia',
                'origin_terminal': 'Rodoviária do Plano Piloto',
                'destination_terminal': 'Terminal Samambaia',
                'base_fare': 5.50,
            },
            {
                'number': '0.104',
                'name': 'UnB - Taguatinga',
                'origin_terminal': 'UnB - Universidade de Brasília',
                'destination_terminal': 'Centro de Taguatinga',
                'base_fare': 5.50,
            },
            {
                'number': '0.105',
                'name': 'Águas Claras - Plano Piloto',
                'origin_terminal': 'Centro de Águas Claras',
                'destination_terminal': 'Esplanada dos Ministérios',
                'base_fare': 5.50,
            },
            {
                'number': '0.106',
                'name': 'Guará - Rodoviária',
                'origin_terminal': 'Centro do Guará',
                'destination_terminal': 'Rodoviária do Plano Piloto',
                'base_fare': 5.50,
            },
        ]
        
        for data in routes_data:
            BusRoute.objects.get_or_create(
                number=data['number'],
                defaults={
                    'name': data['name'],
                    'origin_terminal': data['origin_terminal'],
                    'destination_terminal': data['destination_terminal'],
                    'route_type': route_type,
                    'transport_company': company,
                    'base_fare': data['base_fare'],
                    'wheelchair_accessible': random.choice([True, False]),
                    'operates_weekdays': True,
                    'operates_saturdays': True,
                    'operates_sundays': random.choice([True, False]),
                    'average_frequency': random.randint(15, 45),
                    'estimated_duration': random.randint(45, 90),
                }
            )
        
        self.stdout.write('Rotas criadas')

    def create_route_stops(self):
        """Associa paradas às rotas"""
        routes = BusRoute.objects.all()
        stops = list(BusStop.objects.all())
        
        for route in routes:
            # Seleciona algumas paradas aleatórias para cada rota
            route_stops = random.sample(stops, min(8, len(stops)))
            
            for i, stop in enumerate(route_stops):
                RouteStop.objects.get_or_create(
                    route=route,
                    stop=stop,
                    direction='ida',
                    sequence=i + 1,
                    defaults={
                        'distance_from_origin': i * 2.5,  # Aproximadamente 2.5km entre paradas
                        'estimated_time_from_origin': i * 8,  # Aproximadamente 8 min entre paradas
                    }
                )
                
                # Cria também o sentido volta (invertido)
                RouteStop.objects.get_or_create(
                    route=route,
                    stop=stop,
                    direction='volta',
                    sequence=len(route_stops) - i,
                    defaults={
                        'distance_from_origin': (len(route_stops) - i - 1) * 2.5,
                        'estimated_time_from_origin': (len(route_stops) - i - 1) * 8,
                    }
                )
        
        self.stdout.write('Associações rota-parada criadas') 
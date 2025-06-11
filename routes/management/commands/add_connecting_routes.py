"""
Management command para adicionar rotas que conectam as novas paradas importantes,
melhorando a conectividade do sistema de transporte.
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from routes.models import TransportCompany, RouteType, BusRoute, RouteStop
from stops.models import BusStop


class Command(BaseCommand):
    help = 'Adiciona rotas conectando paradas importantes'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = {'routes_created': 0, 'route_stops_created': 0}

    def handle(self, *args, **options):
        self.stdout.write('Adicionando rotas conectoras...')
        
        with transaction.atomic():
            companies = list(TransportCompany.objects.all())
            route_types = list(RouteType.objects.all())
            
            if not companies or not route_types:
                self.stdout.write(self.style.ERROR('Empresas ou tipos de rota não encontrados!'))
                return
                
            self.add_shopping_routes(companies, route_types)
            self.add_hospital_routes(companies, route_types)
            self.add_university_routes(companies, route_types)
            self.add_recreation_routes(companies, route_types)
            self.add_metro_integration_routes(companies, route_types)
            
        self.print_report()

    def create_route_if_not_exists(self, data, company, route_type):
        """Cria uma rota se ela não existir."""
        route, created = BusRoute.objects.get_or_create(
            number=data['number'],
            defaults={
                'name': data['name'],
                'origin_terminal': data['origin'],
                'destination_terminal': data['destination'],
                'transport_company': company,
                'route_type': route_type,
                'is_bidirectional': data.get('bidirectional', True),
                'operates_weekdays': True,
                'operates_saturdays': True,
                'operates_sundays': data.get('sundays', False),
                'wheelchair_accessible': random.choice([True, False]),
                'data_source': 'BusFeed Enhanced Routes',
            }
        )
        
        if created:
            self.stats['routes_created'] += 1
        return route

    def connect_stops_to_route(self, route, stop_codes):
        """Conecta paradas a uma rota."""
        stops_by_code = {stop.code: stop for stop in BusStop.objects.filter(code__in=stop_codes)}
        
        for sequence, stop_code in enumerate(stop_codes, 1):
            stop = stops_by_code.get(stop_code)
            if stop:
                # Ida
                RouteStop.objects.get_or_create(
                    route=route,
                    stop=stop,
                    direction='ida',
                    sequence=sequence,
                    defaults={
                        'is_timing_point': sequence == 1 or sequence == len(stop_codes),
                    }
                )
                self.stats['route_stops_created'] += 1
                
                # Volta se bidirecional
                if route.is_bidirectional:
                    volta_sequence = len(stop_codes) - sequence + 1
                    RouteStop.objects.get_or_create(
                        route=route,
                        stop=stop,
                        direction='volta',
                        sequence=volta_sequence,
                        defaults={
                            'is_timing_point': volta_sequence == 1 or volta_sequence == len(stop_codes),
                        }
                    )
                    self.stats['route_stops_created'] += 1

    def add_shopping_routes(self, companies, route_types):
        """Adiciona rotas conectando shoppings."""
        shopping_routes = [
            {
                'number': 'SHP01',
                'name': 'Circular Shoppings Norte',
                'origin': 'Shopping Conjunto Nacional',
                'destination': 'Shopping Brasília',
                'stops': ['SHP005', 'SHP006', 'SHP001', 'COM001', 'COM002']
            },
            {
                'number': 'SHP02',
                'name': 'Circular Shoppings Sul',
                'origin': 'Shopping Pátio Brasil',
                'destination': 'Shopping JK Iguatemi',
                'stops': ['SHP002', 'COM003', 'COM004', 'SHP004']
            },
            {
                'number': 'SHP03',
                'name': 'Shoppings Taguatinga',
                'origin': 'Terminal Taguatinga',
                'destination': 'Shopping Boulevard',
                'stops': ['TAG005', 'SHP003', 'SHP010', 'TAG001']
            },
            {
                'number': 'SHP04',
                'name': 'Express Shopping Águas Claras',
                'origin': 'Estação Central',
                'destination': 'Shopping Terraço',
                'stops': ['GOV001', 'MET005', 'SHP008'],
                'bidirectional': True,
                'sundays': True
            }
        ]
        
        for route_data in shopping_routes:
            company = random.choice(companies)
            route_type = route_types[0]  # Convencional
            route = self.create_route_if_not_exists(route_data, company, route_type)
            self.connect_stops_to_route(route, route_data['stops'])

    def add_hospital_routes(self, companies, route_types):
        """Adiciona rotas conectando hospitais."""
        hospital_routes = [
            {
                'number': 'HSP01',
                'name': 'Hospitais Plano Piloto',
                'origin': 'Hospital de Base',
                'destination': 'Hospital Sarah',
                'stops': ['HSP001', 'HSP002', 'HSP004', 'GOV001']
            },
            {
                'number': 'HSP02',
                'name': 'Emergência Ceilândia',
                'origin': 'Terminal Ceilândia',
                'destination': 'Hospital Regional Ceilândia',
                'stops': ['CEI005', 'HSP007', 'UPA001'],
                'sundays': True
            },
            {
                'number': 'HSP03',
                'name': 'Saúde Regional Norte',
                'origin': 'Terminal Sobradinho',
                'destination': 'Hospital Regional Sobradinho',
                'stops': ['SOB001', 'HSP005', 'PLA001', 'HSP008']
            },
            {
                'number': 'HSP04',
                'name': 'Saúde Regional Sul',
                'origin': 'Terminal Gama',
                'destination': 'Hospital Regional Santa Maria',
                'stops': ['GAM001', 'HSP006', 'STM001', 'HSP009', 'REC001', 'UPA002']
            }
        ]
        
        for route_data in hospital_routes:
            company = random.choice(companies)
            route_type = route_types[0]  # Convencional
            route = self.create_route_if_not_exists(route_data, company, route_type)
            self.connect_stops_to_route(route, route_data['stops'])

    def add_university_routes(self, companies, route_types):
        """Adiciona rotas conectando universidades."""
        university_routes = [
            {
                'number': 'UNI01',
                'name': 'Circular Universitária Ampliada',
                'origin': 'UnB Reitoria',
                'destination': 'UniCEUB',
                'stops': ['UNB001', 'UNB002', 'UNB003', 'UNI001', 'UNI002', 'ESC001']
            },
            {
                'number': 'UNI02',
                'name': 'Educação Taguatinga',
                'origin': 'Terminal Taguatinga',
                'destination': 'UCB Taguatinga',
                'stops': ['TAG005', 'UNI003', 'UNI005', 'UNI006']
            },
            {
                'number': 'UNI03',
                'name': 'Campus Planaltina',
                'origin': 'Terminal Planaltina',
                'destination': 'UPIS Planaltina',
                'stops': ['PLA001', 'UNI004']
            }
        ]
        
        for route_data in university_routes:
            company = random.choice(companies)
            route_type = route_types[2] if len(route_types) > 2 else route_types[0]  # Semi-direto
            route = self.create_route_if_not_exists(route_data, company, route_type)
            self.connect_stops_to_route(route, route_data['stops'])

    def add_recreation_routes(self, companies, route_types):
        """Adiciona rotas para áreas de recreação."""
        recreation_routes = [
            {
                'number': 'LAZ01',
                'name': 'Turismo Plano Piloto',
                'origin': 'Estação Central',
                'destination': 'Memorial JK',
                'stops': ['GOV001', 'GOV002', 'GOV003', 'LAZ012', 'LAZ007', 'LAZ008'],
                'sundays': True
            },
            {
                'number': 'LAZ02',
                'name': 'Parques e Lazer Norte',
                'origin': 'Parque Olhos d\'Água',
                'destination': 'Estádio Mané Garrincha',
                'stops': ['LAZ003', 'LAZ009', 'LAZ010', 'LAZ011'],
                'sundays': True
            },
            {
                'number': 'LAZ03',
                'name': 'Parques e Lazer Sul',
                'origin': 'Parque da Cidade Norte',
                'destination': 'Jardim Botânico',
                'stops': ['LAZ001', 'LAZ002', 'LAZ005', 'LAZ006'],
                'sundays': True
            },
            {
                'number': 'LAZ04',
                'name': 'Ecoturismo Brasília',
                'origin': 'Parque Nacional',
                'destination': 'Pontão do Lago Sul',
                'stops': ['LAZ004', 'GOV001', 'LAZ006'],
                'sundays': True
            }
        ]
        
        for route_data in recreation_routes:
            company = random.choice(companies)
            route_type = route_types[1] if len(route_types) > 1 else route_types[0]  # Expresso
            route = self.create_route_if_not_exists(route_data, company, route_type)
            self.connect_stops_to_route(route, route_data['stops'])

    def add_metro_integration_routes(self, companies, route_types):
        """Adiciona rotas de integração com o metrô."""
        metro_routes = [
            {
                'number': 'MET10',
                'name': 'Integração Metrô Sul',
                'origin': 'Estação Galeria',
                'destination': 'Estação 106 Sul',
                'stops': ['MET001', 'MET002', 'MET003', 'MET004']
            },
            {
                'number': 'MET11',
                'name': 'Integração Águas Claras',
                'origin': 'Estação Águas Claras',
                'destination': 'Terminal Águas Claras',
                'stops': ['MET005', 'MET006', 'TER005']
            },
            {
                'number': 'MET12',
                'name': 'Conexão Metrô-Guará',
                'origin': 'Estação Feira',
                'destination': 'Terminal Guará',
                'stops': ['MET006', 'TER004', 'GUA001', 'GUA002']
            }
        ]
        
        for route_data in metro_routes:
            company = companies[0]  # DFTrans
            route_type = route_types[0]  # Convencional
            route = self.create_route_if_not_exists(route_data, company, route_type)
            self.connect_stops_to_route(route, route_data['stops'])

    def print_report(self):
        """Imprime relatório das rotas adicionadas."""
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Rotas conectoras criadas com sucesso!\n'
                f'🚌 Novas rotas: {self.stats["routes_created"]}\n'
                f'🔗 Conexões rota-parada: {self.stats["route_stops_created"]}\n'
            )
        ) 
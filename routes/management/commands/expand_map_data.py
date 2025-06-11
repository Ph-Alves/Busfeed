"""
Management command para expandir significativamente os dados do mapa
com paradas e rotas abrangentes de Brasília.
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from routes.models import TransportCompany, RouteType, BusRoute, RouteStop
from stops.models import BusStop, StopType


class Command(BaseCommand):
    help = 'Expande o mapa com mais paradas e rotas de Brasília'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = {'stops_created': 0, 'routes_created': 0, 'route_stops_created': 0}

    def handle(self, *args, **options):
        self.stdout.write('Expandindo dados do mapa...')
        
        with transaction.atomic():
            # Garantir que tipos básicos existam
            stop_types = self.ensure_stop_types()
            companies = self.ensure_companies()
            route_types = self.ensure_route_types()
            
            # Criar paradas extensivas
            stops = self.create_extensive_stops(stop_types)
            
            # Criar mais rotas
            routes = self.create_extensive_routes(companies, route_types)
            
            # Conectar rotas e paradas
            self.connect_extensive_routes_stops(routes, stops)
            
        self.print_report()

    def ensure_stop_types(self):
        """Garante que os tipos de parada existam."""
        types_data = [
            {'name': 'Terminal', 'color': '#FF5722'},
            {'name': 'Estação', 'color': '#9C27B0'},
            {'name': 'Parada', 'color': '#2196F3'},
            {'name': 'Ponto', 'color': '#4CAF50'},
        ]
        
        stop_types = []
        for data in types_data:
            stop_type, _ = StopType.objects.get_or_create(
                name=data['name'], defaults=data
            )
            stop_types.append(stop_type)
        return stop_types

    def ensure_companies(self):
        """Garante que as empresas existam."""
        companies_data = [
            {'name': 'DFTrans', 'short_name': 'DFT', 'cnpj': '00.394.679/0001-39'},
            {'name': 'Viação Pioneira', 'short_name': 'VPI', 'cnpj': '12.345.678/0001-90'},
            {'name': 'Expresso São José', 'short_name': 'ESJ', 'cnpj': '98.765.432/0001-10'},
            {'name': 'Brasília Transportes', 'short_name': 'BRT', 'cnpj': '11.222.333/0001-44'},
            {'name': 'Viação Capital', 'short_name': 'VCP', 'cnpj': '55.666.777/0001-88'},
        ]
        
        companies = []
        for data in companies_data:
            company, _ = TransportCompany.objects.get_or_create(
                name=data['name'], defaults=data
            )
            companies.append(company)
        return companies

    def ensure_route_types(self):
        """Garante que os tipos de rota existam."""
        types_data = [
            {'name': 'Convencional', 'color': '#2196F3', 'fare_multiplier': Decimal('1.0')},
            {'name': 'Expresso', 'color': '#FF5722', 'fare_multiplier': Decimal('1.5')},
            {'name': 'Semi-Direto', 'color': '#4CAF50', 'fare_multiplier': Decimal('1.2')},
            {'name': 'Circular', 'color': '#FF9800', 'fare_multiplier': Decimal('1.0')},
        ]
        
        route_types = []
        for data in types_data:
            route_type, _ = RouteType.objects.get_or_create(
                name=data['name'], defaults=data
            )
            route_types.append(route_type)
        return route_types

    def create_extensive_stops(self, stop_types):
        """Cria uma rede extensiva de paradas em Brasília."""
        # Paradas extensivas por região administrativa
        stops_data = [
            # Plano Piloto - Asa Norte
            {'code': 'AN001', 'name': 'SQN 102 - Bloco A', 'lat': -15.7530, 'lng': -47.8720, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'AN002', 'name': 'SQN 104 - Bloco C', 'lat': -15.7545, 'lng': -47.8705, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'AN003', 'name': 'SQN 106 - Bloco F', 'lat': -15.7560, 'lng': -47.8690, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'AN004', 'name': 'SQN 108 - Bloco B', 'lat': -15.7571, 'lng': -47.8739, 'neighborhood': 'Asa Norte', 'type': 'Estação'},
            {'code': 'AN005', 'name': 'SQN 110 - Bloco D', 'lat': -15.7585, 'lng': -47.8725, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'AN006', 'name': 'SQN 112 - Bloco G', 'lat': -15.7600, 'lng': -47.8710, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'AN007', 'name': 'SQN 114 - Bloco A', 'lat': -15.7615, 'lng': -47.8695, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'AN008', 'name': 'SQN 116 - Bloco E', 'lat': -15.7630, 'lng': -47.8680, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            
            # Plano Piloto - Asa Sul
            {'code': 'AS001', 'name': 'SQS 102 - Bloco A', 'lat': -15.8080, 'lng': -47.8920, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'AS002', 'name': 'SQS 104 - Bloco C', 'lat': -15.8095, 'lng': -47.8905, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'AS003', 'name': 'SQS 106 - Bloco F', 'lat': -15.8110, 'lng': -47.8890, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'AS004', 'name': 'SQS 108 - Bloco B', 'lat': -15.8125, 'lng': -47.8875, 'neighborhood': 'Asa Sul', 'type': 'Estação'},
            {'code': 'AS005', 'name': 'SQS 110 - Bloco D', 'lat': -15.8140, 'lng': -47.8860, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'AS006', 'name': 'SQS 112 - Bloco G', 'lat': -15.8155, 'lng': -47.8845, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'AS007', 'name': 'SQS 114 - Bloco A', 'lat': -15.8170, 'lng': -47.8830, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'AS008', 'name': 'SQS 116 - Bloco E', 'lat': -15.8185, 'lng': -47.8815, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            
            # Taguatinga
            {'code': 'TAG001', 'name': 'Taguatinga Centro - QSD 1', 'lat': -15.8270, 'lng': -48.0589, 'neighborhood': 'Taguatinga', 'type': 'Terminal'},
            {'code': 'TAG002', 'name': 'Taguatinga Norte - QNG 1', 'lat': -15.8200, 'lng': -48.0550, 'neighborhood': 'Taguatinga', 'type': 'Parada'},
            {'code': 'TAG003', 'name': 'Taguatinga Sul - QSF 5', 'lat': -15.8340, 'lng': -48.0620, 'neighborhood': 'Taguatinga', 'type': 'Parada'},
            {'code': 'TAG004', 'name': 'Shopping Taguatinga', 'lat': -15.8320, 'lng': -48.0570, 'neighborhood': 'Taguatinga', 'type': 'Estação'},
            {'code': 'TAG005', 'name': 'Terminal Taguatinga', 'lat': -15.8280, 'lng': -48.0600, 'neighborhood': 'Taguatinga', 'type': 'Terminal'},
            
            # Ceilândia
            {'code': 'CEI001', 'name': 'Ceilândia Centro - QNM 1', 'lat': -15.8158, 'lng': -48.1109, 'neighborhood': 'Ceilândia', 'type': 'Terminal'},
            {'code': 'CEI002', 'name': 'Ceilândia Norte - QNN 5', 'lat': -15.8100, 'lng': -48.1050, 'neighborhood': 'Ceilândia', 'type': 'Parada'},
            {'code': 'CEI003', 'name': 'Ceilândia Sul - QNO 10', 'lat': -15.8200, 'lng': -48.1150, 'neighborhood': 'Ceilândia', 'type': 'Parada'},
            {'code': 'CEI004', 'name': 'P Sul - QNP 15', 'lat': -15.8250, 'lng': -48.1200, 'neighborhood': 'Ceilândia', 'type': 'Parada'},
            {'code': 'CEI005', 'name': 'Terminal Ceilândia', 'lat': -15.8180, 'lng': -48.1120, 'neighborhood': 'Ceilândia', 'type': 'Terminal'},
            
            # Samambaia
            {'code': 'SAM001', 'name': 'Samambaia Norte - QN 1', 'lat': -15.8700, 'lng': -48.0850, 'neighborhood': 'Samambaia', 'type': 'Parada'},
            {'code': 'SAM002', 'name': 'Samambaia Sul - QS 5', 'lat': -15.8790, 'lng': -48.0944, 'neighborhood': 'Samambaia', 'type': 'Terminal'},
            {'code': 'SAM003', 'name': 'Samambaia Centro - QN 10', 'lat': -15.8745, 'lng': -48.0897, 'neighborhood': 'Samambaia', 'type': 'Estação'},
            
            # Planaltina
            {'code': 'PLA001', 'name': 'Planaltina Centro - Setor Norte', 'lat': -15.6227, 'lng': -47.6537, 'neighborhood': 'Planaltina', 'type': 'Terminal'},
            {'code': 'PLA002', 'name': 'Planaltina Sul - Setor Sul', 'lat': -15.6280, 'lng': -47.6580, 'neighborhood': 'Planaltina', 'type': 'Parada'},
            {'code': 'PLA003', 'name': 'Vale do Amanhecer', 'lat': -15.6150, 'lng': -47.6400, 'neighborhood': 'Planaltina', 'type': 'Parada'},
            
            # Gama
            {'code': 'GAM001', 'name': 'Gama Centro - Setor Central', 'lat': -16.0123, 'lng': -48.0655, 'neighborhood': 'Gama', 'type': 'Terminal'},
            {'code': 'GAM002', 'name': 'Gama Norte - Setor Norte', 'lat': -16.0080, 'lng': -48.0600, 'neighborhood': 'Gama', 'type': 'Parada'},
            {'code': 'GAM003', 'name': 'Gama Sul - Setor Sul', 'lat': -16.0180, 'lng': -48.0700, 'neighborhood': 'Gama', 'type': 'Parada'},
            
            # Sobradinho
            {'code': 'SOB001', 'name': 'Sobradinho Centro', 'lat': -15.6540, 'lng': -47.7896, 'neighborhood': 'Sobradinho', 'type': 'Terminal'},
            {'code': 'SOB002', 'name': 'Sobradinho II', 'lat': -15.6600, 'lng': -47.7950, 'neighborhood': 'Sobradinho II', 'type': 'Parada'},
            
            # Brazlândia
            {'code': 'BRZ001', 'name': 'Brazlândia Centro', 'lat': -15.6686, 'lng': -48.2042, 'neighborhood': 'Brazlândia', 'type': 'Terminal'},
            {'code': 'BRZ002', 'name': 'Brazlândia Norte', 'lat': -15.6650, 'lng': -48.2000, 'neighborhood': 'Brazlândia', 'type': 'Parada'},
            
            # Santa Maria
            {'code': 'STM001', 'name': 'Santa Maria Centro', 'lat': -16.0023, 'lng': -47.9855, 'neighborhood': 'Santa Maria', 'type': 'Terminal'},
            {'code': 'STM002', 'name': 'Santa Maria Norte', 'lat': -15.9980, 'lng': -47.9810, 'neighborhood': 'Santa Maria', 'type': 'Parada'},
            
            # Recanto das Emas
            {'code': 'REC001', 'name': 'Recanto das Emas Centro', 'lat': -15.9045, 'lng': -48.0769, 'neighborhood': 'Recanto das Emas', 'type': 'Terminal'},
            {'code': 'REC002', 'name': 'Recanto Norte', 'lat': -15.9000, 'lng': -48.0720, 'neighborhood': 'Recanto das Emas', 'type': 'Parada'},
            
            # São Sebastião
            {'code': 'SSE001', 'name': 'São Sebastião Centro', 'lat': -15.9059, 'lng': -47.7766, 'neighborhood': 'São Sebastião', 'type': 'Terminal'},
            {'code': 'SSE002', 'name': 'São Sebastião Norte', 'lat': -15.9010, 'lng': -47.7720, 'neighborhood': 'São Sebastião', 'type': 'Parada'},
            
            # Pontos importantes
            {'code': 'UNB001', 'name': 'UnB - Reitoria', 'lat': -15.7634, 'lng': -47.8707, 'neighborhood': 'Asa Norte', 'type': 'Estação'},
            {'code': 'UNB002', 'name': 'UnB - Instituto Central', 'lat': -15.7620, 'lng': -47.8690, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'UNB003', 'name': 'UnB - Faculdade de Tecnologia', 'lat': -15.7610, 'lng': -47.8675, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            
            {'code': 'SHP001', 'name': 'Shopping Brasília', 'lat': -15.7815, 'lng': -47.8911, 'neighborhood': 'Asa Norte', 'type': 'Estação'},
            {'code': 'SHP002', 'name': 'Shopping Pátio Brasil', 'lat': -15.7925, 'lng': -47.8850, 'neighborhood': 'Asa Sul', 'type': 'Estação'},
            {'code': 'SHP003', 'name': 'Shopping DF Plaza', 'lat': -15.8350, 'lng': -48.0650, 'neighborhood': 'Taguatinga', 'type': 'Estação'},
            
            {'code': 'HSP001', 'name': 'Hospital de Base', 'lat': -15.7800, 'lng': -47.8750, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'HSP002', 'name': 'Hospital Universitário', 'lat': -15.7650, 'lng': -47.8600, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'HSP003', 'name': 'Hospital Regional Taguatinga', 'lat': -15.8300, 'lng': -48.0500, 'neighborhood': 'Taguatinga', 'type': 'Parada'},
            
            {'code': 'GOV001', 'name': 'Esplanada dos Ministérios', 'lat': -15.7998, 'lng': -47.8636, 'neighborhood': 'Plano Piloto', 'type': 'Estação'},
            {'code': 'GOV002', 'name': 'Palácio do Planalto', 'lat': -15.7990, 'lng': -47.8600, 'neighborhood': 'Plano Piloto', 'type': 'Parada'},
            {'code': 'GOV003', 'name': 'Supremo Tribunal Federal', 'lat': -15.8010, 'lng': -47.8620, 'neighborhood': 'Plano Piloto', 'type': 'Parada'},
            
            {'code': 'AER001', 'name': 'Aeroporto - Terminal 1', 'lat': -15.8697, 'lng': -47.9208, 'neighborhood': 'Lago Sul', 'type': 'Terminal'},
            {'code': 'AER002', 'name': 'Aeroporto - Terminal 2', 'lat': -15.8705, 'lng': -47.9215, 'neighborhood': 'Lago Sul', 'type': 'Parada'},
        ]
        
        stops = []
        stop_types_dict = {st.name: st for st in stop_types}
        
        for data in stops_data:
            stop_type = stop_types_dict.get(data['type'])
            
            stop, created = BusStop.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'latitude': data['lat'],
                    'longitude': data['lng'],
                    'neighborhood': data['neighborhood'],
                    'stop_type': stop_type,
                    'has_shelter': random.choice([True, False]),
                    'has_seating': random.choice([True, False]),
                    'wheelchair_accessible': random.choice([True, False]),
                    'has_lighting': random.choice([True, False]),
                    'data_source': 'BusFeed Expanded',
                }
            )
            
            if created:
                self.stats['stops_created'] += 1
            stops.append(stop)
            
        return stops

    def create_extensive_routes(self, companies, route_types):
        """Cria uma rede extensiva de rotas."""
        routes_data = [
            # Linhas principais do Plano Piloto
            {'number': '001', 'name': 'Circular Asa Norte', 'origin': 'SQN 102', 'destination': 'SQN 116', 'company': 0, 'route_type': 3},
            {'number': '002', 'name': 'Circular Asa Sul', 'origin': 'SQS 102', 'destination': 'SQS 116', 'company': 0, 'route_type': 3},
            {'number': '003', 'name': 'Asa Norte - Asa Sul', 'origin': 'Terminal Asa Norte', 'destination': 'Terminal Rodoviário', 'company': 0, 'route_type': 0},
            
            # Linhas para Taguatinga
            {'number': '100', 'name': 'Plano Piloto - Taguatinga', 'origin': 'Estação Central', 'destination': 'Terminal Taguatinga', 'company': 0, 'route_type': 0},
            {'number': '101', 'name': 'Asa Norte - Taguatinga', 'origin': 'Terminal Asa Norte', 'destination': 'Taguatinga Centro', 'company': 1, 'route_type': 0},
            {'number': '102', 'name': 'Asa Sul - Taguatinga', 'origin': 'Terminal Rodoviário', 'destination': 'Shopping Taguatinga', 'company': 1, 'route_type': 0},
            {'number': '150', 'name': 'Expresso Taguatinga', 'origin': 'Estação Central', 'destination': 'Terminal Taguatinga', 'company': 0, 'route_type': 1},
            
            # Linhas para Ceilândia
            {'number': '200', 'name': 'Plano Piloto - Ceilândia', 'origin': 'Estação Central', 'destination': 'Terminal Ceilândia', 'company': 0, 'route_type': 0},
            {'number': '201', 'name': 'Taguatinga - Ceilândia', 'origin': 'Terminal Taguatinga', 'destination': 'Ceilândia Centro', 'company': 2, 'route_type': 0},
            {'number': '202', 'name': 'Asa Norte - Ceilândia Norte', 'origin': 'Terminal Asa Norte', 'destination': 'Ceilândia Norte', 'company': 1, 'route_type': 0},
            {'number': '250', 'name': 'Expresso Ceilândia', 'origin': 'Estação Central', 'destination': 'Terminal Ceilândia', 'company': 0, 'route_type': 1},
            
            # Linhas para Samambaia
            {'number': '300', 'name': 'Plano Piloto - Samambaia', 'origin': 'Estação Central', 'destination': 'Terminal Samambaia', 'company': 0, 'route_type': 0},
            {'number': '301', 'name': 'Taguatinga - Samambaia', 'origin': 'Terminal Taguatinga', 'destination': 'Samambaia Centro', 'company': 2, 'route_type': 0},
            {'number': '302', 'name': 'Ceilândia - Samambaia', 'origin': 'Terminal Ceilândia', 'destination': 'Terminal Samambaia', 'company': 3, 'route_type': 0},
            
            # Linhas para Planaltina
            {'number': '400', 'name': 'Plano Piloto - Planaltina', 'origin': 'Estação Central', 'destination': 'Terminal Planaltina', 'company': 0, 'route_type': 0},
            {'number': '401', 'name': 'Sobradinho - Planaltina', 'origin': 'Terminal Sobradinho', 'destination': 'Planaltina Centro', 'company': 4, 'route_type': 0},
            
            # Linhas para Gama
            {'number': '500', 'name': 'Plano Piloto - Gama', 'origin': 'Estação Central', 'destination': 'Terminal Gama', 'company': 0, 'route_type': 0},
            {'number': '501', 'name': 'Santa Maria - Gama', 'origin': 'Terminal Santa Maria', 'destination': 'Gama Centro', 'company': 3, 'route_type': 0},
            
            # Linhas para Sobradinho
            {'number': '600', 'name': 'Plano Piloto - Sobradinho', 'origin': 'Estação Central', 'destination': 'Terminal Sobradinho', 'company': 0, 'route_type': 0},
            {'number': '601', 'name': 'Asa Norte - Sobradinho II', 'origin': 'Terminal Asa Norte', 'destination': 'Sobradinho II', 'company': 4, 'route_type': 0},
            
            # Linhas especiais
            {'number': '700', 'name': 'UnB - Circular Universitária', 'origin': 'UnB Reitoria', 'destination': 'UnB Faculdade de Tecnologia', 'company': 0, 'route_type': 3},
            {'number': '800', 'name': 'Aeroporto - Plano Piloto', 'origin': 'Aeroporto Terminal 1', 'destination': 'Estação Central', 'company': 0, 'route_type': 1},
            {'number': '801', 'name': 'Aeroporto - Hotéis', 'origin': 'Aeroporto Terminal 1', 'destination': 'Setor Hoteleiro', 'company': 1, 'route_type': 1},
            
            # Linhas de bairro
            {'number': '900', 'name': 'Santa Maria - Recanto', 'origin': 'Terminal Santa Maria', 'destination': 'Terminal Recanto', 'company': 2, 'route_type': 0},
            {'number': '901', 'name': 'São Sebastião - Paranoá', 'origin': 'Terminal São Sebastião', 'destination': 'Paranoá Centro', 'company': 3, 'route_type': 0},
            {'number': '902', 'name': 'Brazlândia - Águas Claras', 'origin': 'Terminal Brazlândia', 'destination': 'Águas Claras Centro', 'company': 4, 'route_type': 0},
        ]
        
        routes = []
        for data in routes_data:
            company = companies[data['company'] % len(companies)]
            route_type = route_types[data['route_type'] % len(route_types)]
            
            route, created = BusRoute.objects.get_or_create(
                number=data['number'],
                defaults={
                    'name': data['name'],
                    'origin_terminal': data['origin'],
                    'destination_terminal': data['destination'],
                    'transport_company': company,
                    'route_type': route_type,
                    'is_bidirectional': True,
                    'operates_weekdays': True,
                    'operates_saturdays': True,
                    'operates_sundays': random.choice([True, False]),
                    'wheelchair_accessible': random.choice([True, False]),
                    'data_source': 'BusFeed Expanded',
                }
            )
            
            if created:
                self.stats['routes_created'] += 1
            routes.append(route)
            
        return routes

    def connect_extensive_routes_stops(self, routes, stops):
        """Conecta rotas e paradas de forma inteligente."""
        stops_by_code = {stop.code: stop for stop in stops}
        
        # Mapear paradas por região para conectar rotas
        route_stop_mappings = {
            '001': ['AN001', 'AN002', 'AN003', 'AN004', 'AN005', 'AN006', 'AN007', 'AN008'],  # Circular Asa Norte
            '002': ['AS001', 'AS002', 'AS003', 'AS004', 'AS005', 'AS006', 'AS007', 'AS008'],  # Circular Asa Sul
            '003': ['AN004', 'AN005', 'GOV001', 'AS004', 'AS005'],  # Asa Norte - Asa Sul
            '100': ['GOV001', 'AS004', 'TAG001', 'TAG004', 'TAG005'],  # Plano Piloto - Taguatinga
            '101': ['AN004', 'AN005', 'TAG002', 'TAG001'],  # Asa Norte - Taguatinga
            '102': ['AS004', 'AS005', 'SHP003', 'TAG004'],  # Asa Sul - Taguatinga
            '150': ['GOV001', 'TAG005'],  # Expresso Taguatinga
            '200': ['GOV001', 'TAG001', 'CEI001', 'CEI005'],  # Plano Piloto - Ceilândia
            '201': ['TAG005', 'TAG001', 'CEI002', 'CEI001'],  # Taguatinga - Ceilândia
            '202': ['AN004', 'CEI002', 'CEI001'],  # Asa Norte - Ceilândia Norte
            '250': ['GOV001', 'CEI005'],  # Expresso Ceilândia
            '300': ['GOV001', 'TAG001', 'SAM003', 'SAM002'],  # Plano Piloto - Samambaia
            '301': ['TAG005', 'SAM001', 'SAM003'],  # Taguatinga - Samambaia
            '302': ['CEI005', 'SAM001', 'SAM002'],  # Ceilândia - Samambaia
            '400': ['GOV001', 'SOB001', 'PLA001'],  # Plano Piloto - Planaltina
            '401': ['SOB001', 'SOB002', 'PLA002', 'PLA001'],  # Sobradinho - Planaltina
            '500': ['GOV001', 'STM001', 'GAM001'],  # Plano Piloto - Gama
            '501': ['STM001', 'STM002', 'GAM002', 'GAM001'],  # Santa Maria - Gama
            '600': ['GOV001', 'AN005', 'SOB001'],  # Plano Piloto - Sobradinho
            '601': ['AN004', 'SOB001', 'SOB002'],  # Asa Norte - Sobradinho II
            '700': ['UNB001', 'UNB002', 'UNB003'],  # UnB Circular
            '800': ['AER001', 'AER002', 'GOV001'],  # Aeroporto - Plano Piloto
            '801': ['AER001', 'SHP001'],  # Aeroporto - Hotéis
            '900': ['STM001', 'REC001', 'REC002'],  # Santa Maria - Recanto
            '901': ['SSE001', 'SSE002'],  # São Sebastião - Paranoá
            '902': ['BRZ001', 'BRZ002'],  # Brazlândia - Águas Claras
        }
        
        for route in routes:
            stop_codes = route_stop_mappings.get(route.number, [])
            
            for sequence, stop_code in enumerate(stop_codes, 1):
                stop = stops_by_code.get(stop_code)
                if stop:
                    # Criar conexão ida
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
                    
                    # Criar conexão volta se bidirecional
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

    def print_report(self):
        """Imprime relatório da expansão."""
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Expansão concluída com sucesso!\n'
                f'📍 Paradas criadas: {self.stats["stops_created"]}\n'
                f'🚌 Rotas criadas: {self.stats["routes_created"]}\n'
                f'🔗 Conexões rota-parada criadas: {self.stats["route_stops_created"]}\n'
            )
        ) 
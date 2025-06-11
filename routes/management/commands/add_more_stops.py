"""
Management command para adicionar ainda mais paradas importantes em Brasília,
incluindo pontos de interesse, shoppings, hospitais, universidades e mais.
"""
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from stops.models import BusStop, StopType


class Command(BaseCommand):
    help = 'Adiciona mais paradas importantes e pontos de interesse em Brasília'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = {'stops_created': 0}

    def handle(self, *args, **options):
        self.stdout.write('Adicionando mais paradas importantes...')
        
        with transaction.atomic():
            self.add_shopping_stops()
            self.add_hospital_stops()
            self.add_university_stops()
            self.add_government_stops()
            self.add_transport_hubs()
            self.add_residential_stops()
            self.add_commercial_stops()
            self.add_recreation_stops()
            
        self.print_report()

    def get_stop_type(self, type_name):
        """Obtém ou cria um tipo de parada."""
        stop_type, _ = StopType.objects.get_or_create(
            name=type_name,
            defaults={'color': '#2196F3'}
        )
        return stop_type

    def create_stop_if_not_exists(self, data):
        """Cria uma parada se ela não existir."""
        stop, created = BusStop.objects.get_or_create(
            code=data['code'],
            defaults={
                'name': data['name'],
                'latitude': data['lat'],
                'longitude': data['lng'],
                'neighborhood': data['neighborhood'],
                'stop_type': self.get_stop_type(data['type']),
                'has_shelter': random.choice([True, False]),
                'has_seating': random.choice([True, False]),
                'wheelchair_accessible': random.choice([True, False]),
                'has_lighting': random.choice([True, False]),
                'data_source': 'BusFeed Enhanced',
            }
        )
        
        if created:
            self.stats['stops_created'] += 1
        return stop

    def add_shopping_stops(self):
        """Adiciona paradas de shoppings e centros comerciais."""
        shopping_stops = [
            {'code': 'SHP004', 'name': 'Shopping JK Iguatemi', 'lat': -15.8320, 'lng': -47.8920, 'neighborhood': 'Lago Sul', 'type': 'Estação'},
            {'code': 'SHP005', 'name': 'Shopping Conjunto Nacional', 'lat': -15.7890, 'lng': -47.8890, 'neighborhood': 'Asa Norte', 'type': 'Estação'},
            {'code': 'SHP006', 'name': 'Shopping Park Shopping', 'lat': -15.8050, 'lng': -47.8830, 'neighborhood': 'Asa Norte', 'type': 'Estação'},
            {'code': 'SHP007', 'name': 'Shopping Liberty Mall', 'lat': -15.8380, 'lng': -47.9180, 'neighborhood': 'Guará', 'type': 'Parada'},
            {'code': 'SHP008', 'name': 'Shopping Terraço', 'lat': -15.8240, 'lng': -47.9340, 'neighborhood': 'Águas Claras', 'type': 'Estação'},
            {'code': 'SHP009', 'name': 'Shopping Ceilândia', 'lat': -15.8200, 'lng': -48.1080, 'neighborhood': 'Ceilândia', 'type': 'Estação'},
            {'code': 'SHP010', 'name': 'Shopping Boulevard', 'lat': -15.8350, 'lng': -48.0580, 'neighborhood': 'Taguatinga', 'type': 'Estação'},
        ]
        
        for stop_data in shopping_stops:
            self.create_stop_if_not_exists(stop_data)

    def add_hospital_stops(self):
        """Adiciona paradas de hospitais e centros de saúde."""
        hospital_stops = [
            {'code': 'HSP004', 'name': 'Hospital Sarah', 'lat': -15.7840, 'lng': -47.8980, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'HSP005', 'name': 'Hospital Regional Sobradinho', 'lat': -15.6580, 'lng': -47.7900, 'neighborhood': 'Sobradinho', 'type': 'Parada'},
            {'code': 'HSP006', 'name': 'Hospital Regional Gama', 'lat': -16.0150, 'lng': -48.0680, 'neighborhood': 'Gama', 'type': 'Parada'},
            {'code': 'HSP007', 'name': 'Hospital Regional Ceilândia', 'lat': -15.8180, 'lng': -48.1150, 'neighborhood': 'Ceilândia', 'type': 'Parada'},
            {'code': 'HSP008', 'name': 'Hospital Regional Planaltina', 'lat': -15.6250, 'lng': -47.6580, 'neighborhood': 'Planaltina', 'type': 'Parada'},
            {'code': 'HSP009', 'name': 'Hospital Regional Santa Maria', 'lat': -16.0050, 'lng': -47.9880, 'neighborhood': 'Santa Maria', 'type': 'Parada'},
            {'code': 'UPA001', 'name': 'UPA Samambaia', 'lat': -15.8780, 'lng': -48.0920, 'neighborhood': 'Samambaia', 'type': 'Parada'},
            {'code': 'UPA002', 'name': 'UPA Recanto das Emas', 'lat': -15.9060, 'lng': -48.0780, 'neighborhood': 'Recanto das Emas', 'type': 'Parada'},
        ]
        
        for stop_data in hospital_stops:
            self.create_stop_if_not_exists(stop_data)

    def add_university_stops(self):
        """Adiciona paradas de universidades e centros educacionais."""
        university_stops = [
            {'code': 'UNI001', 'name': 'UniCEUB - Asa Norte', 'lat': -15.7620, 'lng': -47.8820, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'UNI002', 'name': 'IESB - Asa Sul', 'lat': -15.8150, 'lng': -47.8950, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'UNI003', 'name': 'UCB - Taguatinga', 'lat': -15.8320, 'lng': -48.0520, 'neighborhood': 'Taguatinga', 'type': 'Parada'},
            {'code': 'UNI004', 'name': 'UPIS - Planaltina', 'lat': -15.6280, 'lng': -47.6520, 'neighborhood': 'Planaltina', 'type': 'Parada'},
            {'code': 'UNI005', 'name': 'IFB - Ceilândia', 'lat': -15.8200, 'lng': -48.1050, 'neighborhood': 'Ceilândia', 'type': 'Parada'},
            {'code': 'UNI006', 'name': 'IFB - Samambaia', 'lat': -15.8750, 'lng': -48.0900, 'neighborhood': 'Samambaia', 'type': 'Parada'},
            {'code': 'ESC001', 'name': 'EAPE - Centro de Formação', 'lat': -15.7950, 'lng': -47.8820, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
        ]
        
        for stop_data in university_stops:
            self.create_stop_if_not_exists(stop_data)

    def add_government_stops(self):
        """Adiciona paradas de órgãos governamentais e administrativos."""
        government_stops = [
            {'code': 'GOV004', 'name': 'Tribunal Superior Eleitoral', 'lat': -15.8020, 'lng': -47.8650, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'GOV005', 'name': 'Tribunal de Contas da União', 'lat': -15.8040, 'lng': -47.8680, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'GOV006', 'name': 'Ministério da Fazenda', 'lat': -15.8000, 'lng': -47.8580, 'neighborhood': 'Plano Piloto', 'type': 'Parada'},
            {'code': 'GOV007', 'name': 'Ministério da Educação', 'lat': -15.7980, 'lng': -47.8560, 'neighborhood': 'Plano Piloto', 'type': 'Parada'},
            {'code': 'GOV008', 'name': 'Ministério da Saúde', 'lat': -15.7960, 'lng': -47.8540, 'neighborhood': 'Plano Piloto', 'type': 'Parada'},
            {'code': 'GDF001', 'name': 'Palácio do Buriti', 'lat': -15.7950, 'lng': -47.8720, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'GDF002', 'name': 'Complexo da Polícia Civil', 'lat': -15.7880, 'lng': -47.8780, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'GDF003', 'name': 'Detran - Sede', 'lat': -15.8120, 'lng': -47.8920, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
        ]
        
        for stop_data in government_stops:
            self.create_stop_if_not_exists(stop_data)

    def add_transport_hubs(self):
        """Adiciona estações de transporte e terminais importantes."""
        transport_stops = [
            {'code': 'MET001', 'name': 'Estação Galeria - Metrô', 'lat': -15.7940, 'lng': -47.8870, 'neighborhood': 'Asa Sul', 'type': 'Estação'},
            {'code': 'MET002', 'name': 'Estação 102 Sul - Metrô', 'lat': -15.8070, 'lng': -47.8910, 'neighborhood': 'Asa Sul', 'type': 'Estação'},
            {'code': 'MET003', 'name': 'Estação 104 Sul - Metrô', 'lat': -15.8100, 'lng': -47.8890, 'neighborhood': 'Asa Sul', 'type': 'Estação'},
            {'code': 'MET004', 'name': 'Estação 106 Sul - Metrô', 'lat': -15.8130, 'lng': -47.8870, 'neighborhood': 'Asa Sul', 'type': 'Estação'},
            {'code': 'MET005', 'name': 'Estação Águas Claras - Metrô', 'lat': -15.8350, 'lng': -47.9420, 'neighborhood': 'Águas Claras', 'type': 'Terminal'},
            {'code': 'MET006', 'name': 'Estação Feira - Águas Claras', 'lat': -15.8320, 'lng': -47.9380, 'neighborhood': 'Águas Claras', 'type': 'Estação'},
            {'code': 'TER004', 'name': 'Terminal Guará', 'lat': -15.8350, 'lng': -47.9150, 'neighborhood': 'Guará', 'type': 'Terminal'},
            {'code': 'TER005', 'name': 'Terminal Águas Claras', 'lat': -15.8380, 'lng': -47.9450, 'neighborhood': 'Águas Claras', 'type': 'Terminal'},
        ]
        
        for stop_data in transport_stops:
            self.create_stop_if_not_exists(stop_data)

    def add_residential_stops(self):
        """Adiciona paradas em áreas residenciais importantes."""
        residential_stops = [
            # Lago Norte
            {'code': 'LN001', 'name': 'Lago Norte - SHIN QL 1', 'lat': -15.7380, 'lng': -47.8320, 'neighborhood': 'Lago Norte', 'type': 'Parada'},
            {'code': 'LN002', 'name': 'Lago Norte - SHIN QL 5', 'lat': -15.7320, 'lng': -47.8280, 'neighborhood': 'Lago Norte', 'type': 'Parada'},
            {'code': 'LN003', 'name': 'Lago Norte - SHIN QL 10', 'lat': -15.7280, 'lng': -47.8240, 'neighborhood': 'Lago Norte', 'type': 'Parada'},
            
            # Lago Sul
            {'code': 'LS001', 'name': 'Lago Sul - SHIS QI 3', 'lat': -15.8280, 'lng': -47.8520, 'neighborhood': 'Lago Sul', 'type': 'Parada'},
            {'code': 'LS002', 'name': 'Lago Sul - SHIS QI 7', 'lat': -15.8320, 'lng': -47.8480, 'neighborhood': 'Lago Sul', 'type': 'Parada'},
            {'code': 'LS003', 'name': 'Lago Sul - SHIS QI 11', 'lat': -15.8380, 'lng': -47.8420, 'neighborhood': 'Lago Sul', 'type': 'Parada'},
            
            # Guará I e II
            {'code': 'GUA001', 'name': 'Guará I - QE 1', 'lat': -15.8250, 'lng': -47.9120, 'neighborhood': 'Guará', 'type': 'Parada'},
            {'code': 'GUA002', 'name': 'Guará I - QE 5', 'lat': -15.8280, 'lng': -47.9080, 'neighborhood': 'Guará', 'type': 'Parada'},
            {'code': 'GUA003', 'name': 'Guará II - QE 15', 'lat': -15.8380, 'lng': -47.9180, 'neighborhood': 'Guará', 'type': 'Parada'},
            {'code': 'GUA004', 'name': 'Guará II - QE 20', 'lat': -15.8420, 'lng': -47.9220, 'neighborhood': 'Guará', 'type': 'Parada'},
            
            # Sudoeste/Octogonal
            {'code': 'OCT001', 'name': 'Sudoeste - SQSW 101', 'lat': -15.7950, 'lng': -47.9120, 'neighborhood': 'Sudoeste', 'type': 'Parada'},
            {'code': 'OCT002', 'name': 'Sudoeste - SQSW 105', 'lat': -15.7980, 'lng': -47.9150, 'neighborhood': 'Sudoeste', 'type': 'Parada'},
            {'code': 'OCT003', 'name': 'Octogonal - QI 1', 'lat': -15.8080, 'lng': -47.9250, 'neighborhood': 'Octogonal', 'type': 'Parada'},
        ]
        
        for stop_data in residential_stops:
            self.create_stop_if_not_exists(stop_data)

    def add_commercial_stops(self):
        """Adiciona paradas em áreas comerciais importantes."""
        commercial_stops = [
            {'code': 'COM001', 'name': 'Setor Comercial Norte - SCN Q1', 'lat': -15.7850, 'lng': -47.8780, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'COM002', 'name': 'Setor Comercial Norte - SCN Q3', 'lat': -15.7870, 'lng': -47.8760, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'COM003', 'name': 'Setor Comercial Sul - SCS Q2', 'lat': -15.7980, 'lng': -47.8890, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'COM004', 'name': 'Setor Comercial Sul - SCS Q4', 'lat': -15.8000, 'lng': -47.8910, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'COM005', 'name': 'Setor Bancário Norte', 'lat': -15.7920, 'lng': -47.8820, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'COM006', 'name': 'Setor Bancário Sul', 'lat': -15.8020, 'lng': -47.8920, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'COM007', 'name': 'Setor de Autarquias Norte', 'lat': -15.7880, 'lng': -47.8700, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'COM008', 'name': 'Setor de Autarquias Sul', 'lat': -15.8050, 'lng': -47.8800, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
        ]
        
        for stop_data in commercial_stops:
            self.create_stop_if_not_exists(stop_data)

    def add_recreation_stops(self):
        """Adiciona paradas em áreas de lazer e recreação."""
        recreation_stops = [
            {'code': 'LAZ001', 'name': 'Parque da Cidade - Entrada Norte', 'lat': -15.7920, 'lng': -47.9120, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'LAZ002', 'name': 'Parque da Cidade - Entrada Sul', 'lat': -15.8120, 'lng': -47.9220, 'neighborhood': 'Asa Sul', 'type': 'Parada'},
            {'code': 'LAZ003', 'name': 'Parque Olhos d\'Água', 'lat': -15.7650, 'lng': -47.8580, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'LAZ004', 'name': 'Parque Nacional de Brasília', 'lat': -15.7200, 'lng': -47.9800, 'neighborhood': 'Noroeste', 'type': 'Parada'},
            {'code': 'LAZ005', 'name': 'Jardim Botânico', 'lat': -15.8750, 'lng': -47.8350, 'neighborhood': 'Lago Sul', 'type': 'Parada'},
            {'code': 'LAZ006', 'name': 'Pontão do Lago Sul', 'lat': -15.8450, 'lng': -47.8180, 'neighborhood': 'Lago Sul', 'type': 'Parada'},
            {'code': 'LAZ007', 'name': 'Memorial JK', 'lat': -15.7865, 'lng': -47.9060, 'neighborhood': 'Plano Piloto', 'type': 'Parada'},
            {'code': 'LAZ008', 'name': 'Torre de TV', 'lat': -15.7903, 'lng': -47.8956, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'LAZ009', 'name': 'Estádio Mané Garrincha', 'lat': -15.7833, 'lng': -47.8989, 'neighborhood': 'Asa Norte', 'type': 'Estação'},
            {'code': 'LAZ010', 'name': 'Ginásio Nilson Nelson', 'lat': -15.7850, 'lng': -47.9020, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'LAZ011', 'name': 'Centro de Convenções Ulysses Guimarães', 'lat': -15.7900, 'lng': -47.8850, 'neighborhood': 'Asa Norte', 'type': 'Parada'},
            {'code': 'LAZ012', 'name': 'Museu Nacional', 'lat': -15.7950, 'lng': -47.8600, 'neighborhood': 'Plano Piloto', 'type': 'Parada'},
        ]
        
        for stop_data in recreation_stops:
            self.create_stop_if_not_exists(stop_data)

    def print_report(self):
        """Imprime relatório da adição de paradas."""
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Paradas adicionais criadas com sucesso!\n'
                f'📍 Novas paradas: {self.stats["stops_created"]}\n'
            )
        ) 
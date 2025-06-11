"""
Management command para importar rotas e paradas de ônibus do DF via OpenStreetMap.
Utiliza a Overpass API para extrair dados colaborativos do transporte público de Brasília.
"""
import json
import time
import requests
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from routes.models import (
    TransportCompany, RouteType, BusRoute, RouteStop, Vehicle
)
from stops.models import BusStop, StopType


class Command(BaseCommand):
    help = 'Importa rotas e paradas de ônibus do DF via OpenStreetMap/Overpass API'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests.Session()
        
        # Configurar retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # URLs da Overpass API
        self.overpass_urls = [
            'https://overpass-api.de/api/interpreter',
            'https://overpass.private.coffee/api/interpreter',
            'https://overpass.openstreetmap.ru/api/interpreter'
        ]
        
        # Contadores para relatório
        self.stats = {
            'stops_created': 0,
            'stops_updated': 0,
            'routes_created': 0,
            'routes_updated': 0,
            'route_stops_created': 0,
            'companies_created': 0,
            'errors': []
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar no banco de dados',
        )
        parser.add_argument(
            '--bbox',
            type=str,
            default='-16.0,-48.5,-15.2,-47.2',
            help='Bounding box para Brasília (south,west,north,east)',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=120,
            help='Timeout em segundos para consultas à Overpass API',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.bbox = options['bbox']
        self.timeout = options['timeout']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será salva no banco')
            )
        
        try:
            self.stdout.write('Iniciando importação de dados do DF...')
            
            # Importar paradas primeiro
            self.stdout.write('1. Importando paradas de ônibus...')
            self.import_bus_stops()
            
            # Depois importar rotas
            self.stdout.write('2. Importando rotas de ônibus...')
            self.import_bus_routes()
            
            # Relatório final
            self.print_report()
            
        except Exception as e:
            self.stats['errors'].append(f'Erro geral: {str(e)}')
            raise CommandError(f'Erro durante importação: {e}')

    def overpass_query(self, query):
        """Executa query na Overpass API com fallback para múltiplos servidores."""
        for url in self.overpass_urls:
            try:
                response = self.session.post(
                    url,
                    data={'data': query},
                    timeout=self.timeout,
                    headers={'User-Agent': 'BusFeed/1.0 (Django)'}
                )
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Falha em {url}: {e}')
                )
                continue
                
        raise CommandError('Todos os servidores Overpass API falharam')

    def import_bus_stops(self):
        """Importa paradas de ônibus do OpenStreetMap."""
        query = f"""
        [out:json][timeout:{self.timeout}];
        (
          node["highway"="bus_stop"]({self.bbox});
          node["public_transport"="stop_position"]({self.bbox});
          node["public_transport"="platform"]({self.bbox});
        );
        out meta;
        """
        
        try:
            data = self.overpass_query(query)
            
            # Criar tipos de parada se não existirem
            stop_types = self.get_or_create_stop_types()
            
            with transaction.atomic():
                for element in data.get('elements', []):
                    if element['type'] != 'node':
                        continue
                        
                    self.process_bus_stop(element, stop_types)
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
        except Exception as e:
            self.stats['errors'].append(f'Erro ao importar paradas: {e}')
            self.stdout.write(self.style.ERROR(f'Erro ao importar paradas: {e}'))

    def process_bus_stop(self, element, stop_types):
        """Processa uma parada individual do OSM."""
        try:
            tags = element.get('tags', {})
            osm_id = element['id']
            
            # Determinar código da parada
            code = (
                tags.get('ref') or 
                tags.get('local_ref') or 
                f'OSM_{osm_id}'
            )
            
            # Nome da parada
            name = (
                tags.get('name') or 
                tags.get('description') or 
                f'Parada {code}'
            )
            
            # Tipo de parada baseado nas tags
            stop_type = self.determine_stop_type(tags, stop_types)
            
            # Buscar parada existente
            stop, created = BusStop.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'stop_type': stop_type,
                    'latitude': element['lat'],
                    'longitude': element['lon'],
                    'data_source': 'OpenStreetMap',
                    'wheelchair_accessible': tags.get('wheelchair') == 'yes',
                    'has_shelter': tags.get('shelter') == 'yes',
                    'has_seating': tags.get('bench') == 'yes',
                    'neighborhood': tags.get('addr:suburb', ''),
                    'reference_point': tags.get('description', ''),
                }
            )
            
            if not created:
                # Atualizar dados existentes
                stop.name = name
                stop.latitude = element['lat']
                stop.longitude = element['lon']
                stop.wheelchair_accessible = tags.get('wheelchair') == 'yes'
                stop.has_shelter = tags.get('shelter') == 'yes'
                stop.has_seating = tags.get('bench') == 'yes'
                stop.last_verification = timezone.now()
                
                if not self.dry_run:
                    stop.save()
                
                self.stats['stops_updated'] += 1
            else:
                self.stats['stops_created'] += 1
                
        except Exception as e:
            self.stats['errors'].append(f'Erro ao processar parada {osm_id}: {e}')

    def import_bus_routes(self):
        """Importa rotas de ônibus do OpenStreetMap."""
        query = f"""
        [out:json][timeout:{self.timeout}];
        (
          relation["type"="route"]["route"="bus"]({self.bbox});
          relation["type"="route"]["route"="trolleybus"]({self.bbox});
        );
        (._;>;);
        out meta;
        """
        
        try:
            data = self.overpass_query(query)
            
            # Criar empresa e tipo de rota padrão
            company = self.get_or_create_default_company()
            route_type = self.get_or_create_default_route_type()
            
            # Separar relações e elementos
            relations = []
            elements_dict = {}
            
            for element in data.get('elements', []):
                if element['type'] == 'relation':
                    relations.append(element)
                else:
                    elements_dict[element['id']] = element
            
            with transaction.atomic():
                for relation in relations:
                    self.process_bus_route(relation, elements_dict, company, route_type)
                    time.sleep(0.2)  # Rate limiting
                    
        except Exception as e:
            self.stats['errors'].append(f'Erro ao importar rotas: {e}')
            self.stdout.write(self.style.ERROR(f'Erro ao importar rotas: {e}'))

    def process_bus_route(self, relation, elements_dict, company, route_type):
        """Processa uma rota individual do OSM."""
        try:
            tags = relation.get('tags', {})
            osm_id = relation['id']
            
            # Dados básicos da rota
            route_ref = tags.get('ref', f'OSM_{osm_id}')
            route_name = tags.get('name', f'Linha {route_ref}')
            
            # Origem e destino
            from_stop = tags.get('from', '')
            to_stop = tags.get('to', '')
            
            # Buscar rota existente
            route, created = BusRoute.objects.get_or_create(
                number=route_ref,
                transport_company=company,
                defaults={
                    'name': route_name,
                    'route_type': route_type,
                    'origin_terminal': from_stop,
                    'destination_terminal': to_stop,
                    'data_source': 'OpenStreetMap',
                    'operates_weekdays': True,
                    'operates_saturdays': True,
                    'operates_sundays': tags.get('service_times:sunday') != 'no',
                    'wheelchair_accessible': tags.get('wheelchair') == 'yes',
                }
            )
            
            if created:
                self.stats['routes_created'] += 1
            else:
                self.stats['routes_updated'] += 1
                
                # Atualizar dados
                route.name = route_name
                route.origin_terminal = from_stop
                route.destination_terminal = to_stop
                route.wheelchair_accessible = tags.get('wheelchair') == 'yes'
                
                if not self.dry_run:
                    route.save()
            
            # Processar paradas da rota
            self.process_route_stops(relation, route, elements_dict)
            
        except Exception as e:
            self.stats['errors'].append(f'Erro ao processar rota {osm_id}: {e}')

    def process_route_stops(self, relation, route, elements_dict):
        """Processa as paradas de uma rota."""
        try:
            members = relation.get('members', [])
            sequence = 1
            
            # Limpar paradas existentes se não for dry-run
            if not self.dry_run:
                RouteStop.objects.filter(route=route).delete()
            
            for member in members:
                if member['type'] != 'node':
                    continue
                    
                role = member.get('role', '')
                if role not in ['stop', 'platform', '']:
                    continue
                
                node_id = member['ref']
                node = elements_dict.get(node_id)
                
                if not node:
                    continue
                
                # Buscar parada correspondente no banco
                try:
                    # Tentar encontrar por coordenadas próximas
                    lat = node['lat']
                    lon = node['lon']
                    
                    # Buffer de ~50 metros (aproximadamente)
                    lat_buffer = 0.0005
                    lon_buffer = 0.0005
                    
                    stop = BusStop.objects.filter(
                        latitude__range=(lat - lat_buffer, lat + lat_buffer),
                        longitude__range=(lon - lon_buffer, lon + lon_buffer)
                    ).first()
                    
                    if stop and not self.dry_run:
                        RouteStop.objects.create(
                            route=route,
                            stop=stop,
                            direction='ida',  # Simplificação inicial
                            sequence=sequence,
                        )
                        self.stats['route_stops_created'] += 1
                        sequence += 1
                        
                except Exception as e:
                    self.stats['errors'].append(
                        f'Erro ao processar parada {node_id} da rota {route.number}: {e}'
                    )
                    
        except Exception as e:
            self.stats['errors'].append(
                f'Erro ao processar paradas da rota {route.number}: {e}'
            )

    def get_or_create_stop_types(self):
        """Cria tipos de paradas padrão."""
        stop_types = {}
        
        types_data = [
            ('terminal', 'Terminal de Ônibus', '#FF5722'),
            ('parada', 'Parada Simples', '#2196F3'),
            ('abrigo', 'Abrigo de Ônibus', '#4CAF50'),
            ('plataforma', 'Plataforma', '#9C27B0'),
        ]
        
        for key, name, color in types_data:
            if not self.dry_run:
                stop_type, _ = StopType.objects.get_or_create(
                    name=name,
                    defaults={'color': color}
                )
                stop_types[key] = stop_type
                
        return stop_types

    def determine_stop_type(self, tags, stop_types):
        """Determina o tipo de parada baseado nas tags OSM."""
        if not stop_types:
            return None
            
        # Lógica baseada nas tags
        if tags.get('public_transport') == 'station':
            return stop_types.get('terminal')
        elif tags.get('shelter') == 'yes':
            return stop_types.get('abrigo')
        elif tags.get('public_transport') == 'platform':
            return stop_types.get('plataforma')
        else:
            return stop_types.get('parada')

    def get_or_create_default_company(self):
        """Cria empresa de transporte padrão."""
        if self.dry_run:
            return None
            
        company, created = TransportCompany.objects.get_or_create(
            name='DFTrans',
            defaults={
                'short_name': 'DF',
                'cnpj': '00.000.000/0000-00',  # CNPJ placeholder
            }
        )
        
        if created:
            self.stats['companies_created'] += 1
            
        return company

    def get_or_create_default_route_type(self):
        """Cria tipo de rota padrão."""
        if self.dry_run:
            return None
            
        route_type, _ = RouteType.objects.get_or_create(
            name='Ônibus Convencional',
            defaults={
                'description': 'Linhas de ônibus convencionais do DF',
                'color': '#2196F3',
                'fare_multiplier': Decimal('1.0'),
            }
        )
        
        return route_type

    def print_report(self):
        """Imprime relatório final da importação."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('RELATÓRIO DE IMPORTAÇÃO'))
        self.stdout.write('='*50)
        
        self.stdout.write(f'Paradas criadas: {self.stats["stops_created"]}')
        self.stdout.write(f'Paradas atualizadas: {self.stats["stops_updated"]}')
        self.stdout.write(f'Rotas criadas: {self.stats["routes_created"]}')
        self.stdout.write(f'Rotas atualizadas: {self.stats["routes_updated"]}')
        self.stdout.write(f'Relacionamentos rota-parada: {self.stats["route_stops_created"]}')
        self.stdout.write(f'Empresas criadas: {self.stats["companies_created"]}')
        
        if self.stats['errors']:
            self.stdout.write(f'\nErros encontrados: {len(self.stats["errors"])}')
            for error in self.stats['errors'][:10]:  # Mostrar apenas os primeiros 10
                self.stdout.write(self.style.ERROR(f'  - {error}'))
            
            if len(self.stats['errors']) > 10:
                self.stdout.write(f'  ... e mais {len(self.stats["errors"]) - 10} erros')
        
        self.stdout.write('\n' + '='*50) 
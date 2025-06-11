#!/usr/bin/env python
"""
Script para popular dados COMPLETOS de demonstração do BusFeed.
Inclui: Ônibus, Metrô, BRT e trajetos realistas
Execute: python populate_data.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'busfeed.settings')
django.setup()

from routes.models import BusRoute, RouteType, TransportCompany, RouteStop
from stops.models import BusStop, StopType
import random


def create_stop_types():
    """Cria tipos de paradas"""
    print("Criando tipos de paradas...")
    stop_types = [
        {'name': 'Parada Comum', 'icon': 'bus', 'color': '#007bff'},
        {'name': 'Terminal', 'icon': 'building', 'color': '#28a745'},
        {'name': 'Estação BRT', 'icon': 'train', 'color': '#dc3545'},
        {'name': 'Estação Metrô', 'icon': 'subway', 'color': '#6f42c1'},
        {'name': 'Terminal Integração', 'icon': 'arrows-split', 'color': '#fd7e14'},
    ]
    
    for data in stop_types:
        StopType.objects.get_or_create(
            name=data['name'],
            defaults={
                'icon': data['icon'],
                'color': data['color']
            }
        )
    print("✓ Tipos de paradas criados")


def create_route_types():
    """Cria tipos de rotas"""
    print("Criando tipos de rotas...")
    route_types = [
        {'name': 'Ônibus Convencional', 'color': '#007bff', 'icon': 'bus'},
        {'name': 'BRT', 'color': '#dc3545', 'icon': 'train'},
        {'name': 'Metrô', 'color': '#6f42c1', 'icon': 'subway'},
        {'name': 'Expresso', 'color': '#28a745', 'icon': 'lightning'},
        {'name': 'Circular', 'color': '#ffc107', 'icon': 'arrow-repeat'},
        {'name': 'Alimentadora', 'color': '#20c997', 'icon': 'arrow-up-right'},
    ]
    
    for data in route_types:
        RouteType.objects.get_or_create(
            name=data['name'],
            defaults={
                'color': data['color'],
                'icon': data['icon'],
                'fare_multiplier': 1.0 if data['name'] != 'Metrô' else 1.5
            }
        )
    print("✓ Tipos de rotas criados")


def create_companies():
    """Cria empresas de transporte"""
    print("Criando empresas de transporte...")
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
        {
            'name': 'Metrô do Distrito Federal',
            'short_name': 'Metrô-DF',
            'cnpj': '00.123.456/0001-78'
        },
        {
            'name': 'BRT Brasília',
            'short_name': 'BRT-BSB',
            'cnpj': '00.987.654/0001-32'
        },
    ]
    
    for data in companies:
        TransportCompany.objects.get_or_create(
            cnpj=data['cnpj'],
            defaults=data
        )
    print("✓ Empresas de transporte criadas")


def create_comprehensive_stops():
    """Cria paradas completas em Brasília - Ônibus, Metrô e BRT"""
    print("Criando paradas completas...")
    
    stops_data = [
        # ========== PLANO PILOTO ==========
        {'name': 'Rodoviária do Plano Piloto', 'code': 'ROD001', 'lat': -15.7942, 'lng': -47.8822, 'neighborhood': 'Asa Norte', 'type': 'Terminal'},
        {'name': 'Esplanada dos Ministérios', 'code': 'ESP001', 'lat': -15.7998, 'lng': -47.8645, 'neighborhood': 'Zona Cívico-Administrativa', 'type': 'Parada Comum'},
        {'name': 'Congresso Nacional', 'code': 'CON001', 'lat': -15.7998, 'lng': -47.8636, 'neighborhood': 'Zona Cívico-Administrativa', 'type': 'Parada Comum'},
        {'name': 'Palácio do Planalto', 'code': 'PAL001', 'lat': -15.7998, 'lng': -47.8608, 'neighborhood': 'Zona Cívico-Administrativa', 'type': 'Parada Comum'},
        
        # Asa Norte
        {'name': 'Shopping Brasília', 'code': 'SHB001', 'lat': -15.7817, 'lng': -47.8906, 'neighborhood': 'Asa Norte', 'type': 'Parada Comum'},
        {'name': 'UnB - Universidade de Brasília', 'code': 'UNB001', 'lat': -15.7633, 'lng': -47.8707, 'neighborhood': 'Asa Norte', 'type': 'Terminal'},
        {'name': 'SQN 108', 'code': 'SQN108', 'lat': -15.7467, 'lng': -47.8789, 'neighborhood': 'Asa Norte', 'type': 'Parada Comum'},
        {'name': 'SQN 208', 'code': 'SQN208', 'lat': -15.7517, 'lng': -47.8789, 'neighborhood': 'Asa Norte', 'type': 'Parada Comum'},
        {'name': 'SQN 308', 'code': 'SQN308', 'lat': -15.7567, 'lng': -47.8789, 'neighborhood': 'Asa Norte', 'type': 'Parada Comum'},
        {'name': 'SQN 408', 'code': 'SQN408', 'lat': -15.7617, 'lng': -47.8789, 'neighborhood': 'Asa Norte', 'type': 'Parada Comum'},
        {'name': 'W3 Norte - 508/509', 'code': 'W3N508', 'lat': -15.7608, 'lng': -47.8889, 'neighborhood': 'Asa Norte', 'type': 'Parada Comum'},
        {'name': 'W3 Norte - 708/709', 'code': 'W3N708', 'lat': -15.7708, 'lng': -47.8889, 'neighborhood': 'Asa Norte', 'type': 'Parada Comum'},
        
        # Asa Sul
        {'name': 'Hospital de Base', 'code': 'HBB001', 'lat': -15.7808, 'lng': -47.9267, 'neighborhood': 'Asa Sul', 'type': 'Terminal'},
        {'name': 'SQS 108', 'code': 'SQS108', 'lat': -15.8067, 'lng': -47.8789, 'neighborhood': 'Asa Sul', 'type': 'Parada Comum'},
        {'name': 'SQS 208', 'code': 'SQS208', 'lat': -15.8117, 'lng': -47.8789, 'neighborhood': 'Asa Sul', 'type': 'Parada Comum'},
        {'name': 'SQS 308', 'code': 'SQS308', 'lat': -15.8167, 'lng': -47.8789, 'neighborhood': 'Asa Sul', 'type': 'Parada Comum'},
        {'name': 'W3 Sul - 508/509', 'code': 'W3S508', 'lat': -15.8208, 'lng': -47.8889, 'neighborhood': 'Asa Sul', 'type': 'Parada Comum'},
        {'name': 'Shopping Conjunto Nacional', 'code': 'CNB001', 'lat': -15.8167, 'lng': -47.8900, 'neighborhood': 'Asa Sul', 'type': 'Parada Comum'},
        
        # Eixos e Vias Principais
        {'name': 'EPNB - Via L2 Norte', 'code': 'L2N001', 'lat': -15.7500, 'lng': -47.8600, 'neighborhood': 'Asa Norte', 'type': 'Parada Comum'},
        {'name': 'EPNB - Via L2 Sul', 'code': 'L2S001', 'lat': -15.8200, 'lng': -47.8600, 'neighborhood': 'Asa Sul', 'type': 'Parada Comum'},
        {'name': 'EPNB - Via L4 Norte', 'code': 'L4N001', 'lat': -15.7400, 'lng': -47.8400, 'neighborhood': 'Asa Norte', 'type': 'Parada Comum'},
        {'name': 'EPNB - Via L4 Sul', 'code': 'L4S001', 'lat': -15.8300, 'lng': -47.8400, 'neighborhood': 'Asa Sul', 'type': 'Parada Comum'},
        
        # ========== TAGUATINGA ==========
        {'name': 'Centro de Taguatinga', 'code': 'TAG001', 'lat': -15.8267, 'lng': -48.0583, 'neighborhood': 'Taguatinga Centro', 'type': 'Terminal'},
        {'name': 'Shopping Taguatinga', 'code': 'SHT001', 'lat': -15.8389, 'lng': -48.0506, 'neighborhood': 'Taguatinga Norte', 'type': 'Parada Comum'},
        {'name': 'Terminal Taguatinga', 'code': 'TER001', 'lat': -15.8333, 'lng': -48.0500, 'neighborhood': 'Taguatinga Centro', 'type': 'Terminal'},
        {'name': 'Pistão Sul Taguatinga', 'code': 'TAG002', 'lat': -15.8350, 'lng': -48.0600, 'neighborhood': 'Taguatinga Sul', 'type': 'Parada Comum'},
        {'name': 'QNM Taguatinga', 'code': 'TAG003', 'lat': -15.8150, 'lng': -48.0450, 'neighborhood': 'Taguatinga Norte', 'type': 'Parada Comum'},
        {'name': 'Hospital Regional Taguatinga', 'code': 'HRT001', 'lat': -15.8283, 'lng': -48.0472, 'neighborhood': 'Taguatinga Norte', 'type': 'Parada Comum'},
        {'name': 'Taguatinga Shopping', 'code': 'TSH001', 'lat': -15.8394, 'lng': -48.0525, 'neighborhood': 'Taguatinga Norte', 'type': 'Parada Comum'},
        
        # ========== CEILÂNDIA ==========
        {'name': 'Centro de Ceilândia', 'code': 'CEI001', 'lat': -15.8167, 'lng': -48.1067, 'neighborhood': 'Ceilândia Centro', 'type': 'Terminal'},
        {'name': 'Terminal Ceilândia', 'code': 'TER002', 'lat': -15.8200, 'lng': -48.1100, 'neighborhood': 'Ceilândia Centro', 'type': 'Terminal'},
        {'name': 'QNM Ceilândia', 'code': 'CEI002', 'lat': -15.8100, 'lng': -48.1000, 'neighborhood': 'Ceilândia Norte', 'type': 'Parada Comum'},
        {'name': 'P Sul Ceilândia', 'code': 'CEI003', 'lat': -15.8250, 'lng': -48.1150, 'neighborhood': 'Ceilândia Sul', 'type': 'Parada Comum'},
        {'name': 'Shopping Ceilândia', 'code': 'SHC001', 'lat': -15.8178, 'lng': -48.1089, 'neighborhood': 'Ceilândia Centro', 'type': 'Parada Comum'},
        
        # ========== SAMAMBAIA ==========
        {'name': 'Centro de Samambaia', 'code': 'SAM001', 'lat': -15.8783, 'lng': -48.0944, 'neighborhood': 'Samambaia Norte', 'type': 'Terminal'},
        {'name': 'Terminal Samambaia', 'code': 'TER003', 'lat': -15.8800, 'lng': -48.0950, 'neighborhood': 'Samambaia Norte', 'type': 'Terminal'},
        {'name': 'QR Samambaia', 'code': 'SAM002', 'lat': -15.8850, 'lng': -48.0800, 'neighborhood': 'Samambaia Sul', 'type': 'Parada Comum'},
        
        # ========== ÁGUAS CLARAS ==========
        {'name': 'Centro de Águas Claras', 'code': 'AGC001', 'lat': -15.8344, 'lng': -48.0267, 'neighborhood': 'Águas Claras', 'type': 'Terminal'},
        {'name': 'Shopping Águas Claras', 'code': 'SHA001', 'lat': -15.8356, 'lng': -48.0289, 'neighborhood': 'Águas Claras', 'type': 'Parada Comum'},
        {'name': 'Estação Águas Claras', 'code': 'AGC002', 'lat': -15.8400, 'lng': -48.0200, 'neighborhood': 'Águas Claras', 'type': 'Estação Metrô'},
        
        # ========== GUARÁ ==========
        {'name': 'Centro do Guará', 'code': 'GUA001', 'lat': -15.8267, 'lng': -47.9667, 'neighborhood': 'Guará I', 'type': 'Terminal'},
        {'name': 'Shopping Guará', 'code': 'SHG001', 'lat': -15.8300, 'lng': -47.9700, 'neighborhood': 'Guará II', 'type': 'Parada Comum'},
        {'name': 'QE Guará', 'code': 'GUA002', 'lat': -15.8200, 'lng': -47.9600, 'neighborhood': 'Guará I', 'type': 'Parada Comum'},
        
        # ========== SOBRADINHO ==========
        {'name': 'Centro de Sobradinho', 'code': 'SOB001', 'lat': -15.6533, 'lng': -47.7867, 'neighborhood': 'Sobradinho', 'type': 'Terminal'},
        {'name': 'Quadra Central Sobradinho', 'code': 'SOB002', 'lat': -15.6600, 'lng': -47.7900, 'neighborhood': 'Sobradinho', 'type': 'Parada Comum'},
        {'name': 'Hospital Regional Sobradinho', 'code': 'HRS001', 'lat': -15.6550, 'lng': -47.7850, 'neighborhood': 'Sobradinho', 'type': 'Parada Comum'},
        
        # ========== PLANALTINA ==========
        {'name': 'Centro de Planaltina', 'code': 'PLA001', 'lat': -15.6167, 'lng': -47.6533, 'neighborhood': 'Planaltina', 'type': 'Terminal'},
        {'name': 'Setor Tradicional Planaltina', 'code': 'PLA002', 'lat': -15.6200, 'lng': -47.6600, 'neighborhood': 'Planaltina', 'type': 'Parada Comum'},
        {'name': 'Hospital Regional Planaltina', 'code': 'HRP001', 'lat': -15.6183, 'lng': -47.6567, 'neighborhood': 'Planaltina', 'type': 'Parada Comum'},
        
        # ========== GAMA ==========
        {'name': 'Centro do Gama', 'code': 'GAM001', 'lat': -16.0167, 'lng': -48.0650, 'neighborhood': 'Gama', 'type': 'Terminal'},
        {'name': 'Shopping do Gama', 'code': 'SHG002', 'lat': -16.0200, 'lng': -48.0683, 'neighborhood': 'Gama', 'type': 'Parada Comum'},
        {'name': 'Hospital Regional Gama', 'code': 'HRG001', 'lat': -16.0150, 'lng': -48.0617, 'neighborhood': 'Gama', 'type': 'Parada Comum'},
        
        # ========== SANTA MARIA ==========
        {'name': 'Centro de Santa Maria', 'code': 'STM001', 'lat': -16.0033, 'lng': -48.0167, 'neighborhood': 'Santa Maria', 'type': 'Terminal'},
        {'name': 'Shopping Santa Maria', 'code': 'SHS001', 'lat': -16.0067, 'lng': -48.0200, 'neighborhood': 'Santa Maria', 'type': 'Parada Comum'},
        
        # ========== RECANTO DAS EMAS ==========
        {'name': 'Centro Recanto das Emas', 'code': 'REC001', 'lat': -15.9000, 'lng': -48.0667, 'neighborhood': 'Recanto das Emas', 'type': 'Terminal'},
        {'name': 'Shopping Recanto', 'code': 'SHR001', 'lat': -15.9033, 'lng': -48.0700, 'neighborhood': 'Recanto das Emas', 'type': 'Parada Comum'},
        
        # ========== BRAZLÂNDIA ==========
        {'name': 'Centro de Brazlândia', 'code': 'BRZ001', 'lat': -15.6667, 'lng': -48.2000, 'neighborhood': 'Brazlândia', 'type': 'Terminal'},
        {'name': 'Setor Norte Brazlândia', 'code': 'BRZ002', 'lat': -15.6633, 'lng': -48.1967, 'neighborhood': 'Brazlândia', 'type': 'Parada Comum'},
        
        # ========== ESTAÇÕES DE METRÔ ==========
        {'name': 'Estação Central - Metrô', 'code': 'MET001', 'lat': -15.7942, 'lng': -47.8822, 'neighborhood': 'Asa Norte', 'type': 'Estação Metrô'},
        {'name': 'Estação Galeria - Metrô', 'code': 'MET002', 'lat': -15.7900, 'lng': -47.8850, 'neighborhood': 'Asa Norte', 'type': 'Estação Metrô'},
        {'name': 'Estação 108 Sul - Metrô', 'code': 'MET003', 'lat': -15.8067, 'lng': -47.8789, 'neighborhood': 'Asa Sul', 'type': 'Estação Metrô'},
        {'name': 'Estação 114 Sul - Metrô', 'code': 'MET004', 'lat': -15.8117, 'lng': -47.8789, 'neighborhood': 'Asa Sul', 'type': 'Estação Metrô'},
        {'name': 'Estação Shopping - Metrô', 'code': 'MET005', 'lat': -15.8389, 'lng': -48.0506, 'neighborhood': 'Taguatinga Norte', 'type': 'Estação Metrô'},
        {'name': 'Estação Taguatinga Centro - Metrô', 'code': 'MET006', 'lat': -15.8267, 'lng': -48.0583, 'neighborhood': 'Taguatinga Centro', 'type': 'Estação Metrô'},
        {'name': 'Estação Furnas - Metrô', 'code': 'MET007', 'lat': -15.8150, 'lng': -48.0450, 'neighborhood': 'Taguatinga Norte', 'type': 'Estação Metrô'},
        {'name': 'Estação Samambaia - Metrô', 'code': 'MET008', 'lat': -15.8783, 'lng': -48.0944, 'neighborhood': 'Samambaia Norte', 'type': 'Estação Metrô'},
        
        # ========== ESTAÇÕES BRT ==========
        {'name': 'Estação BRT Asa Sul', 'code': 'BRT001', 'lat': -15.8200, 'lng': -47.8600, 'neighborhood': 'Asa Sul', 'type': 'Estação BRT'},
        {'name': 'Estação BRT Guará', 'code': 'BRT002', 'lat': -15.8267, 'lng': -47.9667, 'neighborhood': 'Guará I', 'type': 'Estação BRT'},
        {'name': 'Estação BRT Águas Claras', 'code': 'BRT003', 'lat': -15.8344, 'lng': -48.0267, 'neighborhood': 'Águas Claras', 'type': 'Estação BRT'},
        {'name': 'Estação BRT Taguatinga', 'code': 'BRT004', 'lat': -15.8267, 'lng': -48.0583, 'neighborhood': 'Taguatinga Centro', 'type': 'Estação BRT'},
        {'name': 'Estação BRT Ceilândia', 'code': 'BRT005', 'lat': -15.8167, 'lng': -48.1067, 'neighborhood': 'Ceilândia Centro', 'type': 'Estação BRT'},
    ]
    
    for data in stops_data:
        stop_type, _ = StopType.objects.get_or_create(name=data['type'])
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
                'has_lighting': True,
                'has_security': data['type'] in ['Terminal', 'Estação Metrô', 'Estação BRT'],
            }
        )
    print("✓ Paradas completas criadas")


def create_comprehensive_routes():
    """Cria sistema completo de rotas - Ônibus, Metrô e BRT"""
    print("Criando rotas completas...")
    
    # Buscar tipos e empresas
    bus_type = RouteType.objects.get(name='Ônibus Convencional')
    metro_type = RouteType.objects.get(name='Metrô')
    brt_type = RouteType.objects.get(name='BRT')
    express_type = RouteType.objects.get(name='Expresso')
    circular_type = RouteType.objects.get(name='Circular')
    
    bus_company = TransportCompany.objects.get(short_name='Pioneira')
    metro_company = TransportCompany.objects.get(short_name='Metrô-DF')
    brt_company = TransportCompany.objects.get(short_name='BRT-BSB')
    
    routes_data = [
        # ========== LINHAS DE METRÔ ==========
        {
            'number': 'METRÔ-VERDE',
            'name': 'Linha Verde - Samambaia ↔ Central',
            'origin_terminal': 'Estação Samambaia - Metrô',
            'destination_terminal': 'Estação Central - Metrô',
            'route_type': metro_type,
            'company': metro_company,
            'base_fare': 4.50,
            'color': '#28a745',
        },
        {
            'number': 'METRÔ-LARANJA',
            'name': 'Linha Laranja - Ceilândia ↔ Central',
            'origin_terminal': 'Terminal Ceilândia',
            'destination_terminal': 'Estação Central - Metrô',
            'route_type': metro_type,
            'company': metro_company,
            'base_fare': 4.50,
            'color': '#fd7e14',
        },
        
        # ========== LINHAS BRT ==========
        {
            'number': 'BRT-01',
            'name': 'BRT Eixo Sul - Gama ↔ Asa Sul',
            'origin_terminal': 'Centro do Gama',
            'destination_terminal': 'Estação BRT Asa Sul',
            'route_type': brt_type,
            'company': brt_company,
            'base_fare': 4.00,
            'color': '#dc3545',
        },
        {
            'number': 'BRT-02',
            'name': 'BRT Eixo Oeste - Ceilândia ↔ Águas Claras',
            'origin_terminal': 'Estação BRT Ceilândia',
            'destination_terminal': 'Estação BRT Águas Claras',
            'route_type': brt_type,
            'company': brt_company,
            'base_fare': 4.00,
            'color': '#dc3545',
        },
        
        # ========== LINHAS EXPRESSAS ==========
        {
            'number': 'EXP-101',
            'name': 'Expresso Aeroporto - Rodoviária ↔ Aeroporto',
            'origin_terminal': 'Rodoviária do Plano Piloto',
            'destination_terminal': 'Aeroporto Internacional',
            'route_type': express_type,
            'company': bus_company,
            'base_fare': 8.00,
            'color': '#28a745',
        },
        
        # ========== LINHAS CONVENCIONAIS PRINCIPAIS ==========
        {
            'number': '0.101',
            'name': 'Rodoviária - Taguatinga',
            'origin_terminal': 'Rodoviária do Plano Piloto',
            'destination_terminal': 'Terminal Taguatinga',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 5.50,
            'color': '#007bff',
        },
        {
            'number': '0.102',
            'name': 'Rodoviária - Ceilândia',
            'origin_terminal': 'Rodoviária do Plano Piloto',
            'destination_terminal': 'Terminal Ceilândia',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 5.50,
            'color': '#007bff',
        },
        {
            'number': '0.103',
            'name': 'Rodoviária - Samambaia',
            'origin_terminal': 'Rodoviária do Plano Piloto',
            'destination_terminal': 'Terminal Samambaia',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 5.50,
            'color': '#007bff',
        },
        {
            'number': '0.104',
            'name': 'UnB - Taguatinga',
            'origin_terminal': 'UnB - Universidade de Brasília',
            'destination_terminal': 'Centro de Taguatinga',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 5.50,
            'color': '#007bff',
        },
        {
            'number': '0.105',
            'name': 'Águas Claras - Plano Piloto',
            'origin_terminal': 'Centro de Águas Claras',
            'destination_terminal': 'Esplanada dos Ministérios',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 5.50,
            'color': '#007bff',
        },
        {
            'number': '0.106',
            'name': 'Guará - Rodoviária',
            'origin_terminal': 'Centro do Guará',
            'destination_terminal': 'Rodoviária do Plano Piloto',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 5.50,
            'color': '#007bff',
        },
        {
            'number': '0.107',
            'name': 'Sobradinho - Plano Piloto',
            'origin_terminal': 'Centro de Sobradinho',
            'destination_terminal': 'Rodoviária do Plano Piloto',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 6.00,
            'color': '#007bff',
        },
        {
            'number': '0.108',
            'name': 'Planaltina - Plano Piloto',
            'origin_terminal': 'Centro de Planaltina',
            'destination_terminal': 'Rodoviária do Plano Piloto',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 6.50,
            'color': '#007bff',
        },
        {
            'number': '0.109',
            'name': 'Gama - Plano Piloto',
            'origin_terminal': 'Centro do Gama',
            'destination_terminal': 'Rodoviária do Plano Piloto',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 6.50,
            'color': '#007bff',
        },
        {
            'number': '0.110',
            'name': 'Santa Maria - Plano Piloto',
            'origin_terminal': 'Centro de Santa Maria',
            'destination_terminal': 'Rodoviária do Plano Piloto',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 6.00,
            'color': '#007bff',
        },
        {
            'number': '0.111',
            'name': 'Recanto das Emas - Samambaia',
            'origin_terminal': 'Centro Recanto das Emas',
            'destination_terminal': 'Terminal Samambaia',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 5.50,
            'color': '#007bff',
        },
        {
            'number': '0.112',
            'name': 'Brazlândia - Taguatinga',
            'origin_terminal': 'Centro de Brazlândia',
            'destination_terminal': 'Terminal Taguatinga',
            'route_type': bus_type,
            'company': bus_company,
            'base_fare': 6.00,
            'color': '#007bff',
        },
        
        # ========== LINHAS CIRCULARES ==========
        {
            'number': 'CIRC-01',
            'name': 'Circular Asa Norte',
            'origin_terminal': 'Rodoviária do Plano Piloto',
            'destination_terminal': 'Rodoviária do Plano Piloto',
            'route_type': circular_type,
            'company': bus_company,
            'base_fare': 4.50,
            'color': '#ffc107',
        },
        {
            'number': 'CIRC-02',
            'name': 'Circular Asa Sul',
            'origin_terminal': 'Rodoviária do Plano Piloto',
            'destination_terminal': 'Rodoviária do Plano Piloto',
            'route_type': circular_type,
            'company': bus_company,
            'base_fare': 4.50,
            'color': '#ffc107',
        },
    ]
    
    for data in routes_data:
        BusRoute.objects.get_or_create(
            number=data['number'],
            defaults={
                'name': data['name'],
                'origin_terminal': data['origin_terminal'],
                'destination_terminal': data['destination_terminal'],
                'route_type': data['route_type'],
                'transport_company': data['company'],
                'base_fare': data['base_fare'],
                'wheelchair_accessible': True,
                'operates_weekdays': True,
                'operates_saturdays': True,
                'operates_sundays': data['route_type'].name in ['Metrô', 'BRT'],
                'average_frequency': 15 if data['route_type'].name in ['Metrô', 'BRT'] else random.randint(15, 45),
                'estimated_duration': 30 if data['route_type'].name == 'Metrô' else random.randint(45, 120),
                'is_circular': 'CIRC' in data['number'],
            }
        )
    print("✓ Rotas completas criadas")


def create_realistic_trajectories():
    """Cria trajetos realistas para todas as rotas"""
    print("Criando trajetos realistas...")
    
    # Definir trajetos específicos detalhados
    route_trajectories = {
        # ===== METRÔ =====
        'METRÔ-VERDE': ['MET008', 'MET007', 'MET006', 'MET005', 'AGC002', 'GUA001', 'L2S001', 'MET003', 'MET004', 'MET002', 'MET001'],
        'METRÔ-LARANJA': ['TER002', 'CEI001', 'BRT005', 'BRT004', 'TAG001', 'MET006', 'MET005', 'AGC002', 'L2S001', 'MET001'],
        
        # ===== BRT =====
        'BRT-01': ['GAM001', 'SHG002', 'STM001', 'SHS001', 'GUA001', 'BRT002', 'L2S001', 'BRT001'],
        'BRT-02': ['BRT005', 'CEI001', 'TER002', 'TAG001', 'BRT004', 'AGC001', 'BRT003'],
        
        # ===== EXPRESSO =====
        'EXP-101': ['ROD001', 'L2N001', 'UNB001', 'L4N001'],  # Simulando aeroporto
        
        # ===== ÔNIBUS CONVENCIONAIS =====
        '0.101': ['ROD001', 'ESP001', 'L2N001', 'W3N508', 'SQN308', 'UNB001', 'L4N001', 'AGC001', 'SHA001', 'TAG001', 'SHT001', 'TER001'],
        '0.102': ['ROD001', 'ESP001', 'L2N001', 'W3N508', 'UNB001', 'AGC001', 'TAG001', 'CEI002', 'CEI001', 'TER002'],
        '0.103': ['ROD001', 'ESP001', 'CON001', 'W3S508', 'GUA001', 'AGC001', 'TAG001', 'SAM002', 'SAM001', 'TER003'],
        '0.104': ['UNB001', 'SQN408', 'SQN308', 'L2N001', 'AGC001', 'SHA001', 'TAG003', 'TAG001'],
        '0.105': ['AGC001', 'SHA001', 'BRT003', 'GUA001', 'SHG001', 'W3S508', 'L2S001', 'ESP001', 'CON001'],
        '0.106': ['GUA001', 'SHG001', 'GUA002', 'W3S508', 'SQS308', 'L2S001', 'ESP001', 'ROD001'],
        '0.107': ['SOB001', 'SOB002', 'HRS001', 'L4N001', 'SQN308', 'W3N508', 'L2N001', 'ROD001'],
        '0.108': ['PLA001', 'PLA002', 'HRP001', 'L4N001', 'UNB001', 'L2N001', 'W3N508', 'ROD001'],
        '0.109': ['GAM001', 'SHG002', 'HRG001', 'STM001', 'GUA001', 'L2S001', 'ESP001', 'ROD001'],
        '0.110': ['STM001', 'SHS001', 'GAM001', 'GUA001', 'L2S001', 'W3S508', 'ESP001', 'ROD001'],
        '0.111': ['REC001', 'SHR001', 'SAM002', 'SAM001', 'TER003'],
        '0.112': ['BRZ001', 'BRZ002', 'TAG003', 'TAG001', 'TER001'],
        
        # ===== CIRCULARES =====
        'CIRC-01': ['ROD001', 'L2N001', 'UNB001', 'SQN408', 'SQN308', 'SQN208', 'SQN108', 'W3N508', 'W3N708', 'SHB001', 'ROD001'],
        'CIRC-02': ['ROD001', 'ESP001', 'L2S001', 'SQS108', 'SQS208', 'SQS308', 'W3S508', 'CNB001', 'HBB001', 'ROD001'],
    }
    
    for route in BusRoute.objects.all():
        trajectory = route_trajectories.get(route.number, [])
        
        if not trajectory:
            continue
            
        # Limpar trajetos existentes
        RouteStop.objects.filter(route=route).delete()
        
        # Usar trajeto específico
        route_stops = []
        for stop_code in trajectory:
            try:
                stop = BusStop.objects.get(code=stop_code)
                route_stops.append(stop)
            except BusStop.DoesNotExist:
                print(f"⚠️ Parada {stop_code} não encontrada para rota {route.number}")
                continue
        
        if not route_stops:
            continue
            
        # Criar associações para ida
        for i, stop in enumerate(route_stops):
            distance = i * (3.0 if route.route_type.name == 'Metrô' else 2.5 if route.route_type.name == 'BRT' else 2.0)
            time_origin = i * (8 if route.route_type.name == 'Metrô' else 6 if route.route_type.name == 'BRT' else 10)
            
            RouteStop.objects.get_or_create(
                route=route,
                stop=stop,
                direction='ida',
                sequence=i + 1,
                defaults={
                    'distance_from_origin': distance,
                    'estimated_time_from_origin': time_origin,
                }
            )
            
        # Criar associações para volta (não para circulares)
        if not route.is_circular:
            for i, stop in enumerate(reversed(route_stops)):
                distance = i * (3.0 if route.route_type.name == 'Metrô' else 2.5 if route.route_type.name == 'BRT' else 2.0)
                time_origin = i * (8 if route.route_type.name == 'Metrô' else 6 if route.route_type.name == 'BRT' else 10)
                
                RouteStop.objects.get_or_create(
                    route=route,
                    stop=stop,
                    direction='volta',
                    sequence=i + 1,
                    defaults={
                        'distance_from_origin': distance,
                        'estimated_time_from_origin': time_origin,
                    }
                )
    
    print("✓ Trajetos realistas criados")


def main():
    """Função principal"""
    print("🚌 Populando sistema COMPLETO do BusFeed...")
    print("🚇 Incluindo: Ônibus, Metrô, BRT e Trajetos Realistas")
    print("=" * 60)
    
    try:
        create_stop_types()
        create_route_types()
        create_companies()
        create_comprehensive_stops()
        create_comprehensive_routes()
        create_realistic_trajectories()
        
        print("=" * 60)
        print("✅ Sistema COMPLETO criado com sucesso!")
        print(f"📊 Estatísticas Finais:")
        print(f"   - Tipos de paradas: {StopType.objects.count()}")
        print(f"   - Tipos de rotas: {RouteType.objects.count()}")
        print(f"   - Empresas: {TransportCompany.objects.count()}")
        print(f"   - Paradas: {BusStop.objects.count()}")
        print(f"   - Rotas: {BusRoute.objects.count()}")
        print(f"   - Associações rota-parada: {RouteStop.objects.count()}")
        print("\n🌐 Acesse: http://localhost:8000/rotas/")
        print("🗺️ Mapa: http://localhost:8000/rotas/mapa/")
        print("🕒 Horários: http://localhost:8000/horarios/")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main() 
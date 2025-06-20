"""
Comando para popular o banco de dados com dados mock para desenvolvimento

Este comando cria dados de teste representativos do sistema de transporte
público do Distrito Federal, incluindo paradas, linhas e relacionamentos.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import logging

from paradas.models import Parada, TipoParada
from linhas.models import Linha, LinhaParada, TipoLinha, StatusLinha


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados mock para desenvolvimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa todos os dados existentes antes de popular'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas durante a execução'
        )

    def handle(self, *args, **options):
        """Executa o comando de população de dados"""
        
        if options['verbose']:
            self.stdout.write(
                self.style.SUCCESS('🚌 Iniciando população de dados mock do BusFeed...')
            )

        try:
            with transaction.atomic():
                # Limpa dados existentes se solicitado
                if options['limpar']:
                    self._limpar_dados(options['verbose'])
                
                # Cria dados mock
                paradas = self._criar_paradas_mock(options['verbose'])
                linhas = self._criar_linhas_mock(options['verbose'])
                self._criar_relacionamentos_mock(paradas, linhas, options['verbose'])
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Dados mock criados com sucesso!')
                )
                self._exibir_estatisticas(options['verbose'])
                
        except Exception as e:
            logger.error(f"Erro ao popular dados mock: {e}")
            raise CommandError(f'Erro ao popular dados: {e}')

    def _limpar_dados(self, verbose=False):
        """Remove todos os dados existentes"""
        if verbose:
            self.stdout.write('🧹 Limpando dados existentes...')
        
        # Remove relacionamentos primeiro (devido às foreign keys)
        LinhaParada.objects.all().delete()
        Linha.objects.all().delete()
        Parada.objects.all().delete()
        
        if verbose:
            self.stdout.write('✅ Dados limpos com sucesso')

    def _criar_paradas_mock(self, verbose=False):
        """Cria paradas mock baseadas em locais reais do DF"""
        if verbose:
            self.stdout.write('📍 Criando paradas mock...')
        
        paradas_data = [
            # Terminais principais
            {
                'codigo_dftrans': 'T001',
                'nome': 'Terminal Rodoviário do Plano Piloto',
                'descricao': 'Terminal central de ônibus do Plano Piloto',
                'latitude': -15.7942,
                'longitude': -47.8822,
                'endereco': 'Eixo Monumental, Brasília - DF',
                'tipo': TipoParada.TERMINAL,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 5000,
                'pontos_referencia': 'Próximo ao Shopping Conjunto Nacional, Torre de TV'
            },
            {
                'codigo_dftrans': 'T002',
                'nome': 'Terminal Ceilândia Centro',
                'descricao': 'Terminal principal da Ceilândia',
                'latitude': -15.8267,
                'longitude': -48.1089,
                'endereco': 'QNM 13, Ceilândia Norte - DF',
                'tipo': TipoParada.TERMINAL,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 3500,
                'pontos_referencia': 'Centro da Ceilândia, próximo ao comércio'
            },
            {
                'codigo_dftrans': 'T003',
                'nome': 'Terminal Taguatinga',
                'descricao': 'Terminal de ônibus de Taguatinga',
                'latitude': -15.8311,
                'longitude': -48.0428,
                'endereco': 'Pistão Sul, Taguatinga - DF',
                'tipo': TipoParada.TERMINAL,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 4000,
                'pontos_referencia': 'Centro de Taguatinga, Shopping Taguatinga'
            },
            {
                'codigo_dftrans': 'T004',
                'nome': 'Terminal Samambaia',
                'descricao': 'Terminal de ônibus de Samambaia',
                'latitude': -15.8756,
                'longitude': -48.0844,
                'endereco': 'QS 318, Samambaia Sul - DF',
                'tipo': TipoParada.TERMINAL,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 2800,
                'pontos_referencia': 'Centro de Samambaia'
            },
            {
                'codigo_dftrans': 'T005',
                'nome': 'Terminal Gama',
                'descricao': 'Terminal de ônibus do Gama',
                'latitude': -16.0189,
                'longitude': -48.0644,
                'endereco': 'Setor Central, Gama - DF',
                'tipo': TipoParada.TERMINAL,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 2200,
                'pontos_referencia': 'Centro do Gama'
            },
            
            # Estações de Metrô
            {
                'codigo_dftrans': 'M001',
                'nome': 'Estação Central - Metrô',
                'descricao': 'Estação Central do Metrô de Brasília',
                'latitude': -15.7801,
                'longitude': -47.8825,
                'endereco': 'Eixo Monumental, Brasília - DF',
                'tipo': TipoParada.METRO,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 8000,
                'pontos_referencia': 'Rodoviária do Plano Piloto, Shopping Conjunto Nacional'
            },
            {
                'codigo_dftrans': 'M002',
                'nome': 'Estação Ceilândia Centro - Metrô',
                'descricao': 'Estação de metrô da Ceilândia Centro',
                'latitude': -15.8195,
                'longitude': -48.1067,
                'endereco': 'QNN 102, Ceilândia Norte - DF',
                'tipo': TipoParada.METRO,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 6000,
                'pontos_referencia': 'Centro da Ceilândia, Hospital Regional'
            },
            {
                'codigo_dftrans': 'M003',
                'nome': 'Estação Taguatinga Centro - Metrô',
                'descricao': 'Estação de metrô de Taguatinga Centro',
                'latitude': -15.8289,
                'longitude': -48.0456,
                'endereco': 'Pistão Sul, Taguatinga - DF',
                'tipo': TipoParada.METRO,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 5500,
                'pontos_referencia': 'Centro de Taguatinga'
            },
            
            # Shoppings
            {
                'codigo_dftrans': 'S001',
                'nome': 'Shopping Conjunto Nacional',
                'descricao': 'Parada em frente ao Shopping Conjunto Nacional',
                'latitude': -15.7899,
                'longitude': -47.8919,
                'endereco': 'SDS, Asa Sul, Brasília - DF',
                'tipo': TipoParada.SHOPPING,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 2500,
                'pontos_referencia': 'Shopping Conjunto Nacional, Torre de TV'
            },
            {
                'codigo_dftrans': 'S002',
                'nome': 'Shopping Ceilândia',
                'descricao': 'Parada próxima ao Shopping Ceilândia',
                'latitude': -15.8245,
                'longitude': -48.1125,
                'endereco': 'QNM 11, Ceilândia Norte - DF',
                'tipo': TipoParada.SHOPPING,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 1800,
                'pontos_referencia': 'Shopping Ceilândia, Terminal Ceilândia'
            },
            {
                'codigo_dftrans': 'S003',
                'nome': 'Shopping Brasília',
                'descricao': 'Parada do Shopping Brasília',
                'latitude': -15.7544,
                'longitude': -47.8889,
                'endereco': 'SCN Q 5, Asa Norte - DF',
                'tipo': TipoParada.SHOPPING,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 2200,
                'pontos_referencia': 'Shopping Brasília, Setor Comercial Norte'
            },
            
            # Hospitais
            {
                'codigo_dftrans': 'H001',
                'nome': 'Hospital Regional da Asa Norte',
                'descricao': 'Parada do Hospital Regional da Asa Norte',
                'latitude': -15.7654,
                'longitude': -47.8789,
                'endereco': 'SMHN Q 101, Asa Norte - DF',
                'tipo': TipoParada.HOSPITAL,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 1200,
                'pontos_referencia': 'Hospital Regional, Asa Norte'
            },
            {
                'codigo_dftrans': 'H002',
                'nome': 'Hospital Regional de Ceilândia',
                'descricao': 'Parada do Hospital Regional de Ceilândia',
                'latitude': -15.8178,
                'longitude': -48.1089,
                'endereco': 'QNM 28, Ceilândia Norte - DF',
                'tipo': TipoParada.HOSPITAL,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 900,
                'pontos_referencia': 'Hospital Regional de Ceilândia'
            },
            
            # Universidades
            {
                'codigo_dftrans': 'U001',
                'nome': 'Universidade de Brasília - Campus Darcy Ribeiro',
                'descricao': 'Parada principal da UnB',
                'latitude': -15.7633,
                'longitude': -47.8689,
                'endereco': 'Campus Universitário Darcy Ribeiro, Asa Norte - DF',
                'tipo': TipoParada.EDUCACAO,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 3500,
                'pontos_referencia': 'Universidade de Brasília, ICC'
            },
            
            # Aeroporto
            {
                'codigo_dftrans': 'A001',
                'nome': 'Aeroporto Internacional de Brasília',
                'descricao': 'Terminal de passageiros do aeroporto',
                'latitude': -15.8711,
                'longitude': -47.9178,
                'endereco': 'Lago Sul, Brasília - DF',
                'tipo': TipoParada.AEROPORTO,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 1500,
                'pontos_referencia': 'Aeroporto Internacional de Brasília'
            },
            
            # Paradas principais nas cidades satélites
            {
                'codigo_dftrans': 'P001',
                'nome': 'Setor Comercial Sul - Quadra 2',
                'descricao': 'Parada no Setor Comercial Sul',
                'latitude': -15.7967,
                'longitude': -47.8944,
                'endereco': 'SCS Q 2, Asa Sul - DF',
                'tipo': TipoParada.PRINCIPAL,
                'tem_acessibilidade': False,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 800,
                'pontos_referencia': 'Setor Comercial Sul, próximo ao centro'
            },
            {
                'codigo_dftrans': 'P002',
                'nome': 'Setor Bancário Sul',
                'descricao': 'Parada no Setor Bancário Sul',
                'latitude': -15.7989,
                'longitude': -47.8856,
                'endereco': 'SBS Q 1, Asa Sul - DF',
                'tipo': TipoParada.PRINCIPAL,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 1200,
                'pontos_referencia': 'Setor Bancário Sul, bancos'
            },
            {
                'codigo_dftrans': 'P003',
                'nome': 'Quadra 102 Norte',
                'descricao': 'Parada na Asa Norte - Quadra 102',
                'latitude': -15.7511,
                'longitude': -47.8822,
                'endereco': 'SQN 102, Asa Norte - DF',
                'tipo': TipoParada.SECUNDARIA,
                'tem_acessibilidade': False,
                'tem_cobertura': True,
                'tem_banco': False,
                'movimento_estimado': 400,
                'pontos_referencia': 'Residencial Asa Norte'
            },
            {
                'codigo_dftrans': 'P004',
                'nome': 'Quadra 308 Sul',
                'descricao': 'Parada na Asa Sul - Quadra 308',
                'latitude': -15.8133,
                'longitude': -47.8822,
                'endereco': 'SQS 308, Asa Sul - DF',
                'tipo': TipoParada.SECUNDARIA,
                'tem_acessibilidade': False,
                'tem_cobertura': True,
                'tem_banco': False,
                'movimento_estimado': 350,
                'pontos_referencia': 'Residencial Asa Sul'
            },
            {
                'codigo_dftrans': 'P005',
                'nome': 'QNM 36 - Ceilândia Norte',
                'descricao': 'Parada residencial na Ceilândia Norte',
                'latitude': -15.8089,
                'longitude': -48.1156,
                'endereco': 'QNM 36, Ceilândia Norte - DF',
                'tipo': TipoParada.SECUNDARIA,
                'tem_acessibilidade': False,
                'tem_cobertura': False,
                'tem_banco': False,
                'movimento_estimado': 200,
                'pontos_referencia': 'Área residencial Ceilândia Norte'
            },
            {
                'codigo_dftrans': 'P006',
                'nome': 'QNL 15 - Taguatinga Norte',
                'descricao': 'Parada residencial em Taguatinga Norte',
                'latitude': -15.8178,
                'longitude': -48.0511,
                'endereco': 'QNL 15, Taguatinga Norte - DF',
                'tipo': TipoParada.SECUNDARIA,
                'tem_acessibilidade': False,
                'tem_cobertura': True,
                'tem_banco': False,
                'movimento_estimado': 180,
                'pontos_referencia': 'Área residencial Taguatinga Norte'
            }
        ]
        
        paradas_criadas = []
        for parada_data in paradas_data:
            parada, created = Parada.objects.get_or_create(
                codigo_dftrans=parada_data['codigo_dftrans'],
                defaults=parada_data
            )
            paradas_criadas.append(parada)
            
            if verbose and created:
                self.stdout.write(f'  ✅ Criada: {parada.nome}')
        
        if verbose:
            self.stdout.write(f'📍 {len(paradas_criadas)} paradas criadas/verificadas')
        
        return paradas_criadas

    def _criar_linhas_mock(self, verbose=False):
        """Cria linhas mock baseadas em linhas reais do DFTrans"""
        if verbose:
            self.stdout.write('🚌 Criando linhas mock...')
        
        linhas_data = [
            # Linhas principais
            {
                'codigo': '0.111',
                'nome': 'Plano Piloto / Ceilândia Centro',
                'nome_curto': 'PP - Ceilândia',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Terminal Rodoviário do Plano Piloto',
                'destino': 'Terminal Ceilândia Centro',
                'trajeto_descricao': 'Liga o centro de Brasília à Ceilândia passando pelo Eixo Monumental',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '05:00',
                'ultimo_horario': '23:30',
                'intervalo_pico': 8,
                'intervalo_normal': 15,
                'tempo_viagem_estimado': 45,
                'tem_acessibilidade': True,
                'cor_linha': '#FF0000',
                'observacoes': 'Linha expressa com poucas paradas'
            },
            {
                'codigo': '0.030',
                'nome': 'Plano Piloto / Taguatinga',
                'nome_curto': 'PP - Taguatinga',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Terminal Rodoviário do Plano Piloto',
                'destino': 'Terminal Taguatinga',
                'trajeto_descricao': 'Conecta Brasília a Taguatinga via EPTG',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '05:00',
                'ultimo_horario': '23:45',
                'intervalo_pico': 6,
                'intervalo_normal': 12,
                'tempo_viagem_estimado': 35,
                'tem_acessibilidade': True,
                'cor_linha': '#0000FF',
                'observacoes': 'Uma das linhas mais movimentadas'
            },
            {
                'codigo': '0.143',
                'nome': 'Ceilândia Centro / Taguatinga',
                'nome_curto': 'Ceilândia - Taguatinga',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Terminal Ceilândia Centro',
                'destino': 'Terminal Taguatinga',
                'trajeto_descricao': 'Liga as duas principais cidades satélites',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '05:30',
                'ultimo_horario': '22:30',
                'intervalo_pico': 12,
                'intervalo_normal': 20,
                'tempo_viagem_estimado': 25,
                'tem_acessibilidade': True,
                'cor_linha': '#00FF00',
                'observacoes': 'Importante para integração entre cidades'
            },
            {
                'codigo': '0.108',
                'nome': 'Plano Piloto / Samambaia',
                'nome_curto': 'PP - Samambaia',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Terminal Rodoviário do Plano Piloto',
                'destino': 'Terminal Samambaia',
                'trajeto_descricao': 'Liga Brasília a Samambaia',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '05:15',
                'ultimo_horario': '23:00',
                'intervalo_pico': 10,
                'intervalo_normal': 18,
                'tempo_viagem_estimado': 50,
                'tem_acessibilidade': True,
                'cor_linha': '#FF8000',
                'observacoes': 'Linha com trajeto mais longo'
            },
            {
                'codigo': '0.150',
                'nome': 'Plano Piloto / Gama',
                'nome_curto': 'PP - Gama',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Terminal Rodoviário do Plano Piloto',
                'destino': 'Terminal Gama',
                'trajeto_descricao': 'Conecta Brasília ao Gama',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '05:00',
                'ultimo_horario': '22:45',
                'intervalo_pico': 15,
                'intervalo_normal': 25,
                'tempo_viagem_estimado': 55,
                'tem_acessibilidade': True,
                'cor_linha': '#800080',
                'observacoes': 'Atende região sul do DF'
            },
            
            # Linhas do Metrô
            {
                'codigo': 'METRO-1',
                'nome': 'Linha Laranja - Metrô DF',
                'nome_curto': 'Metrô Laranja',
                'tipo': TipoLinha.METRO,
                'status': StatusLinha.ATIVA,
                'origem': 'Estação Central',
                'destino': 'Estação Ceilândia Centro',
                'trajeto_descricao': 'Linha principal do metrô conectando centro às cidades satélites',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '06:00',
                'ultimo_horario': '23:30',
                'intervalo_pico': 4,
                'intervalo_normal': 8,
                'tempo_viagem_estimado': 30,
                'tem_acessibilidade': True,
                'cor_linha': '#FFA500',
                'observacoes': 'Sistema sobre trilhos'
            },
            
            # Linhas urbanas
            {
                'codigo': '0.201',
                'nome': 'Circular Asa Norte',
                'nome_curto': 'Circular AN',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Setor Comercial Norte',
                'destino': 'Setor Comercial Norte',
                'trajeto_descricao': 'Linha circular atendendo a Asa Norte',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '06:00',
                'ultimo_horario': '22:00',
                'intervalo_pico': 20,
                'intervalo_normal': 30,
                'tempo_viagem_estimado': 40,
                'tem_acessibilidade': False,
                'cor_linha': '#008080',
                'observacoes': 'Atende área residencial'
            },
            {
                'codigo': '0.202',
                'nome': 'Circular Asa Sul',
                'nome_curto': 'Circular AS',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Setor Comercial Sul',
                'destino': 'Setor Comercial Sul',
                'trajeto_descricao': 'Linha circular atendendo a Asa Sul',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '06:00',
                'ultimo_horario': '22:00',
                'intervalo_pico': 20,
                'intervalo_normal': 30,
                'tempo_viagem_estimado': 45,
                'tem_acessibilidade': False,
                'cor_linha': '#4B0082',
                'observacoes': 'Atende área residencial'
            },
            
            # Linhas especiais
            {
                'codigo': '0.900',
                'nome': 'Aeroporto / Plano Piloto',
                'nome_curto': 'Aeroporto Express',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Aeroporto Internacional de Brasília',
                'destino': 'Terminal Rodoviário do Plano Piloto',
                'trajeto_descricao': 'Linha expressa para o aeroporto',
                'tarifa': Decimal('8.00'),
                'primeiro_horario': '05:00',
                'ultimo_horario': '23:00',
                'intervalo_pico': 30,
                'intervalo_normal': 45,
                'tempo_viagem_estimado': 35,
                'tem_acessibilidade': True,
                'cor_linha': '#FFD700',
                'observacoes': 'Linha expressa com tarifa diferenciada'
            },
            {
                'codigo': '0.801',
                'nome': 'UnB / Plano Piloto',
                'nome_curto': 'UnB Express',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Universidade de Brasília',
                'destino': 'Terminal Rodoviário do Plano Piloto',
                'trajeto_descricao': 'Liga a UnB ao centro de Brasília',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '06:00',
                'ultimo_horario': '22:30',
                'intervalo_pico': 10,
                'intervalo_normal': 15,
                'tempo_viagem_estimado': 20,
                'tem_acessibilidade': True,
                'cor_linha': '#228B22',
                'observacoes': 'Alta demanda no período letivo'
            }
        ]
        
        linhas_criadas = []
        for linha_data in linhas_data:
            linha, created = Linha.objects.get_or_create(
                codigo=linha_data['codigo'],
                defaults=linha_data
            )
            linhas_criadas.append(linha)
            
            if verbose and created:
                self.stdout.write(f'  🚌 Criada: {linha.codigo} - {linha.nome}')
        
        if verbose:
            self.stdout.write(f'🚌 {len(linhas_criadas)} linhas criadas/verificadas')
        
        return linhas_criadas

    def _criar_relacionamentos_mock(self, paradas, linhas, verbose=False):
        """Cria relacionamentos entre linhas e paradas"""
        if verbose:
            self.stdout.write('🔗 Criando relacionamentos linha-parada...')
        
        # Mapear paradas por código para facilitar a busca
        paradas_map = {p.codigo_dftrans: p for p in paradas}
        linhas_map = {l.codigo: l for l in linhas}
        
        # Definir relacionamentos linha-parada com ordem
        relacionamentos = [
            # Linha 0.111 - PP / Ceilândia
            ('0.111', [
                ('T001', 1), ('P001', 2), ('P002', 3), ('S001', 4), 
                ('M001', 5), ('M002', 6), ('S002', 7), ('T002', 8)
            ]),
            
            # Linha 0.030 - PP / Taguatinga  
            ('0.030', [
                ('T001', 1), ('P001', 2), ('P002', 3), ('S003', 4),
                ('M003', 5), ('P006', 6), ('T003', 7)
            ]),
            
            # Linha 0.143 - Ceilândia / Taguatinga
            ('0.143', [
                ('T002', 1), ('S002', 2), ('P005', 3), ('P006', 4), ('T003', 5)
            ]),
            
            # Linha 0.108 - PP / Samambaia
            ('0.108', [
                ('T001', 1), ('P001', 2), ('S001', 3), ('T003', 4), ('T004', 5)
            ]),
            
            # Linha 0.150 - PP / Gama
            ('0.150', [
                ('T001', 1), ('P002', 2), ('S001', 3), ('T005', 4)
            ]),
            
            # Metrô
            ('METRO-1', [
                ('M001', 1), ('M003', 2), ('M002', 3)
            ]),
            
            # Linha 0.201 - Circular Asa Norte
            ('0.201', [
                ('S003', 1), ('P003', 2), ('H001', 3), ('U001', 4), ('S003', 5)
            ]),
            
            # Linha 0.202 - Circular Asa Sul
            ('0.202', [
                ('P001', 1), ('P002', 2), ('S001', 3), ('P004', 4), ('P001', 5)
            ]),
            
            # Linha 0.900 - Aeroporto
            ('0.900', [
                ('A001', 1), ('S001', 2), ('T001', 3)
            ]),
            
            # Linha 0.801 - UnB
            ('0.801', [
                ('U001', 1), ('H001', 2), ('S003', 3), ('T001', 4)
            ])
        ]
        
        relacionamentos_criados = 0
        
        for codigo_linha, paradas_linha in relacionamentos:
            linha = linhas_map.get(codigo_linha)
            if not linha:
                if verbose:
                    self.stdout.write(f'  ⚠️  Linha {codigo_linha} não encontrada')
                continue
            
            for codigo_parada, ordem in paradas_linha:
                parada = paradas_map.get(codigo_parada)
                if not parada:
                    if verbose:
                        self.stdout.write(f'  ⚠️  Parada {codigo_parada} não encontrada')
                    continue
                
                linha_parada, created = LinhaParada.objects.get_or_create(
                    linha=linha,
                    parada=parada,
                    defaults={
                        'ordem': ordem,
                        'tempo_parada': 60,  # 1 minuto padrão
                        'distancia_origem': ordem * 2.5,  # Estimativa simples
                        'observacoes': f'Parada {ordem} da linha {codigo_linha}'
                    }
                )
                
                if created:
                    relacionamentos_criados += 1
                    if verbose:
                        self.stdout.write(
                            f'  🔗 {linha.codigo} -> {parada.nome} (ordem {ordem})'
                        )
        
        if verbose:
            self.stdout.write(f'🔗 {relacionamentos_criados} relacionamentos criados')

    def _exibir_estatisticas(self, verbose=False):
        """Exibe estatísticas dos dados criados"""
        if not verbose:
            return
            
        total_paradas = Parada.objects.count()
        total_linhas = Linha.objects.count()
        total_relacionamentos = LinhaParada.objects.count()
        
        # Estatísticas por tipo
        paradas_por_tipo = {}
        for tipo, nome in TipoParada.choices:
            count = Parada.objects.filter(tipo=tipo).count()
            if count > 0:
                paradas_por_tipo[nome] = count
        
        linhas_por_tipo = {}
        for tipo, nome in TipoLinha.choices:
            count = Linha.objects.filter(tipo=tipo).count()
            if count > 0:
                linhas_por_tipo[nome] = count
        
        self.stdout.write('\n📊 ESTATÍSTICAS DOS DADOS MOCK:')
        self.stdout.write(f'  📍 Total de Paradas: {total_paradas}')
        for tipo, count in paradas_por_tipo.items():
            self.stdout.write(f'    - {tipo}: {count}')
        
        self.stdout.write(f'  🚌 Total de Linhas: {total_linhas}')
        for tipo, count in linhas_por_tipo.items():
            self.stdout.write(f'    - {tipo}: {count}')
        
        self.stdout.write(f'  🔗 Total de Relacionamentos: {total_relacionamentos}')
        
        # Paradas com mais movimento
        paradas_movimento = Parada.objects.filter(
            movimento_estimado__gt=0
        ).order_by('-movimento_estimado')[:5]
        
        if paradas_movimento:
            self.stdout.write('\n🏃 Top 5 Paradas por Movimento:')
            for i, parada in enumerate(paradas_movimento, 1):
                self.stdout.write(
                    f'  {i}. {parada.nome}: {parada.movimento_estimado} passageiros/dia'
                )
        
        self.stdout.write('\n✅ Dados mock prontos para uso!') 
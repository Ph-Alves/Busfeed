"""
Comando para adicionar dados extras ao banco de desenvolvimento

Este comando adiciona mais linhas e paradas para tornar o sistema mais
completo para testes e demonstrações.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decimal import Decimal
import logging

from paradas.models import Parada, TipoParada
from linhas.models import Linha, LinhaParada, TipoLinha, StatusLinha


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Adiciona dados extras para testes mais completos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas durante a execução'
        )

    def handle(self, *args, **options):
        """Executa o comando de adição de dados extras"""
        
        if options['verbose']:
            self.stdout.write(
                self.style.SUCCESS('🎯 Adicionando dados extras ao BusFeed...')
            )

        try:
            with transaction.atomic():
                self._adicionar_paradas_extras(options['verbose'])
                self._adicionar_linhas_extras(options['verbose'])
                self._adicionar_relacionamentos_extras(options['verbose'])
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Dados extras adicionados com sucesso!')
                )
                
        except Exception as e:
            logger.error(f"Erro ao adicionar dados extras: {e}")
            raise CommandError(f'Erro ao adicionar dados: {e}')

    def _adicionar_paradas_extras(self, verbose=False):
        """Adiciona paradas extras para completar o sistema"""
        if verbose:
            self.stdout.write('📍 Adicionando paradas extras...')
        
        paradas_extras = [
            # Mais paradas no Plano Piloto
            {
                'codigo_dftrans': 'P010',
                'nome': 'Setor Hoteleiro Norte',
                'descricao': 'Parada no Setor Hoteleiro Norte',
                'latitude': -15.7725,
                'longitude': -47.8856,
                'endereco': 'SHN, Asa Norte, Brasília - DF',
                'tipo': TipoParada.SECUNDARIA,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': False,
                'movimento_estimado': 600,
                'pontos_referencia': 'Hotéis, próximo ao centro'
            },
            {
                'codigo_dftrans': 'P011',
                'nome': 'Setor de Diversões Norte',
                'descricao': 'Parada no Setor de Diversões Norte',
                'latitude': -15.7698,
                'longitude': -47.8801,
                'endereco': 'SDN, Asa Norte, Brasília - DF',
                'tipo': TipoParada.SECUNDARIA,
                'tem_acessibilidade': False,
                'tem_cobertura': False,
                'tem_banco': False,
                'movimento_estimado': 400,
                'pontos_referencia': 'Área de entretenimento'
            },
            
            # Paradas em Taguatinga
            {
                'codigo_dftrans': 'P012',
                'nome': 'QNA 42 - Taguatinga',
                'descricao': 'Parada residencial na QNA 42',
                'latitude': -15.8234,
                'longitude': -48.0567,
                'endereco': 'QNA 42, Taguatinga Norte - DF',
                'tipo': TipoParada.SECUNDARIA,
                'tem_acessibilidade': False,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 300,
                'pontos_referencia': 'Área residencial de Taguatinga'
            },
            {
                'codigo_dftrans': 'P013',
                'nome': 'Shopping Taguatinga',
                'descricao': 'Parada do Shopping Taguatinga',
                'latitude': -15.8298,
                'longitude': -48.0445,
                'endereco': 'Pistão Sul, Taguatinga - DF',
                'tipo': TipoParada.SHOPPING,
                'tem_acessibilidade': True,
                'tem_cobertura': True,
                'tem_banco': True,
                'movimento_estimado': 2000,
                'pontos_referencia': 'Shopping Taguatinga, centro comercial'
            },
            
            # Paradas importantes em outras regiões
            {
                'codigo_dftrans': 'P014',
                'nome': 'Setor de Indústria Gráfica',
                'descricao': 'Parada no Setor de Indústria Gráfica',
                'latitude': -15.7845,
                'longitude': -47.9123,
                'endereco': 'SIG, Brasília - DF',
                'tipo': TipoParada.SECUNDARIA,
                'tem_acessibilidade': False,
                'tem_cobertura': False,
                'tem_banco': False,
                'movimento_estimado': 500,
                'pontos_referencia': 'Área industrial, empresas'
            },
        ]
        
        paradas_criadas = 0
        for parada_data in paradas_extras:
            parada, created = Parada.objects.get_or_create(
                codigo_dftrans=parada_data['codigo_dftrans'],
                defaults=parada_data
            )
            if created:
                paradas_criadas += 1
                if verbose:
                    self.stdout.write(f'  ✅ Criada: {parada.nome}')
        
        if verbose:
            self.stdout.write(f'📍 {paradas_criadas} paradas extras criadas')

    def _adicionar_linhas_extras(self, verbose=False):
        """Adiciona linhas extras para completar o sistema"""
        if verbose:
            self.stdout.write('🚌 Adicionando linhas extras...')
        
        linhas_extras = [
            # Linha para UnB
            {
                'codigo': '0.108',
                'nome': 'Taguatinga / UnB',
                'nome_curto': 'Taguatinga-UnB',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Terminal Taguatinga',
                'destino': 'Universidade de Brasília - Campus Darcy Ribeiro',
                'trajeto_descricao': 'Linha universitária conectando Taguatinga à UnB',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '05:45',
                'ultimo_horario': '23:15',
                'intervalo_pico': 12,
                'intervalo_normal': 20,
                'tempo_viagem_estimado': 40,
                'tem_acessibilidade': True,
                'cor_linha': '#FFFF00',
                'observacoes': 'Linha muito utilizada por estudantes'
            },
            # Linha Shopping
            {
                'codigo': '0.130',
                'nome': 'Ceilândia / Shopping Conjunto Nacional',
                'nome_curto': 'Ceilândia-Shopping',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Terminal Ceilândia Centro',
                'destino': 'Shopping Conjunto Nacional',
                'trajeto_descricao': 'Liga Ceilândia ao principal shopping do Plano Piloto',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '06:00',
                'ultimo_horario': '22:00',
                'intervalo_pico': 25,
                'intervalo_normal': 35,
                'tempo_viagem_estimado': 50,
                'tem_acessibilidade': False,
                'cor_linha': '#0000FF',
                'observacoes': 'Linha popular para compras e lazer'
            },
            # Linha para hospital
            {
                'codigo': '0.140',
                'nome': 'Ceilândia / Hospital Regional Asa Norte',
                'nome_curto': 'Ceilândia-Hospital',
                'tipo': TipoLinha.ONIBUS,
                'status': StatusLinha.ATIVA,
                'origem': 'Shopping Ceilândia',
                'destino': 'Hospital Regional da Asa Norte',
                'trajeto_descricao': 'Conecta Ceilândia aos serviços de saúde da Asa Norte',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '05:30',
                'ultimo_horario': '22:30',
                'intervalo_pico': 30,
                'intervalo_normal': 45,
                'tempo_viagem_estimado': 55,
                'tem_acessibilidade': True,
                'cor_linha': '#FF00FF',
                'observacoes': 'Linha essencial para acesso a serviços de saúde'
            },
            # Linha do Metrô
            {
                'codigo': 'M01',
                'nome': 'Linha Laranja - Metrô',
                'nome_curto': 'Metrô Laranja',
                'tipo': TipoLinha.METRO,
                'status': StatusLinha.ATIVA,
                'origem': 'Estação Central - Metrô',
                'destino': 'Estação Ceilândia Centro - Metrô',
                'trajeto_descricao': 'Linha principal do metrô de Brasília',
                'tarifa': Decimal('5.50'),
                'primeiro_horario': '06:00',
                'ultimo_horario': '23:30',
                'intervalo_pico': 3,
                'intervalo_normal': 6,
                'tempo_viagem_estimado': 30,
                'tem_acessibilidade': True,
                'cor_linha': '#FFA500',
                'observacoes': 'Sistema de metrô com alta frequência'
            },
            # Linha circular
            {
                'codigo': '0.201',
                'nome': 'Circular Ceilândia Norte',
                'nome_curto': 'Circular Ceilândia',
                'tipo': TipoLinha.MICRO,
                'status': StatusLinha.ATIVA,
                'origem': 'Terminal Ceilândia Centro',
                'destino': 'Terminal Ceilândia Centro',
                'trajeto_descricao': 'Linha circular atendendo bairros da Ceilândia Norte',
                'tarifa': Decimal('3.50'),
                'primeiro_horario': '06:00',
                'ultimo_horario': '22:00',
                'intervalo_pico': 20,
                'intervalo_normal': 30,
                'tempo_viagem_estimado': 60,
                'tem_acessibilidade': False,
                'cor_linha': '#800080',
                'observacoes': 'Linha circular para deslocamentos locais'
            }
        ]
        
        linhas_criadas = 0
        for linha_data in linhas_extras:
            linha, created = Linha.objects.get_or_create(
                codigo=linha_data['codigo'],
                defaults=linha_data
            )
            if created:
                linhas_criadas += 1
                if verbose:
                    self.stdout.write(f'  🚌 Criada: {linha.nome}')
        
        if verbose:
            self.stdout.write(f'🚌 {linhas_criadas} linhas extras criadas')

    def _adicionar_relacionamentos_extras(self, verbose=False):
        """Adiciona relacionamentos extras entre linhas e paradas"""
        if verbose:
            self.stdout.write('🔗 Adicionando relacionamentos extras...')
        
        relacionamentos_extras = [
            # Linha 0.108: Taguatinga / UnB
            ('0.108', 'T003', 1, 0, 0.0),  # Terminal Taguatinga (origem)
            ('0.108', 'P012', 2, 60, 3.2),  # QNA 42 - Taguatinga
            ('0.108', 'P013', 3, 90, 5.1),  # Shopping Taguatinga
            ('0.108', 'M001', 4, 240, 18.7),  # Estação Central - Metrô
            ('0.108', 'P001', 5, 90, 22.1),  # Setor Comercial Sul
            ('0.108', 'U001', 6, 120, 28.4),  # UnB (destino)
            
            # Linha 0.130: Ceilândia / Shopping Conjunto Nacional
            ('0.130', 'T002', 1, 0, 0.0),  # Terminal Ceilândia Centro (origem)
            ('0.130', 'S002', 2, 60, 2.1),  # Shopping Ceilândia
            ('0.130', 'M002', 3, 90, 5.7),  # Estação Ceilândia Centro - Metrô
            ('0.130', 'M001', 4, 180, 22.3),  # Estação Central - Metrô
            ('0.130', 'P002', 5, 90, 26.8),  # Setor Bancário Sul
            ('0.130', 'S001', 6, 60, 29.5),  # Shopping Conjunto Nacional (destino)
            
            # Linha 0.140: Ceilândia / Hospital Regional Asa Norte
            ('0.140', 'S002', 1, 0, 0.0),  # Shopping Ceilândia (origem)
            ('0.140', 'T002', 2, 60, 2.1),  # Terminal Ceilândia Centro
            ('0.140', 'M002', 3, 90, 5.2),  # Estação Ceilândia Centro - Metrô
            ('0.140', 'M001', 4, 180, 22.1),  # Estação Central - Metrô
            ('0.140', 'P001', 5, 90, 26.3),  # Setor Comercial Sul
            ('0.140', 'H001', 6, 120, 31.8),  # Hospital Regional da Asa Norte (destino)
            
            # Linha M01: Metrô Laranja
            ('M01', 'M001', 1, 0, 0.0),  # Estação Central - Metrô (origem)
            ('M01', 'M002', 2, 180, 22.5),  # Estação Ceilândia Centro - Metrô (destino)
            
            # Linha 0.201: Circular Ceilândia Norte
            ('0.201', 'T002', 1, 0, 0.0),  # Terminal Ceilândia Centro (origem)
            ('0.201', 'S002', 2, 180, 2.1),  # Shopping Ceilândia
            ('0.201', 'H002', 3, 120, 10.5),  # Hospital Regional de Ceilândia
            ('0.201', 'M002', 4, 90, 13.1),  # Estação Ceilândia Centro - Metrô
            ('0.201', 'T002', 5, 180, 16.8),  # Terminal Ceilândia Centro (volta)
        ]
        
        relacionamentos_criados = 0
        for codigo_linha, codigo_parada, ordem, tempo_parada, distancia in relacionamentos_extras:
            try:
                linha = Linha.objects.get(codigo=codigo_linha)
                parada = Parada.objects.get(codigo_dftrans=codigo_parada)
                
                linha_parada, created = LinhaParada.objects.get_or_create(
                    linha=linha,
                    parada=parada,
                    defaults={
                        'ordem': ordem,
                        'tempo_parada': tempo_parada,
                        'distancia_origem': distancia,
                        'observacoes': f'Parada {ordem} da linha {codigo_linha}'
                    }
                )
                
                if created:
                    relacionamentos_criados += 1
                    if verbose:
                        self.stdout.write(
                            f'  🔗 {linha.codigo} -> {parada.nome} (ordem: {ordem})'
                        )
                        
            except (Linha.DoesNotExist, Parada.DoesNotExist) as e:
                logger.warning(f"Relacionamento extra não criado: {e}")
                continue
        
        if verbose:
            self.stdout.write(f'🔗 {relacionamentos_criados} relacionamentos extras criados') 
"""
Comando para sincronizar dados com a API do DFTrans

Este comando tenta sincronizar dados reais do DFTrans e,
em caso de falha, utiliza dados mock para desenvolvimento.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
import logging
import requests
from datetime import datetime

from services.dftrans_api import DFTransAPI
from paradas.models import Parada, TipoParada
from linhas.models import Linha, LinhaParada, TipoLinha, StatusLinha


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincroniza dados com a API do DFTrans ou usa dados mock'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-mock',
            action='store_true',
            help='Força o uso de dados mock mesmo se a API estiver disponível'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas durante a execução'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Timeout para requisições à API em segundos (padrão: 30)'
        )

    def handle(self, *args, **options):
        """Executa a sincronização de dados"""
        
        if options['verbose']:
            self.stdout.write(
                self.style.SUCCESS('🔄 Iniciando sincronização com DFTrans...')
            )

        try:
            # Verifica se deve forçar uso de dados mock
            if options['force_mock']:
                if options['verbose']:
                    self.stdout.write('🎭 Modo mock forçado pelo usuário')
                self._usar_dados_mock(options['verbose'])
                return

            # Tenta conectar com a API real
            api_disponivel = self._verificar_api_dftrans(
                timeout=options['timeout'],
                verbose=options['verbose']
            )

            if api_disponivel:
                self._sincronizar_api_real(options['verbose'])
            else:
                if options['verbose']:
                    self.stdout.write(
                        self.style.WARNING('⚠️  API DFTrans indisponível, usando dados mock')
                    )
                self._usar_dados_mock(options['verbose'])

        except Exception as e:
            logger.error(f"Erro durante sincronização: {e}")
            if options['verbose']:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro durante sincronização: {e}')
                )
            
            # Em caso de erro, tenta usar dados mock como fallback
            try:
                self.stdout.write(
                    self.style.WARNING('🔄 Tentando fallback para dados mock...')
                )
                self._usar_dados_mock(options['verbose'])
            except Exception as mock_error:
                raise CommandError(f'Falha total na sincronização: {mock_error}')

    def _verificar_api_dftrans(self, timeout=30, verbose=False):
        """Verifica se a API do DFTrans está disponível"""
        if verbose:
            self.stdout.write('🔍 Verificando disponibilidade da API DFTrans...')
        
        try:
            # Tenta inicializar o serviço DFTrans
            dftrans = DFTransAPI()
            
            # Faz uma requisição de teste simples
            test_response = dftrans._fazer_requisicao('paradas', timeout=timeout)
            
            if test_response and len(test_response) > 0:
                if verbose:
                    self.stdout.write('✅ API DFTrans disponível')
                return True
            else:
                if verbose:
                    self.stdout.write('⚠️  API DFTrans retornou dados vazios')
                return False
                
        except requests.exceptions.Timeout:
            if verbose:
                self.stdout.write('⏰ Timeout na conexão com API DFTrans')
            return False
        except requests.exceptions.ConnectionError:
            if verbose:
                self.stdout.write('🔌 Erro de conexão com API DFTrans')
            return False
        except Exception as e:
            if verbose:
                self.stdout.write(f'❌ Erro ao verificar API DFTrans: {e}')
            return False

    def _sincronizar_api_real(self, verbose=False):
        """Sincroniza dados reais da API DFTrans"""
        if verbose:
            self.stdout.write('📡 Sincronizando com API real do DFTrans...')
        
        try:
            dftrans = DFTransAPI()
            
            with transaction.atomic():
                # Sincroniza paradas
                paradas_sincronizadas = self._sincronizar_paradas_api(dftrans, verbose)
                
                # Sincroniza linhas
                linhas_sincronizadas = self._sincronizar_linhas_api(dftrans, verbose)
                
                # Sincroniza relacionamentos
                self._sincronizar_relacionamentos_api(dftrans, verbose)
                
                if verbose:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Sincronização concluída: '
                            f'{paradas_sincronizadas} paradas, '
                            f'{linhas_sincronizadas} linhas'
                        )
                    )
                    
        except Exception as e:
            logger.error(f"Erro na sincronização com API real: {e}")
            raise

    def _sincronizar_paradas_api(self, dftrans, verbose=False):
        """Sincroniza paradas da API DFTrans"""
        if verbose:
            self.stdout.write('📍 Sincronizando paradas...')
        
        try:
            paradas_data = dftrans.obter_paradas()
            contador = 0
            
            for parada_info in paradas_data:
                # Mapeia dados da API para o modelo
                parada_data = self._mapear_parada_api(parada_info)
                
                parada, created = Parada.objects.update_or_create(
                    codigo_dftrans=parada_data['codigo_dftrans'],
                    defaults=parada_data
                )
                
                if created:
                    contador += 1
                    if verbose:
                        self.stdout.write(f'  ✅ Nova parada: {parada.nome}')
            
            return contador
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar paradas: {e}")
            raise

    def _sincronizar_linhas_api(self, dftrans, verbose=False):
        """Sincroniza linhas da API DFTrans"""
        if verbose:
            self.stdout.write('🚌 Sincronizando linhas...')
        
        try:
            linhas_data = dftrans.obter_linhas()
            contador = 0
            
            for linha_info in linhas_data:
                # Mapeia dados da API para o modelo
                linha_data = self._mapear_linha_api(linha_info)
                
                linha, created = Linha.objects.update_or_create(
                    codigo=linha_data['codigo'],
                    defaults=linha_data
                )
                
                if created:
                    contador += 1
                    if verbose:
                        self.stdout.write(f'  ✅ Nova linha: {linha.codigo} - {linha.nome}')
            
            return contador
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar linhas: {e}")
            raise

    def _sincronizar_relacionamentos_api(self, dftrans, verbose=False):
        """Sincroniza relacionamentos linha-parada da API"""
        if verbose:
            self.stdout.write('🔗 Sincronizando relacionamentos...')
        
        try:
            # Implementação futura - por enquanto apenas log
            if verbose:
                self.stdout.write('  ⚠️  Sincronização de relacionamentos ainda não implementada')
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar relacionamentos: {e}")
            raise

    def _mapear_parada_api(self, parada_api):
        """Mapeia dados da API para o modelo Parada"""
        # Implementação baseada na estrutura esperada da API DFTrans
        return {
            'codigo_dftrans': parada_api.get('codigo', ''),
            'nome': parada_api.get('nome', ''),
            'descricao': parada_api.get('descricao', ''),
            'latitude': float(parada_api.get('latitude', 0)),
            'longitude': float(parada_api.get('longitude', 0)),
            'endereco': parada_api.get('endereco', ''),
            'tipo': self._mapear_tipo_parada(parada_api.get('tipo', '')),
            'tem_acessibilidade': parada_api.get('acessibilidade', False),
            'tem_cobertura': parada_api.get('cobertura', False),
            'tem_banco': parada_api.get('banco', False),
            'movimento_estimado': parada_api.get('movimento', 0),
            'pontos_referencia': parada_api.get('referencias', ''),
        }

    def _mapear_linha_api(self, linha_api):
        """Mapeia dados da API para o modelo Linha"""
        return {
            'codigo': linha_api.get('codigo', ''),
            'nome': linha_api.get('nome', ''),
            'nome_curto': linha_api.get('nome_curto', ''),
            'tipo': self._mapear_tipo_linha(linha_api.get('tipo', '')),
            'status': 'active',  # Assume ativa por padrão
            'origem': linha_api.get('origem', ''),
            'destino': linha_api.get('destino', ''),
            'trajeto_descricao': linha_api.get('trajeto', ''),
            'tarifa': linha_api.get('tarifa', 5.50),
            'primeiro_horario': linha_api.get('primeiro_horario'),
            'ultimo_horario': linha_api.get('ultimo_horario'),
            'intervalo_pico': linha_api.get('intervalo_pico'),
            'intervalo_normal': linha_api.get('intervalo_normal'),
            'tempo_viagem_estimado': linha_api.get('tempo_viagem'),
            'tem_acessibilidade': linha_api.get('acessibilidade', False),
            'cor_linha': linha_api.get('cor', ''),
            'observacoes': linha_api.get('observacoes', ''),
        }

    def _mapear_tipo_parada(self, tipo_api):
        """Mapeia tipo de parada da API para o modelo"""
        mapeamento = {
            'terminal': 'terminal',
            'metro': 'metro',
            'shopping': 'shopping',
            'hospital': 'hospital',
            'aeroporto': 'airport',
            'educacao': 'education',
            'principal': 'main',
            'secundaria': 'secondary',
        }
        return mapeamento.get(tipo_api.lower(), 'secondary')

    def _mapear_tipo_linha(self, tipo_api):
        """Mapeia tipo de linha da API para o modelo"""
        mapeamento = {
            'onibus': 'bus',
            'metro': 'metro',
            'brt': 'brt',
            'micro': 'micro',
        }
        return mapeamento.get(tipo_api.lower(), 'bus')

    def _usar_dados_mock(self, verbose=False):
        """Usa dados mock quando a API não está disponível"""
        if verbose:
            self.stdout.write('🎭 Usando dados mock para desenvolvimento...')
        
        # Chama o comando de popular dados mock
        from django.core.management import call_command
        
        try:
            call_command(
                'popular_dados_mock',
                limpar=True,
                verbose=verbose
            )
            
            if verbose:
                self.stdout.write(
                    self.style.SUCCESS('✅ Dados mock carregados com sucesso!')
                )
                
        except Exception as e:
            logger.error(f"Erro ao carregar dados mock: {e}")
            raise CommandError(f'Falha ao carregar dados mock: {e}')

    def _log_estatisticas_sincronizacao(self, verbose=False):
        """Registra estatísticas da sincronização"""
        if not verbose:
            return
            
        total_paradas = Parada.objects.count()
        total_linhas = Linha.objects.count()
        total_relacionamentos = LinhaParada.objects.count()
        
        self.stdout.write('\n📊 ESTATÍSTICAS PÓS-SINCRONIZAÇÃO:')
        self.stdout.write(f'  📍 Total de Paradas: {total_paradas}')
        self.stdout.write(f'  🚌 Total de Linhas: {total_linhas}')
        self.stdout.write(f'  🔗 Total de Relacionamentos: {total_relacionamentos}')
        self.stdout.write(f'  🕐 Última Sincronização: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}') 
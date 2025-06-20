"""
Comando para sincronização automática com a API DFTrans

Este comando implementa a sincronização automática e contínua dos dados
do sistema de transporte público, incluindo paradas, linhas, horários
e atualizações em tempo real.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
import time
import logging
from datetime import timedelta

from services.dftrans_api import DFTransAPI, sync_manager, sincronizar_paradas_dftrans, sincronizar_linhas_dftrans
from linhas.models import Linha
from paradas.models import Parada

logger = logging.getLogger('busfeed.sincronizacao')


class Command(BaseCommand):
    help = 'Executa sincronização automática com a API DFTrans'

    def add_arguments(self, parser):
        parser.add_argument(
            '--modo',
            choices=['completo', 'paradas', 'linhas', 'tempo-real'],
            default='completo',
            help='Tipo de sincronização a ser executada'
        )
        parser.add_argument(
            '--intervalo',
            type=int,
            default=1800,  # 30 minutos
            help='Intervalo em segundos entre sincronizações (padrão: 1800)'
        )
        parser.add_argument(
            '--unica-vez',
            action='store_true',
            help='Executa apenas uma vez ao invés de contínuo'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas'
        )
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Força sincronização mesmo se cache estiver válido'
        )
        parser.add_argument(
            '--duracao',
            type=int,
            help='Duração da sincronização em horas (padrão: contínuo)'
        )

    def handle(self, *args, **options):
        modo = options['modo']
        intervalo = options['intervalo']
        unica_vez = options['unica_vez']
        verbose = options['verbose']
        forcar = options['forcar']
        duracao = options.get('duracao')
        
        # Configura logging
        if verbose:
            logging.getLogger('busfeed.sincronizacao').setLevel(logging.DEBUG)
        
        if unica_vez:
            self.stdout.write(
                self.style.SUCCESS(
                    f"🔄 Executando sincronização única: {modo}"
                )
            )
            self._executar_sincronizacao(modo, verbose, forcar)
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"🔄 Iniciando sincronização automática: {modo} (intervalo: {intervalo}s)"
                )
            )
            self._executar_sincronizacao_continua(
                modo, intervalo, verbose, forcar, duracao
            )

    def _executar_sincronizacao_continua(self, modo, intervalo, verbose, forcar, duracao):
        """Executa sincronização contínua"""
        
        # Calcula tempo de fim se duração foi especificada
        tempo_fim = None
        if duracao:
            tempo_fim = timezone.now() + timedelta(hours=duracao)
            self.stdout.write(f"⏰ Sincronização por {duracao} horas")
        
        contador_ciclo = 0
        
        try:
            while True:
                contador_ciclo += 1
                inicio_ciclo = time.time()
                
                if verbose:
                    self.stdout.write(f"\n--- Ciclo {contador_ciclo} ---")
                
                # Verifica se deve parar
                if tempo_fim and timezone.now() >= tempo_fim:
                    self.stdout.write("⏰ Tempo de sincronização concluído")
                    break
                
                # Executa sincronização
                sucesso = self._executar_sincronizacao(modo, verbose, forcar)
                
                # Calcula tempo do ciclo
                tempo_ciclo = time.time() - inicio_ciclo
                
                if verbose:
                    status = "✅ Sucesso" if sucesso else "❌ Falhou"
                    self.stdout.write(f"⏱️  Ciclo {contador_ciclo} {status} em {tempo_ciclo:.2f}s")
                
                # Aguarda próximo ciclo
                tempo_espera = max(0, intervalo - tempo_ciclo)
                if tempo_espera > 0:
                    if verbose:
                        self.stdout.write(f"⏳ Aguardando {tempo_espera:.0f}s...")
                    time.sleep(tempo_espera)
                
        except KeyboardInterrupt:
            self.stdout.write("\n🛑 Sincronização interrompida pelo usuário")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro durante sincronização: {e}")
            )
            raise CommandError(f"Falha na sincronização: {e}")
        
        self.stdout.write(
            self.style.SUCCESS("✅ Sincronização finalizada")
        )

    def _executar_sincronizacao(self, modo, verbose, forcar):
        """Executa uma rodada de sincronização"""
        
        api = DFTransAPI()
        sucesso_geral = True
        
        try:
            # Verifica status da API
            status = api.verificar_status_api()
            if not status.get('disponivel') and not forcar:
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  API DFTrans indisponível: {status.get('erro', 'N/A')}"
                        )
                    )
                return False
            
            timestamp_inicio = timezone.now()
            
            if modo == 'completo':
                # Sincronização completa
                self.stdout.write("🔄 Iniciando sincronização completa...")
                
                # 1. Sincroniza paradas
                sucesso_paradas = self._sincronizar_paradas(verbose, forcar)
                sucesso_geral = sucesso_geral and sucesso_paradas
                
                # 2. Sincroniza linhas
                sucesso_linhas = self._sincronizar_linhas(verbose, forcar)
                sucesso_geral = sucesso_geral and sucesso_linhas
                
                # 3. Atualiza relacionamentos
                if sucesso_paradas and sucesso_linhas:
                    sucesso_relacionamentos = self._atualizar_relacionamentos(verbose)
                    sucesso_geral = sucesso_geral and sucesso_relacionamentos
                
            elif modo == 'paradas':
                sucesso_geral = self._sincronizar_paradas(verbose, forcar)
                
            elif modo == 'linhas':
                sucesso_geral = self._sincronizar_linhas(verbose, forcar)
                
            elif modo == 'tempo-real':
                sucesso_geral = self._sincronizar_tempo_real(verbose)
            
            # Registra última sincronização
            if sucesso_geral:
                cache.set('ultima_sincronizacao_sucesso', timestamp_inicio, 86400)  # 24h
                
                if verbose:
                    duracao = (timezone.now() - timestamp_inicio).total_seconds()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Sincronização concluída em {duracao:.2f}s"
                        )
                    )
            else:
                cache.set('ultima_sincronizacao_erro', timestamp_inicio, 86400)  # 24h
                
        except Exception as e:
            logger.error(f"Erro durante sincronização {modo}: {e}")
            if verbose:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erro na sincronização: {e}")
                )
            sucesso_geral = False
        
        return sucesso_geral

    def _sincronizar_paradas(self, verbose, forcar):
        """Sincroniza paradas"""
        try:
            if verbose:
                self.stdout.write("📍 Sincronizando paradas...")
            
            # Verifica se já foi sincronizado recentemente
            if not forcar:
                ultima_sync = cache.get('sync_paradas_timestamp')
                if ultima_sync and (timezone.now() - ultima_sync).total_seconds() < 3600:  # 1h
                    if verbose:
                        self.stdout.write("⏭️  Paradas sincronizadas recentemente, pulando...")
                    return True
            
            resultado = sincronizar_paradas_dftrans()
            
            if resultado['success']:
                cache.set('sync_paradas_timestamp', timezone.now(), 86400)
                
                if verbose:
                    self.stdout.write(
                        f"✅ Paradas: {resultado['criadas']} novas, "
                        f"{resultado['atualizadas']} atualizadas"
                    )
                return True
            else:
                if verbose:
                    self.stdout.write(f"❌ Erro ao sincronizar paradas: {resultado.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao sincronizar paradas: {e}")
            return False

    def _sincronizar_linhas(self, verbose, forcar):
        """Sincroniza linhas"""
        try:
            if verbose:
                self.stdout.write("🚌 Sincronizando linhas...")
            
            # Verifica se já foi sincronizado recentemente
            if not forcar:
                ultima_sync = cache.get('sync_linhas_timestamp')
                if ultima_sync and (timezone.now() - ultima_sync).total_seconds() < 3600:  # 1h
                    if verbose:
                        self.stdout.write("⏭️  Linhas sincronizadas recentemente, pulando...")
                    return True
            
            resultado = sincronizar_linhas_dftrans()
            
            if resultado['success']:
                cache.set('sync_linhas_timestamp', timezone.now(), 86400)
                
                if verbose:
                    self.stdout.write(
                        f"✅ Linhas: {resultado['criadas']} novas, "
                        f"{resultado['atualizadas']} atualizadas"
                    )
                return True
            else:
                if verbose:
                    self.stdout.write(f"❌ Erro ao sincronizar linhas: {resultado.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao sincronizar linhas: {e}")
            return False

    def _atualizar_relacionamentos(self, verbose):
        """Atualiza relacionamentos entre linhas e paradas"""
        try:
            if verbose:
                self.stdout.write("🔗 Atualizando relacionamentos...")
            
            from linhas.models import LinhaParada
            
            api = DFTransAPI()
            linhas_atualizadas = 0
            
            # Busca dados atualizados das linhas
            linhas_api = api.buscar_linhas()
            
            for linha_data in linhas_api:
                try:
                    linha = Linha.objects.get(codigo=linha_data['codigo'])
                    paradas_codigo = linha_data.get('paradas', [])
                    
                    if paradas_codigo:
                        # Remove relacionamentos existentes
                        LinhaParada.objects.filter(linha=linha).delete()
                        
                        # Cria novos relacionamentos
                        for ordem, codigo_parada in enumerate(paradas_codigo, 1):
                            try:
                                parada = Parada.objects.get(codigo=codigo_parada)
                                LinhaParada.objects.create(
                                    linha=linha,
                                    parada=parada,
                                    ordem=ordem
                                )
                            except Parada.DoesNotExist:
                                if verbose:
                                    self.stdout.write(
                                        f"⚠️  Parada {codigo_parada} não encontrada para linha {linha.codigo}"
                                    )
                        
                        linhas_atualizadas += 1
                        
                except Linha.DoesNotExist:
                    continue
            
            if verbose:
                self.stdout.write(f"✅ Relacionamentos: {linhas_atualizadas} linhas atualizadas")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar relacionamentos: {e}")
            return False

    def _sincronizar_tempo_real(self, verbose):
        """Sincroniza dados em tempo real"""
        try:
            if verbose:
                self.stdout.write("⚡ Sincronizando dados em tempo real...")
            
            api = DFTransAPI()
            
            # Atualiza cache de alertas
            alertas = api.buscar_alertas_servico()
            cache.set('alertas_tempo_real', alertas, 300)  # 5 min
            
            # Atualiza posições de veículos para linhas principais
            linhas_principais = ['0.111', '0.112', '0.113', '0.130']
            
            for codigo_linha in linhas_principais:
                try:
                    veiculos = api.buscar_posicao_veiculos(codigo_linha)
                    cache.set(f'veiculos_tempo_real_{codigo_linha}', veiculos, 60)  # 1 min
                except Exception as e:
                    if verbose:
                        self.stdout.write(f"⚠️  Erro ao buscar veículos da linha {codigo_linha}: {e}")
            
            # Atualiza previsões para terminais principais
            terminais = Parada.objects.filter(tipo='terminal').values_list('codigo', flat=True)[:10]
            
            for codigo_parada in terminais:
                try:
                    previsoes = api.buscar_horarios_tempo_real(codigo_parada)
                    cache.set(f'previsoes_tempo_real_{codigo_parada}', previsoes, 60)  # 1 min
                except Exception as e:
                    if verbose:
                        self.stdout.write(f"⚠️  Erro ao buscar previsões da parada {codigo_parada}: {e}")
            
            if verbose:
                self.stdout.write("✅ Dados em tempo real atualizados")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar tempo real: {e}")
            return False 
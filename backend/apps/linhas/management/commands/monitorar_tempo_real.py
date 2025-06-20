"""
Comando para monitoramento em tempo real do sistema de transporte

Este comando implementa o monitoramento contínuo dos dados em tempo real
da API DFTrans, incluindo posições de veículos, previsões de chegada
e alertas de serviço.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.cache import cache
import time
import logging
from datetime import timedelta

from services.dftrans_api import DFTransAPI, sync_manager
from linhas.models import Linha
from paradas.models import Parada

logger = logging.getLogger('busfeed.tempo_real')


class Command(BaseCommand):
    help = 'Monitora dados em tempo real do sistema de transporte'

    def add_arguments(self, parser):
        parser.add_argument(
            '--intervalo',
            type=int,
            default=30,
            help='Intervalo em segundos entre atualizações (padrão: 30)'
        )
        parser.add_argument(
            '--linhas',
            nargs='+',
            help='Códigos específicos de linhas para monitorar'
        )
        parser.add_argument(
            '--paradas',
            nargs='+',
            help='Códigos específicos de paradas para monitorar'
        )
        parser.add_argument(
            '--alertas-apenas',
            action='store_true',
            help='Monitora apenas alertas de serviço'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas'
        )
        parser.add_argument(
            '--duracao',
            type=int,
            help='Duração do monitoramento em minutos (padrão: contínuo)'
        )

    def handle(self, *args, **options):
        intervalo = options['intervalo']
        linhas_especificas = options.get('linhas', [])
        paradas_especificas = options.get('paradas', [])
        alertas_apenas = options['alertas_apenas']
        verbose = options['verbose']
        duracao = options.get('duracao')
        
        # Configura logging
        if verbose:
            logging.getLogger('busfeed.tempo_real').setLevel(logging.DEBUG)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"🚌 Iniciando monitoramento em tempo real (intervalo: {intervalo}s)"
            )
        )
        
        # Inicia API DFTrans
        api = DFTransAPI()
        
        # Verifica status da API
        status = api.verificar_status_api()
        if not status.get('disponivel'):
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  API DFTrans não disponível: {status.get('erro', 'Erro desconhecido')}"
                )
            )
            self.stdout.write("Continuando com dados mock/cache...")
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ API DFTrans disponível (tempo: {status.get('tempo_resposta', 0):.2f}s)"
                )
            )
        
        # Calcula tempo de fim se duração foi especificada
        tempo_fim = None
        if duracao:
            tempo_fim = timezone.now() + timedelta(minutes=duracao)
            self.stdout.write(f"⏰ Monitoramento por {duracao} minutos")
        
        contador_ciclo = 0
        
        try:
            while True:
                contador_ciclo += 1
                inicio_ciclo = time.time()
                
                if verbose:
                    self.stdout.write(f"\n--- Ciclo {contador_ciclo} ---")
                
                # Verifica se deve parar
                if tempo_fim and timezone.now() >= tempo_fim:
                    self.stdout.write("⏰ Tempo de monitoramento concluído")
                    break
                
                # Monitora alertas de serviço
                self._monitorar_alertas(api, verbose)
                
                if not alertas_apenas:
                    # Monitora posições de veículos
                    self._monitorar_veiculos(api, linhas_especificas, verbose)
                    
                    # Monitora previsões de chegada
                    self._monitorar_previsoes(api, paradas_especificas, verbose)
                
                # Calcula tempo do ciclo
                tempo_ciclo = time.time() - inicio_ciclo
                
                if verbose:
                    self.stdout.write(f"⏱️  Ciclo completado em {tempo_ciclo:.2f}s")
                
                # Aguarda próximo ciclo
                tempo_espera = max(0, intervalo - tempo_ciclo)
                if tempo_espera > 0:
                    time.sleep(tempo_espera)
                
        except KeyboardInterrupt:
            self.stdout.write("\n🛑 Monitoramento interrompido pelo usuário")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro durante monitoramento: {e}")
            )
            raise CommandError(f"Falha no monitoramento: {e}")
        
        self.stdout.write(
            self.style.SUCCESS("✅ Monitoramento finalizado")
        )

    def _monitorar_alertas(self, api, verbose):
        """Monitora alertas de serviço"""
        try:
            alertas = api.buscar_alertas_servico()
            
            # Verifica novos alertas
            cache_key = 'alertas_monitorados'
            alertas_anteriores = cache.get(cache_key, [])
            alertas_anteriores_ids = {a.get('id') for a in alertas_anteriores}
            
            novos_alertas = [a for a in alertas if a.get('id') not in alertas_anteriores_ids]
            
            if novos_alertas:
                for alerta in novos_alertas:
                    gravidade = alerta.get('gravidade', 'baixa')
                    icon = {'baixa': '📘', 'media': '📙', 'alta': '📕'}.get(gravidade, '📗')
                    
                    self.stdout.write(
                        self.style.WARNING(
                            f"{icon} NOVO ALERTA: {alerta.get('titulo', 'Sem título')}"
                        )
                    )
                    
                    if verbose:
                        self.stdout.write(f"   Tipo: {alerta.get('tipo', 'N/A')}")
                        self.stdout.write(f"   Gravidade: {gravidade}")
                        if alerta.get('linhas_afetadas'):
                            self.stdout.write(f"   Linhas: {', '.join(alerta['linhas_afetadas'])}")
            
            # Atualiza cache
            cache.set(cache_key, alertas, 3600)  # 1 hora
            
            if verbose and not novos_alertas:
                self.stdout.write("✅ Nenhum novo alerta")
                
        except Exception as e:
            if verbose:
                self.stdout.write(f"❌ Erro ao monitorar alertas: {e}")

    def _monitorar_veiculos(self, api, linhas_especificas, verbose):
        """Monitora posições de veículos"""
        try:
            linhas_para_monitorar = linhas_especificas or []
            
            if not linhas_para_monitorar:
                # Se não especificou linhas, monitora algumas principais
                linhas_principais = Linha.objects.filter(
                    codigo__in=['0.111', '0.112', '0.113', '0.130']
                ).values_list('codigo', flat=True)
                linhas_para_monitorar = list(linhas_principais)
            
            total_veiculos = 0
            
            for codigo_linha in linhas_para_monitorar:
                veiculos = api.buscar_posicao_veiculos(codigo_linha)
                total_veiculos += len(veiculos)
                
                if verbose and veiculos:
                    self.stdout.write(f"🚍 Linha {codigo_linha}: {len(veiculos)} veículos ativos")
                    
                    for veiculo in veiculos[:3]:  # Mostra apenas os primeiros 3
                        ocupacao_icon = {
                            'baixa': '🟢',
                            'media': '🟡',
                            'alta': '🔴'
                        }.get(veiculo.get('ocupacao', 'desconhecida'), '⚪')
                        
                        self.stdout.write(
                            f"   📍 Veículo {veiculo.get('id', 'N/A')}: "
                            f"{ocupacao_icon} {veiculo.get('ocupacao', 'N/A')}"
                        )
            
            if verbose:
                self.stdout.write(f"🚍 Total de veículos monitorados: {total_veiculos}")
                
        except Exception as e:
            if verbose:
                self.stdout.write(f"❌ Erro ao monitorar veículos: {e}")

    def _monitorar_previsoes(self, api, paradas_especificas, verbose):
        """Monitora previsões de chegada"""
        try:
            paradas_para_monitorar = paradas_especificas or []
            
            if not paradas_para_monitorar:
                # Se não especificou paradas, monitora terminais principais
                paradas_principais = Parada.objects.filter(
                    tipo='terminal'
                ).values_list('codigo', flat=True)[:5]
                paradas_para_monitorar = list(paradas_principais)
            
            total_previsoes = 0
            
            for codigo_parada in paradas_para_monitorar:
                previsoes = api.buscar_horarios_tempo_real(codigo_parada)
                total_previsoes += len(previsoes)
                
                if verbose and previsoes:
                    try:
                        parada = Parada.objects.get(codigo=codigo_parada)
                        nome_parada = parada.nome
                    except Parada.DoesNotExist:
                        nome_parada = codigo_parada
                    
                    self.stdout.write(f"🚏 {nome_parada}: {len(previsoes)} previsões")
                    
                    # Mostra previsões mais próximas
                    previsoes_ordenadas = sorted(
                        previsoes, 
                        key=lambda x: x.get('tempo_chegada', 999)
                    )
                    
                    for previsao in previsoes_ordenadas[:3]:
                        tempo = previsao.get('tempo_chegada', 'N/A')
                        linha = previsao.get('linha', 'N/A')
                        status_icon = {
                            'normal': '✅',
                            'atrasado': '⏰',
                            'cancelado': '❌'
                        }.get(previsao.get('status', 'normal'), '❓')
                        
                        self.stdout.write(
                            f"   {status_icon} Linha {linha}: {tempo} min"
                        )
            
            if verbose:
                self.stdout.write(f"🚏 Total de previsões: {total_previsoes}")
                
        except Exception as e:
            if verbose:
                self.stdout.write(f"❌ Erro ao monitorar previsões: {e}") 
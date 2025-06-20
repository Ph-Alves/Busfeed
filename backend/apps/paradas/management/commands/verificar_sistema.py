"""
Comando para verificação completa do sistema BusFeed

Este comando verifica se todos os componentes do sistema estão funcionando
corretamente, incluindo banco de dados, APIs, frontend e integrações.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.conf import settings
from django.test.client import Client
import requests
import json
import logging
from datetime import datetime

from django.db import models
from paradas.models import Parada
from linhas.models import Linha, LinhaParada
from rotas.models import Rota
from usuarios.models import Usuario


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verifica o status completo do sistema BusFeed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas durante a verificação'
        )
        parser.add_argument(
            '--skip-frontend',
            action='store_true',
            help='Pula verificação do frontend React'
        )
        parser.add_argument(
            '--skip-apis',
            action='store_true',
            help='Pula verificação das APIs REST'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=10,
            help='Timeout para requisições HTTP em segundos (padrão: 10)'
        )

    def handle(self, *args, **options):
        """Executa a verificação completa do sistema"""
        
        if options['verbose']:
            self.stdout.write(
                self.style.SUCCESS('🔍 Iniciando verificação completa do sistema BusFeed...')
            )

        try:
            resultados = {}
            
            # Verificações básicas
            resultados['banco_dados'] = self._verificar_banco_dados(options['verbose'])
            resultados['modelos'] = self._verificar_modelos(options['verbose'])
            resultados['dados'] = self._verificar_dados(options['verbose'])
            
            # Verificações de APIs
            if not options['skip_apis']:
                resultados['apis'] = self._verificar_apis(options['verbose'], options['timeout'])
            
            # Verificações de frontend
            if not options['skip_frontend']:
                resultados['frontend'] = self._verificar_frontend(options['verbose'], options['timeout'])
            
            # Verificações de integração
            resultados['integracao'] = self._verificar_integracao(options['verbose'])
            
            # Relatório final
            self._gerar_relatorio_final(resultados, options['verbose'])

        except Exception as e:
            logger.error(f"Erro durante verificação: {e}")
            raise CommandError(f'Erro na verificação: {e}')

    def _verificar_banco_dados(self, verbose=False):
        """Verifica conectividade e status do banco de dados"""
        if verbose:
            self.stdout.write('🗄️  Verificando banco de dados...')
        
        try:
            # Testa conexão
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                resultado = cursor.fetchone()
            
            if resultado and resultado[0] == 1:
                if verbose:
                    self.stdout.write('  ✅ Conexão com banco estabelecida')
                
                # Verifica informações do banco
                db_info = connection.get_connection_params()
                if verbose:
                    self.stdout.write(f'  📊 Engine: {connection.vendor}')
                    if hasattr(connection, 'settings_dict'):
                        db_name = connection.settings_dict.get('NAME', 'N/A')
                        self.stdout.write(f'  📊 Database: {db_name}')
                
                return {
                    'status': 'OK',
                    'engine': connection.vendor,
                    'conectado': True
                }
            else:
                return {
                    'status': 'ERRO',
                    'erro': 'Falha na consulta de teste',
                    'conectado': False
                }
                
        except Exception as e:
            if verbose:
                self.stdout.write(f'  ❌ Erro na conexão: {e}')
            return {
                'status': 'ERRO',
                'erro': str(e),
                'conectado': False
            }

    def _verificar_modelos(self, verbose=False):
        """Verifica se os modelos Django estão funcionando"""
        if verbose:
            self.stdout.write('🏗️  Verificando modelos Django...')
        
        resultados = {}
        modelos = [
            ('Parada', Parada),
            ('Linha', Linha),
            ('LinhaParada', LinhaParada),
            ('Rota', Rota),
            ('Usuario', Usuario),
        ]
        
        for nome, modelo in modelos:
            try:
                # Tenta fazer uma consulta simples
                count = modelo.objects.count()
                resultados[nome] = {
                    'status': 'OK',
                    'count': count
                }
                if verbose:
                    self.stdout.write(f'  ✅ {nome}: {count} registros')
                    
            except Exception as e:
                resultados[nome] = {
                    'status': 'ERRO',
                    'erro': str(e)
                }
                if verbose:
                    self.stdout.write(f'  ❌ {nome}: {e}')
        
        return resultados

    def _verificar_dados(self, verbose=False):
        """Verifica a integridade e consistência dos dados"""
        if verbose:
            self.stdout.write('📊 Verificando integridade dos dados...')
        
        resultados = {}
        
        try:
            # Verifica paradas
            total_paradas = Parada.objects.count()
            paradas_com_coordenadas = Parada.objects.filter(
                latitude__isnull=False,
                longitude__isnull=False
            ).count()
            
            resultados['paradas'] = {
                'total': total_paradas,
                'com_coordenadas': paradas_com_coordenadas,
                'percentual_coordenadas': (paradas_com_coordenadas / total_paradas * 100) if total_paradas > 0 else 0
            }
            
            # Verifica linhas
            total_linhas = Linha.objects.count()
            linhas_ativas = Linha.objects.filter(status='active').count()
            
            resultados['linhas'] = {
                'total': total_linhas,
                'ativas': linhas_ativas,
                'percentual_ativas': (linhas_ativas / total_linhas * 100) if total_linhas > 0 else 0
            }
            
            # Verifica relacionamentos
            total_relacionamentos = LinhaParada.objects.count()
            linhas_com_paradas = LinhaParada.objects.values('linha').distinct().count()
            
            resultados['relacionamentos'] = {
                'total': total_relacionamentos,
                'linhas_com_paradas': linhas_com_paradas,
                'media_paradas_por_linha': (total_relacionamentos / linhas_com_paradas) if linhas_com_paradas > 0 else 0
            }
            
            if verbose:
                self.stdout.write(f'  📍 Paradas: {total_paradas} ({paradas_com_coordenadas} com coordenadas)')
                self.stdout.write(f'  🚌 Linhas: {total_linhas} ({linhas_ativas} ativas)')
                self.stdout.write(f'  🔗 Relacionamentos: {total_relacionamentos}')
            
            return resultados
            
        except Exception as e:
            if verbose:
                self.stdout.write(f'  ❌ Erro na verificação de dados: {e}')
            return {
                'status': 'ERRO',
                'erro': str(e)
            }

    def _verificar_apis(self, verbose=False, timeout=10):
        """Verifica se as APIs REST estão funcionando"""
        if verbose:
            self.stdout.write('🌐 Verificando APIs REST...')
        
        resultados = {}
        client = Client()
        
        # Lista de endpoints para testar
        endpoints = [
            ('paradas', '/api/paradas/'),
            ('linhas', '/api/linhas/'),
            ('buscar_paradas', '/api/paradas/buscar/?q=terminal'),
            ('buscar_linhas', '/api/linhas/buscar/?q=0.111'),
        ]
        
        for nome, endpoint in endpoints:
            try:
                response = client.get(endpoint)
                
                if response.status_code == 200:
                    resultados[nome] = {
                        'status': 'OK',
                        'status_code': response.status_code,
                        'content_type': response.get('Content-Type', 'N/A')
                    }
                    if verbose:
                        self.stdout.write(f'  ✅ {nome}: {response.status_code}')
                else:
                    resultados[nome] = {
                        'status': 'ERRO',
                        'status_code': response.status_code
                    }
                    if verbose:
                        self.stdout.write(f'  ❌ {nome}: {response.status_code}')
                        
            except Exception as e:
                resultados[nome] = {
                    'status': 'ERRO',
                    'erro': str(e)
                }
                if verbose:
                    self.stdout.write(f'  ❌ {nome}: {e}')
        
        # Testa API de cálculo de rotas
        try:
            rota_data = {
                'origem': {'lat': -15.7942, 'lng': -47.8822, 'nome': 'Teste Origem'},
                'destino': {'lat': -15.8267, 'lng': -48.1089, 'nome': 'Teste Destino'}
            }
            
            response = client.post(
                '/api/rotas/calcular/',
                data=json.dumps(rota_data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                resultados['calcular_rotas'] = {
                    'status': 'OK',
                    'status_code': response.status_code
                }
                if verbose:
                    self.stdout.write(f'  ✅ calcular_rotas: {response.status_code}')
            else:
                resultados['calcular_rotas'] = {
                    'status': 'ERRO',
                    'status_code': response.status_code
                }
                if verbose:
                    self.stdout.write(f'  ❌ calcular_rotas: {response.status_code}')
                    
        except Exception as e:
            resultados['calcular_rotas'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
            if verbose:
                self.stdout.write(f'  ❌ calcular_rotas: {e}')
        
        return resultados

    def _verificar_frontend(self, verbose=False, timeout=10):
        """Verifica se o frontend React está funcionando"""
        if verbose:
            self.stdout.write('⚛️  Verificando frontend React...')
        
        try:
            # Tenta acessar o frontend
            response = requests.get('http://localhost:3000/', timeout=timeout)
            
            if response.status_code == 200:
                # Verifica se contém elementos React típicos
                content = response.text.lower()
                tem_react = 'react' in content or 'id="root"' in content
                
                resultado = {
                    'status': 'OK',
                    'status_code': response.status_code,
                    'tem_react': tem_react,
                    'tamanho_resposta': len(response.text)
                }
                
                if verbose:
                    self.stdout.write(f'  ✅ Frontend acessível: {response.status_code}')
                    if tem_react:
                        self.stdout.write('  ✅ Elementos React detectados')
                    else:
                        self.stdout.write('  ⚠️  Elementos React não detectados')
                
                return resultado
            else:
                if verbose:
                    self.stdout.write(f'  ❌ Frontend retornou: {response.status_code}')
                return {
                    'status': 'ERRO',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.ConnectionError:
            if verbose:
                self.stdout.write('  ❌ Frontend não está rodando (conexão recusada)')
            return {
                'status': 'ERRO',
                'erro': 'Frontend não está rodando'
            }
        except requests.exceptions.Timeout:
            if verbose:
                self.stdout.write('  ❌ Timeout ao acessar frontend')
            return {
                'status': 'ERRO',
                'erro': 'Timeout'
            }
        except Exception as e:
            if verbose:
                self.stdout.write(f'  ❌ Erro ao verificar frontend: {e}')
            return {
                'status': 'ERRO',
                'erro': str(e)
            }

    def _verificar_integracao(self, verbose=False):
        """Verifica integração entre componentes"""
        if verbose:
            self.stdout.write('🔗 Verificando integração entre componentes...')
        
        resultados = {}
        
        try:
            # Verifica se há linhas com paradas
            linhas_com_paradas = Linha.objects.filter(
                linhaparada__isnull=False
            ).distinct().count()
            
            total_linhas = Linha.objects.count()
            
            # Verifica se há paradas em múltiplas linhas
            paradas_multiplas_linhas = Parada.objects.filter(
                linhaparada__isnull=False
            ).annotate(
                num_linhas=models.Count('linhaparada__linha', distinct=True)
            ).filter(num_linhas__gt=1).count()
            
            resultados['linha_parada'] = {
                'linhas_com_paradas': linhas_com_paradas,
                'total_linhas': total_linhas,
                'percentual_integrado': (linhas_com_paradas / total_linhas * 100) if total_linhas > 0 else 0,
                'paradas_multiplas_linhas': paradas_multiplas_linhas
            }
            
            if verbose:
                self.stdout.write(f'  🔗 Linhas com paradas: {linhas_com_paradas}/{total_linhas}')
                self.stdout.write(f'  🔗 Paradas em múltiplas linhas: {paradas_multiplas_linhas}')
            
            return resultados
            
        except Exception as e:
            if verbose:
                self.stdout.write(f'  ❌ Erro na verificação de integração: {e}')
            return {
                'status': 'ERRO',
                'erro': str(e)
            }

    def _gerar_relatorio_final(self, resultados, verbose=False):
        """Gera relatório final da verificação"""
        self.stdout.write('\n📋 RELATÓRIO FINAL DA VERIFICAÇÃO:')
        self.stdout.write(f'🕐 Executado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        
        # Conta sucessos e falhas
        total_verificacoes = 0
        verificacoes_ok = 0
        
        for categoria, resultado in resultados.items():
            if isinstance(resultado, dict):
                if 'status' in resultado:
                    total_verificacoes += 1
                    if resultado['status'] == 'OK':
                        verificacoes_ok += 1
                else:
                    # Para categorias com subcategorias
                    for sub_categoria, sub_resultado in resultado.items():
                        if isinstance(sub_resultado, dict) and 'status' in sub_resultado:
                            total_verificacoes += 1
                            if sub_resultado['status'] == 'OK':
                                verificacoes_ok += 1
        
        # Status geral
        if verificacoes_ok == total_verificacoes:
            status_geral = '✅ SISTEMA FUNCIONANDO CORRETAMENTE'
            cor = self.style.SUCCESS
        elif verificacoes_ok > total_verificacoes * 0.7:
            status_geral = '⚠️  SISTEMA FUNCIONANDO COM PROBLEMAS MENORES'
            cor = self.style.WARNING
        else:
            status_geral = '❌ SISTEMA COM PROBLEMAS CRÍTICOS'
            cor = self.style.ERROR
        
        self.stdout.write(f'\n{cor(status_geral)}')
        self.stdout.write(f'📊 Verificações: {verificacoes_ok}/{total_verificacoes} OK')
        
        # Detalhes por categoria
        for categoria, resultado in resultados.items():
            self.stdout.write(f'\n📂 {categoria.upper()}:')
            
            if isinstance(resultado, dict) and 'status' in resultado:
                status_icon = '✅' if resultado['status'] == 'OK' else '❌'
                self.stdout.write(f'  {status_icon} Status: {resultado["status"]}')
            else:
                # Para categorias com subcategorias
                for sub_categoria, sub_resultado in resultado.items():
                    if isinstance(sub_resultado, dict):
                        if 'status' in sub_resultado:
                            status_icon = '✅' if sub_resultado['status'] == 'OK' else '❌'
                            self.stdout.write(f'  {status_icon} {sub_categoria}: {sub_resultado["status"]}')
                        else:
                            self.stdout.write(f'  📊 {sub_categoria}: {sub_resultado}')
        
        # Recomendações
        self.stdout.write('\n💡 RECOMENDAÇÕES:')
        
        if verificacoes_ok < total_verificacoes:
            self.stdout.write('  🔧 Corrija os problemas identificados acima')
            
        if 'dados' in resultados:
            dados = resultados['dados']
            if isinstance(dados, dict):
                if 'paradas' in dados and dados['paradas']['total'] == 0:
                    self.stdout.write('  📍 Execute: python manage.py popular_dados_mock --limpar --verbose')
                    
        self.stdout.write('  📚 Consulte a documentação para mais detalhes')
        self.stdout.write('  🆘 Use --verbose para informações detalhadas')
        
        self.stdout.write('\n✅ Verificação concluída!') 
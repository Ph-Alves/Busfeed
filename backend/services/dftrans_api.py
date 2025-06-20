"""
BusFeed - Integração com API DFTrans

Este módulo fornece integração com a API oficial do DFTrans
para obter dados em tempo real sobre linhas, paradas e rotas
do sistema de transporte público do Distrito Federal.
"""

import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import json
import hashlib
import time
from threading import Thread

logger = logging.getLogger('busfeed.dftrans_api')


class DFTransAPIError(Exception):
    """Exceção customizada para erros da API DFTrans"""
    pass


class DFTransAPI:
    """
    Cliente para integração com a API DFTrans
    
    Fornece métodos para buscar informações sobre:
    - Paradas de ônibus
    - Linhas de transporte
    - Rotas e trajetos
    - Horários em tempo real
    - Notificações de serviço
    """
    
    def __init__(self):
        self.base_url = settings.DFTRANS_API_BASE_URL
        self.api_key = settings.DFTRANS_API_KEY
        self.session = requests.Session()
        
        # Configuração de headers
        self.session.headers.update({
            'User-Agent': 'BusFeed/1.0',
            'Accept': 'application/json',
        })
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def _make_request(self, endpoint: str, params: Dict = None, timeout: int = 10) -> Dict:
        """
        Realiza uma requisição para a API DFTrans
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            timeout: Timeout em segundos
            
        Returns:
            Dict: Dados da resposta
            
        Raises:
            DFTransAPIError: Em caso de erro na requisição
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Fazendo requisição para: {url}")
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Resposta recebida: {len(str(data))} caracteres")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {url}: {e}")
            raise DFTransAPIError(f"Erro ao conectar com a API DFTrans: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            raise DFTransAPIError(f"Resposta inválida da API DFTrans: {e}")
    
    def _get_cached_or_fetch(self, cache_key: str, fetch_function, cache_timeout: int = 300):
        """
        Busca dados do cache ou executa a função de fetch
        
        Args:
            cache_key: Chave do cache
            fetch_function: Função para buscar os dados
            cache_timeout: Timeout do cache em segundos
            
        Returns:
            Dados do cache ou da função de fetch
        """
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Dados encontrados no cache: {cache_key}")
            return cached_data
        
        logger.debug(f"Buscando dados da API: {cache_key}")
        data = fetch_function()
        cache.set(cache_key, data, cache_timeout)
        
        return data
    
    def buscar_paradas(self, limite: int = 100) -> List[Dict]:
        """
        Busca todas as paradas de ônibus do DF
        
        Args:
            limite: Número máximo de paradas a retornar
            
        Returns:
            List[Dict]: Lista de paradas
        """
        cache_key = f"dftrans_paradas_{limite}"
        
        def fetch_paradas():
            try:
                # Endpoint para paradas (pode variar dependendo da API real)
                data = self._make_request('paradas', {'limit': limite})
                
                # Processa os dados para o formato esperado
                paradas = []
                for item in data.get('paradas', []):
                    parada = {
                        'codigo': item.get('codigo'),
                        'nome': item.get('nome'),
                        'descricao': item.get('descricao', ''),
                        'latitude': float(item.get('latitude', 0)),
                        'longitude': float(item.get('longitude', 0)),
                        'endereco': item.get('endereco', ''),
                        'linhas': item.get('linhas', []),
                        'tipo': self._determinar_tipo_parada(item),
                        'acessibilidade': item.get('acessibilidade', False),
                    }
                    paradas.append(parada)
                
                return paradas
                
            except Exception as e:
                logger.error(f"Erro ao buscar paradas: {e}")
                return self._get_mock_paradas()  # Fallback para dados mock
        
        return self._get_cached_or_fetch(cache_key, fetch_paradas, cache_timeout=1800)  # 30 min
    
    def buscar_linhas(self) -> List[Dict]:
        """
        Busca todas as linhas de transporte do DF
        
        Returns:
            List[Dict]: Lista de linhas
        """
        cache_key = "dftrans_linhas"
        
        def fetch_linhas():
            try:
                data = self._make_request('linhas')
                
                linhas = []
                for item in data.get('linhas', []):
                    linha = {
                        'codigo': item.get('codigo'),
                        'nome': item.get('nome'),
                        'origem': item.get('origem'),
                        'destino': item.get('destino'),
                        'tipo': item.get('tipo', 'onibus'),
                        'tarifa': float(item.get('tarifa', 0)),
                        'primeiro_horario': item.get('primeiro_horario'),
                        'ultimo_horario': item.get('ultimo_horario'),
                        'intervalo_pico': item.get('intervalo_pico'),
                        'intervalo_normal': item.get('intervalo_normal'),
                        'acessibilidade': item.get('acessibilidade', False),
                        'trajeto': item.get('trajeto', []),
                        'paradas': item.get('paradas', []),
                    }
                    linhas.append(linha)
                
                return linhas
                
            except Exception as e:
                logger.error(f"Erro ao buscar linhas: {e}")
                return self._get_mock_linhas()  # Fallback para dados mock
        
        return self._get_cached_or_fetch(cache_key, fetch_linhas, cache_timeout=3600)  # 1 hora
    
    def buscar_trajeto_linha(self, codigo_linha: str) -> Optional[List[Tuple[float, float]]]:
        """
        Busca o trajeto geográfico de uma linha específica
        
        Args:
            codigo_linha: Código da linha
            
        Returns:
            List[Tuple[float, float]]: Lista de coordenadas do trajeto
        """
        cache_key = f"dftrans_trajeto_{codigo_linha}"
        
        def fetch_trajeto():
            try:
                data = self._make_request(f'linhas/{codigo_linha}/trajeto')
                
                trajeto = []
                for ponto in data.get('trajeto', []):
                    lat = float(ponto.get('latitude', 0))
                    lng = float(ponto.get('longitude', 0))
                    if lat and lng:
                        trajeto.append((lat, lng))
                
                return trajeto
                
            except Exception as e:
                logger.error(f"Erro ao buscar trajeto da linha {codigo_linha}: {e}")
                return []  # Retorna lista vazia em caso de erro
        
        return self._get_cached_or_fetch(cache_key, fetch_trajeto, cache_timeout=7200)  # 2 horas
    
    def buscar_horarios_tempo_real(self, codigo_parada: str) -> List[Dict]:
        """
        Busca horários de chegada em tempo real para uma parada
        
        Args:
            codigo_parada: Código da parada
            
        Returns:
            List[Dict]: Lista de previsões de chegada
        """
        cache_key = f"dftrans_tempo_real_{codigo_parada}"
        
        def fetch_horarios():
            try:
                data = self._make_request(f'paradas/{codigo_parada}/tempo-real')
                
                previsoes = []
                for item in data.get('previsoes', []):
                    previsao = {
                        'linha': item.get('linha'),
                        'destino': item.get('destino'),
                        'tempo_chegada': item.get('tempo_chegada'),  # em minutos
                        'distancia': item.get('distancia'),  # em metros
                        'acessivel': item.get('acessivel', False),
                        'status': item.get('status', 'normal'),  # normal, atrasado, cancelado
                        'veiculo_id': item.get('veiculo_id'),
                        'ultima_atualizacao': item.get('ultima_atualizacao'),
                    }
                    previsoes.append(previsao)
                
                return previsoes
                
            except Exception as e:
                logger.error(f"Erro ao buscar horários tempo real para parada {codigo_parada}: {e}")
                return []  # Retorna lista vazia em caso de erro
        
        return self._get_cached_or_fetch(cache_key, fetch_horarios, cache_timeout=60)  # 1 minuto
    
    def buscar_alertas_servico(self) -> List[Dict]:
        """
        Busca alertas e notificações sobre o serviço de transporte
        
        Returns:
            List[Dict]: Lista de alertas
        """
        cache_key = "dftrans_alertas"
        
        def fetch_alertas():
            try:
                data = self._make_request('alertas')
                
                alertas = []
                for item in data.get('alertas', []):
                    alerta = {
                        'id': item.get('id'),
                        'tipo': item.get('tipo'),  # manutencao, acidente, mudanca_rota
                        'titulo': item.get('titulo'),
                        'descricao': item.get('descricao'),
                        'linhas_afetadas': item.get('linhas_afetadas', []),
                        'paradas_afetadas': item.get('paradas_afetadas', []),
                        'gravidade': item.get('gravidade', 'baixa'),  # baixa, media, alta
                        'data_inicio': item.get('data_inicio'),
                        'data_fim': item.get('data_fim'),
                        'ativo': item.get('ativo', True),
                    }
                    alertas.append(alerta)
                
                return alertas
                
            except Exception as e:
                logger.error(f"Erro ao buscar alertas de serviço: {e}")
                return []
        
        return self._get_cached_or_fetch(cache_key, fetch_alertas, cache_timeout=300)  # 5 minutos
    
    def buscar_posicao_veiculos(self, codigo_linha: str = None) -> List[Dict]:
        """
        Busca posição em tempo real dos veículos
        
        Args:
            codigo_linha: Código da linha (opcional, se None busca todos)
            
        Returns:
            List[Dict]: Lista de posições de veículos
        """
        cache_key = f"dftrans_veiculos_{codigo_linha or 'todos'}"
        
        def fetch_posicoes():
            try:
                endpoint = 'veiculos'
                params = {}
                if codigo_linha:
                    params['linha'] = codigo_linha
                
                data = self._make_request(endpoint, params)
                
                veiculos = []
                for item in data.get('veiculos', []):
                    veiculo = {
                        'id': item.get('id'),
                        'linha': item.get('linha'),
                        'latitude': float(item.get('latitude', 0)),
                        'longitude': float(item.get('longitude', 0)),
                        'velocidade': item.get('velocidade', 0),
                        'direcao': item.get('direcao'),  # ida, volta
                        'timestamp': item.get('timestamp'),
                        'acessivel': item.get('acessivel', False),
                        'ocupacao': item.get('ocupacao', 'desconhecida'),  # baixa, media, alta
                    }
                    veiculos.append(veiculo)
                
                return veiculos
                
            except Exception as e:
                logger.error(f"Erro ao buscar posição dos veículos: {e}")
                return []
        
        return self._get_cached_or_fetch(cache_key, fetch_posicoes, cache_timeout=30)  # 30 segundos
    
    def verificar_status_api(self) -> Dict:
        """
        Verifica o status da API DFTrans
        
        Returns:
            Dict: Status da API
        """
        try:
            start_time = time.time()
            data = self._make_request('status', timeout=5)
            response_time = time.time() - start_time
            
            return {
                'disponivel': True,
                'tempo_resposta': response_time,
                'versao': data.get('versao', 'desconhecida'),
                'ultima_atualizacao': data.get('ultima_atualizacao'),
                'servicos_ativos': data.get('servicos_ativos', []),
                'mensagem': data.get('mensagem', 'API funcionando normalmente')
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status da API: {e}")
            return {
                'disponivel': False,
                'erro': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    def _determinar_tipo_parada(self, parada_data: Dict) -> str:
        """
        Determina o tipo da parada baseado nos dados
        
        Args:
            parada_data: Dados da parada
            
        Returns:
            str: Tipo da parada
        """
        nome = parada_data.get('nome', '').lower()
        
        if 'terminal' in nome:
            return 'terminal'
        elif 'estação' in nome or 'metro' in nome:
            return 'estacao'
        elif 'shopping' in nome or 'centro comercial' in nome:
            return 'shopping'
        elif 'hospital' in nome or 'posto de saúde' in nome:
            return 'saude'
        elif 'escola' in nome or 'universidade' in nome or 'faculdade' in nome:
            return 'educacao'
        else:
            return 'comum'
    
    def _get_mock_paradas(self) -> List[Dict]:
        """Retorna dados mock de paradas para desenvolvimento/fallback"""
        return [
            {
                'codigo': '001',
                'nome': 'Terminal Rodoviário',
                'descricao': 'Terminal central do Plano Piloto',
                'latitude': -15.8267,
                'longitude': -47.9218,
                'endereco': 'Eixo Monumental, Brasília - DF',
                'linhas': ['0.111', '0.112', '0.113'],
                'tipo': 'terminal',
                'acessibilidade': True,
            },
            {
                'codigo': '002',
                'nome': 'Terminal Ceilândia Centro',
                'descricao': 'Terminal da Ceilândia',
                'latitude': -15.8267,
                'longitude': -48.1089,
                'endereco': 'QNM 13, Ceilândia - DF',
                'linhas': ['0.111', '0.114'],
                'tipo': 'terminal',
                'acessibilidade': True,
            },
            # Adicione mais paradas mock conforme necessário
        ]
    
    def _get_mock_linhas(self) -> List[Dict]:
        """Retorna dados mock de linhas para desenvolvimento/fallback"""
        return [
            {
                'codigo': '0.111',
                'nome': 'Rodoviária - Ceilândia (Centro)',
                'origem': 'Terminal Rodoviário',
                'destino': 'Terminal Ceilândia Centro',
                'tipo': 'onibus',
                'tarifa': 5.50,
                'primeiro_horario': '05:00',
                'ultimo_horario': '23:30',
                'intervalo_pico': 10,
                'intervalo_normal': 15,
                'acessibilidade': True,
                'trajeto': [],
                'paradas': ['001', '002'],
            },
            # Adicione mais linhas mock conforme necessário
        ]


class DFTransSyncManager:
    """
    Gerenciador de sincronização automática com a API DFTrans
    """
    
    def __init__(self):
        self.api = DFTransAPI()
        self.is_running = False
    
    def iniciar_sincronizacao_automatica(self):
        """Inicia a sincronização automática em background"""
        if self.is_running:
            logger.warning("Sincronização automática já está rodando")
            return
        
        self.is_running = True
        logger.info("Iniciando sincronização automática com DFTrans")
        
        # Inicia thread para sincronização
        sync_thread = Thread(target=self._loop_sincronizacao, daemon=True)
        sync_thread.start()
    
    def parar_sincronizacao_automatica(self):
        """Para a sincronização automática"""
        self.is_running = False
        logger.info("Sincronização automática parada")
    
    def _loop_sincronizacao(self):
        """Loop principal de sincronização"""
        while self.is_running:
            try:
                # Sincroniza dados principais a cada 30 minutos
                self.sincronizar_dados_principais()
                
                # Aguarda 30 minutos
                for _ in range(1800):  # 30 minutos = 1800 segundos
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Erro durante sincronização automática: {e}")
                time.sleep(300)  # Aguarda 5 minutos em caso de erro
    
    def sincronizar_dados_principais(self):
        """Sincroniza paradas e linhas com o banco de dados"""
        try:
            # Importa aqui para evitar circular import
            from paradas.models import Parada, TipoParada
            from linhas.models import Linha
            
            logger.info("Iniciando sincronização de dados principais")
            
            # Sincroniza paradas
            paradas_api = self.api.buscar_paradas(limite=1000)
            paradas_sincronizadas = 0
            
            for parada_data in paradas_api:
                parada, created = Parada.objects.update_or_create(
                    codigo_dftrans=parada_data['codigo'],
                    defaults={
                        'nome': parada_data['nome'],
                        'descricao': parada_data['descricao'],
                        'latitude': parada_data['latitude'],
                        'longitude': parada_data['longitude'],
                        'endereco': parada_data['endereco'],
                        'tipo': parada_data['tipo'],
                        'tem_acessibilidade': parada_data['acessibilidade'],
                    }
                )
                
                if created:
                    paradas_sincronizadas += 1
            
            logger.info(f"Paradas sincronizadas: {paradas_sincronizadas} novas")
            
            # Sincroniza linhas
            linhas_api = self.api.buscar_linhas()
            linhas_sincronizadas = 0
            
            for linha_data in linhas_api:
                linha, created = Linha.objects.update_or_create(
                    codigo=linha_data['codigo'],
                    defaults={
                        'nome': linha_data['nome'],
                        'origem': linha_data['origem'],
                        'destino': linha_data['destino'],
                        'tipo': linha_data['tipo'],
                        'tarifa': linha_data['tarifa'],
                        'primeiro_horario': linha_data['primeiro_horario'],
                        'ultimo_horario': linha_data['ultimo_horario'],
                        'intervalo_pico': linha_data['intervalo_pico'],
                        'intervalo_normal': linha_data['intervalo_normal'],
                        'tem_acessibilidade': linha_data['acessibilidade'],
                    }
                )
                
                if created:
                    linhas_sincronizadas += 1
            
            logger.info(f"Linhas sincronizadas: {linhas_sincronizadas} novas")
            
        except Exception as e:
            logger.error(f"Erro durante sincronização de dados principais: {e}")


# Instância global do gerenciador de sincronização
sync_manager = DFTransSyncManager()


def sincronizar_paradas_dftrans():
    """
    Função para sincronizar paradas com a API DFTrans
    
    Esta função pode ser chamada manualmente ou via management command
    """
    from paradas.models import Parada, TipoParada
    
    api = DFTransAPI()
    
    try:
        logger.info("Iniciando sincronização de paradas com DFTrans")
        
        paradas = api.buscar_paradas(limite=1000)
        total_criadas = 0
        total_atualizadas = 0
        
        for parada_data in paradas:
            try:
                parada, created = Parada.objects.update_or_create(
                    codigo_dftrans=parada_data['codigo'],
                    defaults={
                        'nome': parada_data['nome'],
                        'descricao': parada_data.get('descricao', ''),
                        'latitude': parada_data['latitude'],
                        'longitude': parada_data['longitude'],
                        'endereco': parada_data.get('endereco', ''),
                        'tipo': parada_data.get('tipo', TipoParada.SECUNDARIA),
                        'tem_acessibilidade': parada_data.get('acessibilidade', False),
                    }
                )
                
                if created:
                    total_criadas += 1
                else:
                    total_atualizadas += 1
                    
                logger.debug(f"Parada {'criada' if created else 'atualizada'}: {parada.nome}")
                
            except Exception as e:
                logger.error(f"Erro ao processar parada {parada_data.get('codigo', 'UNKNOWN')}: {e}")
        
        logger.info(f"Sincronização concluída: {total_criadas} criadas, {total_atualizadas} atualizadas")
        
        return {
            'success': True,
            'criadas': total_criadas,
            'atualizadas': total_atualizadas,
            'total': total_criadas + total_atualizadas
        }
        
    except Exception as e:
        logger.error(f"Erro durante sincronização de paradas: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def sincronizar_linhas_dftrans():
    """
    Função para sincronizar linhas com a API DFTrans
    
    Esta função pode ser chamada manualmente ou via management command
    """
    from linhas.models import Linha
    
    api = DFTransAPI()
    
    try:
        logger.info("Iniciando sincronização de linhas com DFTrans")
        
        linhas = api.buscar_linhas()
        total_criadas = 0
        total_atualizadas = 0
        
        for linha_data in linhas:
            try:
                linha, created = Linha.objects.update_or_create(
                    codigo=linha_data['codigo'],
                    defaults={
                        'nome': linha_data['nome'],
                        'origem': linha_data.get('origem', ''),
                        'destino': linha_data.get('destino', ''),
                        'tipo': linha_data.get('tipo', 'onibus'),
                        'tarifa': linha_data.get('tarifa', 0),
                        'primeiro_horario': linha_data.get('primeiro_horario'),
                        'ultimo_horario': linha_data.get('ultimo_horario'),
                        'intervalo_pico': linha_data.get('intervalo_pico'),
                        'intervalo_normal': linha_data.get('intervalo_normal'),
                        'tem_acessibilidade': linha_data.get('acessibilidade', False),
                    }
                )
                
                if created:
                    total_criadas += 1
                else:
                    total_atualizadas += 1
                    
                logger.debug(f"Linha {'criada' if created else 'atualizada'}: {linha.nome}")
                
            except Exception as e:
                logger.error(f"Erro ao processar linha {linha_data.get('codigo', 'UNKNOWN')}: {e}")
        
        logger.info(f"Sincronização concluída: {total_criadas} criadas, {total_atualizadas} atualizadas")
        
        return {
            'success': True,
            'criadas': total_criadas,
            'atualizadas': total_atualizadas,
            'total': total_criadas + total_atualizadas
        }
        
    except Exception as e:
        logger.error(f"Erro durante sincronização de linhas: {e}")
        return {
            'success': False,
            'error': str(e)
        } 
"""
Utilitários e funções auxiliares para o BusFeed.
Contém decorators, helpers e funções reutilizáveis para todo o sistema.
"""
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
import logging
import hashlib
import json
import time

logger = logging.getLogger('busfeed.utils')


def cache_key_generator(*args, **kwargs) -> str:
    """
    Gera chave única para cache baseada nos argumentos.
    
    Args:
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
        
    Returns:
        String única para usar como chave de cache
    """
    # Criar string única baseada nos argumentos
    cache_string = f"{args}_{sorted(kwargs.items())}"
    
    # Gerar hash MD5 para garantir tamanho consistente
    return hashlib.md5(cache_string.encode('utf-8')).hexdigest()


def smart_cache(timeout: int = None, cache_name: str = 'default', 
               key_prefix: str = None, vary_on: List[str] = None):
    """
    Decorator para cache inteligente de funções.
    
    Args:
        timeout: Tempo de expiração em segundos
        cache_name: Nome do cache a usar (default, routes, stops, etc.)
        key_prefix: Prefixo para a chave de cache
        vary_on: Lista de atributos para variar o cache
        
    Usage:
        @smart_cache(timeout=3600, cache_name='routes', key_prefix='route_stats')
        def get_route_statistics():
            # função custosa
            return data
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave de cache única
            base_key = key_prefix or func.__name__
            
            # Adicionar argumentos à chave se necessário
            if vary_on:
                vary_values = []
                for attr in vary_on:
                    if attr in kwargs:
                        vary_values.append(f"{attr}_{kwargs[attr]}")
                
                if vary_values:
                    base_key += f"_{'_'.join(vary_values)}"
            
            # Adicionar hash dos argumentos para garantir unicidade
            if args or kwargs:
                args_hash = cache_key_generator(*args, **kwargs)
                cache_key = f"{base_key}_{args_hash}"
            else:
                cache_key = base_key
            
            # Tentar buscar do cache
            cached_result = cache.get(cache_key, cache=cache_name)
            
            if cached_result is not None:
                logger.debug(f'Cache hit: {cache_key}')
                return cached_result
            
            # Executar função e cachear resultado
            try:
                result = func(*args, **kwargs)
                
                # Determinar timeout baseado no tipo de dados ou usar padrão
                if timeout is None:
                    cache_timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get(
                        cache_name, 300
                    )
                else:
                    cache_timeout = timeout
                
                cache.set(cache_key, result, cache_timeout, cache=cache_name)
                logger.debug(f'Cache set: {cache_key} (timeout: {cache_timeout}s)')
                
                return result
                
            except Exception as e:
                logger.error(f'Error in cached function {func.__name__}: {e}')
                raise
        
        return wrapper
    return decorator


def performance_monitor(threshold_ms: float = 1000):
    """
    Decorator para monitorar performance de funções.
    Loga avisos quando funções demoram mais que o limite.
    
    Args:
        threshold_ms: Limite em milissegundos para gerar aviso
        
    Usage:
        @performance_monitor(threshold_ms=500)
        def slow_function():
            # função que pode ser lenta
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000
                
                if execution_time > threshold_ms:
                    logger.warning(
                        f'Slow function: {func.__name__} took {execution_time:.2f}ms '
                        f'(threshold: {threshold_ms}ms)'
                    )
                else:
                    logger.debug(
                        f'Function {func.__name__} executed in {execution_time:.2f}ms'
                    )
        
        return wrapper
    return decorator


def safe_api_response(func: Callable) -> Callable:
    """
    Decorator para garantir que APIs sempre retornem JSON válido.
    Captura exceções e retorna erro formatado.
    
    Usage:
        @safe_api_response
        def my_api_view(request):
            # código que pode gerar exceção
            return JsonResponse({'data': data})
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            
            # Se não é JsonResponse, converter para um
            if not isinstance(response, JsonResponse):
                if isinstance(response, dict):
                    response = JsonResponse(response)
                else:
                    response = JsonResponse({'data': response})
            
            # Adicionar timestamp para debugging
            if hasattr(response, 'content'):
                try:
                    content = json.loads(response.content)
                    if isinstance(content, dict):
                        content['_timestamp'] = timezone.now().isoformat()
                        response.content = json.dumps(content).encode('utf-8')
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
            
            return response
            
        except Exception as e:
            logger.error(f'API error in {func.__name__}: {e}', exc_info=True)
            
            error_response = {
                'error': True,
                'message': 'Erro interno do servidor',
                'details': str(e) if settings.DEBUG else None,
                'timestamp': timezone.now().isoformat(),
            }
            
            return JsonResponse(error_response, status=500)
    
    return wrapper


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Valida se as coordenadas são válidas.
    
    Args:
        latitude: Latitude para validar
        longitude: Longitude para validar
        
    Returns:
        True se coordenadas são válidas
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        return (-90 <= lat <= 90) and (-180 <= lng <= 180)
    except (TypeError, ValueError):
        return False


def format_distance(distance_meters: float) -> str:
    """
    Formata distância em metros para exibição amigável.
    
    Args:
        distance_meters: Distância em metros
        
    Returns:
        String formatada (ex: "150m", "1.2km")
    """
    if distance_meters < 1000:
        return f"{int(distance_meters)}m"
    else:
        return f"{distance_meters / 1000:.1f}km"


def format_duration(minutes: int) -> str:
    """
    Formata duração em minutos para exibição amigável.
    
    Args:
        minutes: Duração em minutos
        
    Returns:
        String formatada (ex: "5min", "1h 30min")
    """
    if minutes < 60:
        return f"{minutes}min"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_minutes}min"


def sanitize_query(query: str, max_length: int = 100) -> str:
    """
    Sanitiza query de busca removendo caracteres perigosos.
    
    Args:
        query: String de busca
        max_length: Tamanho máximo permitido
        
    Returns:
        String sanitizada
    """
    if not query:
        return ""
    
    # Remover caracteres potencialmente perigosos
    unsafe_chars = ['<', '>', '"', "'", '&', '%', '\\', '/', ';']
    sanitized = query
    
    for char in unsafe_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limitar tamanho
    sanitized = sanitized[:max_length]
    
    # Remover espaços extras
    return ' '.join(sanitized.split())


def batch_process(items: List[Any], batch_size: int = 100, 
                 processor: Callable = None) -> List[Any]:
    """
    Processa lista de itens em batches para otimizar performance.
    
    Args:
        items: Lista de itens para processar
        batch_size: Tamanho do batch
        processor: Função para processar cada batch
        
    Returns:
        Lista com resultados processados
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        if processor:
            batch_result = processor(batch)
            if isinstance(batch_result, list):
                results.extend(batch_result)
            else:
                results.append(batch_result)
        else:
            results.extend(batch)
    
    return results


def get_client_ip(request) -> str:
    """
    Obtém IP real do cliente considerando proxies.
    
    Args:
        request: Request do Django
        
    Returns:
        IP do cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PerformanceTracker:
    """
    Classe para rastrear performance de operações.
    """
    
    def __init__(self):
        self.start_time = None
        self.checkpoints = []
    
    def start(self):
        """Inicia o rastreamento."""
        self.start_time = time.time()
        self.checkpoints = []
    
    def checkpoint(self, name: str):
        """Adiciona um checkpoint com nome."""
        if self.start_time is None:
            return
        
        current_time = time.time()
        elapsed = (current_time - self.start_time) * 1000
        
        self.checkpoints.append({
            'name': name,
            'elapsed_ms': round(elapsed, 2),
            'timestamp': timezone.now().isoformat()
        })
    
    def finish(self) -> Dict:
        """Finaliza e retorna relatório de performance."""
        if self.start_time is None:
            return {}
        
        total_time = (time.time() - self.start_time) * 1000
        
        return {
            'total_ms': round(total_time, 2),
            'checkpoints': self.checkpoints,
            'started_at': timezone.now().isoformat()
        }


def create_response_metadata(request, additional_data: Dict = None) -> Dict:
    """
    Cria metadados padrão para respostas de API.
    
    Args:
        request: Request do Django
        additional_data: Dados adicionais para incluir
        
    Returns:
        Dicionário com metadados
    """
    metadata = {
        'timestamp': timezone.now().isoformat(),
        'timezone': str(timezone.get_current_timezone()),
        'version': getattr(settings, 'API_VERSION', '1.0'),
        'environment': 'development' if settings.DEBUG else 'production',
    }
    
    if additional_data:
        metadata.update(additional_data)
    
    return metadata


# Constantes úteis para o sistema
BRASILIA_COORDINATES = (-15.7801, -47.9292)
DEFAULT_SEARCH_RADIUS = 1000  # metros
MAX_SEARCH_RESULTS = 50
DEFAULT_PAGINATION_SIZE = 20

# Mapeamento de status HTTP para mensagens amigáveis
HTTP_STATUS_MESSAGES = {
    200: 'Sucesso',
    201: 'Criado com sucesso',
    400: 'Dados inválidos',
    401: 'Não autorizado',
    403: 'Acesso negado',
    404: 'Não encontrado',
    500: 'Erro interno do servidor',
    502: 'Serviço indisponível',
    503: 'Serviço temporariamente indisponível',
} 
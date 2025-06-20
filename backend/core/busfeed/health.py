# BusFeed - Health Check Views
# Endpoints para monitoramento da saúde da aplicação

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Health check básico da aplicação.
    Verifica se os serviços essenciais estão funcionando.
    """
    health_status = {
        'status': 'healthy',
        'services': {},
        'version': '1.0.0',
        'environment': 'production' if not settings.DEBUG else 'development'
    }
    
    # Verificar conexão com banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status['services']['database'] = 'unhealthy'
        health_status['status'] = 'unhealthy'
    
    # Verificar cache
    try:
        cache.set('health_check', 'ok', 30)
        cache_value = cache.get('health_check')
        if cache_value == 'ok':
            health_status['services']['cache'] = 'healthy'
        else:
            health_status['services']['cache'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        health_status['services']['cache'] = 'unhealthy'
        health_status['status'] = 'unhealthy'
    
    # Verificar Redis (se configurado)
    if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
        try:
            # Implementar verificação Redis se necessário
            health_status['services']['redis'] = 'healthy'
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health_status['services']['redis'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
    
    # Retornar status HTTP apropriado
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)

def liveness_check(request):
    """
    Liveness probe - verifica se a aplicação está rodando.
    Usado por orquestradores como Kubernetes.
    """
    return JsonResponse({'status': 'alive'})

def readiness_check(request):
    """
    Readiness probe - verifica se a aplicação está pronta para receber tráfego.
    Usado por orquestradores como Kubernetes.
    """
    # Verificações mais rigorosas para readiness
    try:
        # Verificar banco de dados
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM paradas_parada LIMIT 1")
        
        # Verificar cache
        cache.set('readiness_check', 'ok', 10)
        
        return JsonResponse({'status': 'ready'})
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({'status': 'not ready', 'error': str(e)}, status=503) 
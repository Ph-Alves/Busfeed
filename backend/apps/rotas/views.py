"""
Views para o app de rotas
"""

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .models import Rota
from .serializers import RotaSerializer
from .services import CalculadoraRotas

logger = logging.getLogger(__name__)


class RotaViewSet(viewsets.ModelViewSet):
    """ViewSet para rotas salvas"""
    queryset = Rota.objects.all()
    serializer_class = RotaSerializer


@csrf_exempt
@api_view(['POST'])
def calcular_rotas(request):
    """
    Calcula rotas entre dois pontos
    """
    try:
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        
        origem = data.get('origem')
        destino = data.get('destino')
        opcoes = data.get('opcoes', {})
        
        if not origem or not destino:
            return JsonResponse({
                'error': 'Origem e destino são obrigatórios'
            }, status=400)
        
        # Extrai coordenadas dos objetos origem e destino
        if isinstance(origem, dict):
            origem_coords = (origem.get('lat'), origem.get('lng'))
            origem_nome = origem.get('nome', 'Origem')
        else:
            return JsonResponse({
                'error': 'Formato de origem inválido'
            }, status=400)
            
        if isinstance(destino, dict):
            destino_coords = (destino.get('lat'), destino.get('lng'))
            destino_nome = destino.get('nome', 'Destino')
        else:
            return JsonResponse({
                'error': 'Formato de destino inválido'
            }, status=400)
        
        # Valida coordenadas
        if not all([origem_coords[0], origem_coords[1], destino_coords[0], destino_coords[1]]):
            return JsonResponse({
                'error': 'Coordenadas de origem e destino são obrigatórias'
            }, status=400)
        
        # Usa o serviço de cálculo de rotas
        calculadora = CalculadoraRotas()
        rotas = calculadora.calcular_rotas(
            origem_coords, 
            destino_coords, 
            origem_nome, 
            destino_nome
        )
        
        return JsonResponse({
            'rotas': rotas,
            'total': len(rotas)
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular rotas: {e}")
        return JsonResponse({
            'error': 'Erro interno do servidor',
            'details': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def salvar_rota(request):
    """
    Salva uma rota como favorita
    """
    try:
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        
        serializer = RotaSerializer(data=data)
        if serializer.is_valid():
            rota = serializer.save()
            return JsonResponse({
                'id': rota.id,
                'message': 'Rota salva com sucesso'
            })
        else:
            return JsonResponse({
                'error': 'Dados inválidos',
                'details': serializer.errors
            }, status=400)
            
    except Exception as e:
        logger.error(f"Erro ao salvar rota: {e}")
        return JsonResponse({
            'error': 'Erro interno do servidor'
        }, status=500)


@api_view(['GET'])
def listar_rotas_salvas(request):
    """
    Lista rotas salvas do usuário
    """
    try:
        rotas = Rota.objects.filter(ativa=True).order_by('-criado_em')
        serializer = RotaSerializer(rotas, many=True)
        
        return JsonResponse({
            'results': serializer.data,
            'total': rotas.count()
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar rotas salvas: {e}")
        return JsonResponse({
            'error': 'Erro interno do servidor'
        }, status=500)

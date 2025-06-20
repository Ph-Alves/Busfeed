"""
BusFeed - Serializers para Rotas

Este módulo define os serializers para a API REST de cálculo de rotas.
"""

from rest_framework import serializers
from .models import Rota, RotaLinha, RotaParada


class RotaLinhaSerializer(serializers.ModelSerializer):
    """
    Serializer para relacionamento rota-linha
    """
    
    class Meta:
        model = RotaLinha
        fields = [
            'ordem',
            'linha',
            'parada_embarque',
            'parada_desembarque',
            'tempo_viagem',
            'distancia_percorrida',
        ]


class RotaParadaSerializer(serializers.ModelSerializer):
    """
    Serializer para relacionamento rota-parada
    """
    
    class Meta:
        model = RotaParada
        fields = [
            'parada',
            'tipo_uso',
            'ordem',
            'tempo_parada',
            'observacoes',
        ]


class RotaSerializer(serializers.ModelSerializer):
    """
    Serializer para rotas completas
    """
    
    linhas = RotaLinhaSerializer(many=True, read_only=True, source='rotalinha_set')
    paradas = RotaParadaSerializer(many=True, read_only=True, source='rotaparada_set')
    
    class Meta:
        model = Rota
        fields = [
            'id',
            'nome',
            'descricao',
            'origem_nome',
            'origem_latitude',
            'origem_longitude',
            'destino_nome',
            'destino_latitude',
            'destino_longitude',
            'tipo',
            'status',
            'tempo_total_estimado',
            'tempo_caminhada',
            'tempo_transporte',
            'tempo_espera',
            'distancia_total',
            'distancia_caminhada',
            'custo_total',
            'numero_baldeacoes',
            'avaliacao_media',
            'numero_avaliacoes',
            'linhas',
            'paradas',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']


class BuscarRotaSerializer(serializers.Serializer):
    """
    Serializer para parâmetros de busca de rotas
    """
    
    origem_latitude = serializers.FloatField(
        help_text="Latitude da origem"
    )
    origem_longitude = serializers.FloatField(
        help_text="Longitude da origem"
    )
    destino_latitude = serializers.FloatField(
        help_text="Latitude do destino"
    )
    destino_longitude = serializers.FloatField(
        help_text="Longitude do destino"
    )
    tipo_otimizacao = serializers.ChoiceField(
        choices=['tempo', 'distancia', 'custo', 'baldeacoes'],
        default='tempo',
        help_text="Critério de otimização da rota"
    )
    max_baldeacoes = serializers.IntegerField(
        default=3,
        min_value=0,
        max_value=5,
        help_text="Número máximo de baldeações"
    )
    max_caminhada = serializers.IntegerField(
        default=1000,
        min_value=100,
        max_value=3000,
        help_text="Distância máxima de caminhada em metros"
    )
    apenas_acessivel = serializers.BooleanField(
        default=False,
        help_text="Considerar apenas linhas acessíveis"
    )


class RotaResumoSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para rotas (para listas)
    """
    
    class Meta:
        model = Rota
        fields = [
            'id',
            'nome',
            'origem_nome',
            'destino_nome',
            'tipo',
            'status',
            'tempo_total_estimado',
            'distancia_total',
            'numero_baldeacoes',
            'custo_total',
            'avaliacao_media',
        ] 
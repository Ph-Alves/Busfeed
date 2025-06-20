"""
BusFeed - Serializers para Linhas

Este módulo define os serializers para a API REST das linhas de ônibus.
"""

from rest_framework import serializers
# from rest_framework_gis.serializers import GeoFeatureModelSerializer  # Temporariamente desabilitado
from .models import Linha, LinhaParada
from paradas.serializers import ParadaResumoSerializer


class LinhaSerializer(serializers.ModelSerializer):
    """
    Serializer completo para linhas de ônibus
    """
    
    nome_completo = serializers.ReadOnlyField()
    distancia_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Linha
        fields = [
            'id',
            'codigo',
            'nome',
            'nome_completo',
            'nome_curto',
            'tipo',
            'status',
            'origem',
            'destino',
            'trajeto_descricao',
            'tarifa',
            'primeiro_horario',
            'ultimo_horario',
            'intervalo_pico',
            'intervalo_normal',
            'tempo_viagem_estimado',
            'tem_acessibilidade',
            'cor_linha',
            'observacoes',
            'distancia_total',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']
    
    def get_distancia_total(self, obj):
        """Calcula a distância total do trajeto"""
        # Implementação temporária sem PostGIS
        return None  # Será implementado quando PostGIS estiver ativo


class LinhaResumoSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para linhas (para uso em listas e autocomplete)
    """
    
    nome_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Linha
        fields = [
            'id',
            'codigo',
            'nome',
            'nome_completo',
            'tipo',
            'origem',
            'destino',
            'tarifa',
            'tem_acessibilidade',
            'status',
        ]


# Temporariamente desabilitado até PostGIS estar configurado
# class LinhaGeoJSONSerializer(GeoFeatureModelSerializer):
#     """
#     Serializer GeoJSON para linhas (trajetos no mapa)
#     """
#     
#     class Meta:
#         model = Linha
#         geo_field = 'trajeto_geometria'
#         fields = [
#             'id',
#             'codigo',
#             'nome',
#             'tipo',
#             'origem',
#             'destino',
#             'cor_linha',
#             'tem_acessibilidade',
#             'status',
#         ]


class LinhaParadaSerializer(serializers.ModelSerializer):
    """
    Serializer para relacionamento linha-parada
    """
    
    parada = ParadaResumoSerializer(read_only=True)
    
    class Meta:
        model = LinhaParada
        fields = [
            'ordem',
            'parada',
            'tempo_parada',
            'distancia_origem',
            'observacoes',
        ]


class LinhaComParadasSerializer(serializers.ModelSerializer):
    """
    Serializer para linha com suas paradas ordenadas
    """
    
    paradas_ordenadas = serializers.SerializerMethodField()
    nome_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Linha
        fields = [
            'id',
            'codigo',
            'nome',
            'nome_completo',
            'tipo',
            'origem',
            'destino',
            'tarifa',
            'primeiro_horario',
            'ultimo_horario',
            'intervalo_pico',
            'intervalo_normal',
            'tem_acessibilidade',
            'cor_linha',
            'paradas_ordenadas',
        ]
    
    def get_paradas_ordenadas(self, obj):
        """Retorna as paradas da linha ordenadas por sequência"""
        linha_paradas = obj.get_paradas_ordenadas()
        return LinhaParadaSerializer(linha_paradas, many=True).data


class BuscaLinhasSerializer(serializers.Serializer):
    """
    Serializer para parâmetros de busca de linhas
    """
    
    origem = serializers.CharField(
        required=False,
        help_text="Filtrar por origem"
    )
    destino = serializers.CharField(
        required=False,
        help_text="Filtrar por destino"
    )
    tipo = serializers.ChoiceField(
        choices=['bus', 'metro', 'brt', 'micro'],
        required=False,
        help_text="Filtrar por tipo de transporte"
    )
    acessivel = serializers.BooleanField(
        default=False,
        help_text="Apenas linhas acessíveis"
    )
    parada_id = serializers.IntegerField(
        required=False,
        help_text="ID da parada para filtrar linhas que passam por ela"
    ) 
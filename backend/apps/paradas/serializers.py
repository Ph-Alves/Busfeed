"""
BusFeed - Serializers para Paradas

Este módulo define os serializers para a API REST das paradas de ônibus.
"""

from rest_framework import serializers
# from rest_framework_gis.serializers import GeoFeatureModelSerializer  # Temporariamente desabilitado
from .models import Parada


class ParadaSerializer(serializers.ModelSerializer):
    """
    Serializer padrão para paradas de ônibus
    
    Inclui coordenadas formatadas para facilitar o uso no frontend.
    """
    
    coordenadas = serializers.SerializerMethodField()
    
    class Meta:
        model = Parada
        fields = [
            'id',
            'codigo_dftrans',
            'nome',
            'descricao',
            'coordenadas',
            'latitude',
            'longitude',
            'tipo',
            'tem_acessibilidade',
            'tem_cobertura',
            'tem_banco',
            'movimento_estimado',
            'endereco',
            'pontos_referencia',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']
    
    def get_coordenadas(self, obj):
        """Retorna coordenadas no formato [longitude, latitude] para compatibilidade com mapas"""
        return [obj.longitude, obj.latitude]


class ParadaResumoSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para paradas (para uso em listas e autocomplete)
    """
    
    coordenadas = serializers.SerializerMethodField()
    
    class Meta:
        model = Parada
        fields = [
            'id',
            'codigo_dftrans',
            'nome',
            'descricao',
            'coordenadas',
            'tipo',
            'tem_acessibilidade',
            'endereco',
        ]
    
    def get_coordenadas(self, obj):
        """Retorna coordenadas no formato [longitude, latitude]"""
        return [obj.longitude, obj.latitude]


class ParadaGeoJSONSerializer(serializers.ModelSerializer):
    """
    Serializer GeoJSON para paradas (para uso em mapas)
    
    Retorna dados no formato GeoJSON padrão para facilitar
    a integração com bibliotecas de mapas como Leaflet.
    """
    
    class Meta:
        model = Parada
        fields = [
            'id',
            'codigo_dftrans',
            'nome',
            'descricao',
            'tipo',
            'tem_acessibilidade',
            'tem_cobertura',
            'tem_banco',
            'movimento_estimado',
            'endereco',
        ]
    
    def to_representation(self, instance):
        """Converte para formato GeoJSON"""
        data = super().to_representation(instance)
        
        # Formato GeoJSON padrão
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [instance.longitude, instance.latitude]
            },
            "properties": data
        }


class ParadaProximaSerializer(serializers.Serializer):
    """
    Serializer para busca de paradas próximas
    
    Inclui informações de distância calculada.
    """
    
    parada = ParadaResumoSerializer()
    distancia = serializers.FloatField(help_text="Distância em metros")
    
    class Meta:
        fields = ['parada', 'distancia']


class BuscaParadasProximasSerializer(serializers.Serializer):
    """
    Serializer para parâmetros de busca de paradas próximas
    """
    
    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
        help_text="Latitude do ponto de referência"
    )
    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
        help_text="Longitude do ponto de referência"
    )
    raio = serializers.IntegerField(
        default=500,
        min_value=100,
        max_value=5000,
        help_text="Raio de busca em metros (100-5000)"
    )
    limite = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=50,
        help_text="Número máximo de paradas a retornar (1-50)"
    )
    tipos = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Filtrar por tipos de parada (ex: ['terminal', 'main'])"
    )
    apenas_acessiveis = serializers.BooleanField(
        default=False,
        help_text="Retornar apenas paradas acessíveis"
    ) 
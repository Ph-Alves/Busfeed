"""
BusFeed - Modelos para Paradas de Ônibus

Este módulo define os modelos de dados para paradas de ônibus no sistema
com suporte completo a campos geográficos PostGIS.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# from django.contrib.gis.db import models as gis_models  # Desabilitado temporariamente
# from django.contrib.gis.geos import Point  # Desabilitado temporariamente


class TipoParada(models.TextChoices):
    """Tipos de paradas disponíveis no sistema"""
    PRINCIPAL = 'main', 'Principal'
    SECUNDARIA = 'secondary', 'Secundária'
    TERMINAL = 'terminal', 'Terminal'
    METRO = 'metro', 'Estação de Metrô'
    AEROPORTO = 'airport', 'Aeroporto'
    HOSPITAL = 'hospital', 'Hospital'
    SHOPPING = 'shopping', 'Shopping'
    EDUCACAO = 'education', 'Educacional'


class Parada(models.Model):
    """
    Modelo para paradas de ônibus no Distrito Federal com suporte PostGIS
    """
    
    # Identificação básica
    codigo_dftrans = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Código oficial da parada no sistema DFTrans"
    )
    nome = models.CharField(
        max_length=255,
        help_text="Nome oficial da parada"
    )
    descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada da localização"
    )
    
    # Localização geográfica (preparado para PostGIS)
    # localizacao = gis_models.PointField(  # Será habilitado com PostGIS
    #     help_text="Coordenadas geográficas da parada (SRID=4326)",
    #     srid=4326  # WGS84 - padrão para GPS
    # )
    
    # Campos de latitude e longitude 
    latitude = models.FloatField(
        help_text="Latitude da parada"
    )
    longitude = models.FloatField(
        help_text="Longitude da parada"
    )
    
    # Classificação e características
    tipo = models.CharField(
        max_length=20,
        choices=TipoParada.choices,
        default=TipoParada.SECUNDARIA,
        help_text="Tipo da parada"
    )
    
    # Acessibilidade e infraestrutura
    tem_acessibilidade = models.BooleanField(
        default=False,
        help_text="Indica se a parada tem recursos de acessibilidade"
    )
    tem_cobertura = models.BooleanField(
        default=False,
        help_text="Indica se a parada tem cobertura/abrigo"
    )
    tem_banco = models.BooleanField(
        default=False,
        help_text="Indica se a parada tem bancos para sentar"
    )
    
    # Dados estatísticos
    movimento_estimado = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        help_text="Número estimado de passageiros por dia"
    )
    
    # Endereço e referências
    endereco = models.CharField(
        max_length=500,
        blank=True,
        help_text="Endereço completo da parada"
    )
    pontos_referencia = models.TextField(
        blank=True,
        help_text="Pontos de referência próximos à parada"
    )
    
    # Controle de dados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Parada"
        verbose_name_plural = "Paradas"
        ordering = ['nome']
        indexes = [
            models.Index(fields=['codigo_dftrans']),
            models.Index(fields=['tipo']),
            models.Index(fields=['tem_acessibilidade']),
        ]
    
    @classmethod
    def criar_com_coordenadas(cls, latitude, longitude, **kwargs):
        """
        Método de conveniência para criar parada com lat/lng
        """
        kwargs['latitude'] = latitude
        kwargs['longitude'] = longitude
        return cls.objects.create(**kwargs)
    
    def definir_coordenadas(self, latitude, longitude):
        """
        Define as coordenadas da parada
        """
        self.latitude = latitude
        self.longitude = longitude
    
    def distancia_para(self, outra_parada):
        """
        Calcula a distância em metros para outra parada (aproximação simples)
        """
        if not self.latitude or not self.longitude or not outra_parada.latitude or not outra_parada.longitude:
            return None
        
        # Fórmula de Haversine simplificada para distâncias curtas
        import math
        lat1, lng1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lng2 = math.radians(outra_parada.latitude), math.radians(outra_parada.longitude)
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Raio da Terra em metros
        return c * 6371000
    
    def paradas_proximas(self, raio_metros=500):
        """
        Retorna paradas próximas dentro do raio especificado (implementação simples)
        """
        if not self.latitude or not self.longitude:
            return Parada.objects.none()
        
        # Aproximação simples usando bounding box
        raio_graus = raio_metros / 111000
        
        return Parada.objects.filter(
            latitude__range=(self.latitude - raio_graus, self.latitude + raio_graus),
            longitude__range=(self.longitude - raio_graus, self.longitude + raio_graus)
        ).exclude(id=self.id)

    def __str__(self):
        return f"{self.nome} ({self.codigo_dftrans})"

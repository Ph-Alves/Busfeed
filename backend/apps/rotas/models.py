"""
BusFeed - Modelos para Rotas

Este módulo define os modelos para cálculo e armazenamento de rotas
entre diferentes localizações no sistema de transporte público
com suporte completo a campos geográficos PostGIS.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
# from django.contrib.gis.db import models as gis_models  # Desabilitado temporariamente
# from django.contrib.gis.geos import Point, LineString  # Desabilitado temporariamente


class TipoRota(models.TextChoices):
    """Tipos de rotas disponíveis"""
    DIRETA = 'direct', 'Direta'
    COM_BALDEACAO = 'transfer', 'Com Baldeação'
    CAMINHADA = 'walking', 'Caminhada'
    MISTA = 'mixed', 'Mista (Transporte + Caminhada)'


class StatusRota(models.TextChoices):
    """Status da rota calculada"""
    ATIVA = 'active', 'Ativa'
    INATIVA = 'inactive', 'Inativa'
    TEMPORARIA = 'temporary', 'Temporária'
    MANUTENCAO = 'maintenance', 'Em Manutenção'


class Rota(models.Model):
    """
    Modelo para rotas calculadas entre duas localizações com suporte PostGIS
    """
    
    # Identificação da rota
    nome = models.CharField(
        max_length=255,
        help_text="Nome descritivo da rota"
    )
    descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada da rota"
    )
    
    # Pontos de origem e destino (preparado para PostGIS)
    origem_nome = models.CharField(
        max_length=255,
        help_text="Nome do local de origem"
    )
    # origem_ponto = gis_models.PointField(  # Será habilitado com PostGIS
    #     help_text="Coordenadas geográficas da origem (SRID=4326)",
    #     srid=4326
    # )
    origem_latitude = models.FloatField(
        help_text="Latitude da origem"
    )
    origem_longitude = models.FloatField(
        help_text="Longitude da origem"
    )
    
    destino_nome = models.CharField(
        max_length=255,
        help_text="Nome do local de destino"
    )
    # destino_ponto = gis_models.PointField(  # Será habilitado com PostGIS
    #     help_text="Coordenadas geográficas do destino (SRID=4326)",
    #     srid=4326
    # )
    destino_latitude = models.FloatField(
        help_text="Latitude do destino"
    )
    destino_longitude = models.FloatField(
        help_text="Longitude do destino"
    )
    
    # Geometria completa da rota (preparado para PostGIS)
    # rota_geom = gis_models.LineStringField(  # Será habilitado com PostGIS
    #     null=True,
    #     blank=True,
    #     help_text="Geometria completa da rota (SRID=4326)",
    #     srid=4326
    # )
    
    # Classificação da rota
    tipo = models.CharField(
        max_length=15,
        choices=TipoRota.choices,
        default=TipoRota.DIRETA,
        help_text="Tipo da rota"
    )
    status = models.CharField(
        max_length=15,
        choices=StatusRota.choices,
        default=StatusRota.ATIVA,
        help_text="Status operacional da rota"
    )
    
    # Informações de tempo e distância
    tempo_total_estimado = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(600)],
        help_text="Tempo total estimado em minutos"
    )
    tempo_caminhada = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Tempo de caminhada em minutos"
    )
    tempo_transporte = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(480)],
        help_text="Tempo no transporte público em minutos"
    )
    tempo_espera = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(60)],
        help_text="Tempo de espera estimado em minutos"
    )
    
    # Distâncias
    distancia_total = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Distância total em quilômetros"
    )
    distancia_caminhada = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Distância de caminhada em quilômetros"
    )
    
    # Informações financeiras
    custo_total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Custo total da viagem em reais"
    )
    numero_baldeacoes = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(5)],
        help_text="Número de baldeações necessárias"
    )
    
    # Avaliação e feedback
    avaliacao_media = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text="Avaliação média dos usuários (1-5)"
    )
    numero_avaliacoes = models.PositiveIntegerField(
        default=0,
        help_text="Número total de avaliações"
    )
    
    # Controle de dados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rota"
        verbose_name_plural = "Rotas"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['status']),
            models.Index(fields=['-criado_em']),
        ]
    
    @classmethod
    def criar_com_coordenadas(cls, origem_lat, origem_lng, destino_lat, destino_lng, **kwargs):
        """
        Método de conveniência para criar rota com coordenadas
        """
        kwargs['origem_latitude'] = origem_lat
        kwargs['origem_longitude'] = origem_lng
        kwargs['destino_latitude'] = destino_lat
        kwargs['destino_longitude'] = destino_lng
        return cls.objects.create(**kwargs)
    
    def calcular_distancia_direta(self):
        """
        Calcula a distância direta (linha reta) entre origem e destino usando Haversine
        """
        if not all([self.origem_latitude, self.origem_longitude, 
                   self.destino_latitude, self.destino_longitude]):
            return 0.0
        
        # Fórmula de Haversine
        import math
        lat1, lng1 = math.radians(self.origem_latitude), math.radians(self.origem_longitude)
        lat2, lng2 = math.radians(self.destino_latitude), math.radians(self.destino_longitude)
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Retorna distância em metros
        return c * 6371000
    
    def gerar_geometria_rota(self):
        """
        Placeholder para gerar geometria da rota (será implementado com PostGIS)
        """
        # TODO: Implementar quando PostGIS estiver disponível
        return None

    def __str__(self):
        return f"{self.origem_nome} → {self.destino_nome}"


class RotaLinha(models.Model):
    """
    Modelo intermediário para relacionamento Rota-Linha
    
    Define quais linhas são utilizadas em cada rota e em que ordem.
    """
    
    rota = models.ForeignKey(
        Rota,
        on_delete=models.CASCADE,
        help_text="Rota que utiliza esta linha"
    )
    linha = models.ForeignKey(
        'linhas.Linha',
        on_delete=models.CASCADE,
        help_text="Linha utilizada na rota"
    )
    
    # Ordem da linha na rota
    ordem = models.PositiveIntegerField(
        help_text="Ordem sequencial da linha na rota"
    )
    
    # Paradas de embarque e desembarque
    parada_embarque = models.ForeignKey(
        'paradas.Parada',
        on_delete=models.CASCADE,
        related_name='embarques_rota',
        help_text="Parada de embarque nesta linha"
    )
    parada_desembarque = models.ForeignKey(
        'paradas.Parada',
        on_delete=models.CASCADE,
        related_name='desembarques_rota',
        help_text="Parada de desembarque nesta linha"
    )
    
    # Informações específicas desta etapa
    tempo_viagem = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(240)],
        help_text="Tempo de viagem nesta etapa em minutos"
    )
    distancia_percorrida = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Distância percorrida nesta etapa em quilômetros"
    )
    
    # Controle de dados
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Rota-Linha"
        verbose_name_plural = "Rotas-Linhas"
        unique_together = [['rota', 'ordem']]
        ordering = ['rota', 'ordem']
        indexes = [
            models.Index(fields=['rota', 'ordem']),
        ]
    
    def __str__(self):
        return f"{self.rota} - Etapa {self.ordem}: {self.linha.codigo}"


class RotaParada(models.Model):
    """
    Modelo intermediário para relacionamento Rota-Parada
    
    Define quais paradas são utilizadas em cada rota.
    """
    
    rota = models.ForeignKey(
        Rota,
        on_delete=models.CASCADE,
        help_text="Rota que utiliza esta parada"
    )
    parada = models.ForeignKey(
        'paradas.Parada',
        on_delete=models.CASCADE,
        help_text="Parada utilizada na rota"
    )
    
    # Tipo de uso da parada na rota
    TIPO_USO_CHOICES = [
        ('origem', 'Origem'),
        ('destino', 'Destino'),
        ('embarque', 'Embarque'),
        ('desembarque', 'Desembarque'),
        ('baldeacao', 'Baldeação'),
        ('passagem', 'Passagem'),
    ]
    
    tipo_uso = models.CharField(
        max_length=15,
        choices=TIPO_USO_CHOICES,
        help_text="Tipo de uso da parada na rota"
    )
    
    # Ordem na rota
    ordem = models.PositiveIntegerField(
        help_text="Ordem sequencial da parada na rota"
    )
    
    # Tempo estimado nesta parada
    tempo_parada = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        help_text="Tempo de parada/espera em minutos"
    )
    
    # Observações específicas
    observacoes = models.TextField(
        blank=True,
        help_text="Observações sobre o uso desta parada na rota"
    )
    
    # Controle de dados
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Rota-Parada"
        verbose_name_plural = "Rotas-Paradas"
        unique_together = [['rota', 'parada', 'tipo_uso']]
        ordering = ['rota', 'ordem']
        indexes = [
            models.Index(fields=['rota', 'ordem']),
            models.Index(fields=['tipo_uso']),
        ]
    
    def __str__(self):
        return f"{self.rota} - {self.parada.nome} ({self.tipo_uso})"

"""
BusFeed - Modelos para Linhas de Ônibus

Este módulo define os modelos de dados para linhas de ônibus
com suporte completo a campos geográficos PostGIS.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
# from django.contrib.gis.db import models as gis_models  # Desabilitado temporariamente
# from django.contrib.gis.geos import LineString, Point  # Desabilitado temporariamente


class TipoLinha(models.TextChoices):
    """Tipos de linhas de transporte"""
    ONIBUS = 'bus', 'Ônibus'
    METRO = 'metro', 'Metrô'
    BRT = 'brt', 'BRT'
    MICRO = 'micro', 'Micro-ônibus'


class StatusLinha(models.TextChoices):
    """Status operacional da linha"""
    ATIVA = 'active', 'Ativa'
    INATIVA = 'inactive', 'Inativa'
    MANUTENCAO = 'maintenance', 'Em Manutenção'
    TEMPORARIA = 'temporary', 'Temporária'


class Linha(models.Model):
    """
    Modelo para linhas de transporte público no DF com suporte PostGIS
    """
    
    # Identificação da linha
    codigo = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código oficial da linha (ex: 0.111, 0.030)"
    )
    nome = models.CharField(
        max_length=255,
        help_text="Nome descritivo da linha"
    )
    nome_curto = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nome abreviado para exibição"
    )
    
    # Classificação
    tipo = models.CharField(
        max_length=10,
        choices=TipoLinha.choices,
        default=TipoLinha.ONIBUS,
        help_text="Tipo de transporte da linha"
    )
    status = models.CharField(
        max_length=15,
        choices=StatusLinha.choices,
        default=StatusLinha.ATIVA,
        help_text="Status operacional atual"
    )
    
    # Trajeto e destinos
    origem = models.CharField(
        max_length=255,
        help_text="Ponto de origem da linha"
    )
    destino = models.CharField(
        max_length=255,
        help_text="Ponto de destino da linha"
    )
    trajeto_descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada do trajeto"
    )
    
    # Geometria do trajeto (preparado para PostGIS)
    # trajeto_geom = gis_models.LineStringField(  # Será habilitado com PostGIS
    #     null=True,
    #     blank=True,
    #     help_text="Geometria do trajeto da linha (SRID=4326)",
    #     srid=4326
    # )
    
    # Informações operacionais
    tarifa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Valor da tarifa em reais"
    )
    
    # Horários de operação
    primeiro_horario = models.TimeField(
        null=True,
        blank=True,
        help_text="Horário do primeiro ônibus"
    )
    ultimo_horario = models.TimeField(
        null=True,
        blank=True,
        help_text="Horário do último ônibus"
    )
    
    # Frequência e tempo de viagem
    intervalo_pico = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        help_text="Intervalo entre ônibus no horário de pico (minutos)"
    )
    intervalo_normal = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        help_text="Intervalo entre ônibus no horário normal (minutos)"
    )
    tempo_viagem_estimado = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(5), MaxValueValidator(300)],
        help_text="Tempo estimado de viagem completa (minutos)"
    )
    
    # Acessibilidade
    tem_acessibilidade = models.BooleanField(
        default=False,
        help_text="Indica se a linha tem veículos acessíveis"
    )
    
    # Metadados
    cor_linha = models.CharField(
        max_length=7,
        blank=True,
        help_text="Cor da linha em hexadecimal (ex: #FF0000)"
    )
    observacoes = models.TextField(
        blank=True,
        help_text="Observações sobre a linha"
    )
    
    # Controle de dados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Linha"
        verbose_name_plural = "Linhas"
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    @property
    def nome_completo(self):
        """Retorna o nome completo da linha com origem e destino"""
        return f"{self.codigo} - {self.origem} / {self.destino}"
    
    def get_paradas_ordenadas(self):
        """Retorna as paradas da linha ordenadas por sequência"""
        return self.linhaparada_set.all().order_by('ordem')
    
    def calcular_distancia_total(self):
        """Calcula a distância total do trajeto baseado nas paradas"""
        paradas = self.get_paradas_ordenadas()
        if paradas.count() < 2:
            return 0.0
        
        distancia_total = 0.0
        parada_anterior = None
        
        for linha_parada in paradas:
            if parada_anterior:
                distancia = parada_anterior.parada.distancia_para(linha_parada.parada)
                if distancia:
                    distancia_total += distancia / 1000  # Converte para km
            parada_anterior = linha_parada
        
        return distancia_total
    
    def gerar_trajeto_das_paradas(self):
        """
        Placeholder para gerar geometria do trajeto (será implementado com PostGIS)
        """
        # TODO: Implementar quando PostGIS estiver disponível
        return None
    
    def paradas_proximas_ao_trajeto(self, raio_metros=200):
        """
        Retorna paradas próximas às paradas desta linha
        """
        from paradas.models import Parada
        paradas_da_linha = [lp.parada for lp in self.get_paradas_ordenadas()]
        
        if not paradas_da_linha:
            return Parada.objects.none()
        
        # Busca paradas próximas a qualquer parada da linha
        proximas = set()
        for parada in paradas_da_linha:
            proximas.update(parada.paradas_proximas(raio_metros))
        
        return Parada.objects.filter(id__in=[p.id for p in proximas])


class LinhaParada(models.Model):
    """
    Modelo para relacionamento entre linhas e paradas com informações adicionais
    """
    
    linha = models.ForeignKey(
        Linha,
        on_delete=models.CASCADE,
        help_text="Linha de transporte"
    )
    parada = models.ForeignKey(
        'paradas.Parada',
        on_delete=models.CASCADE,
        help_text="Parada de ônibus"
    )
    ordem = models.PositiveIntegerField(
        help_text="Ordem da parada no trajeto da linha"
    )
    tempo_parada = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Tempo de parada em segundos"
    )
    distancia_origem = models.FloatField(
        null=True,
        blank=True,
        help_text="Distância da origem da linha em quilômetros"
    )
    observacoes = models.TextField(
        blank=True,
        help_text="Observações sobre esta parada na linha"
    )
    
    class Meta:
        verbose_name = "Linha-Parada"
        verbose_name_plural = "Linhas-Paradas"
        unique_together = [['linha', 'parada'], ['linha', 'ordem']]
        ordering = ['linha', 'ordem']
        indexes = [
            models.Index(fields=['linha', 'ordem']),
        ]
    
    def __str__(self):
        return f"{self.linha.codigo} - {self.parada.nome} (#{self.ordem})"

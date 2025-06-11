"""
Modelos para paradas de ônibus do BusFeed.
Gerencia informações sobre paradas, acessibilidade e facilidades.
"""
from django.db import models  # Usando models regular
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, GeoModel


class StopType(BaseModel):
    """
    Tipos de paradas de ônibus (terminal, parada simples, abrigo, etc.).
    """
    name = models.CharField(
        'Nome',
        max_length=50,
        unique=True,
        help_text='Nome do tipo de parada'
    )
    description = models.TextField(
        'Descrição',
        blank=True,
        help_text='Descrição detalhada do tipo de parada'
    )
    icon = models.CharField(
        'Ícone',
        max_length=50,
        blank=True,
        help_text='Nome do ícone para representar este tipo de parada'
    )
    color = models.CharField(
        'Cor',
        max_length=7,
        default='#007bff',
        help_text='Cor hexadecimal para representar este tipo de parada'
    )
    
    class Meta:
        verbose_name = 'Tipo de Parada'
        verbose_name_plural = 'Tipos de Paradas'
        ordering = ['name']
        
    def __str__(self):
        return self.name


class BusStop(BaseModel, GeoModel):
    """
    Modelo principal para paradas de ônibus.
    Contém informações completas sobre localização, acessibilidade e facilidades.
    """
    code = models.CharField(
        'Código',
        max_length=20,
        unique=True,
        help_text='Código oficial da parada (fornecido pelo DFTrans)'
    )
    name = models.CharField(
        'Nome',
        max_length=200,
        help_text='Nome oficial da parada'
    )
    nickname = models.CharField(
        'Apelido',
        max_length=200,
        blank=True,
        help_text='Nome popular ou apelido da parada'
    )
    stop_type = models.ForeignKey(
        StopType,
        on_delete=models.PROTECT,
        related_name='stops',
        verbose_name='Tipo de Parada'
    )
    
    # Informações de acessibilidade
    wheelchair_accessible = models.BooleanField(
        'Acessível para Cadeirantes',
        default=False,
        help_text='Indica se a parada é acessível para cadeirantes'
    )
    audio_announcements = models.BooleanField(
        'Anúncios Sonoros',
        default=False,
        help_text='Indica se a parada possui anúncios sonoros'
    )
    tactile_paving = models.BooleanField(
        'Piso Tátil',
        default=False,
        help_text='Indica se a parada possui piso tátil'
    )
    braille_info = models.BooleanField(
        'Informações em Braille',
        default=False,
        help_text='Indica se a parada possui informações em Braille'
    )
    
    # Facilidades disponíveis
    has_shelter = models.BooleanField(
        'Possui Abrigo',
        default=False,
        help_text='Indica se a parada possui abrigo/cobertura'
    )
    has_seating = models.BooleanField(
        'Possui Assentos',
        default=False,
        help_text='Indica se a parada possui bancos ou assentos'
    )
    has_lighting = models.BooleanField(
        'Possui Iluminação',
        default=False,
        help_text='Indica se a parada possui iluminação adequada'
    )
    has_security = models.BooleanField(
        'Possui Segurança',
        default=False,
        help_text='Indica se a parada possui câmeras ou segurança'
    )
    has_wifi = models.BooleanField(
        'Possui Wi-Fi',
        default=False,
        help_text='Indica se a parada oferece acesso Wi-Fi gratuito'
    )
    has_charging_station = models.BooleanField(
        'Possui Carregador',
        default=False,
        help_text='Indica se a parada possui estação de carregamento'
    )
    
    # Informações adicionais
    zone = models.CharField(
        'Zona',
        max_length=50,
        blank=True,
        help_text='Zona tarifária da parada (se aplicável)'
    )
    neighborhood = models.CharField(
        'Bairro',
        max_length=100,
        blank=True,
        help_text='Bairro onde a parada está localizada'
    )
    reference_point = models.CharField(
        'Ponto de Referência',
        max_length=200,
        blank=True,
        help_text='Ponto de referência próximo à parada'
    )
    
    # Horário de funcionamento
    operating_hours_start = models.TimeField(
        'Início Funcionamento',
        null=True,
        blank=True,
        help_text='Horário de início de funcionamento da parada'
    )
    operating_hours_end = models.TimeField(
        'Fim Funcionamento',
        null=True,
        blank=True,
        help_text='Horário de fim de funcionamento da parada'
    )
    
    # Metadados
    data_source = models.CharField(
        'Fonte dos Dados',
        max_length=100,
        default='DFTrans',
        help_text='Fonte original dos dados da parada'
    )
    last_verification = models.DateTimeField(
        'Última Verificação',
        null=True,
        blank=True,
        help_text='Data da última verificação dos dados da parada'
    )
    verified_by_users = models.PositiveIntegerField(
        'Verificado por Usuários',
        default=0,
        help_text='Número de usuários que verificaram/confirmaram os dados'
    )
    
    class Meta:
        verbose_name = 'Parada de Ônibus'
        verbose_name_plural = 'Paradas de Ônibus'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['neighborhood']),
            models.Index(fields=['zone']),
        ]
        
    def __str__(self):
        return f'{self.code} - {self.name}'
        
    def get_accessibility_score(self):
        """
        Calcula um score de acessibilidade baseado nas facilidades disponíveis.
        
        Returns:
            int: Score de 0 a 100 representando o nível de acessibilidade
        """
        accessibility_features = [
            self.wheelchair_accessible,
            self.audio_announcements,
            self.tactile_paving,
            self.braille_info,
        ]
        return int((sum(accessibility_features) / len(accessibility_features)) * 100)
        
    def get_comfort_score(self):
        """
        Calcula um score de conforto baseado nas facilidades disponíveis.
        
        Returns:
            int: Score de 0 a 100 representando o nível de conforto
        """
        comfort_features = [
            self.has_shelter,
            self.has_seating,
            self.has_lighting,
            self.has_security,
            self.has_wifi,
            self.has_charging_station,
        ]
        return int((sum(comfort_features) / len(comfort_features)) * 100)
        
    def is_operational(self):
        """
        Verifica se a parada está em funcionamento no horário atual.
        
        Returns:
            bool: True se a parada está operacional, False caso contrário
        """
        if not self.operating_hours_start or not self.operating_hours_end:
            return True  # Assume operacional se não há horários definidos
            
        from datetime import time
        from django.utils import timezone
        
        now = timezone.now().time()
        return self.operating_hours_start <= now <= self.operating_hours_end


class StopAmenity(BaseModel):
    """
    Facilidades adicionais disponíveis em paradas específicas.
    Permite flexibilidade para adicionar novas facilidades sem alterar o modelo principal.
    """
    name = models.CharField(
        'Nome',
        max_length=100,
        help_text='Nome da facilidade/comodidade'
    )
    description = models.TextField(
        'Descrição',
        blank=True,
        help_text='Descrição detalhada da facilidade'
    )
    icon = models.CharField(
        'Ícone',
        max_length=50,
        blank=True,
        help_text='Nome do ícone para representar esta facilidade'
    )
    category = models.CharField(
        'Categoria',
        max_length=50,
        choices=[
            ('accessibility', 'Acessibilidade'),
            ('comfort', 'Conforto'),
            ('safety', 'Segurança'),
            ('technology', 'Tecnologia'),
            ('commercial', 'Comercial'),
            ('other', 'Outros'),
        ],
        default='other',
        help_text='Categoria da facilidade'
    )
    
    class Meta:
        verbose_name = 'Facilidade da Parada'
        verbose_name_plural = 'Facilidades das Paradas'
        ordering = ['category', 'name']
        
    def __str__(self):
        return f'{self.name} ({self.get_category_display()})'


class StopAmenityMapping(BaseModel):
    """
    Mapeamento entre paradas e suas facilidades.
    Permite relação many-to-many com informações adicionais.
    """
    stop = models.ForeignKey(
        BusStop,
        on_delete=models.CASCADE,
        related_name='amenity_mappings',
        verbose_name='Parada'
    )
    amenity = models.ForeignKey(
        StopAmenity,
        on_delete=models.CASCADE,
        related_name='stop_mappings',
        verbose_name='Facilidade'
    )
    is_working = models.BooleanField(
        'Funcionando',
        default=True,
        help_text='Indica se a facilidade está funcionando no momento'
    )
    notes = models.TextField(
        'Observações',
        blank=True,
        help_text='Observações sobre o estado ou funcionamento da facilidade'
    )
    verified_date = models.DateTimeField(
        'Data de Verificação',
        null=True,
        blank=True,
        help_text='Data da última verificação do estado da facilidade'
    )
    
    class Meta:
        verbose_name = 'Facilidade da Parada'
        verbose_name_plural = 'Facilidades das Paradas'
        unique_together = ['stop', 'amenity']
        ordering = ['stop__name', 'amenity__name']
        
    def __str__(self):
        status = "✓" if self.is_working else "✗"
        return f'{self.stop.name} - {self.amenity.name} ({status})'

"""
Modelos para rotas de ônibus do BusFeed.
Gerencia informações sobre linhas, trajetos e horários.
"""
from django.db import models  # Usando models regular
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, GeoModel
from stops.models import BusStop


class TransportCompany(BaseModel):
    """
    Empresas de transporte público responsáveis pelas rotas.
    """
    name = models.CharField(
        'Nome',
        max_length=200,
        help_text='Nome da empresa de transporte'
    )
    short_name = models.CharField(
        'Nome Abreviado',
        max_length=50,
        blank=True,
        help_text='Nome abreviado da empresa'
    )
    cnpj = models.CharField(
        'CNPJ',
        max_length=18,
        unique=True,
        help_text='CNPJ da empresa'
    )
    phone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True,
        help_text='Telefone de contato da empresa'
    )
    email = models.EmailField(
        'Email',
        blank=True,
        help_text='Email de contato da empresa'
    )
    website = models.URLField(
        'Website',
        blank=True,
        help_text='Website oficial da empresa'
    )
    license_number = models.CharField(
        'Número da Licença',
        max_length=50,
        blank=True,
        help_text='Número da licença de operação'
    )
    
    class Meta:
        verbose_name = 'Empresa de Transporte'
        verbose_name_plural = 'Empresas de Transporte'
        ordering = ['name']
        
    def __str__(self):
        return self.short_name or self.name


class RouteType(BaseModel):
    """
    Tipos de rotas (convencional, BRT, expresso, etc.).
    """
    name = models.CharField(
        'Nome',
        max_length=50,
        unique=True,
        help_text='Nome do tipo de rota'
    )
    description = models.TextField(
        'Descrição',
        blank=True,
        help_text='Descrição detalhada do tipo de rota'
    )
    icon = models.CharField(
        'Ícone',
        max_length=50,
        blank=True,
        help_text='Nome do ícone para representar este tipo de rota'
    )
    color = models.CharField(
        'Cor',
        max_length=7,
        default='#007bff',
        help_text='Cor hexadecimal para representar este tipo de rota'
    )
    fare_multiplier = models.DecimalField(
        'Multiplicador de Tarifa',
        max_digits=4,
        decimal_places=2,
        default=1.0,
        help_text='Multiplicador aplicado à tarifa base'
    )
    
    class Meta:
        verbose_name = 'Tipo de Rota'
        verbose_name_plural = 'Tipos de Rotas'
        ordering = ['name']
        
    def __str__(self):
        return self.name


class BusRoute(BaseModel, GeoModel):
    """
    Modelo principal para rotas de ônibus.
    Representa uma linha completa com seus trajetos.
    """
    number = models.CharField(
        'Número',
        max_length=20,
        help_text='Número oficial da linha'
    )
    name = models.CharField(
        'Nome',
        max_length=200,
        help_text='Nome descritivo da linha'
    )
    short_name = models.CharField(
        'Nome Resumido',
        max_length=100,
        blank=True,
        help_text='Nome resumido da linha para exibição'
    )
    description = models.TextField(
        'Descrição',
        blank=True,
        help_text='Descrição detalhada da rota'
    )
    
    # Relações
    route_type = models.ForeignKey(
        RouteType,
        on_delete=models.PROTECT,
        related_name='routes',
        verbose_name='Tipo de Rota'
    )
    transport_company = models.ForeignKey(
        TransportCompany,
        on_delete=models.PROTECT,
        related_name='routes',
        verbose_name='Empresa de Transporte'
    )
    
    # Trajeto
    origin_terminal = models.CharField(
        'Terminal de Origem',
        max_length=200,
        help_text='Terminal ou ponto de partida'
    )
    destination_terminal = models.CharField(
        'Terminal de Destino',
        max_length=200,
        help_text='Terminal ou ponto final'
    )
    path = models.TextField(
        'Trajeto',
        blank=True,
        help_text='Descrição textual do trajeto da rota'
    )
    
    # Informações operacionais
    is_circular = models.BooleanField(
        'Rota Circular',
        default=False,
        help_text='Indica se a rota é circular (sem volta)'
    )
    is_bidirectional = models.BooleanField(
        'Bidirecional',
        default=True,
        help_text='Indica se a rota opera nos dois sentidos'
    )
    operates_weekdays = models.BooleanField(
        'Opera Dias Úteis',
        default=True,
        help_text='Indica se opera em dias úteis'
    )
    operates_saturdays = models.BooleanField(
        'Opera Sábados',
        default=True,
        help_text='Indica se opera aos sábados'
    )
    operates_sundays = models.BooleanField(
        'Opera Domingos',
        default=False,
        help_text='Indica se opera aos domingos e feriados'
    )
    
    # Horários
    first_departure = models.TimeField(
        'Primeira Partida',
        null=True,
        blank=True,
        help_text='Horário da primeira partida'
    )
    last_departure = models.TimeField(
        'Última Partida',
        null=True,
        blank=True,
        help_text='Horário da última partida'
    )
    average_frequency = models.PositiveIntegerField(
        'Frequência Média (min)',
        null=True,
        blank=True,
        help_text='Frequência média entre partidas em minutos'
    )
    estimated_duration = models.PositiveIntegerField(
        'Duração Estimada (min)',
        null=True,
        blank=True,
        help_text='Duração estimada do trajeto completo em minutos'
    )
    
    # Tarifação
    base_fare = models.DecimalField(
        'Tarifa Base',
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Tarifa base da rota'
    )
    accepts_integration = models.BooleanField(
        'Aceita Integração',
        default=True,
        help_text='Indica se aceita integração tarifária'
    )
    
    # Acessibilidade
    wheelchair_accessible = models.BooleanField(
        'Acessível para Cadeirantes',
        default=False,
        help_text='Indica se a frota é acessível para cadeirantes'
    )
    audio_announcements = models.BooleanField(
        'Anúncios Sonoros',
        default=False,
        help_text='Indica se possui anúncios sonoros'
    )
    
    # Metadados
    data_source = models.CharField(
        'Fonte dos Dados',
        max_length=100,
        default='DFTrans',
        help_text='Fonte original dos dados da rota'
    )
    last_update = models.DateTimeField(
        'Última Atualização',
        null=True,
        blank=True,
        help_text='Data da última atualização dos dados'
    )
    
    class Meta:
        verbose_name = 'Rota de Ônibus'
        verbose_name_plural = 'Rotas de Ônibus'
        ordering = ['number', 'name']
        unique_together = ['number', 'transport_company']
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['operates_weekdays', 'operates_saturdays', 'operates_sundays']),
        ]
        
    def __str__(self):
        return f'{self.number} - {self.name}'
        
    def get_full_name(self):
        """Retorna o nome completo da rota."""
        return f'{self.number} - {self.origin_terminal} ↔ {self.destination_terminal}'
        
    def is_operational_today(self):
        """
        Verifica se a rota está operacional hoje.
        
        Returns:
            bool: True se a rota opera hoje
        """
        from datetime import datetime
        
        today = datetime.now().weekday()  # 0=segunda, 6=domingo
        
        if today < 5:  # Segunda a sexta
            return self.operates_weekdays
        elif today == 5:  # Sábado
            return self.operates_saturdays
        else:  # Domingo
            return self.operates_sundays
            
    def get_current_fare(self):
        """
        Calcula a tarifa atual considerando o multiplicador do tipo de rota.
        
        Returns:
            Decimal: Tarifa atual da rota
        """
        if self.base_fare:
            return self.base_fare * self.route_type.fare_multiplier
        return None


class RouteStop(BaseModel):
    """
    Relação entre rotas e paradas com informações específicas.
    Define a sequência de paradas em cada rota.
    """
    route = models.ForeignKey(
        BusRoute,
        on_delete=models.CASCADE,
        related_name='route_stops',
        verbose_name='Rota'
    )
    stop = models.ForeignKey(
        BusStop,
        on_delete=models.CASCADE,
        related_name='route_stops',
        verbose_name='Parada'
    )
    direction = models.CharField(
        'Direção',
        max_length=20,
        choices=[
            ('ida', 'Ida'),
            ('volta', 'Volta'),
            ('circular', 'Circular'),
        ],
        help_text='Direção do trajeto (ida, volta ou circular)'
    )
    sequence = models.PositiveIntegerField(
        'Sequência',
        help_text='Ordem da parada na rota'
    )
    distance_from_origin = models.FloatField(
        'Distância da Origem (km)',
        null=True,
        blank=True,
        help_text='Distância em quilômetros desde a origem'
    )
    estimated_time_from_origin = models.PositiveIntegerField(
        'Tempo Estimado da Origem (min)',
        null=True,
        blank=True,
        help_text='Tempo estimado em minutos desde a origem'
    )
    is_timing_point = models.BooleanField(
        'Ponto de Controle',
        default=False,
        help_text='Indica se é um ponto de controle de horário'
    )
    
    class Meta:
        verbose_name = 'Parada da Rota'
        verbose_name_plural = 'Paradas das Rotas'
        unique_together = ['route', 'stop', 'direction', 'sequence']
        ordering = ['route', 'direction', 'sequence']
        indexes = [
            models.Index(fields=['route', 'direction', 'sequence']),
        ]
        
    def __str__(self):
        return f'{self.route.number} - {self.stop.name} ({self.direction})'


class Vehicle(BaseModel):
    """
    Modelo para veículos da frota.
    """
    fleet_number = models.CharField(
        'Número da Frota',
        max_length=20,
        unique=True,
        help_text='Número identificador do veículo na frota'
    )
    license_plate = models.CharField(
        'Placa',
        max_length=8,
        unique=True,
        help_text='Placa do veículo'
    )
    model = models.CharField(
        'Modelo',
        max_length=100,
        help_text='Modelo do veículo'
    )
    manufacturer = models.CharField(
        'Fabricante',
        max_length=100,
        help_text='Fabricante do veículo'
    )
    year = models.PositiveIntegerField(
        'Ano',
        help_text='Ano de fabricação'
    )
    capacity = models.PositiveIntegerField(
        'Capacidade',
        help_text='Capacidade total de passageiros'
    )
    fuel_type = models.CharField(
        'Tipo de Combustível',
        max_length=20,
        choices=[
            ('diesel', 'Diesel'),
            ('gasoline', 'Gasolina'),
            ('ethanol', 'Etanol'),
            ('electric', 'Elétrico'),
            ('hybrid', 'Híbrido'),
            ('cng', 'GNV'),
        ],
        default='diesel',
        help_text='Tipo de combustível utilizado'
    )
    
    # Acessibilidade
    wheelchair_accessible = models.BooleanField(
        'Acessível para Cadeirantes',
        default=False,
        help_text='Indica se o veículo é acessível para cadeirantes'
    )
    low_floor = models.BooleanField(
        'Piso Baixo',
        default=False,
        help_text='Indica se o veículo possui piso baixo'
    )
    audio_system = models.BooleanField(
        'Sistema de Áudio',
        default=False,
        help_text='Indica se possui sistema de anúncios sonoros'
    )
    air_conditioning = models.BooleanField(
        'Ar Condicionado',
        default=False,
        help_text='Indica se possui ar condicionado'
    )
    
    # Empresa
    transport_company = models.ForeignKey(
        TransportCompany,
        on_delete=models.PROTECT,
        related_name='vehicles',
        verbose_name='Empresa de Transporte'
    )
    
    # Status operacional
    is_operational = models.BooleanField(
        'Operacional',
        default=True,
        help_text='Indica se o veículo está em operação'
    )
    last_maintenance = models.DateField(
        'Última Manutenção',
        null=True,
        blank=True,
        help_text='Data da última manutenção'
    )
    
    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['fleet_number']
        indexes = [
            models.Index(fields=['transport_company', 'is_operational']),
        ]
        
    def __str__(self):
        return f'{self.fleet_number} - {self.license_plate}'
        
    def get_age(self):
        """Calcula a idade do veículo em anos."""
        from datetime import datetime
        current_year = datetime.now().year
        return current_year - self.year


class VehicleLocation(BaseModel, GeoModel):
    """
    Localização em tempo real dos veículos.
    Usado para tracking GPS e informações em tempo real.
    """
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name='Veículo'
    )
    route = models.ForeignKey(
        BusRoute,
        on_delete=models.CASCADE,
        related_name='vehicle_locations',
        verbose_name='Rota',
        null=True,
        blank=True
    )
    speed = models.FloatField(
        'Velocidade (km/h)',
        null=True,
        blank=True,
        help_text='Velocidade atual em km/h'
    )
    heading = models.FloatField(
        'Direção (graus)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text='Direção em graus (0-360)'
    )
    passenger_count = models.PositiveIntegerField(
        'Contagem de Passageiros',
        null=True,
        blank=True,
        help_text='Número atual de passageiros no veículo'
    )
    
    class Meta:
        verbose_name = 'Localização do Veículo'
        verbose_name_plural = 'Localizações dos Veículos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vehicle', '-created_at']),
            models.Index(fields=['route', '-created_at']),
        ]
        
    def __str__(self):
        return f'{self.vehicle.fleet_number} - {self.created_at}'

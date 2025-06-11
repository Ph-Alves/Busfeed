from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, time, timedelta


class Schedule(models.Model):
    """
    Modelo para horários de rotas de ônibus.
    """
    WEEKDAY = 'weekday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'
    HOLIDAY = 'holiday'
    
    DAY_TYPE_CHOICES = [
        (WEEKDAY, 'Dias úteis'),
        (SATURDAY, 'Sábado'),
        (SUNDAY, 'Domingo'),
        (HOLIDAY, 'Feriado'),
    ]
    
    IDA = 'ida'
    VOLTA = 'volta'
    CIRCULAR = 'circular'
    
    DIRECTION_CHOICES = [
        (IDA, 'Ida'),
        (VOLTA, 'Volta'),
        (CIRCULAR, 'Circular'),
    ]
    
    route = models.ForeignKey(
        'routes.BusRoute',
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Rota'
    )
    
    day_type = models.CharField(
        max_length=10,
        choices=DAY_TYPE_CHOICES,
        verbose_name='Tipo de dia'
    )
    
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        default=IDA,
        verbose_name='Direção'
    )
    
    start_time = models.TimeField(
        verbose_name='Horário inicial'
    )
    
    end_time = models.TimeField(
        verbose_name='Horário final'
    )
    
    frequency_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(180)],
        verbose_name='Frequência (minutos)',
        help_text='Intervalo entre partidas em minutos'
    )
    
    peak_frequency_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(180)],
        null=True,
        blank=True,
        verbose_name='Frequência no pico (minutos)',
        help_text='Frequência reduzida nos horários de pico'
    )
    
    peak_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Início do horário de pico'
    )
    
    peak_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Fim do horário de pico'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Observações especiais sobre este horário'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Horário'
        verbose_name_plural = 'Horários'
        unique_together = [['route', 'day_type', 'direction', 'start_time', 'end_time']]
        ordering = ['route__number', 'day_type', 'direction', 'start_time']
        
    def __str__(self):
        return f'{self.route.number} - {self.get_day_type_display()} ({self.get_direction_display()}): {self.start_time}-{self.end_time}'
    
    def get_current_frequency(self):
        """
        Retorna a frequência atual baseada no horário.
        """
        now = timezone.now().time()
        
        # Se tem horário de pico definido e estamos no pico
        if (self.peak_frequency_minutes and self.peak_start_time and self.peak_end_time):
            if self.peak_start_time <= now <= self.peak_end_time:
                return self.peak_frequency_minutes
        
        return self.frequency_minutes
    
    def get_next_departures(self, count=5):
        """
        Retorna os próximos horários de partida.
        """
        now = timezone.now()
        current_time = now.time()
        departures = []
        
        # Se ainda não passou do horário de funcionamento hoje
        if current_time < self.end_time:
            frequency = self.get_current_frequency()
            
            # Encontrar próxima partida
            if current_time < self.start_time:
                next_departure = datetime.combine(now.date(), self.start_time)
            else:
                # Calcular próxima partida baseada na frequência
                minutes_since_start = (
                    datetime.combine(now.date(), current_time) - 
                    datetime.combine(now.date(), self.start_time)
                ).total_seconds() / 60
                
                next_interval = int(minutes_since_start // frequency + 1)
                next_departure = datetime.combine(now.date(), self.start_time) + timedelta(minutes=next_interval * frequency)
            
            # Gerar lista de próximas partidas
            departure = next_departure
            for _ in range(count):
                if departure.time() <= self.end_time:
                    departures.append(departure.time())
                    departure += timedelta(minutes=frequency)
                else:
                    break
        
        return departures
    
    def is_operational_now(self):
        """
        Verifica se o horário está operacional no momento atual.
        """
        if not self.is_active:
            return False
            
        now = timezone.now()
        current_time = now.time()
        current_weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Verificar tipo de dia
        if current_weekday < 5:  # Segunda a sexta
            day_type = self.WEEKDAY
        elif current_weekday == 5:  # Sábado
            day_type = self.SATURDAY
        else:  # Domingo
            day_type = self.SUNDAY
        
        if self.day_type != day_type:
            return False
        
        # Verificar horário
        return self.start_time <= current_time <= self.end_time


class SpecialSchedule(models.Model):
    """
    Horários especiais para datas específicas (feriados, eventos, etc.).
    """
    route = models.ForeignKey(
        'routes.BusRoute',
        on_delete=models.CASCADE,
        related_name='special_schedules',
        verbose_name='Rota'
    )
    
    date = models.DateField(
        verbose_name='Data'
    )
    
    direction = models.CharField(
        max_length=10,
        choices=Schedule.DIRECTION_CHOICES,
        default=Schedule.IDA,
        verbose_name='Direção'
    )
    
    description = models.CharField(
        max_length=200,
        verbose_name='Descrição',
        help_text='Ex: Natal, Ano Novo, etc.'
    )
    
    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Horário inicial'
    )
    
    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Horário final'
    )
    
    frequency_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(180)],
        null=True,
        blank=True,
        verbose_name='Frequência (minutos)'
    )
    
    is_suspended = models.BooleanField(
        default=False,
        verbose_name='Suspenso',
        help_text='Marca se o serviço está suspenso nesta data'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Horário Especial'
        verbose_name_plural = 'Horários Especiais'
        unique_together = [['route', 'date', 'direction']]
        ordering = ['date', 'route__number']
        
    def __str__(self):
        return f'{self.route.number} - {self.date} ({self.description})'

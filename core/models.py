"""
Modelos base para o BusFeed.
Contém classes abstratas e utilitárias.
"""
from django.db import models  # Usando models regular ao invés do GIS
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class TimestampedModel(models.Model):
    """
    Modelo abstrato que adiciona campos de timestamp.
    Usado como base para outros modelos que precisam rastrear quando foram criados/atualizados.
    """
    created_at = models.DateTimeField(
        'Criado em',
        auto_now_add=True,
        help_text='Data e hora de criação do registro'
    )
    updated_at = models.DateTimeField(
        'Atualizado em', 
        auto_now=True,
        help_text='Data e hora da última atualização'
    )
    
    class Meta:
        abstract = True


class GeoModel(models.Model):
    """
    Modelo abstrato para funcionalidades de localização.
    Versão simplificada sem PostGIS.
    """
    latitude = models.FloatField(
        'Latitude',
        null=True,
        blank=True,
        help_text='Latitude da localização'
    )
    longitude = models.FloatField(
        'Longitude',
        null=True,
        blank=True,
        help_text='Longitude da localização'
    )
    address = models.TextField(
        'Endereço',
        blank=True,
        help_text='Endereço textual da localização'
    )
    
    class Meta:
        abstract = True
        
    def get_latitude(self):
        """Retorna a latitude da localização."""
        return self.latitude
        
    def get_longitude(self):
        """Retorna a longitude da localização.""" 
        return self.longitude


class ActiveManager(models.Manager):
    """
    Manager customizado que filtra apenas registros ativos.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeleteModel(models.Model):
    """
    Modelo abstrato que implementa soft delete.
    Registros não são realmente deletados, apenas marcados como inativos.
    """
    is_active = models.BooleanField(
        'Ativo',
        default=True,
        help_text='Indica se o registro está ativo no sistema'
    )
    deleted_at = models.DateTimeField(
        'Deletado em',
        null=True,
        blank=True,
        help_text='Data e hora em que o registro foi marcado como deletado'
    )
    
    objects = models.Manager()  # Manager padrão
    active_objects = ActiveManager()  # Manager apenas para registros ativos
    
    class Meta:
        abstract = True
        
    def soft_delete(self):
        """Marca o registro como deletado sem removê-lo do banco."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
        
    def restore(self):
        """Restaura um registro marcado como deletado."""
        self.is_active = True
        self.deleted_at = None
        self.save()


class BaseModel(TimestampedModel, SoftDeleteModel):
    """
    Modelo base que combina timestamp e soft delete.
    Use como base para a maioria dos modelos do BusFeed.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Identificador único universal'
    )
    
    class Meta:
        abstract = True


class SystemSettings(BaseModel):
    """
    Modelo para configurações dinâmicas do sistema.
    Permite ajustar parâmetros sem necessidade de deployment.
    """
    key = models.CharField(
        'Chave',
        max_length=100,
        unique=True,
        help_text='Nome único da configuração'
    )
    value = models.TextField(
        'Valor',
        help_text='Valor da configuração (pode ser JSON para estruturas complexas)'
    )
    description = models.TextField(
        'Descrição',
        help_text='Descrição do que essa configuração controla'
    )
    data_type = models.CharField(
        'Tipo de Dados',
        max_length=20,
        choices=[
            ('string', 'Texto'),
            ('integer', 'Número Inteiro'),
            ('float', 'Número Decimal'),
            ('boolean', 'Verdadeiro/Falso'),
            ('json', 'JSON'),
        ],
        default='string',
        help_text='Tipo de dados da configuração'
    )
    
    class Meta:
        verbose_name = 'Configuração do Sistema'
        verbose_name_plural = 'Configurações do Sistema'
        ordering = ['key']
        
    def __str__(self):
        return f'{self.key}: {self.value[:50]}'
        
    def get_value(self):
        """
        Retorna o valor da configuração convertido para o tipo correto.
        """
        import json
        
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'float':
            return float(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes', 'on']
        elif self.data_type == 'json':
            return json.loads(self.value)
        else:
            return self.value

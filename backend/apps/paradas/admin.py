from django.contrib import admin
from .models import Parada


@admin.register(Parada)
class ParadaAdmin(admin.ModelAdmin):
    """Administração de paradas de ônibus"""
    
    list_display = [
        'codigo_dftrans', 'nome', 'tipo', 'latitude', 'longitude',
        'tem_acessibilidade', 'tem_cobertura', 'movimento_estimado'
    ]
    list_filter = ['tipo', 'tem_acessibilidade', 'tem_cobertura', 'tem_banco']
    search_fields = ['codigo_dftrans', 'nome', 'endereco', 'pontos_referencia']
    ordering = ['nome']
    
    fieldsets = [
        ('Identificação', {
            'fields': ['codigo_dftrans', 'nome', 'descricao', 'tipo']
        }),
        ('Localização', {
            'fields': ['latitude', 'longitude', 'endereco', 'pontos_referencia']
        }),
        ('Infraestrutura', {
            'fields': [
                'tem_acessibilidade', 'tem_cobertura', 'tem_banco',
                'movimento_estimado'
            ]
        }),
    ]

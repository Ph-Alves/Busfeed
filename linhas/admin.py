from django.contrib import admin
from .models import Linha, LinhaParada


class LinhaParadaInline(admin.TabularInline):
    """Inline para editar paradas de uma linha"""
    model = LinhaParada
    extra = 0
    fields = ['parada', 'ordem', 'tempo_parada', 'distancia_origem', 'observacoes']
    ordering = ['ordem']


@admin.register(Linha)
class LinhaAdmin(admin.ModelAdmin):
    """Administração de linhas de transporte"""
    
    list_display = [
        'codigo', 'nome', 'tipo', 'origem', 'destino', 
        'tarifa', 'status', 'tem_acessibilidade'
    ]
    list_filter = ['tipo', 'status', 'tem_acessibilidade']
    search_fields = ['codigo', 'nome', 'origem', 'destino']
    ordering = ['codigo']
    
    fieldsets = [
        ('Identificação', {
            'fields': ['codigo', 'nome', 'nome_curto', 'tipo', 'status']
        }),
        ('Trajeto', {
            'fields': ['origem', 'destino', 'trajeto_descricao']
        }),
        ('Operação', {
            'fields': [
                'tarifa', 'primeiro_horario', 'ultimo_horario',
                'intervalo_pico', 'intervalo_normal', 'tempo_viagem_estimado'
            ]
        }),
        ('Características', {
            'fields': ['tem_acessibilidade', 'cor_linha', 'observacoes']
        }),
    ]
    
    inlines = [LinhaParadaInline]


@admin.register(LinhaParada)
class LinhaParadaAdmin(admin.ModelAdmin):
    """Administração de relacionamentos linha-parada"""
    
    list_display = ['linha', 'parada', 'ordem', 'tempo_parada', 'distancia_origem']
    list_filter = ['linha__tipo', 'linha__status']
    search_fields = ['linha__codigo', 'linha__nome', 'parada__nome']
    ordering = ['linha', 'ordem']

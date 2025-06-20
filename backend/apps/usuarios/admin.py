"""
BusFeed - Admin para Usuários

Este módulo define as interfaces administrativas para o sistema de usuários.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Usuario, LocalFavorito, HistoricoBusca, AvaliacaoRota


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Interface administrativa para usuários do BusFeed
    """
    
    # Campos exibidos na lista
    list_display = [
        'username', 'email', 'get_full_name_display', 'is_active',
        'tem_necessidades_especiais', 'total_favoritos', 'total_buscas',
        'date_joined', 'last_login'
    ]
    
    # Filtros laterais
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'tem_necessidades_especiais',
        'prefere_acessibilidade', 'date_joined', 'last_login'
    ]
    
    # Campos de busca
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telefone']
    
    # Ordenação padrão
    ordering = ['-date_joined']
    
    # Configuração dos fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais BusFeed', {
            'fields': (
                'telefone', 'data_nascimento', 'endereco_principal'
            )
        }),
        ('Preferências de Transporte', {
            'fields': (
                'tem_necessidades_especiais', 'prefere_acessibilidade'
            )
        }),
        ('Configurações de Notificação', {
            'fields': (
                'receber_notificacoes_email', 'receber_notificacoes_push'
            )
        }),
        ('Controle de Dados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos readonly
    readonly_fields = ['criado_em', 'atualizado_em', 'date_joined', 'last_login']
    
    # Ações customizadas
    actions = ['ativar_usuarios', 'desativar_usuarios', 'resetar_preferencias']
    
    def get_full_name_display(self, obj):
        """Exibe nome completo ou email se não tiver nome"""
        full_name = obj.get_full_name()
        return full_name if full_name else obj.email
    get_full_name_display.short_description = 'Nome Completo'
    
    def total_favoritos(self, obj):
        """Exibe total de locais favoritos"""
        count = obj.locais_favoritos.count()
        if count > 0:
            url = reverse('admin:usuarios_localfavorito_changelist')
            return format_html(
                '<a href="{}?usuario={}">{}</a>',
                url, obj.id, count
            )
        return count
    total_favoritos.short_description = 'Favoritos'
    
    def total_buscas(self, obj):
        """Exibe total de buscas realizadas"""
        count = obj.historico_buscas.count()
        if count > 0:
            url = reverse('admin:usuarios_historicobusca_changelist')
            return format_html(
                '<a href="{}?usuario={}">{}</a>',
                url, obj.id, count
            )
        return count
    total_buscas.short_description = 'Buscas'
    
    def ativar_usuarios(self, request, queryset):
        """Ativa usuários selecionados"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} usuários ativados com sucesso.')
    ativar_usuarios.short_description = 'Ativar usuários selecionados'
    
    def desativar_usuarios(self, request, queryset):
        """Desativa usuários selecionados"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} usuários desativados com sucesso.')
    desativar_usuarios.short_description = 'Desativar usuários selecionados'
    
    def resetar_preferencias(self, request, queryset):
        """Reseta preferências dos usuários selecionados"""
        count = queryset.update(
            tem_necessidades_especiais=False,
            prefere_acessibilidade=False,
            receber_notificacoes_email=True,
            receber_notificacoes_push=True
        )
        self.message_user(request, f'Preferências resetadas para {count} usuários.')
    resetar_preferencias.short_description = 'Resetar preferências dos usuários'


@admin.register(LocalFavorito)
class LocalFavoritoAdmin(admin.ModelAdmin):
    """
    Interface administrativa para locais favoritos
    """
    
    list_display = [
        'nome', 'usuario', 'categoria', 'endereco_resumido',
        'vezes_usado', 'ultimo_uso', 'cor_preview', 'criado_em'
    ]
    
    list_filter = [
        'categoria', 'criado_em', 'ultimo_uso'
    ]
    
    search_fields = [
        'nome', 'endereco', 'usuario__username', 'usuario__email'
    ]
    
    readonly_fields = ['vezes_usado', 'ultimo_uso', 'criado_em', 'atualizado_em']
    
    ordering = ['-ultimo_uso', '-vezes_usado']
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': ('usuario', 'nome', 'endereco', 'categoria')
        }),
        ('Personalização', {
            'fields': ('descricao', 'cor_marcador')
        }),
        ('Estatísticas de Uso', {
            'fields': ('vezes_usado', 'ultimo_uso'),
            'classes': ('collapse',)
        }),
        ('Controle de Dados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    ]
    
    def endereco_resumido(self, obj):
        """Exibe endereço resumido"""
        if len(obj.endereco) > 50:
            return obj.endereco[:47] + '...'
        return obj.endereco
    endereco_resumido.short_description = 'Endereço'
    
    def cor_preview(self, obj):
        """Exibe preview da cor do marcador"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.cor_marcador
        )
    cor_preview.short_description = 'Cor'


@admin.register(HistoricoBusca)
class HistoricoBuscaAdmin(admin.ModelAdmin):
    """
    Interface administrativa para histórico de buscas
    """
    
    list_display = [
        'usuario', 'origem_destino', 'data_busca', 'numero_resultados',
        'tempo_resposta_formatado', 'dispositivo', 'rota_selecionada'
    ]
    
    list_filter = [
        'data_busca', 'dispositivo', 'numero_resultados'
    ]
    
    search_fields = [
        'origem_nome', 'destino_nome', 'usuario__username', 'usuario__email'
    ]
    
    readonly_fields = ['data_busca', 'user_agent']
    
    ordering = ['-data_busca']
    
    date_hierarchy = 'data_busca'
    
    fieldsets = [
        ('Informações da Busca', {
            'fields': ('usuario', 'origem_nome', 'destino_nome', 'rota_selecionada')
        }),
        ('Resultados', {
            'fields': ('numero_resultados', 'tempo_resposta')
        }),
        ('Contexto Técnico', {
            'fields': ('dispositivo', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Controle de Dados', {
            'fields': ('data_busca',),
            'classes': ('collapse',)
        }),
    ]
    
    def origem_destino(self, obj):
        """Exibe origem e destino formatados"""
        return f"{obj.origem_nome} → {obj.destino_nome}"
    origem_destino.short_description = 'Rota Buscada'
    
    def tempo_resposta_formatado(self, obj):
        """Exibe tempo de resposta formatado"""
        if obj.tempo_resposta:
            return f"{obj.tempo_resposta:.2f}s"
        return '-'
    tempo_resposta_formatado.short_description = 'Tempo'


@admin.register(AvaliacaoRota)
class AvaliacaoRotaAdmin(admin.ModelAdmin):
    """
    Interface administrativa para avaliações de rotas
    """
    
    list_display = [
        'usuario', 'rota', 'nota_display', 'data_avaliacao',
        'data_viagem', 'aprovada', 'denunciada'
    ]
    
    list_filter = [
        'nota', 'aprovada', 'denunciada', 'data_avaliacao', 'data_viagem'
    ]
    
    search_fields = [
        'usuario__username', 'usuario__email', 'comentario'
    ]
    
    readonly_fields = ['data_avaliacao']
    
    ordering = ['-data_avaliacao']
    
    date_hierarchy = 'data_avaliacao'
    
    actions = ['aprovar_avaliacoes', 'rejeitar_avaliacoes', 'marcar_como_denunciada']
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': ('usuario', 'rota', 'data_viagem')
        }),
        ('Avaliação', {
            'fields': ('nota', 'comentario')
        }),
        ('Aspectos Específicos', {
            'fields': ('pontualidade', 'conforto', 'seguranca'),
            'classes': ('collapse',)
        }),
        ('Moderação', {
            'fields': ('aprovada', 'denunciada')
        }),
        ('Controle de Dados', {
            'fields': ('data_avaliacao',),
            'classes': ('collapse',)
        }),
    ]
    
    def nota_display(self, obj):
        """Exibe nota com estrelas"""
        stars = '★' * obj.nota + '☆' * (5 - obj.nota)
        return format_html(
            '<span title="Nota: {}/5">{}</span>',
            obj.nota, stars
        )
    nota_display.short_description = 'Nota'
    
    def aprovar_avaliacoes(self, request, queryset):
        """Aprova avaliações selecionadas"""
        count = queryset.update(aprovada=True, denunciada=False)
        self.message_user(request, f'{count} avaliações aprovadas com sucesso.')
    aprovar_avaliacoes.short_description = 'Aprovar avaliações selecionadas'
    
    def rejeitar_avaliacoes(self, request, queryset):
        """Rejeita avaliações selecionadas"""
        count = queryset.update(aprovada=False)
        self.message_user(request, f'{count} avaliações rejeitadas com sucesso.')
    rejeitar_avaliacoes.short_description = 'Rejeitar avaliações selecionadas'
    
    def marcar_como_denunciada(self, request, queryset):
        """Marca avaliações como denunciadas"""
        count = queryset.update(denunciada=True, aprovada=False)
        self.message_user(request, f'{count} avaliações marcadas como denunciadas.')
    marcar_como_denunciada.short_description = 'Marcar como denunciadas'


# Configuração do site admin
admin.site.site_header = "BusFeed - Administração"
admin.site.site_title = "BusFeed Admin"
admin.site.index_title = "Bem-vindo ao Painel Administrativo do BusFeed"

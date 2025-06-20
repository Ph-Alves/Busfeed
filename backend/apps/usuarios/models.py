"""
BusFeed - Modelos para Usuários

Este módulo define os modelos de usuários e suas preferências
no sistema de transporte público.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado para o BusFeed
    
    Estende o modelo padrão do Django com informações específicas
    do sistema de transporte público.
    """
    
    # Informações pessoais adicionais
    telefone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Número de telefone do usuário"
    )
    data_nascimento = models.DateField(
        null=True,
        blank=True,
        help_text="Data de nascimento"
    )
    
    # Localização preferencial
    endereco_principal = models.CharField(
        max_length=500,
        blank=True,
        help_text="Endereço principal do usuário"
    )
    # localizacao_principal = models.PointField(  # Temporariamente desabilitado
    #     null=True,
    #     blank=True,
    #     help_text="Coordenadas da localização principal"
    # )
    
    # Preferências de transporte
    tem_necessidades_especiais = models.BooleanField(
        default=False,
        help_text="Indica se o usuário tem necessidades especiais de acessibilidade"
    )
    prefere_acessibilidade = models.BooleanField(
        default=False,
        help_text="Prefere rotas e veículos acessíveis"
    )
    
    # Configurações de notificação
    receber_notificacoes_email = models.BooleanField(
        default=True,
        help_text="Receber notificações por email"
    )
    receber_notificacoes_push = models.BooleanField(
        default=True,
        help_text="Receber notificações push"
    )
    
    # Controle de dados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        
    def __str__(self):
        return f"{self.username} ({self.get_full_name() or self.email})"
    
    @property
    def coordenadas_principais(self):
        """Retorna as coordenadas principais como lista [lat, lng]"""
        if self.localizacao_principal:
            return [self.localizacao_principal.y, self.localizacao_principal.x]
        return None


class LocalFavorito(models.Model):
    """
    Modelo para locais favoritos dos usuários
    
    Permite que usuários salvem locais frequentemente visitados
    para acesso rápido.
    """
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='locais_favoritos',
        help_text="Usuário dono do local favorito"
    )
    
    # Informações do local
    nome = models.CharField(
        max_length=255,
        help_text="Nome do local favorito"
    )
    endereco = models.CharField(
        max_length=500,
        help_text="Endereço do local"
    )
    # localizacao = models.PointField(  # Temporariamente desabilitado
    #     help_text="Coordenadas geográficas do local"
    # )
    
    # Categorização
    CATEGORIA_CHOICES = [
        ('casa', 'Casa'),
        ('trabalho', 'Trabalho'),
        ('estudo', 'Estudo'),
        ('familia', 'Família'),
        ('lazer', 'Lazer'),
        ('saude', 'Saúde'),
        ('compras', 'Compras'),
        ('outro', 'Outro'),
    ]
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='outro',
        help_text="Categoria do local"
    )
    
    # Metadados
    descricao = models.TextField(
        blank=True,
        help_text="Descrição adicional do local"
    )
    cor_marcador = models.CharField(
        max_length=7,
        default='#FF0000',
        help_text="Cor do marcador em hexadecimal"
    )
    
    # Estatísticas de uso
    vezes_usado = models.PositiveIntegerField(
        default=0,
        help_text="Número de vezes que foi usado em buscas"
    )
    ultimo_uso = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data do último uso"
    )
    
    # Controle de dados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Local Favorito"
        verbose_name_plural = "Locais Favoritos"
        unique_together = [['usuario', 'nome']]
        ordering = ['-ultimo_uso', '-vezes_usado', 'nome']
        indexes = [
            models.Index(fields=['usuario', 'categoria']),
            models.Index(fields=['ultimo_uso']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.nome}"
    
    @property
    def coordenadas(self):
        """Retorna as coordenadas como lista [lat, lng]"""
        if self.localizacao:
            return [self.localizacao.y, self.localizacao.x]
        return None
    
    def incrementar_uso(self):
        """Incrementa o contador de uso e atualiza a data"""
        from django.utils import timezone
        
        self.vezes_usado += 1
        self.ultimo_uso = timezone.now()
        self.save()


class HistoricoBusca(models.Model):
    """
    Modelo para histórico de buscas dos usuários
    
    Armazena o histórico de buscas para melhorar a experiência
    e fornecer sugestões personalizadas.
    """
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='historico_buscas',
        help_text="Usuário que realizou a busca"
    )
    
    # Dados da busca
    origem_nome = models.CharField(
        max_length=255,
        help_text="Nome do local de origem"
    )
    # origem_coordenadas = models.PointField(  # Temporariamente desabilitado
    #     help_text="Coordenadas da origem"
    # )
    
    destino_nome = models.CharField(
        max_length=255,
        help_text="Nome do local de destino"
    )
    # destino_coordenadas = models.PointField(  # Temporariamente desabilitado
    #     help_text="Coordenadas do destino"
    # )
    
    # Rota selecionada (se houver)
    rota_selecionada = models.ForeignKey(
        'rotas.Rota',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Rota que foi selecionada pelo usuário"
    )
    
    # Metadados da busca
    data_busca = models.DateTimeField(auto_now_add=True)
    tempo_resposta = models.FloatField(
        null=True,
        blank=True,
        help_text="Tempo de resposta da busca em segundos"
    )
    numero_resultados = models.PositiveIntegerField(
        default=0,
        help_text="Número de rotas encontradas"
    )
    
    # Dispositivo e contexto
    dispositivo = models.CharField(
        max_length=50,
        blank=True,
        help_text="Tipo de dispositivo usado"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent do navegador"
    )
    
    class Meta:
        verbose_name = "Histórico de Busca"
        verbose_name_plural = "Histórico de Buscas"
        ordering = ['-data_busca']
        indexes = [
            models.Index(fields=['usuario', '-data_busca']),
            models.Index(fields=['data_busca']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.origem_nome} → {self.destino_nome}"


class AvaliacaoRota(models.Model):
    """
    Modelo para avaliações de rotas pelos usuários
    
    Permite que usuários avaliem e comentem sobre rotas utilizadas.
    """
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='avaliacoes',
        help_text="Usuário que fez a avaliação"
    )
    rota = models.ForeignKey(
        'rotas.Rota',
        on_delete=models.CASCADE,
        related_name='avaliacoes',
        help_text="Rota avaliada"
    )
    
    # Avaliação
    nota = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Nota de 1 a 5"
    )
    comentario = models.TextField(
        blank=True,
        help_text="Comentário sobre a rota"
    )
    
    # Aspectos específicos da avaliação
    pontualidade = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Avaliação da pontualidade (1-5)"
    )
    conforto = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Avaliação do conforto (1-5)"
    )
    seguranca = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Avaliação da segurança (1-5)"
    )
    
    # Metadados
    data_avaliacao = models.DateTimeField(auto_now_add=True)
    data_viagem = models.DateField(
        null=True,
        blank=True,
        help_text="Data em que a viagem foi realizada"
    )
    
    # Controle de moderação
    aprovada = models.BooleanField(
        default=True,
        help_text="Indica se a avaliação foi aprovada"
    )
    denunciada = models.BooleanField(
        default=False,
        help_text="Indica se a avaliação foi denunciada"
    )
    
    class Meta:
        verbose_name = "Avaliação de Rota"
        verbose_name_plural = "Avaliações de Rotas"
        unique_together = [['usuario', 'rota']]
        ordering = ['-data_avaliacao']
        indexes = [
            models.Index(fields=['rota', '-data_avaliacao']),
            models.Index(fields=['aprovada']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.rota} ({self.nota}⭐)"
    
    def save(self, *args, **kwargs):
        """Override save para atualizar a avaliação média da rota"""
        super().save(*args, **kwargs)
        
        # Atualiza a avaliação média da rota
        if self.rota:
            self.rota.adicionar_avaliacao(self.nota)

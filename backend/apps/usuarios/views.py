"""
BusFeed - Views para Usuários

Este módulo implementa as views para autenticação e gerenciamento
de usuários no sistema.
"""

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Usuario, LocalFavorito, HistoricoBusca, AvaliacaoRota
from .serializers import (
    UsuarioRegistroSerializer, UsuarioLoginSerializer, UsuarioPerfilSerializer,
    LocalFavoritoSerializer, LocalFavoritoListSerializer, HistoricoBuscaSerializer,
    AvaliacaoRotaSerializer, UsuarioStatisticsSerializer, TokenSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def registro(request):
    """
    Registra um novo usuário no sistema
    
    Endpoint: POST /api/usuarios/registro/
    """
    serializer = UsuarioRegistroSerializer(data=request.data)
    
    if serializer.is_valid():
        usuario = serializer.save()
        
        # Cria token de autenticação
        token, created = Token.objects.get_or_create(user=usuario)
        
        # Retorna dados do usuário e token
        token_serializer = TokenSerializer(token)
        
        return Response({
            'message': 'Usuário registrado com sucesso',
            'usuario': UsuarioPerfilSerializer(usuario).data,
            'token': token_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario(request):
    """
    Realiza login do usuário
    
    Endpoint: POST /api/usuarios/login/
    """
    serializer = UsuarioLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        usuario = serializer.validated_data['usuario']
        
        # Atualiza último login
        usuario.last_login = timezone.now()
        usuario.save(update_fields=['last_login'])
        
        # Obtém ou cria token
        token, created = Token.objects.get_or_create(user=usuario)
        
        # Retorna dados do usuário e token
        token_serializer = TokenSerializer(token)
        
        return Response({
            'message': 'Login realizado com sucesso',
            'usuario': UsuarioPerfilSerializer(usuario).data,
            'token': token_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_usuario(request):
    """
    Realiza logout do usuário
    
    Endpoint: POST /api/usuarios/logout/
    """
    try:
        # Remove o token do usuário
        request.user.auth_token.delete()
        
        return Response({
            'message': 'Logout realizado com sucesso'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': 'Erro ao realizar logout'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil(request):
    """
    Retorna o perfil do usuário logado
    
    Endpoint: GET /api/usuarios/perfil/
    """
    serializer = UsuarioPerfilSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def atualizar_perfil(request):
    """
    Atualiza o perfil do usuário logado
    
    Endpoint: PUT/PATCH /api/usuarios/perfil/
    """
    serializer = UsuarioPerfilSerializer(
        request.user, 
        data=request.data, 
        partial=request.method == 'PATCH'
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Perfil atualizado com sucesso',
            'usuario': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estatisticas(request):
    """
    Retorna estatísticas do usuário
    
    Endpoint: GET /api/usuarios/estatisticas/
    """
    usuario = request.user
    
    # Calcula estatísticas
    total_buscas = usuario.historico_buscas.count()
    total_favoritos = usuario.locais_favoritos.count()
    total_avaliacoes = usuario.avaliacoes.count()
    
    # Última busca
    ultima_busca = usuario.historico_buscas.first()
    ultima_busca_data = ultima_busca.data_busca if ultima_busca else None
    
    # Categoria favorita
    categoria_favorita = usuario.locais_favoritos.values('categoria').annotate(
        total=Count('categoria')
    ).order_by('-total').first()
    categoria_favorita = categoria_favorita['categoria'] if categoria_favorita else 'Nenhuma'
    
    # Dispositivo mais usado
    dispositivo_mais_usado = usuario.historico_buscas.values('dispositivo').annotate(
        total=Count('dispositivo')
    ).order_by('-total').first()
    dispositivo_mais_usado = dispositivo_mais_usado['dispositivo'] if dispositivo_mais_usado else 'Desconhecido'
    
    data = {
        'total_buscas': total_buscas,
        'total_favoritos': total_favoritos,
        'total_avaliacoes': total_avaliacoes,
        'ultima_busca': ultima_busca_data,
        'categoria_favorita': categoria_favorita,
        'dispositivo_mais_usado': dispositivo_mais_usado
    }
    
    serializer = UsuarioStatisticsSerializer(data)
    return Response(serializer.data)


class LocalFavoritoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de locais favoritos
    """
    serializer_class = LocalFavoritoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas os favoritos do usuário logado"""
        return LocalFavorito.objects.filter(usuario=self.request.user)
    
    def get_serializer_class(self):
        """Retorna serializer apropriado para a ação"""
        if self.action == 'list':
            return LocalFavoritoListSerializer
        return LocalFavoritoSerializer
    
    @action(detail=True, methods=['post'])
    def usar(self, request, pk=None):
        """
        Incrementa o contador de uso de um favorito
        
        Endpoint: POST /api/usuarios/favoritos/{id}/usar/
        """
        favorito = self.get_object()
        favorito.incrementar_uso()
        
        return Response({
            'message': 'Uso registrado com sucesso',
            'vezes_usado': favorito.vezes_usado,
            'ultimo_uso': favorito.ultimo_uso
        })
    
    @action(detail=False, methods=['get'])
    def mais_usados(self, request):
        """
        Retorna os favoritos mais usados do usuário
        
        Endpoint: GET /api/usuarios/favoritos/mais-usados/
        """
        favoritos = self.get_queryset().filter(
            vezes_usado__gt=0
        ).order_by('-vezes_usado', '-ultimo_uso')[:10]
        
        serializer = LocalFavoritoListSerializer(favoritos, many=True)
        return Response(serializer.data)


class HistoricoBuscaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento do histórico de buscas
    """
    serializer_class = HistoricoBuscaSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']  # Não permite PUT/PATCH
    
    def get_queryset(self):
        """Retorna apenas o histórico do usuário logado"""
        return HistoricoBusca.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recentes(self, request):
        """
        Retorna as buscas mais recentes do usuário
        
        Endpoint: GET /api/usuarios/historico/recentes/
        """
        # Últimas 20 buscas
        historico = self.get_queryset()[:20]
        
        serializer = self.get_serializer(historico, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def frequentes(self, request):
        """
        Retorna as rotas mais buscadas pelo usuário
        
        Endpoint: GET /api/usuarios/historico/frequentes/
        """
        # Agrupa por origem-destino e conta frequência
        from django.db.models import Count
        
        frequentes = self.get_queryset().values(
            'origem_nome', 'destino_nome'
        ).annotate(
            total_buscas=Count('id')
        ).filter(
            total_buscas__gt=1
        ).order_by('-total_buscas')[:10]
        
        return Response(list(frequentes))
    
    @action(detail=False, methods=['delete'])
    def limpar(self, request):
        """
        Limpa o histórico de buscas do usuário
        
        Endpoint: DELETE /api/usuarios/historico/limpar/
        """
        dias = request.query_params.get('dias', None)
        
        queryset = self.get_queryset()
        
        if dias:
            try:
                dias = int(dias)
                data_limite = timezone.now() - timedelta(days=dias)
                queryset = queryset.filter(data_busca__lt=data_limite)
            except ValueError:
                return Response({
                    'error': 'Parâmetro "dias" deve ser um número inteiro'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        total_removido = queryset.count()
        queryset.delete()
        
        return Response({
            'message': f'{total_removido} registros removidos do histórico'
        })


class AvaliacaoRotaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de avaliações de rotas
    """
    serializer_class = AvaliacaoRotaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas as avaliações do usuário logado"""
        return AvaliacaoRota.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def minhas_avaliacoes(self, request):
        """
        Retorna todas as avaliações do usuário
        
        Endpoint: GET /api/usuarios/avaliacoes/minhas-avaliacoes/
        """
        avaliacoes = self.get_queryset().select_related('rota')
        serializer = self.get_serializer(avaliacoes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estatisticas_avaliacoes(self, request):
        """
        Retorna estatísticas das avaliações do usuário
        
        Endpoint: GET /api/usuarios/avaliacoes/estatisticas-avaliacoes/
        """
        from django.db.models import Avg
        
        avaliacoes = self.get_queryset()
        
        stats = avaliacoes.aggregate(
            total=Count('id'),
            nota_media=Avg('nota'),
            pontualidade_media=Avg('pontualidade'),
            conforto_medio=Avg('conforto'),
            seguranca_media=Avg('seguranca')
        )
        
        return Response(stats)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_busca(request):
    """
    Registra uma busca no histórico do usuário
    
    Endpoint: POST /api/usuarios/registrar-busca/
    """
    serializer = HistoricoBuscaSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        busca = serializer.save()
        return Response({
            'message': 'Busca registrada com sucesso',
            'id': busca.id
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def verificar_username(request):
    """
    Verifica se um username está disponível
    
    Endpoint: GET /api/usuarios/verificar-username/?username=exemplo
    """
    username = request.query_params.get('username')
    
    if not username:
        return Response({
            'error': 'Parâmetro username é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    disponivel = not Usuario.objects.filter(username=username).exists()
    
    return Response({
        'username': username,
        'disponivel': disponivel
    })

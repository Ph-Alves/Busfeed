"""
BusFeed - Serializers para Usuários

Este módulo implementa os serializers para os modelos de usuários,
histórico de buscas, locais favoritos e avaliações.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from .models import Usuario, LocalFavorito, HistoricoBusca, AvaliacaoRota


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuários"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'telefone', 'data_nascimento'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        usuario = Usuario.objects.create_user(password=password, **validated_data)
        return usuario


class UsuarioLoginSerializer(serializers.Serializer):
    """Serializer para login de usuários"""
    
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            usuario = authenticate(username=username, password=password)
            
            if not usuario:
                raise serializers.ValidationError('Credenciais inválidas.')
            
            if not usuario.is_active:
                raise serializers.ValidationError('Conta desativada.')
            
            attrs['usuario'] = usuario
            return attrs
        
        raise serializers.ValidationError('Username e senha são obrigatórios.')


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """Serializer para perfil do usuário"""
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'telefone', 'data_nascimento', 'endereco_principal',
            'tem_necessidades_especiais', 'prefere_acessibilidade',
            'receber_notificacoes_email', 'receber_notificacoes_push',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']


class TokenSerializer(serializers.ModelSerializer):
    """Serializer para tokens de autenticação"""
    
    class Meta:
        model = Token
        fields = ['key', 'created']


class LocalFavoritoSerializer(serializers.ModelSerializer):
    """Serializer para locais favoritos"""
    
    class Meta:
        model = LocalFavorito
        fields = [
            'id', 'nome', 'endereco', 'categoria', 'descricao',
            'cor_marcador', 'vezes_usado', 'ultimo_uso',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'vezes_usado', 'ultimo_uso', 'criado_em', 'atualizado_em']
    
    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class LocalFavoritoListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de locais favoritos"""
    
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = LocalFavorito
        fields = [
            'id', 'nome', 'endereco', 'categoria', 'categoria_display',
            'vezes_usado', 'ultimo_uso'
        ]


class HistoricoBuscaSerializer(serializers.ModelSerializer):
    """Serializer para histórico de buscas"""
    
    class Meta:
        model = HistoricoBusca
        fields = [
            'id', 'origem_nome', 'destino_nome', 'data_busca',
            'tempo_resposta', 'numero_resultados', 'dispositivo'
        ]
        read_only_fields = ['id', 'data_busca']
    
    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class AvaliacaoRotaSerializer(serializers.ModelSerializer):
    """Serializer para avaliações de rotas"""
    
    rota_info = serializers.SerializerMethodField()
    
    class Meta:
        model = AvaliacaoRota
        fields = [
            'id', 'rota', 'rota_info', 'nota', 'comentario',
            'pontualidade', 'conforto', 'seguranca',
            'data_avaliacao', 'data_viagem', 'aprovada'
        ]
        read_only_fields = ['id', 'data_avaliacao', 'aprovada', 'rota_info']
    
    def get_rota_info(self, obj):
        """Retorna informações básicas da rota avaliada"""
        return {
            'id': obj.rota.id,
            'nome': obj.rota.nome,
            'origem': obj.rota.origem_nome,
            'destino': obj.rota.destino_nome
        }
    
    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class UsuarioStatisticsSerializer(serializers.Serializer):
    """Serializer para estatísticas do usuário"""
    
    total_buscas = serializers.IntegerField()
    total_favoritos = serializers.IntegerField()
    total_avaliacoes = serializers.IntegerField()
    ultima_busca = serializers.DateTimeField(allow_null=True)
    categoria_favorita = serializers.CharField()
    dispositivo_mais_usado = serializers.CharField()


 
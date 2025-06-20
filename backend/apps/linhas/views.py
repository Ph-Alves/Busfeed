"""
BusFeed - Views para Linhas

Este módulo define as views da API REST para linhas de ônibus.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import math

from .models import Linha
from .serializers import (
    LinhaSerializer,
    LinhaResumoSerializer,
    # LinhaGeoJSONSerializer,  # Temporariamente desabilitado
    LinhaComParadasSerializer,
    BuscaLinhasSerializer
)


class LinhaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para linhas de ônibus
    
    Fornece endpoints para:
    - Listar todas as linhas
    - Buscar linha por ID
    - Buscar linhas por origem/destino
    - Buscar linhas que passam por uma parada
    """
    
    queryset = Linha.objects.filter(status='active').order_by('codigo')
    serializer_class = LinhaSerializer
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado baseado na action"""
        if self.action == 'list':
            return LinhaResumoSerializer
        elif self.action == 'com_paradas':
            return LinhaComParadasSerializer
        return LinhaSerializer
    
    def get_queryset(self):
        """
        Filtra o queryset baseado nos parâmetros da requisição
        """
        queryset = super().get_queryset()
        
        # Filtro por tipo
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtro por acessibilidade
        acessivel = self.request.query_params.get('acessivel')
        if acessivel and acessivel.lower() == 'true':
            queryset = queryset.filter(tem_acessibilidade=True)
        
        # Filtro por origem
        origem = self.request.query_params.get('origem')
        if origem:
            queryset = queryset.filter(origem__icontains=origem)
        
        # Filtro por destino
        destino = self.request.query_params.get('destino')
        if destino:
            queryset = queryset.filter(destino__icontains=destino)
        
        # Busca por texto
        busca = self.request.query_params.get('busca')
        if busca:
            queryset = queryset.filter(
                Q(codigo__icontains=busca) |
                Q(nome__icontains=busca) |
                Q(origem__icontains=busca) |
                Q(destino__icontains=busca)
            )
        
        return queryset
    
    @extend_schema(
        summary="Obter linha com paradas ordenadas",
        description="Retorna uma linha específica com todas suas paradas ordenadas por sequência",
        responses={200: LinhaComParadasSerializer}
    )
    @action(detail=True, methods=['get'])
    def com_paradas(self, request, pk=None):
        """
        Retorna uma linha com suas paradas ordenadas
        """
        linha = self.get_object()
        serializer = LinhaComParadasSerializer(linha)
        return Response(serializer.data)
    
    # Temporariamente desabilitado até PostGIS estar configurado
    # @extend_schema(
    #     summary="Obter trajetos em formato GeoJSON",
    #     description="Retorna trajetos das linhas em formato GeoJSON para exibição no mapa",
    #     responses={200: LinhaGeoJSONSerializer(many=True)}
    # )
    # @action(detail=False, methods=['get'])
    # def geojson(self, request):
    #     """
    #     Retorna trajetos das linhas em formato GeoJSON
    #     """
    #     queryset = self.get_queryset().exclude(trajeto_geometria__isnull=True)
    #     
    #     # Limita para evitar sobrecarga
    #     limite = min(int(request.query_params.get('limite', 50)), 200)
    #     linhas = queryset[:limite]
    #     
    #     serializer = LinhaGeoJSONSerializer(linhas, many=True)
    #     
    #     # Formata como FeatureCollection GeoJSON
    #     geojson_data = {
    #         "type": "FeatureCollection",
    #         "features": serializer.data
    #     }
    #     
    #     return Response(geojson_data)
    
    @extend_schema(
        summary="Buscar linhas que passam por uma parada",
        description="Busca todas as linhas que passam por uma parada específica",
        parameters=[
            OpenApiParameter(
                name='parada_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description='ID da parada'
            ),
        ],
        responses={200: LinhaResumoSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def por_parada(self, request):
        """
        Busca linhas que passam por uma parada específica
        """
        parada_id = request.query_params.get('parada_id')
        if not parada_id:
            return Response(
                {'error': 'Parâmetro "parada_id" é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            parada_id = int(parada_id)
        except ValueError:
            return Response(
                {'error': 'ID da parada deve ser um número inteiro'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Busca linhas que passam pela parada
        queryset = Linha.objects.filter(
            status='active',
            paradas__id=parada_id
        ).order_by('codigo')
        
        serializer = LinhaResumoSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Buscar linhas por texto",
        description="Busca linhas por código, nome, origem ou destino",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Texto de busca'
            ),
            OpenApiParameter(
                name='limite',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Número máximo de resultados (padrão: 20)'
            ),
        ],
        responses={200: LinhaResumoSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Busca linhas por texto com ranking inteligente
        """
        termo_busca = request.query_params.get('q', '').strip()
        if len(termo_busca) < 2:
            return Response(
                {'error': 'Termo de busca deve ter pelo menos 2 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        limite = min(int(request.query_params.get('limite', 20)), 100)
        
        # Busca com ranking: código exato > nome que inicia > origem/destino > nome que contém
        queryset = Linha.objects.filter(status='active')
        
        # 1. Prioridade: código exato
        codigo_exato = queryset.filter(codigo__iexact=termo_busca)
        
        # 2. Prioridade: nome que inicia com o termo
        nome_inicia = queryset.filter(nome__istartswith=termo_busca).exclude(
            id__in=codigo_exato.values_list('id', flat=True)
        )
        
        # 3. Prioridade: origem ou destino que contém o termo
        origem_destino = queryset.filter(
            Q(origem__icontains=termo_busca) | 
            Q(destino__icontains=termo_busca)
        ).exclude(
            id__in=codigo_exato.values_list('id', flat=True)
        ).exclude(
            id__in=nome_inicia.values_list('id', flat=True)
        )
        
        # 4. Prioridade: nome que contém o termo
        nome_contem = queryset.filter(nome__icontains=termo_busca).exclude(
            id__in=codigo_exato.values_list('id', flat=True)
        ).exclude(
            id__in=nome_inicia.values_list('id', flat=True)
        ).exclude(
            id__in=origem_destino.values_list('id', flat=True)
        )
        
        # Combina resultados priorizados
        resultados = []
        
        # Adiciona resultados respeitando o limite
        for queryset_prioritario in [codigo_exato, nome_inicia, origem_destino, nome_contem]:
            if len(resultados) >= limite:
                break
            
            restante = limite - len(resultados)
            resultados.extend(queryset_prioritario.order_by('codigo')[:restante])
        
        serializer = LinhaResumoSerializer(resultados, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Obter linhas para autocomplete",
        description="Endpoint otimizado para autocomplete em formulários de busca",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Texto de busca (mínimo 2 caracteres)'
            ),
        ],
        responses={200: LinhaResumoSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """
        Autocomplete otimizado para busca rápida de linhas
        """
        termo_busca = request.query_params.get('q', '').strip()
        if len(termo_busca) < 2:
            return Response([])
        
        # Busca otimizada priorizando código e nome
        queryset = Linha.objects.filter(
            status='active'
        ).filter(
            Q(codigo__istartswith=termo_busca) |
            Q(nome__istartswith=termo_busca) |
            Q(origem__icontains=termo_busca) |
            Q(destino__icontains=termo_busca)
        ).order_by('codigo')[:15]  # Limite reduzido para autocomplete
        
        # Retorna apenas dados essenciais para autocomplete
        resultados = []
        for linha in queryset:
            resultados.append({
                'id': linha.id,
                'codigo': linha.codigo,
                'nome': linha.nome,
                'origem': linha.origem,
                'destino': linha.destino,
                'tipo': linha.tipo,
                'tem_acessibilidade': linha.tem_acessibilidade
            })
        
        return Response(resultados)
    
    @extend_schema(
        summary="Buscar rotas entre duas paradas",
        description="Busca linhas que conectam duas paradas específicas",
        parameters=[
            OpenApiParameter(
                name='origem_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description='ID da parada de origem'
            ),
            OpenApiParameter(
                name='destino_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description='ID da parada de destino'
            ),
        ],
        responses={200: LinhaResumoSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def entre_paradas(self, request):
        """
        Busca linhas que conectam duas paradas
        """
        origem_id = request.query_params.get('origem_id')
        destino_id = request.query_params.get('destino_id')
        
        if not origem_id or not destino_id:
            return Response(
                {'error': 'Parâmetros "origem_id" e "destino_id" são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            origem_id = int(origem_id)
            destino_id = int(destino_id)
        except ValueError:
            return Response(
                {'error': 'IDs das paradas devem ser números inteiros'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Busca linhas que passam pelas duas paradas
        linhas_origem = set(Linha.objects.filter(
            status='active',
            paradas__id=origem_id
        ).values_list('id', flat=True))
        
        linhas_destino = set(Linha.objects.filter(
            status='active',
            paradas__id=destino_id
        ).values_list('id', flat=True))
        
        # Interseção - linhas que passam por ambas as paradas
        linhas_comuns = linhas_origem.intersection(linhas_destino)
        
        if not linhas_comuns:
            return Response([])
        
        # Busca as linhas completas
        queryset = Linha.objects.filter(
            id__in=linhas_comuns
        ).order_by('codigo')
        
        serializer = LinhaResumoSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Obter informações resumidas para o mapa",
        description="Retorna informações das linhas otimizadas para exibição no mapa",
        parameters=[
            OpenApiParameter(
                name='parada_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='ID da parada para filtrar linhas que passam por ela'
            ),
            OpenApiParameter(
                name='tipos',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Tipos de linha separados por vírgula (ex: urbano,metropolitano)'
            ),
        ],
        responses={200: LinhaResumoSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def mapa_info(self, request):
        """
        Retorna informações das linhas otimizadas para o mapa
        """
        queryset = self.get_queryset()
        
        # Filtra por parada se especificado
        parada_id = request.query_params.get('parada_id')
        if parada_id:
            try:
                parada_id = int(parada_id)
                queryset = queryset.filter(paradas__id=parada_id)
            except ValueError:
                return Response(
                    {'error': 'ID da parada deve ser um número inteiro'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Filtra por tipos se especificado
        tipos = request.query_params.get('tipos')
        if tipos:
            tipos_lista = [t.strip() for t in tipos.split(',')]
            queryset = queryset.filter(tipo__in=tipos_lista)
        
        # Limita para performance
        linhas = queryset[:50]
        
        # Prepara dados otimizados para o mapa
        dados_mapa = []
        for linha in linhas:
            dados_mapa.append({
                'id': linha.id,
                'codigo': linha.codigo,
                'nome': linha.nome,
                'tipo': linha.tipo,
                'origem': linha.origem,
                'destino': linha.destino,
                'cor': self._get_cor_linha(linha.tipo),
                'tem_acessibilidade': linha.tem_acessibilidade,
                'status': linha.status
            })
        
        return Response(dados_mapa)
    
    def _get_cor_linha(self, tipo_linha: str) -> str:
        """Retorna a cor da linha baseada no tipo"""
        cores = {
            'urbano': '#2196F3',      # Azul
            'metropolitano': '#4CAF50', # Verde
            'circular': '#FF9800',     # Laranja
            'semi_urbano': '#9C27B0',  # Roxo
            'rural': '#795548',        # Marrom
            'especial': '#F44336',     # Vermelho
        }
        return cores.get(tipo_linha, '#607D8B')  # Cinza padrão
    
    @extend_schema(
        summary="Obter trajeto de uma linha específica",
        description="Retorna as paradas de uma linha em ordem sequencial para exibição no mapa",
        responses={200: LinhaComParadasSerializer}
    )
    @action(detail=True, methods=['get'])
    def trajeto(self, request, pk=None):
        """
        Retorna o trajeto completo de uma linha com todas as paradas em ordem
        """
        linha = self.get_object()
        
        # Busca paradas da linha em ordem
        from .models import LinhaParada
        linhas_paradas = LinhaParada.objects.filter(
            linha=linha
        ).select_related('parada').order_by('ordem')
        
        # Prepara dados do trajeto
        paradas_trajeto = []
        coordenadas_trajeto = []
        
        for lp in linhas_paradas:
            parada = lp.parada
            parada_info = {
                'id': parada.id,
                'nome': parada.nome,
                'codigo': parada.codigo_dftrans,
                'coordenadas': [float(parada.latitude), float(parada.longitude)],
                'ordem': lp.ordem,
                'tipo': parada.tipo,
                'tem_acessibilidade': parada.tem_acessibilidade
            }
            paradas_trajeto.append(parada_info)
            coordenadas_trajeto.append([float(parada.longitude), float(parada.latitude)])
        
        # Dados completos do trajeto
        trajeto_data = {
            'linha': {
                'id': linha.id,
                'codigo': linha.codigo,
                'nome': linha.nome,
                'tipo': linha.tipo,
                'origem': linha.origem,
                'destino': linha.destino,
                'cor': self._get_cor_linha(linha.tipo),
                'tem_acessibilidade': linha.tem_acessibilidade
            },
            'paradas': paradas_trajeto,
            'coordenadas_trajeto': coordenadas_trajeto,
            'estatisticas': {
                'total_paradas': len(paradas_trajeto),
                'distancia_estimada': self._calcular_distancia_trajeto(coordenadas_trajeto),
                'tempo_estimado': self._calcular_tempo_trajeto(coordenadas_trajeto)
            }
        }
        
        return Response(trajeto_data)
    
    def _calcular_distancia_trajeto(self, coordenadas: list) -> float:
        """Calcula a distância total estimada do trajeto"""
        if len(coordenadas) < 2:
            return 0.0
        
        distancia_total = 0.0
        for i in range(len(coordenadas) - 1):
            lon1, lat1 = coordenadas[i]
            lon2, lat2 = coordenadas[i + 1]
            
            # Função simples de distância (haversine seria importada do services)
            from math import radians, sin, cos, sqrt, asin
            
            # Converte para radianos
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            
            # Fórmula de Haversine
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            distancia_total += 2 * asin(sqrt(a)) * 6371000  # Raio da Terra em metros
        
        return round(distancia_total / 1000, 2)  # Retorna em km
    
    def _calcular_tempo_trajeto(self, coordenadas: list) -> int:
        """Calcula o tempo estimado do trajeto em minutos"""
        distancia_km = self._calcular_distancia_trajeto(coordenadas)
        # Velocidade média estimada de 20 km/h no trânsito urbano
        tempo_minutos = (distancia_km / 20) * 60
        return round(tempo_minutos)

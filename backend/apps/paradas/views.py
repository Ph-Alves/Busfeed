"""
BusFeed - Views para Paradas

Este módulo define as views da API REST para paradas de ônibus.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
# from django.contrib.gis.geos import Point  # Temporariamente desabilitado
# from django.contrib.gis.measure import Distance  # Temporariamente desabilitado
# from django.contrib.gis.db.models.functions import Distance as DistanceFunction  # Temporariamente desabilitado
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import math

from .models import Parada
from .serializers import (
    ParadaSerializer,
    ParadaResumoSerializer,
    ParadaGeoJSONSerializer,
    BuscaParadasProximasSerializer,
    ParadaProximaSerializer
)


def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância entre dois pontos usando a fórmula de Haversine
    Retorna a distância em metros
    """
    # Converte graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Fórmula de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Raio da Terra em metros
    r = 6371000
    
    return c * r


class ParadaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para paradas de ônibus
    
    Fornece endpoints para:
    - Listar todas as paradas
    - Buscar parada por ID
    - Buscar paradas próximas a um ponto
    - Buscar paradas por nome/descrição
    - Obter dados em formato GeoJSON
    """
    
    queryset = Parada.objects.all().order_by('nome')
    serializer_class = ParadaSerializer
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado baseado na action"""
        if self.action == 'list':
            return ParadaResumoSerializer
        elif self.action == 'geojson':
            return ParadaGeoJSONSerializer
        elif self.action == 'proximas':
            return ParadaProximaSerializer
        return ParadaSerializer
    
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
        
        # Busca por texto
        busca = self.request.query_params.get('busca')
        if busca:
            queryset = queryset.filter(
                Q(nome__icontains=busca) |
                Q(descricao__icontains=busca) |
                Q(endereco__icontains=busca) |
                Q(codigo_dftrans__icontains=busca)
            )
        
        return queryset
    
    @extend_schema(
        summary="Buscar paradas próximas",
        description="Busca paradas de ônibus próximas a um ponto geográfico",
        parameters=[
            OpenApiParameter(
                name='latitude',
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Latitude do ponto de referência'
            ),
            OpenApiParameter(
                name='longitude',
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Longitude do ponto de referência'
            ),
            OpenApiParameter(
                name='raio',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Raio de busca em metros (padrão: 500)'
            ),
            OpenApiParameter(
                name='limite',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Número máximo de resultados (padrão: 10)'
            ),
        ],
        responses={200: ParadaProximaSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def proximas(self, request):
        """
        Busca paradas próximas a um ponto geográfico
        """
        # Valida os parâmetros
        serializer = BuscaParadasProximasSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        lat_ref = data['latitude']
        lon_ref = data['longitude']
        raio_metros = data.get('raio', 500)
        limite = data.get('limite', 10)
        tipos = data.get('tipos', [])
        apenas_acessiveis = data.get('apenas_acessiveis', False)
        
        # Busca todas as paradas
        queryset = Parada.objects.all()
        
        # Aplica filtros adicionais
        if tipos:
            queryset = queryset.filter(tipo__in=tipos)
        
        if apenas_acessiveis:
            queryset = queryset.filter(tem_acessibilidade=True)
        
        # Calcula distâncias e filtra por raio
        paradas_proximas = []
        for parada in queryset:
            distancia = calcular_distancia_haversine(
                lat_ref, lon_ref, 
                parada.latitude, parada.longitude
            )
            
            if distancia <= raio_metros:
                paradas_proximas.append({
                    'parada': parada,
                    'distancia': distancia
                })
        
        # Ordena por distância e limita resultados
        paradas_proximas.sort(key=lambda x: x['distancia'])
        paradas_proximas = paradas_proximas[:limite]
        
        # Prepara os dados de resposta
        resultados = []
        for item in paradas_proximas:
            resultado = {
                'parada': ParadaResumoSerializer(item['parada']).data,
                'distancia': round(item['distancia'], 2)
            }
            resultados.append(resultado)
        
        return Response(resultados)
    
    @extend_schema(
        summary="Obter paradas em formato GeoJSON",
        description="Retorna paradas em formato GeoJSON para uso em mapas",
        parameters=[
            OpenApiParameter(
                name='bbox',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Bounding box (sw_lat,sw_lng,ne_lat,ne_lng) para filtrar paradas'
            ),
            OpenApiParameter(
                name='zoom',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Nível de zoom para otimizar densidade (padrão: 15)'
            ),
            OpenApiParameter(
                name='limite',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Número máximo de paradas (padrão: 200)'
            ),
        ],
        responses={200: ParadaGeoJSONSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def geojson(self, request):
        """
        Retorna paradas em formato GeoJSON otimizado para mapas
        """
        queryset = self.get_queryset()
        
        # Filtra por bounding box se fornecido
        bbox = request.query_params.get('bbox')
        if bbox:
            try:
                sw_lat, sw_lng, ne_lat, ne_lng = map(float, bbox.split(','))
                queryset = queryset.filter(
                    latitude__gte=sw_lat,
                    latitude__lte=ne_lat,
                    longitude__gte=sw_lng,
                    longitude__lte=ne_lng
                )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Formato de bbox inválido. Use: sw_lat,sw_lng,ne_lat,ne_lng'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Otimiza densidade baseada no zoom
        zoom = int(request.query_params.get('zoom', 15))
        limite = int(request.query_params.get('limite', 200))
        
        # Para zooms baixos, reduz a densidade
        if zoom < 12:
            limite = min(limite, 50)
            # Prioriza paradas principais (terminais, estações)
            queryset = queryset.filter(
                Q(tipo='terminal') | Q(tipo='estacao') | Q(tem_acessibilidade=True)
            )
        elif zoom < 15:
            limite = min(limite, 100)
        
        paradas = queryset[:limite]
        
        # Prepara dados GeoJSON
        features = []
        for parada in paradas:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(parada.longitude), float(parada.latitude)]
                },
                "properties": {
                    "id": parada.id,
                    "nome": parada.nome,
                    "codigo": parada.codigo_dftrans,
                    "tipo": parada.tipo,
                    "endereco": parada.endereco,
                    "tem_acessibilidade": parada.tem_acessibilidade,
                    # Dados para popup do mapa
                    "popup_info": {
                        "titulo": parada.nome,
                        "subtitulo": f"Código: {parada.codigo_dftrans}",
                        "endereco": parada.endereco,
                        "tipo": parada.get_tipo_display(),
                        "acessivel": parada.tem_acessibilidade,
                        "icone": self._get_icone_parada(parada)
                    }
                }
            }
            features.append(feature)
        
        geojson_data = {
            "type": "FeatureCollection",
            "features": features,
            "meta": {
                "total": len(features),
                "zoom": zoom,
                "bbox": bbox
            }
        }
        
        return Response(geojson_data)
    
    def _get_icone_parada(self, parada):
        """Retorna o ícone apropriado para a parada baseado no tipo"""
        icones = {
            'terminal': 'terminal',
            'estacao': 'train',
            'parada_comum': 'bus',
            'ponto_referencia': 'marker'
        }
        return icones.get(parada.tipo, 'bus')
    
    @extend_schema(
        summary="Obter informações detalhadas de uma parada para popup do mapa",
        description="Retorna informações completas de uma parada incluindo linhas que passam por ela",
        responses={200: ParadaSerializer}
    )
    @action(detail=True, methods=['get'])
    def popup_info(self, request, pk=None):
        """
        Retorna informações detalhadas para popup do mapa
        """
        parada = self.get_object()
        
        # Busca linhas que passam por esta parada
        from linhas.models import LinhaParada
        from linhas.serializers import LinhaResumoSerializer
        
        linhas_parada = LinhaParada.objects.filter(
            parada=parada
        ).select_related('linha').order_by('linha__codigo')[:10]
        
        linhas = [lp.linha for lp in linhas_parada if lp.linha.status == 'active']
        
        # Prepara resposta com informações completas
        data = {
            'parada': ParadaSerializer(parada).data,
            'linhas': LinhaResumoSerializer(linhas, many=True).data,
            'estatisticas': {
                'total_linhas': len(linhas),
                'tipos_linha': list(set([linha.tipo for linha in linhas])),
                'tem_acessibilidade': parada.tem_acessibilidade
            }
        }
        
        return Response(data)
    
    @extend_schema(
        summary="Buscar paradas por texto",
        description="Busca paradas por nome, descrição ou código",
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
        responses={200: ParadaResumoSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Busca paradas por texto com ranking inteligente
        """
        termo_busca = request.query_params.get('q', '').strip()
        if len(termo_busca) < 2:
            return Response(
                {'error': 'Termo de busca deve ter pelo menos 2 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        limite = min(int(request.query_params.get('limite', 20)), 100)
        
        # Busca com ranking: código exato > nome que inicia > nome que contém > descrição/endereço
        queryset = Parada.objects.all()
        
        # 1. Prioridade: código exato
        codigo_exato = queryset.filter(codigo_dftrans__iexact=termo_busca)
        
        # 2. Prioridade: nome que inicia com o termo
        nome_inicia = queryset.filter(nome__istartswith=termo_busca).exclude(
            id__in=codigo_exato.values_list('id', flat=True)
        )
        
        # 3. Prioridade: nome que contém o termo
        nome_contem = queryset.filter(nome__icontains=termo_busca).exclude(
            id__in=codigo_exato.values_list('id', flat=True)
        ).exclude(
            id__in=nome_inicia.values_list('id', flat=True)
        )
        
        # 4. Prioridade: descrição ou endereço
        desc_endereco = queryset.filter(
            Q(descricao__icontains=termo_busca) | 
            Q(endereco__icontains=termo_busca)
        ).exclude(
            id__in=codigo_exato.values_list('id', flat=True)
        ).exclude(
            id__in=nome_inicia.values_list('id', flat=True)
        ).exclude(
            id__in=nome_contem.values_list('id', flat=True)
        )
        
        # Combina resultados priorizados
        resultados = []
        
        # Adiciona resultados respeitando o limite
        for queryset_prioritario in [codigo_exato, nome_inicia, nome_contem, desc_endereco]:
            if len(resultados) >= limite:
                break
            
            restante = limite - len(resultados)
            resultados.extend(queryset_prioritario.order_by('nome')[:restante])
        
        serializer = ParadaResumoSerializer(resultados, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Obter paradas para autocomplete",
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
        responses={200: ParadaResumoSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """
        Autocomplete otimizado para busca rápida
        """
        termo_busca = request.query_params.get('q', '').strip()
        if len(termo_busca) < 2:
            return Response([])
        
        # Busca otimizada com apenas os campos necessários
        queryset = Parada.objects.all().filter(
            Q(nome__istartswith=termo_busca) |
            Q(codigo_dftrans__icontains=termo_busca)
        ).order_by('nome')[:15]  # Limite reduzido para autocomplete
        
        # Retorna apenas dados essenciais para autocomplete
        resultados = []
        for parada in queryset:
            resultados.append({
                'id': parada.id,
                'nome': parada.nome,
                'codigo': parada.codigo_dftrans,
                'endereco': parada.endereco,
                'latitude': float(parada.latitude),
                'longitude': float(parada.longitude)
            })
        
        return Response(resultados)

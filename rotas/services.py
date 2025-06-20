"""
BusFeed - Serviços para Cálculo de Rotas (Versão Temporária)

Este módulo implementa a lógica de cálculo de rotas entre localizações
usando o sistema de transporte público do DF.
Versão temporária sem PostGIS para desenvolvimento sem GDAL.
"""

import logging
import math
from typing import List, Dict, Tuple, Optional
from decimal import Decimal
# from django.contrib.gis.geos import Point  # Temporariamente desabilitado
# from django.contrib.gis.measure import Distance  # Temporariamente desabilitado
# from django.contrib.gis.db.models.functions import Distance as DistanceFunction  # Temporariamente desabilitado
from django.db.models import Q

from paradas.models import Parada
from linhas.models import Linha, LinhaParada
from .models import Rota, RotaLinha, RotaParada, TipoRota

logger = logging.getLogger('busfeed.rotas')


def calcular_distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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


class CalculadoraRotas:
    """
    Classe responsável pelo cálculo de rotas entre dois pontos (Versão Temporária)
    
    Implementa algoritmos simplificados para encontrar:
    - Rotas diretas (uma linha apenas)
    - Rotas com baldeação (múltiplas linhas)
    - Rotas mistas (transporte + caminhada)
    """
    
    def __init__(self):
        self.raio_busca_paradas = 800  # metros
        self.distancia_maxima_caminhada = 1500  # metros
        self.velocidade_caminhada = 80  # metros por minuto
        self.velocidade_onibus = 300  # metros por minuto
        self.tempo_espera_padrao = 8  # minutos
        self.tempo_baldeacao = 5  # minutos
    
    def calcular_rotas(
        self, 
        origem_coords: Tuple[float, float], 
        destino_coords: Tuple[float, float],
        origem_nome: str = "",
        destino_nome: str = "",
        max_rotas: int = 5
    ) -> List[Dict]:
        """
        Calcula rotas entre origem e destino
        
        Args:
            origem_coords: (latitude, longitude) da origem
            destino_coords: (latitude, longitude) do destino
            origem_nome: Nome do local de origem
            destino_nome: Nome do local de destino
            max_rotas: Número máximo de rotas a retornar
            
        Returns:
            List[Dict]: Lista de rotas calculadas
        """
        logger.info(f"Calculando rotas de {origem_nome} para {destino_nome}")
        
        rotas = []
        
        # 1. Busca paradas próximas à origem e destino
        paradas_origem = self._buscar_paradas_proximas(origem_coords)
        paradas_destino = self._buscar_paradas_proximas(destino_coords)
        
        if not paradas_origem or not paradas_destino:
            logger.warning("Não foram encontradas paradas próximas")
            return self._criar_rota_emergencia(origem_coords, destino_coords, origem_nome, destino_nome)
        
        # 2. Tenta encontrar rotas diretas
        rotas_diretas = self._calcular_rotas_diretas(
            origem_coords, destino_coords, origem_nome, destino_nome,
            paradas_origem, paradas_destino
        )
        rotas.extend(rotas_diretas)
        
        # 3. Se não encontrou rotas diretas suficientes, busca com baldeação
        if len(rotas) < max_rotas:
            rotas_baldeacao = self._calcular_rotas_com_baldeacao(
                origem_coords, destino_coords, origem_nome, destino_nome,
                paradas_origem, paradas_destino, max_rotas - len(rotas)
            )
            rotas.extend(rotas_baldeacao)
        
        # 4. Remove duplicatas baseadas nas linhas utilizadas
        rotas = self._remover_rotas_duplicadas(rotas)
        
        # 5. Ordena por qualidade e tempo total
        rotas.sort(key=lambda r: (-r['qualidade'], r['tempo_total']))
        
        # 6. Marca a melhor rota como recomendada
        if rotas:
            rotas[0]['recomendada'] = True
            
        # 7. Adiciona informações de comparação
        rotas = self._adicionar_informacoes_comparacao(rotas)
        
        return rotas[:max_rotas]
    
    def _buscar_paradas_proximas(self, coords: Tuple[float, float], raio: int = None) -> List[Parada]:
        """Busca paradas próximas a um ponto usando cálculo simples de distância"""
        if raio is None:
            raio = self.raio_busca_paradas
        
        lat, lon = coords
        paradas_proximas = []
        
        # Busca todas as paradas e calcula distância
        for parada in Parada.objects.all():
            distancia = calcular_distancia_haversine(lat, lon, parada.latitude, parada.longitude)
            if distancia <= raio:
                paradas_proximas.append((parada, distancia))
        
        # Ordena por distância e retorna as 10 mais próximas
        paradas_proximas.sort(key=lambda x: x[1])
        return [parada for parada, _ in paradas_proximas[:10]]
    
    def _calcular_rotas_diretas(
        self, 
        origem_coords: Tuple[float, float], 
        destino_coords: Tuple[float, float],
        origem_nome: str,
        destino_nome: str,
        paradas_origem: List[Parada],
        paradas_destino: List[Parada]
    ) -> List[Dict]:
        """Calcula rotas diretas (uma linha apenas)"""
        rotas_diretas = []
        
        for parada_origem in paradas_origem:
            for parada_destino in paradas_destino:
                # Busca linhas que conectam as duas paradas
                linhas_conectoras = self._buscar_linhas_conectoras(parada_origem, parada_destino)
                
                for linha in linhas_conectoras:
                    rota = self._criar_rota_direta(
                        origem_coords, destino_coords, origem_nome, destino_nome,
                        parada_origem, parada_destino, linha
                    )
                    if rota:
                        rotas_diretas.append(rota)
        
        return rotas_diretas
    
    def _calcular_rotas_com_baldeacao(
        self,
        origem_coords: Tuple[float, float], 
        destino_coords: Tuple[float, float],
        origem_nome: str,
        destino_nome: str,
        paradas_origem: List[Parada],
        paradas_destino: List[Parada],
        max_rotas: int
    ) -> List[Dict]:
        """Calcula rotas com baldeação usando paradas intermediárias"""
        rotas_baldeacao = []
        
        # Busca paradas que podem servir como pontos de baldeação
        paradas_baldeacao = self._buscar_paradas_baldeacao(paradas_origem, paradas_destino)
        
        for parada_origem in paradas_origem[:3]:  # Limita origem para performance
            for parada_destino in paradas_destino[:3]:  # Limita destino para performance
                for parada_intermediaria in paradas_baldeacao[:5]:  # Máximo 5 pontos de baldeação
                    
                    # Primeira linha: origem -> intermediária
                    linhas_primeira = self._buscar_linhas_conectoras(parada_origem, parada_intermediaria)
                    
                    # Segunda linha: intermediária -> destino
                    linhas_segunda = self._buscar_linhas_conectoras(parada_intermediaria, parada_destino)
                    
                    for linha1 in linhas_primeira[:2]:  # Máximo 2 linhas por segmento
                        for linha2 in linhas_segunda[:2]:
                            
                            # Evita usar a mesma linha duas vezes
                            if linha1.id == linha2.id:
                                continue
                            
                            rota = self._criar_rota_com_baldeacao(
                                origem_coords, destino_coords, origem_nome, destino_nome,
                                parada_origem, parada_intermediaria, parada_destino,
                                linha1, linha2
                            )
                            
                            if rota:
                                rotas_baldeacao.append(rota)
                                
                                # Para quando atingir limite
                                if len(rotas_baldeacao) >= max_rotas:
                                    return rotas_baldeacao[:max_rotas]
        
        return rotas_baldeacao[:max_rotas]
    
    def _buscar_paradas_baldeacao(self, paradas_origem: List[Parada], paradas_destino: List[Parada]) -> List[Parada]:
        """Busca paradas que podem servir como pontos de baldeação"""
        # Busca paradas que têm conexões com ambos os conjuntos
        paradas_baldeacao = []
        
        # IDs das paradas de origem e destino
        ids_origem = [p.id for p in paradas_origem]
        ids_destino = [p.id for p in paradas_destino]
        
        # Busca linhas que conectam com as paradas origem
        linhas_origem = set(LinhaParada.objects.filter(
            parada_id__in=ids_origem
        ).values_list('linha_id', flat=True))
        
        # Busca linhas que conectam com as paradas destino
        linhas_destino = set(LinhaParada.objects.filter(
            parada_id__in=ids_destino
        ).values_list('linha_id', flat=True))
        
        # Busca paradas que servem tanto linhas de origem quanto de destino
        paradas_intermediarias = Parada.objects.filter(
            linhaparada__linha_id__in=linhas_origem
        ).filter(
            linhaparada__linha_id__in=linhas_destino
        ).exclude(
            id__in=ids_origem + ids_destino
        ).distinct()[:10]
        
        return list(paradas_intermediarias)
    
    def _buscar_linhas_conectoras(self, parada_origem: Parada, parada_destino: Parada) -> List[Linha]:
        """Busca linhas que conectam duas paradas na ordem correta"""
        # Busca linhas que passam por ambas as paradas
        linhas_origem = set(LinhaParada.objects.filter(
            parada=parada_origem
        ).values_list('linha_id', flat=True))
        
        linhas_destino = set(LinhaParada.objects.filter(
            parada=parada_destino
        ).values_list('linha_id', flat=True))
        
        linhas_comuns = linhas_origem & linhas_destino
        
        if not linhas_comuns:
            return []
        
        # Verifica a ordem das paradas
        linhas_validas = []
        for linha_id in linhas_comuns:
            try:
                lp_origem = LinhaParada.objects.get(linha_id=linha_id, parada=parada_origem)
                lp_destino = LinhaParada.objects.get(linha_id=linha_id, parada=parada_destino)
                
                if lp_origem.ordem < lp_destino.ordem:
                    linha = Linha.objects.get(id=linha_id, status='active')
                    linhas_validas.append(linha)
            except (LinhaParada.DoesNotExist, Linha.DoesNotExist):
                continue
        
        return linhas_validas
    
    def _criar_rota_direta(
        self,
        origem_coords: Tuple[float, float], 
        destino_coords: Tuple[float, float],
        origem_nome: str,
        destino_nome: str,
        parada_origem: Parada,
        parada_destino: Parada,
        linha: Linha
    ) -> Optional[Dict]:
        """Cria uma rota direta utilizando apenas uma linha"""
        try:
            # Calcula distâncias de caminhada
            dist_origem = calcular_distancia_haversine(
                origem_coords[0], origem_coords[1],
                parada_origem.latitude, parada_origem.longitude
            )
            
            dist_destino = calcular_distancia_haversine(
                parada_destino.latitude, parada_destino.longitude,
                destino_coords[0], destino_coords[1]
            )
            
            # Calcula distância de ônibus entre as paradas
            dist_onibus = calcular_distancia_haversine(
                parada_origem.latitude, parada_origem.longitude,
                parada_destino.latitude, parada_destino.longitude
            )
            
            # Calcula tempos
            tempo_caminhada_origem = (dist_origem / self.velocidade_caminhada)
            tempo_caminhada_destino = (dist_destino / self.velocidade_caminhada)
            tempo_onibus = (dist_onibus / self.velocidade_onibus)
            tempo_espera = self.tempo_espera_padrao
            
            tempo_total = tempo_caminhada_origem + tempo_espera + tempo_onibus + tempo_caminhada_destino
            
            # Calcula preço (valor fixo por enquanto)
            preco = Decimal('4.50')  # Preço padrão do DF
            
            # Busca horários da linha (simplificado)
            horarios = self._obter_horarios_linha(linha)
            
            rota = {
                'id': f"rota_direta_{linha.id}_{parada_origem.id}_{parada_destino.id}",
                'tipo': 'direta',
                'origem': {
                    'nome': origem_nome,
                    'coordenadas': origem_coords,
                    'endereco': f"Próximo a {parada_origem.nome}"
                },
                'destino': {
                    'nome': destino_nome,
                    'coordenadas': destino_coords,
                    'endereco': f"Próximo a {parada_destino.nome}"
                },
                'tempo_total': round(tempo_total, 1),
                'preco_total': float(preco),
                'distancia_total': round((dist_origem + dist_onibus + dist_destino) / 1000, 2),  # km
                'etapas': [
                    {
                        'tipo': 'caminhada',
                        'descricao': f'Caminhe até {parada_origem.nome}',
                        'origem': origem_nome,
                        'destino': parada_origem.nome,
                        'distancia': round(dist_origem, 0),
                        'tempo': round(tempo_caminhada_origem, 1),
                        'coordenadas_origem': origem_coords,
                        'coordenadas_destino': [parada_origem.latitude, parada_origem.longitude]
                    },
                    {
                        'tipo': 'onibus',
                        'descricao': f'Linha {linha.codigo} - {linha.nome}',
                        'origem': parada_origem.nome,
                        'destino': parada_destino.nome,
                        'linha': {
                            'id': linha.id,
                            'codigo': linha.codigo,
                            'nome': linha.nome,
                            'tipo': linha.tipo,
                            'tem_acessibilidade': linha.tem_acessibilidade
                        },
                        'parada_origem': {
                            'id': parada_origem.id,
                            'nome': parada_origem.nome,
                            'codigo': parada_origem.codigo_dftrans,
                            'coordenadas': [parada_origem.latitude, parada_origem.longitude]
                        },
                        'parada_destino': {
                            'id': parada_destino.id,
                            'nome': parada_destino.nome,
                            'codigo': parada_destino.codigo_dftrans,
                            'coordenadas': [parada_destino.latitude, parada_destino.longitude]
                        },
                        'distancia': round(dist_onibus, 0),
                        'tempo': round(tempo_onibus + tempo_espera, 1),
                        'tempo_espera': tempo_espera,
                        'preco': float(preco),
                        'horarios': horarios[:5]  # Próximos 5 horários
                    },
                    {
                        'tipo': 'caminhada',
                        'descricao': f'Caminhe de {parada_destino.nome} até o destino',
                        'origem': parada_destino.nome,
                        'destino': destino_nome,
                        'distancia': round(dist_destino, 0),
                        'tempo': round(tempo_caminhada_destino, 1),
                        'coordenadas_origem': [parada_destino.latitude, parada_destino.longitude],
                        'coordenadas_destino': destino_coords
                    }
                ],
                'qualidade': self._calcular_qualidade_rota(tempo_total, dist_origem + dist_destino, 1),
                'recomendada': False  # Será definido depois do ranking
            }
            
            return rota
            
        except Exception as e:
            logger.error(f"Erro ao criar rota direta: {e}")
            return None
    
    def _criar_rota_com_baldeacao(
        self,
        origem_coords: Tuple[float, float], 
        destino_coords: Tuple[float, float],
        origem_nome: str,
        destino_nome: str,
        parada_origem: Parada,
        parada_intermediaria: Parada,
        parada_destino: Parada,
        linha1: Linha,
        linha2: Linha
    ) -> Optional[Dict]:
        """Cria uma rota com baldeação"""
        try:
            # Distâncias de caminhada
            dist_origem = calcular_distancia_haversine(
                origem_coords[0], origem_coords[1],
                parada_origem.latitude, parada_origem.longitude
            )
            
            dist_destino = calcular_distancia_haversine(
                parada_destino.latitude, parada_destino.longitude,
                destino_coords[0], destino_coords[1]
            )
            
            # Distâncias de ônibus
            dist_onibus1 = calcular_distancia_haversine(
                parada_origem.latitude, parada_origem.longitude,
                parada_intermediaria.latitude, parada_intermediaria.longitude
            )
            
            dist_onibus2 = calcular_distancia_haversine(
                parada_intermediaria.latitude, parada_intermediaria.longitude,
                parada_destino.latitude, parada_destino.longitude
            )
            
            # Tempos
            tempo_caminhada_origem = (dist_origem / self.velocidade_caminhada)
            tempo_caminhada_destino = (dist_destino / self.velocidade_caminhada)
            tempo_onibus1 = (dist_onibus1 / self.velocidade_onibus)
            tempo_onibus2 = (dist_onibus2 / self.velocidade_onibus)
            tempo_espera = self.tempo_espera_padrao * 2  # Espera em duas paradas
            tempo_baldeacao = self.tempo_baldeacao
            
            tempo_total = (tempo_caminhada_origem + tempo_espera + tempo_onibus1 + 
                          tempo_baldeacao + tempo_onibus2 + tempo_caminhada_destino)
            
            # Preços (duas passagens)
            preco = Decimal('9.00')  # 2x o preço padrão
            
            rota = {
                'id': f"rota_baldeacao_{linha1.id}_{linha2.id}_{parada_origem.id}_{parada_destino.id}",
                'tipo': 'baldeacao',
                'origem': {
                    'nome': origem_nome,
                    'coordenadas': origem_coords,
                    'endereco': f"Próximo a {parada_origem.nome}"
                },
                'destino': {
                    'nome': destino_nome,
                    'coordenadas': destino_coords,
                    'endereco': f"Próximo a {parada_destino.nome}"
                },
                'tempo_total': round(tempo_total, 1),
                'preco_total': float(preco),
                'distancia_total': round((dist_origem + dist_onibus1 + dist_onibus2 + dist_destino) / 1000, 2),
                'numero_baldeacoes': 1,
                'etapas': [
                    {
                        'tipo': 'caminhada',
                        'descricao': f'Caminhe até {parada_origem.nome}',
                        'origem': origem_nome,
                        'destino': parada_origem.nome,
                        'distancia': round(dist_origem, 0),
                        'tempo': round(tempo_caminhada_origem, 1),
                        'coordenadas_origem': origem_coords,
                        'coordenadas_destino': [parada_origem.latitude, parada_origem.longitude]
                    },
                    {
                        'tipo': 'onibus',
                        'descricao': f'Linha {linha1.codigo} - {linha1.nome}',
                        'origem': parada_origem.nome,
                        'destino': parada_intermediaria.nome,
                        'linha': {
                            'id': linha1.id,
                            'codigo': linha1.codigo,
                            'nome': linha1.nome,
                            'tipo': linha1.tipo,
                            'tem_acessibilidade': linha1.tem_acessibilidade
                        },
                        'parada_origem': {
                            'id': parada_origem.id,
                            'nome': parada_origem.nome,
                            'codigo': parada_origem.codigo_dftrans,
                            'coordenadas': [parada_origem.latitude, parada_origem.longitude]
                        },
                        'parada_destino': {
                            'id': parada_intermediaria.id,
                            'nome': parada_intermediaria.nome,
                            'codigo': parada_intermediaria.codigo_dftrans,
                            'coordenadas': [parada_intermediaria.latitude, parada_intermediaria.longitude]
                        },
                        'distancia': round(dist_onibus1, 0),
                        'tempo': round(tempo_onibus1 + self.tempo_espera_padrao, 1),
                        'preco': 4.50
                    },
                    {
                        'tipo': 'baldeacao',
                        'descricao': f'Baldeação em {parada_intermediaria.nome}',
                        'origem': parada_intermediaria.nome,
                        'destino': parada_intermediaria.nome,
                        'tempo': tempo_baldeacao,
                        'coordenadas': [parada_intermediaria.latitude, parada_intermediaria.longitude]
                    },
                    {
                        'tipo': 'onibus',
                        'descricao': f'Linha {linha2.codigo} - {linha2.nome}',
                        'origem': parada_intermediaria.nome,
                        'destino': parada_destino.nome,
                        'linha': {
                            'id': linha2.id,
                            'codigo': linha2.codigo,
                            'nome': linha2.nome,
                            'tipo': linha2.tipo,
                            'tem_acessibilidade': linha2.tem_acessibilidade
                        },
                        'parada_origem': {
                            'id': parada_intermediaria.id,
                            'nome': parada_intermediaria.nome,
                            'codigo': parada_intermediaria.codigo_dftrans,
                            'coordenadas': [parada_intermediaria.latitude, parada_intermediaria.longitude]
                        },
                        'parada_destino': {
                            'id': parada_destino.id,
                            'nome': parada_destino.nome,
                            'codigo': parada_destino.codigo_dftrans,
                            'coordenadas': [parada_destino.latitude, parada_destino.longitude]
                        },
                        'distancia': round(dist_onibus2, 0),
                        'tempo': round(tempo_onibus2 + self.tempo_espera_padrao, 1),
                        'preco': 4.50
                    },
                    {
                        'tipo': 'caminhada',
                        'descricao': f'Caminhe de {parada_destino.nome} até o destino',
                        'origem': parada_destino.nome,
                        'destino': destino_nome,
                        'distancia': round(dist_destino, 0),
                        'tempo': round(tempo_caminhada_destino, 1),
                        'coordenadas_origem': [parada_destino.latitude, parada_destino.longitude],
                        'coordenadas_destino': destino_coords
                    }
                ],
                'qualidade': self._calcular_qualidade_rota(tempo_total, dist_origem + dist_destino, 2),
                'recomendada': False
            }
            
            return rota
            
        except Exception as e:
            logger.error(f"Erro ao criar rota com baldeação: {e}")
            return None
    
    def _obter_horarios_linha(self, linha: Linha) -> List[str]:
        """Obtém os próximos horários de uma linha (simulado)"""
        # Por enquanto retorna horários simulados
        # Futuramente integrará com API real do DFTrans
        from datetime import datetime, timedelta
        
        agora = datetime.now()
        horarios = []
        
        # Gera horários a cada 15-30 minutos
        intervalo = 20  # minutos
        for i in range(8):
            proximo_horario = agora + timedelta(minutes=i * intervalo)
            horarios.append(proximo_horario.strftime("%H:%M"))
        
        return horarios
    
    def _calcular_qualidade_rota(self, tempo_total: float, distancia_caminhada: float, num_baldeacoes: int) -> float:
        """Calcula um score de qualidade da rota (0-10)"""
        # Score base
        score = 10.0
        
        # Penaliza tempo excessivo (acima de 60 min)
        if tempo_total > 60:
            score -= (tempo_total - 60) * 0.05
        
        # Penaliza caminhada excessiva (acima de 500m)
        if distancia_caminhada > 500:
            score -= (distancia_caminhada - 500) * 0.002
        
        # Penaliza baldeações
        score -= num_baldeacoes * 1.5
        
        # Garante que o score não seja negativo
        return max(0.0, round(score, 1))
    
    def _criar_rota_emergencia(self, origem_coords: Tuple[float, float], destino_coords: Tuple[float, float], 
                              origem_nome: str, destino_nome: str) -> List[Dict]:
        """Cria uma rota de emergência quando não há transporte público disponível"""
        distancia = calcular_distancia_haversine(
            origem_coords[0], origem_coords[1],
            destino_coords[0], destino_coords[1]
        )
        
        # Se a distância for menor que 2km, sugere caminhada
        if distancia <= 2000:
            tempo_caminhada = distancia / self.velocidade_caminhada
            return [{
                'id': 'rota_caminhada',
                'tipo': 'caminhada',
                'origem': {
                    'nome': origem_nome,
                    'coordenadas': origem_coords,
                    'endereco': origem_nome
                },
                'destino': {
                    'nome': destino_nome,
                    'coordenadas': destino_coords,
                    'endereco': destino_nome
                },
                'tempo_total': round(tempo_caminhada, 1),
                'preco_total': 0.0,
                'distancia_total': round(distancia / 1000, 2),
                'etapas': [{
                    'tipo': 'caminhada',
                    'descricao': f'Caminhe de {origem_nome} até {destino_nome}',
                    'origem': origem_nome,
                    'destino': destino_nome,
                    'distancia': round(distancia, 0),
                    'tempo': round(tempo_caminhada, 1),
                    'coordenadas_origem': origem_coords,
                    'coordenadas_destino': destino_coords
                }],
                'qualidade': 8.0 if distancia <= 1000 else 6.0,
                'recomendada': True,
                'observacoes': ['Não há transporte público disponível para esta rota', 
                              'Rota exclusiva a pé']
            }]
        
        # Para distâncias maiores, retorna mensagem informativa
        return [{
            'id': 'rota_indisponivel',
            'tipo': 'indisponivel',
            'origem': {
                'nome': origem_nome,
                'coordenadas': origem_coords,
                'endereco': origem_nome
            },
            'destino': {
                'nome': destino_nome,
                'coordenadas': destino_coords,
                'endereco': destino_nome
            },
            'tempo_total': 0,
            'preco_total': 0.0,
            'distancia_total': round(distancia / 1000, 2),
            'etapas': [],
            'qualidade': 0.0,
            'recomendada': False,
            'observacoes': [
                'Não há transporte público disponível para esta rota',
                'Considere utilizar outros meios de transporte',
                f'Distância em linha reta: {round(distancia / 1000, 2)} km'
            ]
        }]
    
    def _remover_rotas_duplicadas(self, rotas: List[Dict]) -> List[Dict]:
        """Remove rotas duplicadas baseadas nas linhas utilizadas"""
        rotas_unicas = []
        assinaturas_vistas = set()
        
        for rota in rotas:
            # Cria assinatura baseada nas linhas utilizadas
            linhas_ids = []
            for etapa in rota['etapas']:
                if etapa['tipo'] == 'onibus' and 'linha' in etapa:
                    linhas_ids.append(etapa['linha']['id'])
            
            assinatura = tuple(sorted(linhas_ids))
            
            if assinatura not in assinaturas_vistas:
                assinaturas_vistas.add(assinatura)
                rotas_unicas.append(rota)
        
        return rotas_unicas
    
    def _adicionar_informacoes_comparacao(self, rotas: List[Dict]) -> List[Dict]:
        """Adiciona informações de comparação entre as rotas"""
        if not rotas:
            return rotas
        
        # Calcula estatísticas para comparação
        tempos = [r['tempo_total'] for r in rotas]
        precos = [r['preco_total'] for r in rotas]
        
        tempo_min = min(tempos)
        preco_min = min(precos)
        
        for rota in rotas:
            rota['comparacao'] = {
                'mais_rapida': rota['tempo_total'] == tempo_min,
                'mais_barata': rota['preco_total'] == preco_min,
                'diferenca_tempo': round(rota['tempo_total'] - tempo_min, 1),
                'diferenca_preco': round(rota['preco_total'] - preco_min, 2)
            }
            
            # Adiciona badges/tags
            tags = []
            if rota['recomendada']:
                tags.append('Recomendada')
            if rota['comparacao']['mais_rapida']:
                tags.append('Mais Rápida')
            if rota['comparacao']['mais_barata']:
                tags.append('Mais Barata')
            if rota['tipo'] == 'direta':
                tags.append('Sem Baldeação')
            
            rota['tags'] = tags
        
        return rotas


# Instância global do calculador
calculadora_rotas = CalculadoraRotas() 
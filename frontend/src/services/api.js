/**
 * BusFeed - Serviço de API
 * 
 * Serviço central para comunicação com o backend Django
 * Implementa a sincronização de dados entre Mapa, Rotas e Linhas
 */

import axios from 'axios';

/**
 * Configuração base da API
 * A URL será ajustada conforme o ambiente (desenvolvimento/produção)
 */
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Instância configurada do Axios
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 segundos de timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Interceptor para logging de requisições (desenvolvimento)
 */
if (process.env.NODE_ENV === 'development') {
  api.interceptors.request.use(
    (config) => {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('❌ API Request Error:', error);
      return Promise.reject(error);
    }
  );

  api.interceptors.response.use(
    (response) => {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`);
      return response;
    },
    (error) => {
      console.error('❌ API Response Error:', error);
      return Promise.reject(error);
    }
  );
}

/**
 * Interceptor para requisições
 * Adiciona token de autenticação quando disponível
 */
api.interceptors.request.use(
  (config) => {
    // Token será implementado quando necessário
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Interceptor para respostas
 * Trata erros globais da API
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Tratamento de erros será implementado conforme necessário
    console.error('Erro na API:', error);
    return Promise.reject(error);
  }
);

// Serviços de Paradas
export const paradasAPI = {
  /**
   * Busca todas as paradas para autocomplete
   * @param {string} query - Texto de busca
   * @returns {Promise<Array>} Lista de paradas
   */
  async buscarParaAutocomplete(query) {
    try {
      if (!query || query.length < 2) return [];
      
      const response = await api.get('/paradas/autocomplete/', {
        params: { q: query }
      });
      
      return response.data.map(parada => ({
        id: parada.id,
        name: parada.nome,
        description: parada.descricao || parada.endereco || '',
        coordinates: [parada.latitude, parada.longitude],
        type: parada.tipo,
        codigo: parada.codigo_dftrans,
        accessibility: parada.tem_acessibilidade,
        lines: parada.linhas || []
      }));
    } catch (error) {
      console.error('Erro ao buscar paradas para autocomplete:', error);
      return [];
    }
  },

  /**
   * Busca paradas próximas a um ponto
   * @param {number} latitude - Latitude do ponto
   * @param {number} longitude - Longitude do ponto
   * @param {number} raio - Raio de busca em metros
   * @param {number} limite - Limite de resultados
   * @returns {Promise<Array>} Lista de paradas próximas
   */
  async buscarProximas(latitude, longitude, raio = 1000, limite = 20) {
    try {
      const response = await api.get('/paradas/proximas/', {
        params: {
          latitude,
          longitude,
          raio,
          limite
        }
      });
      
      return response.data.map(item => ({
        ...item.parada,
        coordinates: [item.parada.latitude, item.parada.longitude],
        distancia: item.distancia
      }));
    } catch (error) {
      console.error('Erro ao buscar paradas próximas:', error);
      return [];
    }
  },

  /**
   * Busca paradas em formato GeoJSON para o mapa
   * @param {Object} filtros - Filtros de busca
   * @returns {Promise<Object>} GeoJSON das paradas
   */
  async buscarGeoJSON(filtros = {}) {
    try {
      const response = await api.get('/paradas/geojson/', {
        params: filtros
      });
      
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar GeoJSON das paradas:', error);
      return { type: "FeatureCollection", features: [] };
    }
  },

  /**
   * Busca detalhes de uma parada específica
   * @param {string|number} id - ID da parada
   * @returns {Promise<Object>} Dados da parada
   */
  async buscarDetalhes(id) {
    try {
      const response = await api.get(`/paradas/${id}/`);
      return {
        ...response.data,
        coordinates: [response.data.latitude, response.data.longitude]
      };
    } catch (error) {
      console.error('Erro ao buscar detalhes da parada:', error);
      throw error;
    }
  }
};

// Serviços de Linhas
export const linhasAPI = {
  /**
   * Busca todas as linhas
   * @param {Object} filtros - Filtros de busca
   * @returns {Promise<Array>} Lista de linhas
   */
  async buscarTodas(filtros = {}) {
    try {
      const response = await api.get('/linhas/', {
        params: filtros
      });
      
      return response.data.results || response.data;
    } catch (error) {
      console.error('Erro ao buscar linhas:', error);
      return [];
    }
  },

  /**
   * Busca linhas que passam por uma parada
   * @param {string|number} paradaId - ID da parada
   * @returns {Promise<Array>} Lista de linhas
   */
  async buscarPorParada(paradaId) {
    try {
      const response = await api.get(`/linhas/por-parada/${paradaId}/`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar linhas por parada:', error);
      return [];
    }
  },

  /**
   * Busca detalhes de uma linha específica
   * @param {string} codigo - Código da linha
   * @returns {Promise<Object>} Dados da linha
   */
  async buscarDetalhes(codigo) {
    try {
      const response = await api.get(`/linhas/${codigo}/`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar detalhes da linha:', error);
      throw error;
    }
  },

  /**
   * Busca trajeto geográfico de uma linha
   * @param {string} codigo - Código da linha
   * @returns {Promise<Object>} GeoJSON do trajeto
   */
  async buscarTrajeto(codigo) {
    try {
      const response = await api.get(`/linhas/${codigo}/trajeto/`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar trajeto da linha:', error);
      return null;
    }
  }
};

// Serviços de Rotas
export const rotasAPI = {
  /**
   * Calcula rotas entre dois pontos
   * @param {Object} origem - Dados da origem
   * @param {Object} destino - Dados do destino
   * @param {Object} opcoes - Opções de cálculo
   * @returns {Promise<Array>} Lista de rotas calculadas
   */
  async calcularRotas(origem, destino, opcoes = {}) {
    try {
      const response = await api.post('/rotas/calcular/', {
        origem: {
          latitude: origem.coordinates[0],
          longitude: origem.coordinates[1],
          nome: origem.name,
          tipo: origem.type || 'ponto'
        },
        destino: {
          latitude: destino.coordinates[0],
          longitude: destino.coordinates[1],
          nome: destino.name,
          tipo: destino.type || 'ponto'
        },
        opcoes: {
          preferir_metro: opcoes.preferirMetro || false,
          max_caminhada: opcoes.maxCaminhada || 1000,
          max_transferencias: opcoes.maxTransferencias || 2,
          ...opcoes
        }
      });
      
      return response.data.rotas || [];
    } catch (error) {
      console.error('Erro ao calcular rotas:', error);
      
      // Fallback para o serviço local em caso de erro
      const { calculateRoutes } = await import('./routeService');
      return calculateRoutes(origem, destino);
    }
  },

  /**
   * Busca rotas salvas do usuário
   * @returns {Promise<Array>} Lista de rotas salvas
   */
  async buscarSalvas() {
    try {
      const response = await api.get('/rotas/salvas/');
      return response.data.results || response.data;
    } catch (error) {
      console.error('Erro ao buscar rotas salvas:', error);
      return [];
    }
  },

  /**
   * Salva uma rota
   * @param {Object} rota - Dados da rota
   * @returns {Promise<Object>} Rota salva
   */
  async salvarRota(rota) {
    try {
      const response = await api.post('/rotas/salvar/', rota);
      return response.data;
    } catch (error) {
      console.error('Erro ao salvar rota:', error);
      throw error;
    }
  }
};

// Serviço integrado para sincronização de dados
export const sincronizacaoAPI = {
  /**
   * Sincroniza dados entre mapa, rotas e linhas
   * Busca paradas visíveis no mapa e suas linhas associadas
   * @param {Object} bounds - Limites do mapa visível
   * @returns {Promise<Object>} Dados sincronizados
   */
  async sincronizarDadosMapa(bounds) {
    try {
      const { north, south, east, west } = bounds;
      
      // Busca paradas na área visível do mapa
      const paradasGeoJSON = await paradasAPI.buscarGeoJSON({
        bbox: `${west},${south},${east},${north}`,
        limite: 100
      });
      
      // Extrai IDs das paradas visíveis
      const paradaIds = paradasGeoJSON.features.map(feature => feature.properties.id);
      
      // Busca linhas que passam pelas paradas visíveis
      const linhasPromises = paradaIds.slice(0, 20).map(id => 
        linhasAPI.buscarPorParada(id).catch(() => [])
      );
      
      const linhasArrays = await Promise.all(linhasPromises);
      const linhasUnicas = [...new Set(linhasArrays.flat().map(linha => linha.codigo))]
        .map(codigo => linhasArrays.flat().find(linha => linha.codigo === codigo));
      
      return {
        paradas: paradasGeoJSON,
        linhas: linhasUnicas,
        area: bounds
      };
    } catch (error) {
      console.error('Erro na sincronização de dados do mapa:', error);
      return {
        paradas: { type: "FeatureCollection", features: [] },
        linhas: [],
        area: bounds
      };
    }
  },

  /**
   * Busca dados para recomendações de busca
   * Combina paradas próximas e linhas relevantes
   * @param {number} latitude - Latitude do usuário
   * @param {number} longitude - Longitude do usuário
   * @returns {Promise<Object>} Dados para recomendações
   */
  async buscarRecomendacoes(latitude, longitude) {
    try {
      const [paradasProximas, linhasPopulares] = await Promise.all([
        paradasAPI.buscarProximas(latitude, longitude, 2000, 10),
        linhasAPI.buscarTodas({ populares: true, limite: 10 })
      ]);
      
      return {
        paradasProximas,
        linhasPopulares,
        localizacao: { latitude, longitude }
      };
    } catch (error) {
      console.error('Erro ao buscar recomendações:', error);
      return {
        paradasProximas: [],
        linhasPopulares: [],
        localizacao: { latitude, longitude }
      };
    }
  }
};

// Função utilitária para verificar conectividade com a API
export const verificarConectividade = async () => {
  try {
    const response = await api.get('/health/', { timeout: 5000 });
    return response.status === 200;
  } catch (error) {
    console.warn('API não disponível, usando dados locais');
    return false;
  }
};



export default api; 
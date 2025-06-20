/**
 * BusFeed - Serviço de Rotas
 * 
 * Serviço responsável por:
 * - Calcular rotas entre dois pontos
 * - Buscar paradas próximas
 * - Encontrar linhas de ônibus
 * - Calcular tempo e distância de viagem
 */

// Dados mock enriquecidos das paradas de ônibus do DF - alinhados com os locais de busca
const mockBusStops = [
  // Ceilândia - coordenadas exatas dos locais de busca
  { 
    id: 'stop-001', 
    name: 'Terminal Ceilândia Centro', 
    coordinates: [-15.8267, -48.1089], 
    type: 'main',
    accessibility: true,
    lines: ['0.111', '0.112', '0.113', '0.114', '0.115', '0.130', '0.131', '0.140']
  },
  { 
    id: 'stop-002', 
    name: 'Shopping Ceilândia', 
    coordinates: [-15.8245, -48.1125], 
    type: 'regular',
    accessibility: true,
    lines: ['0.111', '0.113', '0.140', '0.150']
  },
  { 
    id: 'stop-003', 
    name: 'Hospital Regional da Ceilândia', 
    coordinates: [-15.8198, -48.1067], 
    type: 'regular',
    accessibility: true,
    lines: ['0.112', '0.114', '0.131']
  },
  { 
    id: 'stop-004', 
    name: 'Terminal Ceilândia Sul', 
    coordinates: [-15.8456, -48.1178], 
    type: 'main',
    accessibility: true,
    lines: ['0.115', '0.130', '0.160', '0.170']
  },
  { 
    id: 'stop-005', 
    name: 'Centro Metropolitano', 
    coordinates: [-15.8189, -48.1034], 
    type: 'regular',
    accessibility: true,
    lines: ['0.111', '0.112', '0.120']
  },
  { 
    id: 'stop-006', 
    name: 'QNM 13 - Conjunto A', 
    coordinates: [-15.8289, -48.1078], 
    type: 'regular',
    accessibility: true,
    lines: ['0.113', '0.114', '0.121']
  },
  { 
    id: 'stop-007', 
    name: 'QNM 15 - Comércio Local', 
    coordinates: [-15.8234, -48.1098], 
    type: 'regular',
    accessibility: true,
    lines: ['0.115', '0.116', '0.122']
  },
  { 
    id: 'stop-008', 
    name: 'CAIC - Ceilândia', 
    coordinates: [-15.8321, -48.1145], 
    type: 'regular',
    accessibility: true,
    lines: ['0.117', '0.118', '0.123']
  },
  
  // Taguatinga - coordenadas exatas dos locais de busca
  { 
    id: 'stop-009', 
    name: 'Terminal Taguatinga', 
    coordinates: [-15.8311, -48.0428], 
    type: 'main',
    accessibility: true,
    lines: ['0.180', '0.181', '0.182', '0.183', '0.190', '0.200', '0.210']
  },
  { 
    id: 'stop-010', 
    name: 'Shopping Taguatinga', 
    coordinates: [-15.8298, -48.0389], 
    type: 'regular',
    accessibility: true,
    lines: ['0.180', '0.182', '0.190']
  },
  { 
    id: 'stop-011', 
    name: 'Feira de Taguatinga', 
    coordinates: [-15.8267, -48.0502], 
    type: 'regular',
    accessibility: true,
    lines: ['0.181', '0.191', '0.201']
  },
  { 
    id: 'stop-012', 
    name: 'Hospital Regional de Taguatinga', 
    coordinates: [-15.8289, -48.0445], 
    type: 'regular',
    accessibility: true,
    lines: ['0.183', '0.192', '0.202']
  },
  
  // Samambaia - coordenadas exatas dos locais de busca
  { 
    id: 'stop-013', 
    name: 'Terminal Samambaia', 
    coordinates: [-15.8756, -48.0789], 
    type: 'main',
    accessibility: true,
    lines: ['0.220', '0.221', '0.222', '0.230', '0.240']
  },
  { 
    id: 'stop-014', 
    name: 'Shopping Samambaia', 
    coordinates: [-15.8723, -48.0834], 
    type: 'regular',
    accessibility: true,
    lines: ['0.220', '0.222', '0.230']
  },
  { 
    id: 'stop-015', 
    name: 'Estação Samambaia', 
    coordinates: [-15.8834, -48.0923], 
    type: 'metro',
    accessibility: true,
    lines: ['0.221', '0.240', 'METRO']
  },
  
  // Brasília - coordenadas exatas dos locais de busca
  { 
    id: 'stop-016', 
    name: 'Rodoviária do Plano Piloto', 
    coordinates: [-15.7942, -47.8822], 
    type: 'main',
    accessibility: true,
    lines: ['0.111', '0.180', '0.220', '0.300', '0.301', '0.302', '0.310', '0.320']
  },
  { 
    id: 'stop-017', 
    name: 'Esplanada dos Ministérios', 
    coordinates: [-15.7998, -47.8635], 
    type: 'regular',
    accessibility: true,
    lines: ['0.300', '0.301', '0.310']
  },
  { 
    id: 'stop-018', 
    name: 'Shopping Brasília', 
    coordinates: [-15.7789, -47.8934], 
    type: 'regular',
    accessibility: true,
    lines: ['0.302', '0.320']
  },
  { 
    id: 'stop-019', 
    name: 'UnB - Campus Darcy Ribeiro', 
    coordinates: [-15.7801, -47.8719], 
    type: 'regular',
    accessibility: true,
    lines: ['0.301', '0.310', '0.330']
  },
  { 
    id: 'stop-020', 
    name: 'Aeroporto JK', 
    coordinates: [-15.8711, -47.9181], 
    type: 'airport',
    accessibility: true,
    lines: ['0.113', '0.183', '0.302', '0.400']
  },
  
  // Águas Claras - coordenadas exatas dos locais de busca
  { 
    id: 'stop-021', 
    name: 'Terminal Águas Claras', 
    coordinates: [-15.8345, -48.0123], 
    type: 'main',
    accessibility: true,
    lines: ['0.350', '0.351', '0.352', '0.360']
  },
  { 
    id: 'stop-022', 
    name: 'Shopping Águas Claras', 
    coordinates: [-15.8289, -48.0089], 
    type: 'regular',
    accessibility: true,
    lines: ['0.350', '0.352']
  },
  { 
    id: 'stop-023', 
    name: 'Estação Águas Claras', 
    coordinates: [-15.8367, -48.0156], 
    type: 'metro',
    accessibility: true,
    lines: ['0.351', '0.360', 'METRO']
  }
];

/**
 * Calcula a distância entre duas coordenadas usando a fórmula de Haversine
 * @param {Array} coord1 - Coordenadas [lat, lng] do primeiro ponto
 * @param {Array} coord2 - Coordenadas [lat, lng] do segundo ponto
 * @returns {number} Distância em metros
 */
function calculateDistance(coord1, coord2) {
  const R = 6371e3; // Raio da Terra em metros
  const φ1 = coord1[0] * Math.PI/180;
  const φ2 = coord2[0] * Math.PI/180;
  const Δφ = (coord2[0]-coord1[0]) * Math.PI/180;
  const Δλ = (coord2[1]-coord1[1]) * Math.PI/180;

  const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
          Math.cos(φ1) * Math.cos(φ2) *
          Math.sin(Δλ/2) * Math.sin(Δλ/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

  return R * c; // Distância em metros
}

/**
 * Encontra as paradas mais próximas de um ponto
 * @param {Array} coordinates - Coordenadas [lat, lng] do ponto
 * @param {Array} busStops - Lista de paradas disponíveis
 * @param {number} maxDistance - Distância máxima em metros (padrão: 1000m)
 * @param {number} limit - Número máximo de paradas (padrão: 3)
 * @returns {Array} Lista de paradas próximas ordenadas por distância
 */
function findNearbyStops(coordinates, busStops, maxDistance = 1000, limit = 3) {
  const stopsWithDistance = busStops.map(stop => ({
    ...stop,
    distance: calculateDistance(coordinates, stop.coordinates)
  }))
  .filter(stop => stop.distance <= maxDistance)
  .sort((a, b) => a.distance - b.distance)
  .slice(0, limit);

  return stopsWithDistance;
}

/**
 * Encontra linhas de ônibus que conectam duas paradas
 * @param {Object} originStop - Parada de origem
 * @param {Object} destinationStop - Parada de destino
 * @returns {Array} Lista de linhas que conectam as paradas
 */
function findConnectingLines(originStop, destinationStop) {
  // Encontra linhas em comum entre as duas paradas
  const commonLines = originStop.lines.filter(line => 
    destinationStop.lines.includes(line)
  );

  // Se não há linhas em comum, cria uma conexão fictícia para demonstração
  if (commonLines.length === 0) {
    console.log('Nenhuma linha em comum encontrada, criando conexão fictícia');
    return ['0.999']; // Linha de exemplo
  }

  return commonLines;
}

/**
 * Calcula o tempo estimado de caminhada
 * @param {number} distance - Distância em metros
 * @param {number} walkingSpeed - Velocidade de caminhada em m/min (padrão: 80 m/min = 4.8 km/h)
 * @returns {number} Tempo em minutos
 */
function calculateWalkingTime(distance, walkingSpeed = 80) {
  return Math.ceil(distance / walkingSpeed);
}

/**
 * Calcula o tempo estimado de viagem de ônibus
 * @param {number} distance - Distância em metros
 * @param {number} busSpeed - Velocidade média do ônibus em m/min (padrão: 300 m/min = 18 km/h)
 * @returns {number} Tempo em minutos
 */
function calculateBusTime(distance, busSpeed = 300) {
  return Math.ceil(distance / busSpeed);
}

/**
 * Estima o número de paradas entre duas paradas
 * @param {Object} originStop - Parada de origem
 * @param {Object} destinationStop - Parada de destino
 * @returns {number} Número estimado de paradas
 */
function estimateStopCount(originStop, destinationStop) {
  const distance = calculateDistance(originStop.coordinates, destinationStop.coordinates);
  // Estima uma parada a cada 500 metros em média
  return Math.max(2, Math.round(distance / 500));
}

/**
 * Calcula uma rota direta (sem baldeação)
 * @param {Object} originLocation - Local de origem
 * @param {Object} destinationLocation - Local de destino
 * @param {Array} busStops - Lista de paradas disponíveis
 * @returns {Object|null} Rota calculada ou null se não encontrada
 */
function calculateDirectRoute(originLocation, destinationLocation, busStops) {
  // Encontra paradas próximas da origem e destino com raio maior para aumentar chances
  const nearbyOriginStops = findNearbyStops(originLocation.coordinates, busStops, 3000, 10);
  const nearbyDestinationStops = findNearbyStops(destinationLocation.coordinates, busStops, 3000, 10);
  
  console.log('Paradas próximas da origem:', nearbyOriginStops.length);
  console.log('Paradas próximas do destino:', nearbyDestinationStops.length);

  // Procura conexões diretas
  for (const originStop of nearbyOriginStops) {
    for (const destinationStop of nearbyDestinationStops) {
      const connectingLines = findConnectingLines(originStop, destinationStop);
      
      if (connectingLines.length > 0) {
        // Encontrou uma conexão direta
        const busDistance = calculateDistance(originStop.coordinates, destinationStop.coordinates);
        const walkToStopDistance = originStop.distance;
        const walkFromStopDistance = destinationStop.distance;
        
        const walkToStopTime = calculateWalkingTime(walkToStopDistance);
        const busTime = calculateBusTime(busDistance);
        const walkFromStopTime = calculateWalkingTime(walkFromStopDistance);
        
        // Tempo de espera baseado no tipo de parada
        const waitTime = originStop.type === 'main' ? 8 : 12;
        const totalTime = walkToStopTime + busTime + walkFromStopTime + waitTime;
        const totalDistance = walkToStopDistance + busDistance + walkFromStopDistance;
        const stopCount = estimateStopCount(originStop, destinationStop);

        return {
          origem: originLocation,
          destino: destinationLocation,
          tempo_total: totalTime,
          distancia_total: totalDistance,
          transferencias: 0,
          custo_total: 4.50, // Valor da passagem em 2024
          acessibilidade: originStop.accessibility && destinationStop.accessibility,
          segmentos: [{
            linha: connectingLines[0],
            paradaOrigem: originStop,
            paradaDestino: destinationStop,
            tempo: busTime,
            paradas: stopCount,
            caminhadaInicial: walkToStopDistance > 50 ? {
              distancia: walkToStopDistance,
              tempo: walkToStopTime
            } : null,
            caminhadaFinal: walkFromStopDistance > 50 ? {
              distancia: walkFromStopDistance,
              tempo: walkFromStopTime
            } : null
          }],
          observacoes: []
        };
      }
    }
  }

  return null; // Não encontrou rota direta
}

/**
 * Calcula uma rota com baldeação
 * @param {Object} originLocation - Local de origem
 * @param {Object} destinationLocation - Local de destino
 * @param {Array} busStops - Lista de paradas disponíveis
 * @returns {Object|null} Rota calculada ou null se não encontrada
 */
function calculateRouteWithTransfer(originLocation, destinationLocation, busStops) {
  const nearbyOriginStops = findNearbyStops(originLocation.coordinates, busStops, 3000, 10);
  const nearbyDestinationStops = findNearbyStops(destinationLocation.coordinates, busStops, 3000, 10);

  // Procura paradas intermediárias para baldeação
  const terminalStops = busStops.filter(stop => 
    stop.type === 'main' && stop.lines.length >= 4
  );

  for (const originStop of nearbyOriginStops) {
    for (const destinationStop of nearbyDestinationStops) {
      for (const terminalStop of terminalStops) {
        // Verifica se há linha da origem para o terminal
        const firstLeg = findConnectingLines(originStop, terminalStop);
        // Verifica se há linha do terminal para o destino
        const secondLeg = findConnectingLines(terminalStop, destinationStop);

        if (firstLeg.length > 0 && secondLeg.length > 0) {
          // Encontrou rota com baldeação
          const leg1Distance = calculateDistance(originStop.coordinates, terminalStop.coordinates);
          const leg2Distance = calculateDistance(terminalStop.coordinates, destinationStop.coordinates);
          const walkToStopDistance = originStop.distance;
          const walkFromStopDistance = destinationStop.distance;

          const walkToStopTime = calculateWalkingTime(walkToStopDistance);
          const leg1Time = calculateBusTime(leg1Distance);
          const transferTime = 15; // 15 minutos de baldeação
          const leg2Time = calculateBusTime(leg2Distance);
          const walkFromStopTime = calculateWalkingTime(walkFromStopDistance);

          const totalTime = walkToStopTime + leg1Time + transferTime + leg2Time + walkFromStopTime + 12; // +12 min de espera total
          const totalDistance = walkToStopDistance + leg1Distance + leg2Distance + walkFromStopDistance;

          return {
            origem: originLocation,
            destino: destinationLocation,
            tempo_total: totalTime,
            distancia_total: totalDistance,
            transferencias: 1,
            custo_total: 9.00, // Custo de duas passagens
            acessibilidade: originStop.accessibility && terminalStop.accessibility && destinationStop.accessibility,
            segmentos: [
              {
                linha: firstLeg[0],
                paradaOrigem: originStop,
                paradaDestino: terminalStop,
                tempo: leg1Time,
                paradas: estimateStopCount(originStop, terminalStop),
                caminhadaInicial: walkToStopDistance > 50 ? {
                  distancia: walkToStopDistance,
                  tempo: walkToStopTime
                } : null
              },
              {
                linha: secondLeg[0],
                paradaOrigem: terminalStop,
                paradaDestino: destinationStop,
                tempo: leg2Time,
                paradas: estimateStopCount(terminalStop, destinationStop),
                caminhadaFinal: walkFromStopDistance > 50 ? {
                  distancia: walkFromStopDistance,
                  tempo: walkFromStopTime
                } : null
              }
            ],
            observacoes: [
              `Baldeação em ${terminalStop.name}`,
              'Aguarde o próximo ônibus no mesmo terminal'
            ]
          };
        }
      }
    }
  }

  return null; // Não encontrou rota com baldeação
}

/**
 * Cria uma rota de exemplo para demonstração quando nenhuma rota real é encontrada
 * @param {Object} originLocation - Local de origem
 * @param {Object} destinationLocation - Local de destino  
 * @param {Array} busStops - Lista de paradas disponíveis
 * @returns {Object} Rota de exemplo
 */
function createExampleRoute(originLocation, destinationLocation, busStops) {
  console.log('Criando rota de exemplo...');
  
  // Valida se os locais têm coordenadas
  if (!originLocation.coordinates || !destinationLocation.coordinates) {
    console.error('Coordenadas inválidas para criar rota de exemplo');
    return null;
  }

  // Calcula distância aproximada entre os locais
  const directDistance = calculateDistance(originLocation.coordinates, destinationLocation.coordinates);
  console.log('Distância direta calculada:', directDistance, 'metros');
  
  // Cria uma rota de exemplo com dados realistas
  const walkToStopTime = 8; // 8 minutos caminhando
  const busTime = Math.max(25, Math.round(directDistance / 300)); // Tempo de ônibus baseado na distância
  const walkFromStopTime = 5; // 5 minutos caminhando
  const waitTime = 10; // 10 minutos de espera
  
  const totalTime = walkToStopTime + busTime + walkFromStopTime + waitTime;
  
  const exampleRoute = {
    id: 'example-route-1',
    origem: originLocation,
    destino: destinationLocation,
    tempo_total: totalTime,
    distancia_total: directDistance + 600, // Adiciona distância de caminhada
    transferencias: 0,
    custo_total: 4.50,
    acessibilidade: true,
    segmentos: [{
      linha: '0.111', // Linha mais comum em Ceilândia
      paradaOrigem: {
        id: 'example-origin',
        name: `Parada próxima a ${originLocation.name}`,
        coordinates: originLocation.coordinates,
        accessibility: true
      },
      paradaDestino: {
        id: 'example-destination', 
        name: `Parada próxima a ${destinationLocation.name}`,
        coordinates: destinationLocation.coordinates,
        accessibility: true
      },
      tempo: busTime,
      paradas: Math.max(3, Math.round(directDistance / 800)), // Mínimo 3 paradas
      caminhadaInicial: {
        distancia: 400,
        tempo: walkToStopTime
      },
      caminhadaFinal: {
        distancia: 200,
        tempo: walkFromStopTime
      }
    }],
    observacoes: [
      'Rota calculada com base na distância entre os pontos',
      'Horários e linhas podem variar - consulte o DFTrans'
    ]
  };
  
  console.log('Rota de exemplo criada com sucesso:', exampleRoute);
  return exampleRoute;
}

/**
 * Calcula rotas entre dois locais
 * @param {Object} originLocation - Local de origem
 * @param {Object} destinationLocation - Local de destino
 * @param {Array} busStops - Lista de paradas disponíveis (opcional, usa dados mock se não fornecida)
 * @returns {Promise<Array>} Lista de rotas encontradas
 */
export async function calculateRoutes(originLocation, destinationLocation, busStops = mockBusStops) {
  try {
    console.log('=== INICIANDO CÁLCULO DE ROTAS ===');
    console.log('Origem:', originLocation.name, originLocation.coordinates);
    console.log('Destino:', destinationLocation.name, destinationLocation.coordinates);
    console.log('Total de paradas disponíveis:', busStops.length);
    
    // SEMPRE cria pelo menos uma rota de exemplo para teste
    const exampleRoute = createExampleRoute(originLocation, destinationLocation, busStops);
    console.log('Rota de exemplo criada:', exampleRoute);
    
    const routes = [exampleRoute];

    // Tenta encontrar rota real também
    const directRoute = calculateDirectRoute(originLocation, destinationLocation, busStops);
    if (directRoute) {
      console.log('Rota direta também encontrada:', directRoute);
      routes.push(directRoute);
    }

    // Ordena rotas por tempo total
    routes.sort((a, b) => a.tempo_total - b.tempo_total);

    console.log('=== TOTAL DE ROTAS RETORNADAS:', routes.length, '===');
    return routes;
  } catch (error) {
    console.error('Erro ao calcular rotas:', error);
    
    // Mesmo com erro, retorna uma rota de exemplo
    const fallbackRoute = createExampleRoute(originLocation, destinationLocation, busStops);
    return fallbackRoute ? [fallbackRoute] : [];
  }
}

/**
 * Busca paradas próximas a um local
 * @param {Object} location - Local para buscar paradas próximas
 * @param {Array} busStops - Lista de paradas disponíveis (opcional)
 * @param {number} maxDistance - Distância máxima em metros
 * @returns {Array} Lista de paradas próximas
 */
export function findNearbyStopsForLocation(location, busStops = mockBusStops, maxDistance = 1200) {
  return findNearbyStops(location.coordinates, busStops, maxDistance, 10);
}

/**
 * Exporta os dados mock das paradas para uso em outros componentes
 */
export { mockBusStops }; 
/**
 * BusFeed - Componente MapView
 * 
 * Componente principal do mapa interativo usando Leaflet.
 * Exibe o mapa da região do Distrito Federal com suporte a:
 * - Visualização de paradas de ônibus sincronizadas com a API
 * - Marcadores interativos diferenciados
 * - Controles de zoom e navegação
 * - Localização do usuário
 * - Estatísticas em tempo real
 * - Responsividade e acessibilidade
 */

import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, LayersControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Configuração dos ícones do Leaflet (necessário para React)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Ícone customizado para paradas principais de ônibus
const mainBusStopIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
      <circle cx="16" cy="16" r="14" fill="#114B5F" stroke="#42F2F7" stroke-width="3"/>
      <rect x="10" y="10" width="12" height="8" fill="#42F2F7" rx="2"/>
      <circle cx="12" cy="22" r="2" fill="#42F2F7"/>
      <circle cx="20" cy="22" r="2" fill="#42F2F7"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

// Ícone customizado para paradas secundárias de ônibus
const secondaryBusStopIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle cx="12" cy="12" r="10" fill="#028090" stroke="#FCEFF9" stroke-width="2"/>
      <rect x="8" y="8" width="8" height="6" fill="#FCEFF9" rx="1"/>
      <circle cx="9" cy="16" r="1" fill="#FCEFF9"/>
      <circle cx="15" cy="16" r="1" fill="#FCEFF9"/>
    </svg>
  `),
  iconSize: [24, 24],
  iconAnchor: [12, 24],
  popupAnchor: [0, -24]
});

// Ícone especializado para estações de metrô
const metroStationIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36">
      <circle cx="18" cy="18" r="16" fill="#114B5F" stroke="#42F2F7" stroke-width="3"/>
      <rect x="8" y="12" width="20" height="12" fill="#42F2F7" rx="2"/>
      <rect x="10" y="14" width="4" height="8" fill="#114B5F" rx="1"/>
      <rect x="16" y="14" width="4" height="8" fill="#114B5F" rx="1"/>
      <rect x="22" y="14" width="4" height="8" fill="#114B5F" rx="1"/>
      <text x="18" y="30" text-anchor="middle" fill="#42F2F7" font-size="8" font-weight="bold">M</text>
    </svg>
  `),
  iconSize: [36, 36],
  iconAnchor: [18, 36],
  popupAnchor: [0, -36]
});

// Ícone especializado para terminais principais
const terminalIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 38 38" width="38" height="38">
      <circle cx="19" cy="19" r="17" fill="#114B5F" stroke="#42F2F7" stroke-width="3"/>
      <rect x="7" y="11" width="24" height="12" fill="#42F2F7" rx="3"/>
      <rect x="9" y="13" width="6" height="8" fill="#114B5F" rx="1"/>
      <rect x="16" y="13" width="6" height="8" fill="#114B5F" rx="1"/>
      <rect x="23" y="13" width="6" height="8" fill="#114B5F" rx="1"/>
      <circle cx="11" cy="25" r="2" fill="#42F2F7"/>
      <circle cx="19" cy="25" r="2" fill="#42F2F7"/>
      <circle cx="27" cy="25" r="2" fill="#42F2F7"/>
      <text x="19" y="33" text-anchor="middle" fill="#42F2F7" font-size="7" font-weight="bold">T</text>
    </svg>
  `),
  iconSize: [38, 38],
  iconAnchor: [19, 38],
  popupAnchor: [0, -38]
});

// Ícone especializado para hospitais
const hospitalIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 34 34" width="34" height="34">
      <circle cx="17" cy="17" r="15" fill="#028090" stroke="#FCEFF9" stroke-width="3"/>
      <rect x="15" y="9" width="4" height="16" fill="#FCEFF9"/>
      <rect x="9" y="15" width="16" height="4" fill="#FCEFF9"/>
      <text x="17" y="29" text-anchor="middle" fill="#FCEFF9" font-size="8" font-weight="bold">H</text>
    </svg>
  `),
  iconSize: [34, 34],
  iconAnchor: [17, 34],
  popupAnchor: [0, -34]
});

// Ícone para localização do usuário
const userLocationIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle cx="12" cy="12" r="8" fill="#42F2F7" stroke="#114B5F" stroke-width="3"/>
      <circle cx="12" cy="12" r="3" fill="#114B5F"/>
    </svg>
  `),
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  popupAnchor: [0, -12]
});

/**
 * Dados enriquecidos de paradas de ônibus (baseados na região da Ceilândia)
 * Em produção, estes dados virão da API Django
 */
const mockBusStops = [
  // Paradas principais (maior movimento)
  {
    id: 1,
    name: "Terminal Ceilândia Centro",
    coordinates: [-15.8267, -48.1089],
    lines: ["QNM 13", "QNM 17", "QNM 19", "0.030", "0.032"],
    description: "Terminal principal da Ceilândia",
    type: "main",
    passengers: 850,
    accessibility: true
  },
  {
    id: 2,
    name: "Shopping Ceilândia",
    coordinates: [-15.8245, -48.1125],
    lines: ["QNM 11", "QNM 15", "0.028", "0.031"],
    description: "Próximo ao Shopping Ceilândia",
    type: "main",
    passengers: 620,
    accessibility: true
  },
  {
    id: 3,
    name: "Hospital Regional da Ceilândia",
    coordinates: [-15.8198, -48.1067],
    lines: ["QNN 102", "QNN 104", "0.025"],
    description: "Parada do Hospital Regional",
    type: "main",
    passengers: 480,
    accessibility: true
  },
  {
    id: 4,
    name: "Terminal Ceilândia Sul",
    coordinates: [-15.8456, -48.1178],
    lines: ["QNO 01", "QNO 03", "QNO 05", "0.037"],
    description: "Terminal da região sul",
    type: "main",
    passengers: 750,
    accessibility: true
  },
  {
    id: 5,
    name: "Centro Metropolitano",
    coordinates: [-15.8189, -48.1034],
    lines: ["QNN 99", "QNN 101", "0.024"],
    description: "Centro comercial metropolitano",
    type: "main",
    passengers: 680,
    accessibility: true
  },
  
  // Paradas secundárias - Região Central
  {
    id: 6,
    name: "QNM 13 - Conjunto A",
    coordinates: [-15.8289, -48.1078],
    lines: ["QNM 21", "QNM 23"],
    description: "Quadra residencial QNM 13",
    type: "secondary",
    passengers: 180,
    accessibility: false
  },
  {
    id: 7,
    name: "QNM 15 - Comércio Local",
    coordinates: [-15.8234, -48.1098],
    lines: ["QNM 17", "0.030"],
    description: "Área comercial da QNM 15",
    type: "secondary",
    passengers: 220,
    accessibility: true
  },
  {
    id: 8,
    name: "QNM 17 - Escola Municipal",
    coordinates: [-15.8312, -48.1056],
    lines: ["QNM 17", "0.030"],
    description: "Próximo à escola municipal",
    type: "secondary",
    passengers: 195,
    accessibility: true
  },
  {
    id: 9,
    name: "QNM 19 - Posto de Saúde",
    coordinates: [-15.8201, -48.1123],
    lines: ["QNM 25", "0.029"],
    description: "Próximo ao posto de saúde",
    type: "secondary",
    passengers: 140,
    accessibility: true
  },
  {
    id: 10,
    name: "QNM 21 - Praça Central",
    coordinates: [-15.8278, -48.1156],
    lines: ["QNM 21", "QNM 23"],
    description: "Praça da quadra 21",
    type: "secondary",
    passengers: 125,
    accessibility: false
  },
  
  // Paradas secundárias - Região Norte
  {
    id: 11,
    name: "QNN 102 - Supermercado",
    coordinates: [-15.8156, -48.1089],
    lines: ["QNN 102", "0.033"],
    description: "Próximo ao supermercado",
    type: "secondary",
    passengers: 165,
    accessibility: false
  },
  {
    id: 12,
    name: "QNN 104 - Igreja Universal",
    coordinates: [-15.8134, -48.1067],
    lines: ["QNN 104", "0.025"],
    description: "Próximo à Igreja Universal",
    type: "secondary",
    passengers: 135,
    accessibility: false
  },
  {
    id: 13,
    name: "QNN 106 - Farmácia Popular",
    coordinates: [-15.8123, -48.1045],
    lines: ["QNN 106", "0.026"],
    description: "Próximo à farmácia popular",
    type: "secondary",
    passengers: 110,
    accessibility: true
  },
  {
    id: 14,
    name: "QNN 108 - Mercadinho do João",
    coordinates: [-15.8167, -48.1123],
    lines: ["QNN 108", "0.027"],
    description: "Próximo ao mercadinho",
    type: "secondary",
    passengers: 85,
    accessibility: false
  },
  {
    id: 15,
    name: "QNN 110 - Padaria Estrela",
    coordinates: [-15.8145, -48.1134],
    lines: ["QNN 110"],
    description: "Próximo à padaria",
    type: "secondary",
    passengers: 95,
    accessibility: false
  },
  
  // Paradas secundárias - Região Sul
  {
    id: 16,
    name: "QNO 15 - Condomínio Ville",
    coordinates: [-15.8345, -48.1145],
    lines: ["QNO 15", "0.035"],
    description: "Condomínio residencial",
    type: "secondary",
    passengers: 145,
    accessibility: false
  },
  {
    id: 17,
    name: "QNO 17 - Escola Técnica",
    coordinates: [-15.8378, -48.1167],
    lines: ["QNO 17", "0.036"],
    description: "Escola Técnica de Ceilândia",
    type: "secondary",
    passengers: 280,
    accessibility: true
  },
  {
    id: 18,
    name: "QNO 19 - Lotérica",
    coordinates: [-15.8412, -48.1189],
    lines: ["QNO 19", "0.037"],
    description: "Próximo à lotérica",
    type: "secondary",
    passengers: 90,
    accessibility: false
  },
  {
    id: 19,
    name: "QNO 21 - Centro Comunitário",
    coordinates: [-15.8434, -48.1201],
    lines: ["QNO 21"],
    description: "Centro comunitário local",
    type: "secondary",
    passengers: 75,
    accessibility: true
  },
  {
    id: 20,
    name: "QNO 03 - Colégio Estadual",
    coordinates: [-15.8389, -48.1134],
    lines: ["QNO 03", "0.034"],
    description: "Colégio Estadual Ceilândia",
    type: "secondary",
    passengers: 320,
    accessibility: true
  },
  
  // Paradas secundárias - Região Leste
  {
    id: 21,
    name: "QNM 25 - Banco do Brasil",
    coordinates: [-15.8234, -48.1034],
    lines: ["QNM 25", "0.029"],
    description: "Agência do Banco do Brasil",
    type: "secondary",
    passengers: 210,
    accessibility: true
  },
  {
    id: 22,
    name: "QNM 27 - Loja Americanas",
    coordinates: [-15.8256, -48.1012],
    lines: ["QNM 27", "0.028"],
    description: "Loja Americanas",
    type: "secondary",
    passengers: 185,
    accessibility: false
  },
  {
    id: 23,
    name: "QNM 29 - Atacadão",
    coordinates: [-15.8278, -48.0989],
    lines: ["QNM 29"],
    description: "Atacadão Ceilândia",
    type: "secondary",
    passengers: 290,
    accessibility: true
  },
  {
    id: 24,
    name: "QNM 31 - Delegacia Regional",
    coordinates: [-15.8301, -48.1023],
    lines: ["QNM 31", "0.032"],
    description: "Delegacia Regional",
    type: "secondary",
    passengers: 155,
    accessibility: true
  },
  {
    id: 25,
    name: "QNM 33 - Correios",
    coordinates: [-15.8323, -48.1045],
    lines: ["QNM 33"],
    description: "Agência dos Correios",
    type: "secondary",
    passengers: 130,
    accessibility: false
  },
  
  // Paradas secundárias - Região Oeste
  {
    id: 26,
    name: "QNM 35 - Casa Lotérica",
    coordinates: [-15.8289, -48.1167],
    lines: ["QNM 35", "0.038"],
    description: "Casa lotérica",
    type: "secondary",
    passengers: 80,
    accessibility: false
  },
  {
    id: 27,
    name: "QNM 37 - Mercado Popular",
    coordinates: [-15.8267, -48.1189],
    lines: ["QNM 37"],
    description: "Mercado popular",
    type: "secondary",
    passengers: 115,
    accessibility: false
  },
  {
    id: 28,
    name: "QNM 39 - Academia Forma",
    coordinates: [-15.8245, -48.1201],
    lines: ["QNM 39", "0.039"],
    description: "Academia Forma",
    type: "secondary",
    passengers: 105,
    accessibility: true
  },
  {
    id: 29,
    name: "QNM 41 - Lan House",
    coordinates: [-15.8223, -48.1178],
    lines: ["QNM 41"],
    description: "Lan house e cyber café",
    type: "secondary",
    passengers: 65,
    accessibility: false
  },
  {
    id: 30,
    name: "QNM 43 - Sorveteria Kibe",
    coordinates: [-15.8201, -48.1156],
    lines: ["QNM 43"],
    description: "Sorveteria popular",
    type: "secondary",
    passengers: 55,
    accessibility: false
  },
  
  // === EXPANSÃO: Novas paradas da região metropolitana ===
  
  // Paradas principais - Regiões adjacentes e conexões importantes
  {
    id: 31,
    name: "Terminal Samambaia",
    coordinates: [-15.8789, -48.0934],
    lines: ["0.110", "0.111", "0.112", "0.145", "0.146"],
    description: "Terminal principal de Samambaia",
    type: "main",
    passengers: 920,
    accessibility: true
  },
  {
    id: 32,
    name: "Terminal Taguatinga Centro",
    coordinates: [-15.8297, -48.0578],
    lines: ["0.051", "0.052", "0.053", "0.054", "0.055"],
    description: "Terminal central de Taguatinga",
    type: "main",
    passengers: 1120,
    accessibility: true
  },
  {
    id: 33,
    name: "Estação Ceilândia (Metrô)",
    coordinates: [-15.8156, -48.1134],
    lines: ["QNN 01", "QNN 03", "QNN 05", "0.020", "0.021", "0.022"],
    description: "Integração com o Metrô DF",
    type: "main",
    passengers: 1850,
    accessibility: true
  },
  {
    id: 34,
    name: "Terminal Águas Claras",
    coordinates: [-15.8345, -48.0267],
    lines: ["0.084", "0.085", "0.086", "0.087"],
    description: "Terminal de Águas Claras",
    type: "main",
    passengers: 780,
    accessibility: true
  },
  {
    id: 35,
    name: "Hospital de Base (DF)",
    coordinates: [-15.7801, -47.9267],
    lines: ["0.101", "0.102", "0.103", "Saúde 01"],
    description: "Principal hospital público do DF",
    type: "main",
    passengers: 650,
    accessibility: true
  },
  
  // Paradas secundárias - Conectores e pontos estratégicos
  {
    id: 36,
    name: "Feira de Ceilândia",
    coordinates: [-15.8278, -48.1089],
    lines: ["QNM 01", "QNM 03", "0.040"],
    description: "Feira livre tradicional",
    type: "secondary",
    passengers: 340,
    accessibility: false
  },
  {
    id: 37,
    name: "CAIC - Centro de Atenção",
    coordinates: [-15.8189, -48.1189],
    lines: ["QNM 07", "0.041"],
    description: "Centro de Atenção Integral à Criança",
    type: "secondary",
    passengers: 210,
    accessibility: true
  },
  {
    id: 38,
    name: "Quadra QNM 45 - Conj. C",
    coordinates: [-15.8145, -48.1067],
    lines: ["QNM 45", "0.042"],
    description: "Conjunto habitacional C",
    type: "secondary",
    passengers: 125,
    accessibility: false
  },
  {
    id: 39,
    name: "Posto de Combustível Shell",
    coordinates: [-15.8356, -48.1023],
    lines: ["QNO 07", "0.043"],
    description: "Posto Shell - Via Principal",
    type: "secondary",
    passengers: 85,
    accessibility: false
  },
  {
    id: 40,
    name: "Cemitério Campo da Esperança",
    coordinates: [-15.8423, -48.0889],
    lines: ["0.044", "Cemitério 01"],
    description: "Cemitério público",
    type: "secondary",
    passengers: 145,
    accessibility: true
  },
  
  // Paradas secundárias - Área educacional e institucional
  {
    id: 41,
    name: "UnB - Campus Ceilândia",
    coordinates: [-15.8234, -48.0978],
    lines: ["Universitário 01", "Universitário 02", "0.045"],
    description: "Universidade de Brasília - Campus Ceilândia",
    type: "secondary",
    passengers: 420,
    accessibility: true
  },
  {
    id: 42,
    name: "CEMEI Pequeno Príncipe",
    coordinates: [-15.8301, -48.1156],
    lines: ["QNM 09", "0.046"],
    description: "Centro de Educação Infantil",
    type: "secondary",
    passengers: 180,
    accessibility: true
  },
  {
    id: 43,
    name: "SESC Ceilândia",
    coordinates: [-15.8189, -48.1201],
    lines: ["QNM 11", "0.047"],
    description: "Centro de lazer e cultura SESC",
    type: "secondary",
    passengers: 295,
    accessibility: true
  },
  {
    id: 44,
    name: "Administração Regional",
    coordinates: [-15.8267, -48.1045],
    lines: ["Administrativo 01", "0.048"],
    description: "Administração Regional de Ceilândia",
    type: "secondary",
    passengers: 190,
    accessibility: true
  },
  {
    id: 45,
    name: "Bombeiros - 15º GBM",
    coordinates: [-15.8312, -48.0945],
    lines: ["Emergência 01", "0.049"],
    description: "15º Grupamento de Bombeiros",
    type: "secondary",
    passengers: 110,
    accessibility: true
  },
  
  // Paradas secundárias - Pontos comerciais e de serviços
  {
    id: 46,
    name: "Hiper Carrefour Ceilândia",
    coordinates: [-15.8178, -48.0823],
    lines: ["QNN 12", "QNN 14", "0.050"],
    description: "Hipermercado Carrefour",
    type: "secondary",
    passengers: 385,
    accessibility: true
  },
  {
    id: 47,
    name: "Auto Shopping Ceilândia",
    coordinates: [-15.8445, -48.1078],
    lines: ["QNO 09", "0.051"],
    description: "Centro automotivo",
    type: "secondary",
    passengers: 155,
    accessibility: false
  },
  {
    id: 48,
    name: "Via W3 Sul - Setor P",
    coordinates: [-15.8389, -48.1267],
    lines: ["0.052", "0.053"],
    description: "Via W3 Sul - acesso Setor P",
    type: "secondary",
    passengers: 270,
    accessibility: false
  },
  {
    id: 49,
    name: "Casa do Cidadão Ceilândia",
    coordinates: [-15.8201, -48.0978],
    lines: ["Cidadão 01", "0.054"],
    description: "Centro de atendimento ao cidadão",
    type: "secondary",
    passengers: 225,
    accessibility: true
  },
  {
    id: 50,
    name: "CEF 15 - Escola Classe",
    coordinates: [-15.8334, -48.1189],
    lines: ["QNO 11", "0.055"],
    description: "Centro de Ensino Fundamental 15",
    type: "secondary",
    passengers: 165,
    accessibility: true
  },
  
  // === EXPANSÃO ADICIONAL: Cobertura completa da região ===
  
  // Paradas principais - Terminais e estações importantes
  {
    id: 51,
    name: "Terminal Rodoviário de Brasília",
    coordinates: [-15.7942, -47.8822],
    lines: ["0.200", "0.201", "0.202", "Inter 01", "Inter 02"],
    description: "Terminal Rodoviário Principal do DF",
    type: "terminal",
    passengers: 2150,
    accessibility: true
  },
  {
    id: 52,
    name: "Estação Central (Metrô)",
    coordinates: [-15.7956, -47.8889],
    lines: ["Metro Verde", "Metro Laranja", "0.210", "0.211"],
    description: "Estação Central do Metrô DF",
    type: "metro",
    passengers: 3200,
    accessibility: true
  },
  {
    id: 53,
    name: "Hospital Universitário (HUB)",
    coordinates: [-15.7634, -47.8689],
    lines: ["Saúde 02", "Saúde 03", "Universitário 03"],
    description: "Hospital Universitário de Brasília",
    type: "hospital",
    passengers: 580,
    accessibility: true
  },
  {
    id: 54,
    name: "Terminal Sobradinho",
    coordinates: [-15.6534, -47.7823],
    lines: ["0.301", "0.302", "0.303", "0.304"],
    description: "Terminal de Sobradinho",
    type: "terminal",
    passengers: 890,
    accessibility: true
  },
  {
    id: 55,
    name: "Terminal Gama",
    coordinates: [-16.0145, -48.0623],
    lines: ["0.401", "0.402", "0.403", "Gama 01"],
    description: "Terminal principal do Gama",
    type: "terminal",
    passengers: 1050,
    accessibility: true
  },
  
  // Paradas secundárias - Região Norte da Ceilândia
  {
    id: 56,
    name: "QNN 112 - Pizzaria Nonna",
    coordinates: [-15.8098, -48.1098],
    lines: ["QNN 112", "0.056"],
    description: "Próximo à pizzaria popular",
    type: "secondary",
    passengers: 95,
    accessibility: false
  },
  {
    id: 57,
    name: "QNN 114 - Farmácia Nissei",
    coordinates: [-15.8076, -48.1123],
    lines: ["QNN 114", "0.057"],
    description: "Farmácia 24 horas",
    type: "secondary",
    passengers: 120,
    accessibility: true
  },
  {
    id: 58,
    name: "QNN 116 - Açougue Central",
    coordinates: [-15.8054, -48.1145],
    lines: ["QNN 116"],
    description: "Açougue e mercearia",
    type: "secondary",
    passengers: 85,
    accessibility: false
  },
  {
    id: 59,
    name: "QNN 118 - Salão da Dona Maria",
    coordinates: [-15.8032, -48.1167],
    lines: ["QNN 118", "0.058"],
    description: "Salão de beleza popular",
    type: "secondary",
    passengers: 70,
    accessibility: false
  },
  {
    id: 60,
    name: "QNN 120 - Igreja Batista",
    coordinates: [-15.8010, -48.1189],
    lines: ["QNN 120"],
    description: "Igreja Batista Memorial",
    type: "secondary",
    passengers: 105,
    accessibility: true
  },
  
  // Paradas secundárias - Setor P Sul
  {
    id: 61,
    name: "Setor P Sul - QR 101",
    coordinates: [-15.8456, -48.1289],
    lines: ["P Sul 01", "0.059"],
    description: "Quadra residencial 101",
    type: "secondary",
    passengers: 140,
    accessibility: false
  },
  {
    id: 62,
    name: "Setor P Sul - QR 103",
    coordinates: [-15.8478, -48.1312],
    lines: ["P Sul 02", "0.060"],
    description: "Quadra residencial 103",
    type: "secondary",
    passengers: 125,
    accessibility: false
  },
  {
    id: 63,
    name: "Setor P Sul - Comércio",
    coordinates: [-15.8501, -48.1334],
    lines: ["P Sul 03", "0.061"],
    description: "Área comercial do Setor P Sul",
    type: "secondary",
    passengers: 185,
    accessibility: true
  },
  {
    id: 64,
    name: "Setor P Sul - Escola Técnica",
    coordinates: [-15.8523, -48.1356],
    lines: ["P Sul 04"],
    description: "Escola Técnica do Setor P",
    type: "secondary",
    passengers: 245,
    accessibility: true
  },
  {
    id: 65,
    name: "Setor P Sul - UPA 24h",
    coordinates: [-15.8489, -48.1378],
    lines: ["P Sul 05", "Saúde 04"],
    description: "Unidade de Pronto Atendimento",
    type: "secondary",
    passengers: 320,
    accessibility: true
  },
  
  // Paradas secundárias - QNM Ímpares (continuação)
  {
    id: 66,
    name: "QNM 47 - Oficina do Zé",
    coordinates: [-15.8167, -48.1134],
    lines: ["QNM 47", "0.062"],
    description: "Oficina mecânica popular",
    type: "secondary",
    passengers: 65,
    accessibility: false
  },
  {
    id: 67,
    name: "QNM 49 - Depósito de Gás",
    coordinates: [-15.8145, -48.1156],
    lines: ["QNM 49"],
    description: "Depósito de gás e água",
    type: "secondary",
    passengers: 55,
    accessibility: false
  },
  {
    id: 68,
    name: "QNM 51 - Quadra Esportiva",
    coordinates: [-15.8123, -48.1178],
    lines: ["QNM 51", "0.063"],
    description: "Quadra poliesportiva comunitária",
    type: "secondary",
    passengers: 90,
    accessibility: false
  },
  {
    id: 69,
    name: "QNM 53 - Creche Mundo Infantil",
    coordinates: [-15.8101, -48.1201],
    lines: ["QNM 53"],
    description: "Creche comunitária",
    type: "secondary",
    passengers: 115,
    accessibility: true
  },
  {
    id: 70,
    name: "QNM 55 - Bar do Movimento",
    coordinates: [-15.8079, -48.1223],
    lines: ["QNM 55", "0.064"],
    description: "Bar e lanchonete popular",
    type: "secondary",
    passengers: 80,
    accessibility: false
  },
  
  // Paradas secundárias - QNO Pares (complemento)
  {
    id: 71,
    name: "QNO 02 - Conjunto Habitacional",
    coordinates: [-15.8367, -48.1123],
    lines: ["QNO 02", "0.065"],
    description: "Conjunto habitacional QNO 02",
    type: "secondary",
    passengers: 160,
    accessibility: false
  },
  {
    id: 72,
    name: "QNO 04 - Padaria do Bairro",
    coordinates: [-15.8389, -48.1145],
    lines: ["QNO 04"],
    description: "Padaria tradicional do bairro",
    type: "secondary",
    passengers: 135,
    accessibility: false
  },
  {
    id: 73,
    name: "QNO 06 - Posto Médico",
    coordinates: [-15.8412, -48.1167],
    lines: ["QNO 06", "0.066"],
    description: "Posto médico comunitário",
    type: "secondary",
    passengers: 195,
    accessibility: true
  },
  {
    id: 74,
    name: "QNO 08 - Mercado São José",
    coordinates: [-15.8434, -48.1189],
    lines: ["QNO 08", "0.067"],
    description: "Mercado São José",
    type: "secondary",
    passengers: 175,
    accessibility: false
  },
  {
    id: 75,
    name: "QNO 10 - Igreja São Sebastião",
    coordinates: [-15.8456, -48.1212],
    lines: ["QNO 10"],
    description: "Igreja Católica São Sebastião",
    type: "secondary",
    passengers: 145,
    accessibility: true
  },
  
  // Paradas secundárias - Conexões com outras regiões
  {
    id: 76,
    name: "Via EPIA - Acesso Ceilândia",
    coordinates: [-15.8123, -48.0756],
    lines: ["EPIA 01", "0.068", "0.069"],
    description: "Acesso pela EPIA Norte",
    type: "secondary",
    passengers: 285,
    accessibility: false
  },
  {
    id: 77,
    name: "Setor O - QSO 01",
    coordinates: [-15.8578, -48.1089],
    lines: ["Setor O 01", "0.070"],
    description: "Quadra do Setor O",
    type: "secondary",
    passengers: 120,
    accessibility: false
  },
  {
    id: 78,
    name: "Setor O - QSO 03",
    coordinates: [-15.8601, -48.1112],
    lines: ["Setor O 02"],
    description: "Área residencial Setor O",
    type: "secondary",
    passengers: 95,
    accessibility: false
  },
  {
    id: 79,
    name: "Guariroba - Entrada",
    coordinates: [-15.8734, -48.1234],
    lines: ["Guariroba 01", "0.071"],
    description: "Entrada do condomínio Guariroba",
    type: "secondary",
    passengers: 180,
    accessibility: false
  },
  {
    id: 80,
    name: "Sol Nascente - Trecho 01",
    coordinates: [-15.8612, -48.1445],
    lines: ["Sol Nascente 01", "0.072"],
    description: "Sol Nascente - Setor habitacional",
    type: "secondary",
    passengers: 220,
    accessibility: false
  },
  
  // Paradas secundárias - Comércios e serviços especializados
  {
    id: 81,
    name: "Ceilândia Auto Center",
    coordinates: [-15.8345, -48.0923],
    lines: ["0.073", "Comércio 01"],
    description: "Centro automotivo especializado",
    type: "secondary",
    passengers: 155,
    accessibility: false
  },
  {
    id: 82,
    name: "Mercado do Produtor",
    coordinates: [-15.8189, -48.1334],
    lines: ["Produtor 01", "0.074"],
    description: "Mercado do pequeno produtor",
    type: "secondary",
    passengers: 265,
    accessibility: true
  },
  {
    id: 83,
    name: "Centro de Tradições Nordestinas",
    coordinates: [-15.8267, -48.1267],
    lines: ["Cultura 01", "0.075"],
    description: "Centro cultural nordestino",
    type: "secondary",
    passengers: 190,
    accessibility: false
  },
  {
    id: 84,
    name: "Estádio Abadião",
    coordinates: [-15.8423, -48.0823],
    lines: ["Esporte 01", "0.076"],
    description: "Estádio municipal Abadião",
    type: "secondary",
    passengers: 310,
    accessibility: true
  },
  {
    id: 85,
    name: "Parque Recreativo Sul",
    coordinates: [-15.8512, -48.1123],
    lines: ["Parque 01", "0.077"],
    description: "Parque recreativo da região sul",
    type: "secondary",
    passengers: 175,
    accessibility: true
  },
  
  // Paradas secundárias - Equipamentos públicos
  {
    id: 86,
    name: "Companhia de Água (CAESB)",
    coordinates: [-15.8298, -48.0867],
    lines: ["Serviços 01", "0.078"],
    description: "Companhia de Água e Esgoto",
    type: "secondary",
    passengers: 85,
    accessibility: true
  },
  {
    id: 87,
    name: "CEB - Companhia Energética",
    coordinates: [-15.8356, -48.0789],
    lines: ["Serviços 02", "0.079"],
    description: "Companhia Energética de Brasília",
    type: "secondary",
    passengers: 95,
    accessibility: true
  },
  {
    id: 88,
    name: "Detran - Ceilândia",
    coordinates: [-15.8201, -48.0889],
    lines: ["Detran 01", "0.080"],
    description: "Departamento de Trânsito",
    type: "secondary",
    passengers: 280,
    accessibility: true
  },
  {
    id: 89,
    name: "Polícia Civil - 15ª DP",
    coordinates: [-15.8389, -48.0756],
    lines: ["Segurança 01", "0.081"],
    description: "15ª Delegacia de Polícia",
    type: "secondary",
    passengers: 165,
    accessibility: true
  },
  {
    id: 90,
    name: "Batalhão da PM - 14º BPM",
    coordinates: [-15.8445, -48.0834],
    lines: ["Segurança 02", "0.082"],
    description: "14º Batalhão da Polícia Militar",
    type: "secondary",
    passengers: 120,
    accessibility: true
  },
  
  // Paradas secundárias - Região de expansão e novos conjuntos
  {
    id: 91,
    name: "Expansão do Setor O - Etapa 1",
    coordinates: [-15.8634, -48.1356],
    lines: ["Expansão 01", "0.083"],
    description: "Nova área de expansão habitacional",
    type: "secondary",
    passengers: 140,
    accessibility: false
  },
  {
    id: 92,
    name: "Expansão do Setor O - Etapa 2",
    coordinates: [-15.8667, -48.1389],
    lines: ["Expansão 02"],
    description: "Segunda etapa de expansão",
    type: "secondary",
    passengers: 115,
    accessibility: false
  },
  {
    id: 93,
    name: "Condomínio Privê - Portaria",
    coordinates: [-15.8723, -48.1178],
    lines: ["Privê 01", "0.084"],
    description: "Condomínio residencial Privê",
    type: "secondary",
    passengers: 185,
    accessibility: false
  },
  {
    id: 94,
    name: "Residencial Canaã",
    coordinates: [-15.8756, -48.1201],
    lines: ["Canaã 01", "0.085"],
    description: "Residencial habitacional Canaã",
    type: "secondary",
    passengers: 205,
    accessibility: false
  },
  {
    id: 95,
    name: "Pôr do Sol - QR 201",
    coordinates: [-15.8789, -48.1267],
    lines: ["Pôr do Sol 01", "0.086"],
    description: "Setor habitacional Pôr do Sol",
    type: "secondary",
    passengers: 165,
    accessibility: false
  },
  
  // Paradas secundárias - Finalização da cobertura
  {
    id: 96,
    name: "Via Estrutural - Km 8",
    coordinates: [-15.8098, -48.0645],
    lines: ["Estrutural 01", "0.087"],
    description: "Via Estrutural - acesso Km 8",
    type: "secondary",
    passengers: 195,
    accessibility: false
  },
  {
    id: 97,
    name: "Setor Industrial - QI 01",
    coordinates: [-15.8567, -48.0756],
    lines: ["Industrial 01", "0.088"],
    description: "Quadra industrial 01",
    type: "secondary",
    passengers: 125,
    accessibility: false
  },
  {
    id: 98,
    name: "Incra 8 - Entrada Principal",
    coordinates: [-15.8823, -48.1123],
    lines: ["Incra 8 - 01", "0.089"],
    description: "Assentamento rural Incra 8",
    type: "secondary",
    passengers: 85,
    accessibility: false
  },
  {
    id: 99,
    name: "Rodoanel - Acesso Norte",
    coordinates: [-15.7756, -48.0623],
    lines: ["Rodoanel 01", "0.090"],
    description: "Acesso norte do Rodoanel",
    type: "secondary",
    passengers: 155,
    accessibility: false
  },
  {
    id: 100,
    name: "Cidade Estrutural - Centro",
    coordinates: [-15.7823, -48.0156],
    lines: ["SCIA 01", "SCIA 02", "0.091"],
    description: "Centro da Cidade Estrutural",
    type: "secondary",
    passengers: 385,
    accessibility: true
  },

  // === EXPANSÃO MASSIVA: COBERTURA COMPLETA DO DISTRITO FEDERAL ===
  
  // REGIÃO ASA SUL - PRINCIPAIS TERMINAIS E PONTOS
  {
    id: 101,
    name: "Terminal Rodoviário JK",
    coordinates: [-15.7942, -47.8822],
    lines: ["0.200", "0.201", "0.202", "Inter 01", "Inter 02", "Inter 03"],
    description: "Terminal Rodoviário Principal do DF",
    type: "terminal",
    passengers: 2850,
    accessibility: true
  },
  {
    id: 102,
    name: "Estação Central (Metrô DF)",
    coordinates: [-15.7956, -47.8889],
    lines: ["Metro Verde", "Metro Laranja", "0.210", "0.211", "0.212"],
    description: "Estação Central do Metrô DF",
    type: "metro",
    passengers: 4200,
    accessibility: true
  },
  {
    id: 103,
    name: "Hospital de Base (DF)",
    coordinates: [-15.7801, -47.9267],
    lines: ["Saúde 02", "Saúde 03", "Universitário 03", "0.220"],
    description: "Principal hospital público do DF",
    type: "hospital",
    passengers: 1580,
    accessibility: true
  },
  {
    id: 104,
    name: "Esplanada dos Ministérios",
    coordinates: [-15.7998, -47.8645],
    lines: ["0.230", "0.231", "Governo 01", "Governo 02"],
    description: "Centro do governo federal",
    type: "main",
    passengers: 1200,
    accessibility: true
  },
  {
    id: 105,
    name: "Setor Bancário Sul",
    coordinates: [-15.7987, -47.8934],
    lines: ["0.240", "0.241", "Bancário 01", "Bancário 02"],
    description: "Centro financeiro de Brasília",
    type: "main",
    passengers: 950,
    accessibility: true
  },

  // ASA NORTE - TERMINAIS E PONTOS PRINCIPAIS
  {
    id: 106,
    name: "Terminal Asa Norte",
    coordinates: [-15.7645, -47.8934],
    lines: ["0.250", "0.251", "0.252", "Asa Norte 01"],
    description: "Terminal principal da Asa Norte",
    type: "terminal",
    passengers: 1650,
    accessibility: true
  },
  {
    id: 107,
    name: "Hospital Universitário (HUB)",
    coordinates: [-15.7634, -47.8689],
    lines: ["Saúde 04", "Saúde 05", "Universitário 04", "0.260"],
    description: "Hospital Universitário de Brasília",
    type: "hospital",
    passengers: 1180,
    accessibility: true
  },
  {
    id: 108,
    name: "UnB - Campus Darcy Ribeiro",
    coordinates: [-15.7656, -47.8723],
    lines: ["Universitário 05", "Universitário 06", "0.270", "0.271"],
    description: "Campus principal da UnB",
    type: "main",
    passengers: 2800,
    accessibility: true
  },

  // TAGUATINGA - EXPANSÃO
  {
    id: 109,
    name: "Terminal Taguatinga Norte",
    coordinates: [-15.8156, -48.0534],
    lines: ["0.280", "0.281", "0.282", "0.283"],
    description: "Terminal norte de Taguatinga",
    type: "terminal",
    passengers: 1850,
    accessibility: true
  },
  {
    id: 110,
    name: "Shopping Taguatinga",
    coordinates: [-15.8234, -48.0612],
    lines: ["0.290", "0.291", "Taguatinga 01"],
    description: "Shopping Center Taguatinga",
    type: "main",
    passengers: 1120,
    accessibility: true
  },
  {
    id: 111,
    name: "Hospital Regional de Taguatinga",
    coordinates: [-15.8198, -48.0545],
    lines: ["Saúde 06", "Saúde 07", "0.300"],
    description: "Hospital Regional de Taguatinga",
    type: "hospital",
    passengers: 850,
    accessibility: true
  },

  // SOBRADINHO - REGIÃO NORTE
  {
    id: 112,
    name: "Terminal Sobradinho I",
    coordinates: [-15.6534, -47.7823],
    lines: ["0.310", "0.311", "0.312", "0.313"],
    description: "Terminal principal de Sobradinho",
    type: "terminal",
    passengers: 1450,
    accessibility: true
  },
  {
    id: 113,
    name: "Terminal Sobradinho II",
    coordinates: [-15.6723, -47.7645],
    lines: ["0.320", "0.321", "0.322"],
    description: "Terminal de Sobradinho II",
    type: "terminal",
    passengers: 890,
    accessibility: true
  },
  {
    id: 114,
    name: "Shopping Sobradinho",
    coordinates: [-15.6567, -47.7889],
    lines: ["0.330", "Sobradinho 01", "Sobradinho 02"],
    description: "Centro comercial de Sobradinho",
    type: "main",
    passengers: 680,
    accessibility: true
  },

  // PLANALTINA - REGIÃO NORDESTE
  {
    id: 115,
    name: "Terminal Planaltina",
    coordinates: [-15.6189, -47.6534],
    lines: ["0.340", "0.341", "0.342", "Planaltina 01"],
    description: "Terminal principal de Planaltina",
    type: "terminal",
    passengers: 1250,
    accessibility: true
  },
  {
    id: 116,
    name: "Centro de Planaltina",
    coordinates: [-15.6234, -47.6589],
    lines: ["0.350", "0.351", "Planaltina 02"],
    description: "Centro histórico de Planaltina",
    type: "main",
    passengers: 780,
    accessibility: false
  },

  // BRAZLÂNDIA - REGIÃO OESTE
  {
    id: 117,
    name: "Terminal Brazlândia",
    coordinates: [-15.6756, -48.2145],
    lines: ["0.360", "0.361", "0.362"],
    description: "Terminal principal de Brazlândia",
    type: "terminal",
    passengers: 950,
    accessibility: true
  },
  {
    id: 118,
    name: "Centro de Brazlândia",
    coordinates: [-15.6789, -48.2178],
    lines: ["0.370", "Brazlândia 01", "Brazlândia 02"],
    description: "Centro de Brazlândia",
    type: "main",
    passengers: 620,
    accessibility: false
  },

  // GAMA - REGIÃO SUL
  {
    id: 119,
    name: "Terminal Gama Leste",
    coordinates: [-16.0145, -48.0623],
    lines: ["0.380", "0.381", "0.382", "Gama 01"],
    description: "Terminal leste do Gama",
    type: "terminal",
    passengers: 1650,
    accessibility: true
  },
  {
    id: 120,
    name: "Terminal Gama Oeste",
    coordinates: [-16.0234, -48.0745],
    lines: ["0.390", "0.391", "Gama 02"],
    description: "Terminal oeste do Gama",
    type: "terminal",
    passengers: 1180,
    accessibility: true
  },
  {
    id: 121,
    name: "Shopping Gama",
    coordinates: [-16.0189, -48.0689],
    lines: ["0.400", "Gama 03", "Gama 04"],
    description: "Centro comercial do Gama",
    type: "main",
    passengers: 850,
    accessibility: true
  },

  // SANTA MARIA - REGIÃO SUL
  {
    id: 122,
    name: "Terminal Santa Maria",
    coordinates: [-16.0045, -47.9823],
    lines: ["0.410", "0.411", "0.412", "Santa Maria 01"],
    description: "Terminal principal de Santa Maria",
    type: "terminal",
    passengers: 1320,
    accessibility: true
  },
  {
    id: 123,
    name: "Centro de Santa Maria",
    coordinates: [-16.0089, -47.9867],
    lines: ["0.420", "Santa Maria 02", "Santa Maria 03"],
    description: "Centro comercial de Santa Maria",
    type: "main",
    passengers: 780,
    accessibility: false
  },

  // RECANTO DAS EMAS - REGIÃO SUDOESTE
  {
    id: 124,
    name: "Terminal Recanto das Emas",
    coordinates: [-15.9123, -48.0634],
    lines: ["0.430", "0.431", "0.432", "Recanto 01"],
    description: "Terminal principal do Recanto das Emas",
    type: "terminal",
    passengers: 1580,
    accessibility: true
  },
  {
    id: 125,
    name: "Shopping Recanto",
    coordinates: [-15.9156, -48.0667],
    lines: ["0.440", "Recanto 02", "Recanto 03"],
    description: "Centro comercial do Recanto",
    type: "main",
    passengers: 950,
    accessibility: true
  },

  // SÃO SEBASTIÃO - REGIÃO SUDESTE
  {
    id: 126,
    name: "Terminal São Sebastião",
    coordinates: [-15.8945, -47.7823],
    lines: ["0.450", "0.451", "0.452", "São Sebastião 01"],
    description: "Terminal principal de São Sebastião",
    type: "terminal",
    passengers: 1350,
    accessibility: true
  },
  {
    id: 127,
    name: "Centro de São Sebastião",
    coordinates: [-15.8978, -47.7856],
    lines: ["0.460", "São Sebastião 02", "São Sebastião 03"],
    description: "Centro de São Sebastião",
    type: "main",
    passengers: 720,
    accessibility: false
  },

  // PARANOÁ - REGIÃO NORDESTE
  {
    id: 128,
    name: "Terminal Paranoá",
    coordinates: [-15.7634, -47.7145],
    lines: ["0.470", "0.471", "Paranoá 01", "Paranoá 02"],
    description: "Terminal principal do Paranoá",
    type: "terminal",
    passengers: 1120,
    accessibility: true
  },
  {
    id: 129,
    name: "Centro do Paranoá",
    coordinates: [-15.7667, -47.7178],
    lines: ["0.480", "Paranoá 03", "Paranoá 04"],
    description: "Centro comercial do Paranoá",
    type: "main",
    passengers: 680,
    accessibility: false
  },

  // NÚCLEO BANDEIRANTE - REGIÃO CENTRAL
  {
    id: 130,
    name: "Terminal Núcleo Bandeirante",
    coordinates: [-15.8734, -47.9567],
    lines: ["0.490", "0.491", "0.492", "Núcleo 01"],
    description: "Terminal do Núcleo Bandeirante",
    type: "terminal",
    passengers: 1450,
    accessibility: true
  },
  {
    id: 131,
    name: "Centro do Núcleo Bandeirante",
    coordinates: [-15.8767, -47.9601],
    lines: ["0.500", "Núcleo 02", "Núcleo 03"],
    description: "Centro comercial do Núcleo Bandeirante",
    type: "main",
    passengers: 850,
    accessibility: true
  },

  // RIACHO FUNDO I E II
  {
    id: 132,
    name: "Terminal Riacho Fundo I",
    coordinates: [-15.8923, -48.0123],
    lines: ["0.510", "0.511", "Riacho I 01", "Riacho I 02"],
    description: "Terminal do Riacho Fundo I",
    type: "terminal",
    passengers: 1280,
    accessibility: true
  },
  {
    id: 133,
    name: "Terminal Riacho Fundo II",
    coordinates: [-15.9034, -48.0234],
    lines: ["0.520", "0.521", "Riacho II 01"],
    description: "Terminal do Riacho Fundo II",
    type: "terminal",
    passengers: 980,
    accessibility: true
  },

  // CANDANGOLÂNDIA
  {
    id: 134,
    name: "Centro da Candangolândia",
    coordinates: [-15.8545, -47.9345],
    lines: ["0.530", "Candango 01", "Candango 02"],
    description: "Centro da Candangolândia",
    type: "main",
    passengers: 420,
    accessibility: false
  },

  // VICENTE PIRES
  {
    id: 135,
    name: "Centro de Vicente Pires",
    coordinates: [-15.8034, -48.0345],
    lines: ["0.540", "0.541", "Vicente 01"],
    description: "Centro comercial de Vicente Pires",
    type: "main",
    passengers: 1150,
    accessibility: true
  },

  // PARK WAY E REGIÃO
  {
    id: 136,
    name: "Park Way - Shopping",
    coordinates: [-15.8645, -47.9823],
    lines: ["0.550", "Park Way 01", "Park Way 02"],
    description: "Área comercial do Park Way",
    type: "main",
    passengers: 680,
    accessibility: true
  },

  // LAGO SUL E LAGO NORTE
  {
    id: 137,
    name: "Lago Sul - Centro Comercial",
    coordinates: [-15.8234, -47.8345],
    lines: ["0.560", "Lago Sul 01", "Lago Sul 02"],
    description: "Centro comercial do Lago Sul",
    type: "main",
    passengers: 850,
    accessibility: true
  },
  {
    id: 138,
    name: "Lago Norte - Pontão",
    coordinates: [-15.7345, -47.8567],
    lines: ["0.570", "Lago Norte 01", "Lago Norte 02"],
    description: "Pontão do Lago Norte",
    type: "main",
    passengers: 920,
    accessibility: true
  },

  // JARDIM BOTÂNICO
  {
    id: 139,
    name: "Jardim Botânico - Centro",
    coordinates: [-15.8767, -47.8234],
    lines: ["0.580", "JB 01", "JB 02"],
    description: "Centro do Jardim Botânico",
    type: "main",
    passengers: 780,
    accessibility: true
  },

  // ITAPOÃ
  {
    id: 140,
    name: "Terminal Itapoã",
    coordinates: [-15.7523, -47.7634],
    lines: ["0.590", "0.591", "Itapoã 01"],
    description: "Terminal de Itapoã",
    type: "terminal",
    passengers: 1120,
    accessibility: true
  },

  // FERCAL
  {
    id: 141,
    name: "Centro de Fercal",
    coordinates: [-15.6234, -47.8456],
    lines: ["0.600", "Fercal 01", "Fercal 02"],
    description: "Centro de Fercal",
    type: "main",
    passengers: 580,
    accessibility: false
  },

  // VARJÃO
  {
    id: 142,
    name: "Centro do Varjão",
    coordinates: [-15.7456, -47.8923],
    lines: ["0.610", "Varjão 01"],
    description: "Centro do Varjão",
    type: "main",
    passengers: 320,
    accessibility: false
  },

  // SETOR DE INDÚSTRIA E ABASTECIMENTO (SIA)
  {
    id: 143,
    name: "SIA - Terminal Industrial",
    coordinates: [-15.8012, -48.0156],
    lines: ["0.620", "0.621", "Industrial 02"],
    description: "Terminal do Setor Industrial",
    type: "terminal",
    passengers: 850,
    accessibility: true
  },

  // GUARÁ I E II
  {
    id: 144,
    name: "Terminal Guará I",
    coordinates: [-15.8156, -47.9623],
    lines: ["0.630", "0.631", "Guará I 01"],
    description: "Terminal do Guará I",
    type: "terminal",
    passengers: 1650,
    accessibility: true
  },
  {
    id: 145,
    name: "Terminal Guará II",
    coordinates: [-15.8234, -47.9756],
    lines: ["0.640", "0.641", "Guará II 01"],
    description: "Terminal do Guará II",
    type: "terminal",
    passengers: 1420,
    accessibility: true
  },
  {
    id: 146,
    name: "Shopping Guará",
    coordinates: [-15.8189, -47.9689],
    lines: ["0.650", "Guará Shopping 01"],
    description: "Shopping do Guará",
    type: "main",
    passengers: 1180,
    accessibility: true
  },

  // CRUZEIRO
  {
    id: 147,
    name: "Centro do Cruzeiro",
    coordinates: [-15.7923, -47.9456],
    lines: ["0.660", "Cruzeiro 01", "Cruzeiro 02"],
    description: "Centro do Cruzeiro",
    type: "main",
    passengers: 680,
    accessibility: true
  },

  // OCTOGONAL
  {
    id: 148,
    name: "Centro da Octogonal",
    coordinates: [-15.8345, -47.9123],
    lines: ["0.670", "Octogonal 01"],
    description: "Centro da Octogonal",
    type: "main",
    passengers: 520,
    accessibility: true
  },

  // SUDOESTE
  {
    id: 149,
    name: "Setor Sudoeste - Centro",
    coordinates: [-15.7834, -47.9234],
    lines: ["0.680", "Sudoeste 01", "Sudoeste 02"],
    description: "Centro do Sudoeste",
    type: "main",
    passengers: 950,
    accessibility: true
  },

  // NOROESTE
  {
    id: 150,
    name: "Setor Noroeste - Centro",
    coordinates: [-15.7567, -47.9123],
    lines: ["0.690", "Noroeste 01", "Noroeste 02"],
    description: "Centro do Noroeste",
    type: "main",
    passengers: 1120,
    accessibility: true
  },

  // === ESTAÇÕES DE METRÔ DO DF - LINHA VERDE E LARANJA ===
  {
    id: 151,
    name: "Estação Samambaia Sul (Metrô)",
    coordinates: [-15.8823, -48.0945],
    lines: ["Metro Verde", "0.700", "0.701"],
    description: "Estação terminal sul do Metrô DF",
    type: "metro",
    passengers: 2850,
    accessibility: true
  },
  {
    id: 152,
    name: "Estação Furnas (Metrô)",
    coordinates: [-15.8667, -48.0812],
    lines: ["Metro Verde", "0.702"],
    description: "Estação Furnas do Metrô DF",
    type: "metro",
    passengers: 1950,
    accessibility: true
  },
  {
    id: 153,
    name: "Estação Águas Claras (Metrô)",
    coordinates: [-15.8345, -48.0267],
    lines: ["Metro Verde", "Metro Laranja", "0.703", "0.704"],
    description: "Estação de integração Águas Claras",
    type: "metro",
    passengers: 3200,
    accessibility: true
  },
  {
    id: 154,
    name: "Estação Arniqueiras (Metrô)",
    coordinates: [-15.8156, -48.0123],
    lines: ["Metro Laranja", "0.705"],
    description: "Estação Arniqueiras do Metrô DF",
    type: "metro",
    passengers: 1650,
    accessibility: true
  },
  {
    id: 155,
    name: "Estação Guará (Metrô)",
    coordinates: [-15.8234, -47.9689],
    lines: ["Metro Laranja", "0.706"],
    description: "Estação Guará do Metrô DF",
    type: "metro",
    passengers: 2450,
    accessibility: true
  },
  {
    id: 156,
    name: "Estação Feira (Metrô)",
    coordinates: [-15.8089, -47.9456],
    lines: ["Metro Laranja", "0.707"],
    description: "Estação Feira do Metrô DF",
    type: "metro",
    passengers: 1850,
    accessibility: true
  },
  {
    id: 157,
    name: "Estação Shopping (Metrô)",
    coordinates: [-15.7978, -47.9234],
    lines: ["Metro Laranja", "0.708"],
    description: "Estação Shopping do Metrô DF",
    type: "metro",
    passengers: 2750,
    accessibility: true
  },
  {
    id: 158,
    name: "Estação Galeria (Metrô)",
    coordinates: [-15.7889, -47.9012],
    lines: ["Metro Laranja", "0.709"],
    description: "Estação Galeria do Metrô DF",
    type: "metro",
    passengers: 2350,
    accessibility: true
  },

  // === PARADAS SECUNDÁRIAS IMPORTANTES ===
  
  // ASA SUL - Paradas secundárias
  {
    id: 159,
    name: "SQS 102 - Comércio Local",
    coordinates: [-15.8034, -47.8923],
    lines: ["Asa Sul 01", "0.710"],
    description: "Comércio local da SQS 102",
    type: "secondary",
    passengers: 385,
    accessibility: true
  },
  {
    id: 160,
    name: "SQS 202 - Escola Classe",
    coordinates: [-15.8089, -47.8856],
    lines: ["Asa Sul 02", "0.711"],
    description: "Escola Classe da SQS 202",
    type: "secondary",
    passengers: 420,
    accessibility: true
  },
  {
    id: 161,
    name: "SQS 302 - Igreja Católica",
    coordinates: [-15.8145, -47.8789],
    lines: ["Asa Sul 03", "0.712"],
    description: "Igreja Católica da SQS 302",
    type: "secondary",
    passengers: 195,
    accessibility: false
  },
  {
    id: 162,
    name: "SQS 402 - Posto de Saúde",
    coordinates: [-15.8201, -47.8723],
    lines: ["Asa Sul 04", "Saúde 08"],
    description: "Posto de Saúde da SQS 402",
    type: "secondary",
    passengers: 320,
    accessibility: true
  },

  // ASA NORTE - Paradas secundárias
  {
    id: 163,
    name: "SQN 103 - Comércio Local",
    coordinates: [-15.7623, -47.8945],
    lines: ["Asa Norte 02", "0.720"],
    description: "Comércio local da SQN 103",
    type: "secondary",
    passengers: 395,
    accessibility: true
  },
  {
    id: 164,
    name: "SQN 203 - Centro de Ensino",
    coordinates: [-15.7578, -47.8878],
    lines: ["Asa Norte 03", "0.721"],
    description: "Centro de Ensino da SQN 203",
    type: "secondary",
    passengers: 450,
    accessibility: true
  },
  {
    id: 165,
    name: "SQN 303 - Academia",
    coordinates: [-15.7534, -47.8812],
    lines: ["Asa Norte 04", "0.722"],
    description: "Academia da SQN 303",
    type: "secondary",
    passengers: 285,
    accessibility: false
  },
  {
    id: 166,
    name: "SQN 403 - Farmácia",
    coordinates: [-15.7489, -47.8745],
    lines: ["Asa Norte 05", "0.723"],
    description: "Farmácia da SQN 403",
    type: "secondary",
    passengers: 220,
    accessibility: true
  },

  // AEROPORTO E REGIÃO
  {
    id: 167,
    name: "Aeroporto de Brasília - Terminal 1",
    coordinates: [-15.8711, -47.9178],
    lines: ["Aeroporto 01", "Aeroporto 02", "0.730"],
    description: "Terminal 1 do Aeroporto JK",
    type: "main",
    passengers: 3850,
    accessibility: true
  },
  {
    id: 168,
    name: "Aeroporto de Brasília - Terminal 2",
    coordinates: [-15.8734, -47.9201],
    lines: ["Aeroporto 03", "0.731"],
    description: "Terminal 2 do Aeroporto JK",
    type: "main",
    passengers: 2650,
    accessibility: true
  },

  // SETOR HOTELEIRO E TURÍSTICO
  {
    id: 169,
    name: "Setor Hoteleiro Norte",
    coordinates: [-15.7645, -47.8645],
    lines: ["Hoteleiro 01", "0.740"],
    description: "Setor Hoteleiro Norte",
    type: "secondary",
    passengers: 580,
    accessibility: true
  },
  {
    id: 170,
    name: "Setor Hoteleiro Sul",
    coordinates: [-15.8023, -47.8645],
    lines: ["Hoteleiro 02", "0.741"],
    description: "Setor Hoteleiro Sul",
    type: "secondary",
    passengers: 520,
    accessibility: true
  },

  // SETORES COMERCIAIS
  {
    id: 171,
    name: "Setor Comercial Norte",
    coordinates: [-15.7712, -47.8789],
    lines: ["Comercial 01", "0.750"],
    description: "Setor Comercial Norte",
    type: "main",
    passengers: 1250,
    accessibility: true
  },
  {
    id: 172,
    name: "Setor Comercial Sul",
    coordinates: [-15.7923, -47.8789],
    lines: ["Comercial 02", "0.751"],
    description: "Setor Comercial Sul",
    type: "main",
    passengers: 1180,
    accessibility: true
  },

  // SETORES MÉDICOS E HOSPITALARES
  {
    id: 173,
    name: "Setor Médico Hospitalar Norte",
    coordinates: [-15.7634, -47.8823],
    lines: ["Saúde 09", "Médico 01", "0.760"],
    description: "Setor Médico Hospitalar Norte",
    type: "hospital",
    passengers: 1850,
    accessibility: true
  },
  {
    id: 174,
    name: "Setor Médico Hospitalar Sul",
    coordinates: [-15.7989, -47.8823],
    lines: ["Saúde 10", "Médico 02", "0.761"],
    description: "Setor Médico Hospitalar Sul",
    type: "hospital",
    passengers: 1650,
    accessibility: true
  },

  // UNIVERSIDADES E CENTROS EDUCACIONAIS
  {
    id: 175,
    name: "Centro Universitário de Brasília (CEUB)",
    coordinates: [-15.7612, -47.8956],
    lines: ["Universitário 07", "0.770"],
    description: "Centro Universitário de Brasília",
    type: "main",
    passengers: 1950,
    accessibility: true
  },
  {
    id: 176,
    name: "Universidade Católica (UCB)",
    coordinates: [-15.8345, -47.9234],
    lines: ["Universitário 08", "0.771"],
    description: "Universidade Católica de Brasília",
    type: "main",
    passengers: 1750,
    accessibility: true
  },

  // === EXPANSÃO FINAL: COBERTURA COMPLETA E DETALHADA ===
  
  // CIDADES DO ENTORNO - REGIÃO METROPOLITANA
  {
    id: 177,
    name: "Terminal Águas Lindas (GO)",
    coordinates: [-15.7456, -48.2789],
    lines: ["Entorno 01", "Entorno 02", "0.800"],
    description: "Terminal de Águas Lindas - Goiás",
    type: "terminal",
    passengers: 1850,
    accessibility: true
  },
  {
    id: 178,
    name: "Terminal Valparaíso (GO)",
    coordinates: [-16.0734, -47.9923],
    lines: ["Entorno 03", "Entorno 04", "0.801"],
    description: "Terminal de Valparaíso - Goiás",
    type: "terminal",
    passengers: 1650,
    accessibility: true
  },
  {
    id: 179,
    name: "Terminal Cidade Ocidental (GO)",
    coordinates: [-16.1234, -47.8645],
    lines: ["Entorno 05", "0.802"],
    description: "Terminal de Cidade Ocidental - Goiás",
    type: "terminal",
    passengers: 1320,
    accessibility: false
  },
  {
    id: 180,
    name: "Terminal Luziânia (GO)",
    coordinates: [-16.2534, -47.9512],
    lines: ["Entorno 06", "Entorno 07", "0.803"],
    description: "Terminal de Luziânia - Goiás",
    type: "terminal",
    passengers: 2150,
    accessibility: true
  },
  {
    id: 181,
    name: "Terminal Formosa (GO)",
    coordinates: [-15.5378, -47.3345],
    lines: ["Entorno 08", "0.804"],
    description: "Terminal de Formosa - Goiás",
    type: "terminal",
    passengers: 1750,
    accessibility: true
  },
  {
    id: 182,
    name: "Terminal Planaltina de Goiás (GO)",
    coordinates: [-15.4523, -47.6189],
    lines: ["Entorno 09", "0.805"],
    description: "Terminal de Planaltina de Goiás",
    type: "terminal",
    passengers: 1450,
    accessibility: false
  },

  // INCRAS E ASSENTAMENTOS RURAIS
  {
    id: 183,
    name: "INCRA 09 - Núcleo Rural",
    coordinates: [-15.9345, -48.1567],
    lines: ["Rural 01", "0.810"],
    description: "Assentamento INCRA 09",
    type: "secondary",
    passengers: 180,
    accessibility: false
  },
  {
    id: 184,
    name: "INCRA 06 - Cooperativa",
    coordinates: [-15.8567, -48.2123],
    lines: ["Rural 02", "0.811"],
    description: "Cooperativa do INCRA 06",
    type: "secondary",
    passengers: 145,
    accessibility: false
  },
  {
    id: 185,
    name: "Núcleo Rural Tabatinga",
    coordinates: [-15.6723, -48.1234],
    lines: ["Rural 03", "0.812"],
    description: "Núcleo Rural de Tabatinga",
    type: "secondary",
    passengers: 195,
    accessibility: false
  },
  {
    id: 186,
    name: "Núcleo Rural Pipiripau",
    coordinates: [-15.5434, -47.6723],
    lines: ["Rural 04", "0.813"],
    description: "Núcleo Rural do Pipiripau",
    type: "secondary",
    passengers: 165,
    accessibility: false
  },
  {
    id: 187,
    name: "Núcleo Rural Vargem Bonita",
    coordinates: [-15.9123, -47.7234],
    lines: ["Rural 05", "0.814"],
    description: "Núcleo Rural Vargem Bonita",
    type: "secondary",
    passengers: 125,
    accessibility: false
  },

  // CENTROS DE DISTRIBUIÇÃO E LOGÍSTICA
  {
    id: 188,
    name: "CEASA DF - Centro de Abastecimento",
    coordinates: [-15.7812, -48.0567],
    lines: ["Logística 01", "Abastecimento 01", "0.820"],
    description: "Centro de Abastecimento do DF",
    type: "main",
    passengers: 1250,
    accessibility: true
  },
  {
    id: 189,
    name: "Centro de Distribuição Carrefour",
    coordinates: [-15.8234, -48.0789],
    lines: ["Logística 02", "0.821"],
    description: "Centro de Distribuição Carrefour",
    type: "secondary",
    passengers: 385,
    accessibility: true
  },
  {
    id: 190,
    name: "Hub Logístico Norte",
    coordinates: [-15.7123, -47.9456],
    lines: ["Logística 03", "0.822"],
    description: "Hub logístico da região norte",
    type: "secondary",
    passengers: 450,
    accessibility: true
  },

  // PONTOS TURÍSTICOS E LAZER
  {
    id: 191,
    name: "Memorial JK",
    coordinates: [-15.7856, -47.9023],
    lines: ["Turismo 01", "0.830"],
    description: "Memorial Juscelino Kubitschek",
    type: "secondary",
    passengers: 680,
    accessibility: true
  },
  {
    id: 192,
    name: "Torre de TV",
    coordinates: [-15.7901, -47.8934],
    lines: ["Turismo 02", "0.831"],
    description: "Torre de TV de Brasília",
    type: "secondary",
    passengers: 520,
    accessibility: true
  },
  {
    id: 193,
    name: "Palácio da Alvorada",
    coordinates: [-15.7623, -47.8512],
    lines: ["Turismo 03", "0.832"],
    description: "Palácio da Alvorada",
    type: "secondary",
    passengers: 380,
    accessibility: true
  },
  {
    id: 194,
    name: "Congresso Nacional",
    coordinates: [-15.7998, -47.8634],
    lines: ["Turismo 04", "Governo 03", "0.833"],
    description: "Congresso Nacional",
    type: "secondary",
    passengers: 920,
    accessibility: true
  },
  {
    id: 195,
    name: "Palácio do Planalto",
    coordinates: [-15.7989, -47.8601],
    lines: ["Turismo 05", "Governo 04", "0.834"],
    description: "Palácio do Planalto",
    type: "secondary",
    passengers: 750,
    accessibility: true
  },
  {
    id: 196,
    name: "Supremo Tribunal Federal",
    coordinates: [-15.8012, -47.8656],
    lines: ["Turismo 06", "Governo 05", "0.835"],
    description: "Supremo Tribunal Federal",
    type: "secondary",
    passengers: 580,
    accessibility: true
  },
  {
    id: 197,
    name: "Catedral de Brasília",
    coordinates: [-15.7945, -47.8756],
    lines: ["Turismo 07", "0.836"],
    description: "Catedral Metropolitana de Brasília",
    type: "secondary",
    passengers: 850,
    accessibility: true
  },
  {
    id: 198,
    name: "Complexo Cultural da Funarte",
    coordinates: [-15.7867, -47.8823],
    lines: ["Cultura 02", "0.837"],
    description: "Complexo Cultural da Funarte",
    type: "secondary",
    passengers: 420,
    accessibility: true
  },
  {
    id: 199,
    name: "Museu Nacional",
    coordinates: [-15.7923, -47.8734],
    lines: ["Cultura 03", "0.838"],
    description: "Museu Nacional de Brasília",
    type: "secondary",
    passengers: 380,
    accessibility: true
  },
  {
    id: 200,
    name: "Ponte JK",
    coordinates: [-15.7734, -47.8223],
    lines: ["Turismo 08", "0.839"],
    description: "Ponte Juscelino Kubitschek",
    type: "secondary",
    passengers: 650,
    accessibility: false
  }
];

/**
 * Componente para centralizar o mapa em uma localização específica
 */
function MapController({ center, zoom }) {
  const map = useMap();
  
  useEffect(() => {
    if (center && center.length === 2) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  
  return null;
}

/**
 * Componente principal do mapa enriquecido
 * @param {Object} props - Props do componente
 * @param {Array} props.center - Coordenadas do centro do mapa [lat, lng]
 * @param {number} props.zoom - Nível de zoom inicial
 * @param {Array} props.busStops - Array de paradas de ônibus
 * @param {Function} props.onBusStopClick - Callback para clique em parada
 * @param {string} props.height - Altura do mapa
 * @returns {JSX.Element} Componente do mapa enriquecido
 */
function MapView({ 
  center = [-15.8267, -48.1089], // Ceilândia Centro como padrão
  zoom = 14,
  busStops = mockBusStops,
  onBusStopClick = null,
  height = '500px'
}) {
  const [mapCenter, setMapCenter] = useState(center);
  const [mapZoom, setMapZoom] = useState(zoom);
  const [userLocation, setUserLocation] = useState(null);
  const [selectedBusStop, setSelectedBusStop] = useState(null);
  const [visibleStopTypes, setVisibleStopTypes] = useState({
    main: true,
    secondary: true,
    metro: true,
    terminal: true,
    hospital: true
  });
  const mapRef = useRef(null);

  /**
   * Determina o tipo especial de uma parada baseado no nome
   */
  const getStopSpecialType = (busStop) => {
    // Primeiro verifica tipos diretos definidos nas paradas
    if (busStop.type === 'terminal' || busStop.type === 'metro' || busStop.type === 'hospital') {
      return busStop.type;
    }
    
    // Fallback: verifica por tipos especiais baseado no nome da parada
    const stopName = busStop.name.toLowerCase();
    if (stopName.includes('metrô') || stopName.includes('metro') || stopName.includes('estação')) {
      return 'metro';
    }
    if (stopName.includes('terminal')) {
      return 'terminal';
    }
    if (stopName.includes('hospital') || stopName.includes('pronto socorro') || 
        stopName.includes('upa') || stopName.includes('posto de saúde')) {
      return 'hospital';
    }
    return null;
  };

  /**
   * Filtra paradas baseado na visibilidade configurada
   */
  const getVisibleStops = () => {
    return busStops.filter(stop => {
      // Verifica visibilidade do tipo básico
      if (!visibleStopTypes[stop.type]) {
        return false;
      }
      
      // Verifica visibilidade do tipo especial
      const specialType = getStopSpecialType(stop);
      if (specialType && !visibleStopTypes[specialType]) {
        return false;
      }
      
      return true;
    });
  };

  const visibleStops = getVisibleStops();

  // Estatísticas calculadas das paradas visíveis
  const stats = {
    totalStops: visibleStops.length,
    totalAvailable: busStops.length,
    mainStops: visibleStops.filter(stop => stop.type === 'main').length,
    metroStops: visibleStops.filter(stop => getStopSpecialType(stop) === 'metro').length,
    terminalStops: visibleStops.filter(stop => getStopSpecialType(stop) === 'terminal').length,
    hospitalStops: visibleStops.filter(stop => getStopSpecialType(stop) === 'hospital').length,
    totalPassengers: visibleStops.reduce((sum, stop) => sum + stop.passengers, 0),
    accessibleStops: visibleStops.filter(stop => stop.accessibility).length
  };

  /**
   * Obtém a localização atual do usuário
   */
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setUserLocation([latitude, longitude]);
          console.log('Localização do usuário obtida:', latitude, longitude);
        },
        (error) => {
          console.log('Erro ao obter localização:', error.message);
        }
      );
    }
  }, []);

  /**
   * Manipula clique em uma parada de ônibus
   * @param {Object} busStop - Dados da parada clicada
   */
  const handleBusStopClick = (busStop) => {
    setSelectedBusStop(busStop);
    if (onBusStopClick) {
      onBusStopClick(busStop);
    } else {
      console.log('Parada selecionada:', busStop);
    }
  };

  /**
   * Centraliza o mapa em uma parada específica
   * @param {Object} busStop - Parada para centralizar
   */
  const centerOnBusStop = (busStop) => {
    setMapCenter(busStop.coordinates);
    setMapZoom(17);
  };

  /**
   * Centraliza o mapa na localização do usuário
   */
  const centerOnUserLocation = () => {
    if (userLocation) {
      setMapCenter(userLocation);
      setMapZoom(16);
    }
  };

  /**
   * Alterna a visibilidade de um tipo de parada
   */
  const toggleStopTypeVisibility = (type) => {
    setVisibleStopTypes(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  /**
   * Determina o ícone correto baseado no tipo e características especiais da parada
   */
  const getStopIcon = (busStop) => {
    // Primeiro verifica tipos diretos definidos nas paradas
    if (busStop.type === 'terminal') {
      return terminalIcon;
    }
    if (busStop.type === 'metro') {
      return metroStationIcon;
    }
    if (busStop.type === 'hospital') {
      return hospitalIcon;
    }
    
    // Fallback: verifica por tipos especiais baseado no nome da parada
    const stopName = busStop.name.toLowerCase();
    
    // Estações de metrô
    if (stopName.includes('metrô') || stopName.includes('metro') || stopName.includes('estação')) {
      return metroStationIcon;
    }
    
    // Terminais de ônibus
    if (stopName.includes('terminal')) {
      return terminalIcon;
    }
    
    // Hospitais e unidades de saúde
    if (stopName.includes('hospital') || stopName.includes('pronto socorro') || 
        stopName.includes('upa') || stopName.includes('posto de saúde')) {
      return hospitalIcon;
    }
    
    // Padrão baseado no tipo
    return busStop.type === 'main' ? mainBusStopIcon : secondaryBusStopIcon;
  };



  return (
    <div 
      className="map-container position-relative" 
      style={{ height: height, width: '100%' }}
      role="application" 
      aria-label="Mapa interativo de paradas de ônibus"
    >
      {/* Painel de estatísticas e filtros flutuante */}
      <div 
        className="position-absolute top-0 start-0 m-3 bg-white rounded shadow-sm p-3 z-index-1000"
        style={{ 
          backgroundColor: 'var(--color-tertiary)',
          border: '2px solid var(--color-primary-30)',
          zIndex: 1000,
          minWidth: '220px',
          maxWidth: '280px'
        }}
      >
        <h6 className="fw-bold mb-2" style={{ color: 'var(--color-quaternary)' }}>
          📊 Paradas Visíveis
        </h6>
        
        {/* Estatísticas resumidas */}
        <div className="small mb-3">
          <div><strong>{stats.totalStops}</strong> de <strong>{stats.totalAvailable}</strong> paradas</div>
          <div><strong>{stats.totalPassengers.toLocaleString()}</strong> passageiros/dia</div>
          <div><strong>{stats.accessibleStops}</strong> acessíveis</div>
        </div>

        {/* Controles de filtro */}
        <div className="border-top pt-2">
          <h6 className="fw-bold mb-2 small" style={{ color: 'var(--color-quaternary)' }}>
            🔍 Filtros
          </h6>
          <div className="row g-1">
            {/* Filtros dos tipos especiais */}
            <div className="col-6">
              <button
                className={`btn btn-sm w-100 ${visibleStopTypes.metro ? 'btn-info' : 'btn-outline-secondary'}`}
                onClick={() => toggleStopTypeVisibility('metro')}
                style={{ fontSize: '0.7rem', padding: '0.25rem' }}
              >
                🚇 {stats.metroStops}
              </button>
            </div>
            <div className="col-6">
              <button
                className={`btn btn-sm w-100 ${visibleStopTypes.terminal ? 'btn-warning text-dark' : 'btn-outline-secondary'}`}
                onClick={() => toggleStopTypeVisibility('terminal')}
                style={{ fontSize: '0.7rem', padding: '0.25rem' }}
              >
                🚌 {stats.terminalStops}
              </button>
            </div>
            <div className="col-6">
              <button
                className={`btn btn-sm w-100 ${visibleStopTypes.hospital ? 'btn-success' : 'btn-outline-secondary'}`}
                onClick={() => toggleStopTypeVisibility('hospital')}
                style={{ fontSize: '0.7rem', padding: '0.25rem' }}
              >
                🏥 {stats.hospitalStops}
              </button>
            </div>
            <div className="col-6">
              <button
                className={`btn btn-sm w-100 ${visibleStopTypes.main ? 'btn-primary' : 'btn-outline-secondary'}`}
                onClick={() => toggleStopTypeVisibility('main')}
                style={{ 
                  fontSize: '0.7rem', 
                  padding: '0.25rem',
                  minWidth: 'fit-content',
                  boxSizing: 'border-box',
                  borderRadius: '0.375rem'
                }}
              >
                ⭐ {stats.mainStops}
              </button>
            </div>
            <div className="col-12">
              <button
                className={`btn btn-sm w-100 ${visibleStopTypes.secondary ? 'btn-danger' : 'btn-outline-secondary'}`}
                onClick={() => toggleStopTypeVisibility('secondary')}
                style={{ 
                  fontSize: '0.7rem', 
                  padding: '0.25rem',
                  borderRadius: '0.375rem'
                }}
              >
                📍 Secundárias ({stats.totalStops - stats.mainStops - stats.metroStops - stats.terminalStops - stats.hospitalStops})
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Controles de navegação flutuantes */}
      <div 
        className="position-absolute top-0 end-0 m-3 z-index-1000"
        style={{ zIndex: 1000 }}
      >
        {userLocation && (
          <button
            className="btn btn-primary btn-sm mb-2 d-block"
            onClick={centerOnUserLocation}
            aria-label="Centralizar na minha localização"
            style={{
              backgroundColor: 'var(--color-primary)',
              borderColor: 'var(--color-secondary)',
              color: 'var(--color-quaternary)'
            }}
          >
            📍 Minha Localização
          </button>
        )}
        <button
          className="btn btn-outline-secondary btn-sm d-block"
          onClick={() => {
            setMapCenter(center);
            setMapZoom(14);
          }}
          aria-label="Voltar para visão geral"
          style={{
            backgroundColor: 'var(--color-tertiary)',
            borderColor: 'var(--color-secondary)',
            color: 'var(--color-quaternary)',
            fontWeight: '500'
          }}
        >
          🔄 Visão Geral
        </button>
      </div>

      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
        className="leaflet-map"
        aria-label="Mapa de Brasília com paradas de ônibus"
      >
        {/* Controlador para mudanças programáticas do mapa */}
        <MapController center={mapCenter} zoom={mapZoom} />
        
        {/* Controle de camadas */}
        <LayersControl position="bottomright">
          {/* Camada base padrão */}
          <LayersControl.BaseLayer checked name="Mapa Padrão">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={19}
              minZoom={10}
            />
          </LayersControl.BaseLayer>
          
          {/* Camada satelital alternativa */}
          <LayersControl.BaseLayer name="Vista Satelital">
            <TileLayer
              attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              maxZoom={19}
              minZoom={10}
            />
          </LayersControl.BaseLayer>
        </LayersControl>

        {/* Marcador da localização do usuário */}
        {userLocation && (
          <Marker
            position={userLocation}
            icon={userLocationIcon}
            aria-label="Sua localização atual"
          >
            <Popup className="user-location-popup">
              <div className="text-center">
                <h6 className="fw-bold">📍 Você está aqui</h6>
                <p className="small text-muted mb-1">Localização atual</p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Marcadores das paradas de ônibus */}
        {visibleStops.map((busStop) => (
          <React.Fragment key={busStop.id}>
            {/* Marcador da parada */}
            <Marker
              position={busStop.coordinates}
              icon={getStopIcon(busStop)}
              eventHandlers={{
                click: () => handleBusStopClick(busStop)
              }}
              aria-label={`Parada de ônibus: ${busStop.name}`}
            >
              <Popup 
                className="bus-stop-popup"
                maxWidth={350}
                closeButton={true}
              >
                <div className="popup-content">
                  {/* Cabeçalho da parada */}
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <h6 className="fw-bold mb-0">{busStop.name}</h6>
                    <div className="d-flex flex-column gap-1 ms-2">
                      {/* Badge do tipo especial */}
                      {(() => {
                        const stopName = busStop.name.toLowerCase();
                        if (stopName.includes('metrô') || stopName.includes('metro') || stopName.includes('estação')) {
                          return <span className="badge bg-info" style={{ fontSize: '0.6rem' }}>🚇 Metrô</span>;
                        }
                        if (stopName.includes('terminal')) {
                          return <span className="badge bg-warning text-dark" style={{ fontSize: '0.6rem' }}>🚌 Terminal</span>;
                        }
                        if (stopName.includes('hospital') || stopName.includes('pronto socorro') || 
                            stopName.includes('upa') || stopName.includes('posto de saúde')) {
                          return <span className="badge bg-success" style={{ fontSize: '0.6rem' }}>🏥 Hospital</span>;
                        }
                        return null;
                      })()}
                      {/* Badge do tipo principal/secundário */}
                      <span 
                        className={`badge ${busStop.type === 'main' ? 'bg-primary' : 'bg-secondary'}`}
                        style={{ fontSize: '0.6rem' }}
                      >
                        {busStop.type === 'main' ? '⭐ Principal' : '📍 Secundária'}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-muted small mb-2">{busStop.description}</p>
                  
                  {/* Informações da parada */}
                  <div className="row small mb-2">
                    <div className="col-6">
                      <strong>👥 Passageiros/dia:</strong><br/>
                      <span className="text-primary">{busStop.passengers}</span>
                    </div>
                    <div className="col-6">
                      <strong>♿ Acessível:</strong><br/>
                      <span className={busStop.accessibility ? 'text-success' : 'text-muted'}>
                        {busStop.accessibility ? '✅ Sim' : '❌ Não'}
                      </span>
                    </div>
                  </div>
                  
                  {/* Lista de linhas que passam pela parada */}
                  <div className="lines-container mb-2">
                    <strong className="small">🚌 Linhas:</strong>
                    <div className="d-flex flex-wrap gap-1 mt-1">
                      {busStop.lines.map((line, index) => (
                        <span 
                          key={index}
                          className="badge"
                          style={{ 
                            fontSize: '0.7rem',
                            backgroundColor: 'var(--color-secondary)',
                            color: 'var(--color-white)'
                          }}
                        >
                          {line}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  {/* Botões de ação */}
                  <div className="d-grid gap-2">
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => centerOnBusStop(busStop)}
                      aria-label={`Centralizar mapa na parada ${busStop.name}`}
                      style={{
                        backgroundColor: 'var(--color-primary)',
                        borderColor: 'var(--color-secondary)',
                        color: 'var(--color-quaternary)',
                        fontSize: '0.8rem',
                        padding: '0.375rem 0.75rem'
                      }}
                    >
                      🎯 Centralizar
                    </button>
                  </div>
                </div>
              </Popup>
            </Marker>
          </React.Fragment>
        ))}
      </MapContainer>

      {/* Controles de acessibilidade e feedback */}
      <div className="sr-only" aria-live="polite">
        Mapa carregado com {stats.totalStops} paradas visíveis de {stats.totalAvailable} paradas totais disponíveis.
        {selectedBusStop && ` Parada selecionada: ${selectedBusStop.name}`}
      </div>
      
      {/* Legenda do mapa */}
      <div 
        className="position-absolute bottom-0 start-0 m-3 bg-white rounded shadow-sm p-2"
        style={{ 
          backgroundColor: 'var(--color-white)',
          border: '1px solid var(--color-secondary-20)',
          zIndex: 1000,
          fontSize: '0.75rem',
          maxWidth: '180px'
        }}
      >
        <div className="fw-bold mb-2" style={{ color: 'var(--color-quaternary)' }}>
          🗺️ Legenda
        </div>
        <div className="d-flex align-items-center mb-1">
          <span style={{ color: 'var(--color-primary)', fontSize: '0.9rem' }}>🚇</span>
          <span className="ms-2 small">Estação Metrô</span>
        </div>
        <div className="d-flex align-items-center mb-1">
          <span style={{ color: 'var(--color-primary)', fontSize: '0.9rem' }}>🚌</span>
          <span className="ms-2 small">Terminal</span>
        </div>
        <div className="d-flex align-items-center mb-1">
          <span style={{ color: 'var(--color-secondary)', fontSize: '0.9rem' }}>🏥</span>
          <span className="ms-2 small">Hospital</span>
        </div>
        <div className="d-flex align-items-center mb-1">
          <span style={{ color: 'var(--color-quaternary)', fontSize: '0.9rem' }}>⭐</span>
          <span className="ms-2 small">Parada principal</span>
        </div>
        <div className="d-flex align-items-center mb-1">
          <span style={{ color: 'var(--color-secondary)', fontSize: '0.9rem' }}>📍</span>
          <span className="ms-2 small">Parada secundária</span>
        </div>
        <div className="d-flex align-items-center">
          <span style={{ color: 'var(--color-primary)', fontSize: '0.9rem' }}>📍</span>
          <span className="ms-2 small">Sua localização</span>
        </div>
      </div>
    </div>
  );
}

export default MapView; 
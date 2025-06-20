/**
 * BusFeed - Página do Mapa
 * 
 * Página principal com mapa interativo e busca de rotas
 */

import React, { useState, useEffect } from 'react';
import MapView from '../components/map/MapView';
import Header from '../components/common/Header';

function MapPage() {
  // Estados do mapa
  const [mapCenter, setMapCenter] = useState([-15.8267, -48.1089]); // Ceilândia Centro
  const [mapZoom, setMapZoom] = useState(14);
  
  // Estados de localização
  const [userLocation, setUserLocation] = useState(null);

  /**
   * Inicialização da página
   */
  useEffect(() => {
    // Tenta obter localização do usuário
    getUserLocation();
  }, []);

  /**
   * Obtém localização do usuário
   */
  const getUserLocation = () => {
    if (!navigator.geolocation) {
      console.warn('Geolocalização não suportada pelo navegador');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        };
        
        setUserLocation(location);
        
        // Se estiver na região do DF, centraliza no usuário
        if (isInDFRegion(location.latitude, location.longitude)) {
          setMapCenter([location.latitude, location.longitude]);
          setMapZoom(16);
        }
      },
      (error) => {
        console.warn('Erro ao obter localização:', error.message);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutos
      }
    );
  };

  /**
   * Verifica se a localização está na região do DF
   */
  const isInDFRegion = (lat, lng) => {
    // Bounds aproximados do Distrito Federal
    const dfBounds = {
      north: -15.4,
      south: -16.1,
      east: -47.2,
      west: -48.4
    };
    
    return lat >= dfBounds.south && lat <= dfBounds.north &&
           lng >= dfBounds.west && lng <= dfBounds.east;
  };

  /**
   * Manipula clique em parada no mapa
   */
  const handleBusStopClick = (parada) => {
    console.log('Parada selecionada:', parada);
    // Aqui poderia abrir um modal com detalhes da parada
  };

  return (
    <div 
      className="map-page"
      style={{
        paddingTop: '50px', /* Este é o valor que realmente controla o espaçamento */
        marginTop: '20px'
      }}
    >
      {/* Header principal da aplicação */}
      <Header showSearch={false} />

      {/* Área do mapa - tela completa */}
      <div 
        className="map-container"
        style={{
          height: 'calc(100vh - 140px)' /* Esta altura deve sempre ser: 100vh - (paddingTop + marginTop) */
        }}
      >
        <MapView
          center={mapCenter}
          zoom={mapZoom}
          height="100%"
          onBusStopClick={handleBusStopClick}
          userLocation={userLocation}
          showUserLocation={true}
        />
      </div>
    </div>
  );
}

export default MapPage; 
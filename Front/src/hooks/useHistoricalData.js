// useHistoricalData.js

import { useState, useEffect } from 'react';

const useHistoricalData = (selectedCrypto, timeframe, removeEurSuffix, setError) => {
  const [historicalData, setHistoricalData] = useState([]);

  useEffect(() => {
    const getHistoricalData = async () => {
      if (selectedCrypto && timeframe) {
        const data = await fetchHistoricalData(selectedCrypto.asset, timeframe);
        if (data) {
          setHistoricalData(data);
        }
      }
    };

    getHistoricalData();
  }, [selectedCrypto, timeframe]);

  // Fonction pour récupérer les données historiques
  const fetchHistoricalData = async (asset, period) => {
    const assetWithoutEur = removeEurSuffix(asset);
    console.log(`Fetching historical data for asset: ${assetWithoutEur}EUR, period: ${period}`);

    try {
      const response = await fetch(
        `http://localhost:8080/api/prices/${assetWithoutEur}EUR/history?period=${period}`
      );
      if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erreur lors du chargement des données historiques:', error);
      setError('Erreur lors du chargement des données historiques');
      return null;
    }
  };

  return historicalData;
};

export default useHistoricalData;

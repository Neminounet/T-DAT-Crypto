import React, { useState, useEffect } from 'react';
import './CryptoItem.css';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS } from 'chart.js/auto';

const CryptoItem = ({ crypto, onClick, removeEurSuffix, assetIcons, assetNames }) => {
  const [historicalData, setHistoricalData] = useState([]);
  const [priceChange, setPriceChange] = useState(null); // Pour déterminer la variation du prix
  const assetSymbol = removeEurSuffix(crypto.asset);
  const iconPath = assetIcons[assetSymbol] || '/icons/default.png';
  const assetName = assetNames[assetSymbol] || assetSymbol;

  // URL pour récupérer les données historiques
  const HISTORY_API_URL = `http://localhost:8080/api/prices/${crypto.asset}/history?period=1m`;

  useEffect(() => {
    const fetchHistoricalData = async () => {
      try {
        const response = await fetch(HISTORY_API_URL);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
        const data = await response.json();
        setHistoricalData(data);

        // Calculer la variation du prix sur le mois
        if (data.length > 1) {
          const firstPrice = data[0].price;
          const lastPrice = data[data.length - 1].price;
          const change = ((lastPrice - firstPrice) / firstPrice) * 100;
          setPriceChange(change);
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des données historiques:', error);
      }
    };

    fetchHistoricalData();
  }, [HISTORY_API_URL]);

  // Configurer les données et options du graphique
  const chartData = {
    labels: historicalData.map((entry) => entry.bucket),
    datasets: [
      {
        data: historicalData.map((entry) => entry.price),
        borderColor: priceChange > 0 ? '#4CAF50' : '#FF5733',
        borderWidth: 2,
        fill: false,
        pointRadius: 0, // Pas de points individuels
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // Pas de légende
      },
      tooltip: {
        enabled: false, // Désactiver les info-bulles
      },
    },
    scales: {
      x: {
        display: false, // Masquer l'axe des X
      },
      y: {
        display: false, // Masquer l'axe des Y
      },
    },
  };

  // Calculer la classe de variation du prix (positive ou négative)
  const priceClass = crypto.price_change_percent > 0 ? 'positive' : 'negative';

  // Déterminer l'icône de flèche
  const arrowIcon =
    priceChange > 0 ? (
      <span className="price-arrow">&#9650;</span> // Flèche vers le haut
    ) : (
      <span className="price-arrow">&#9660;</span> // Flèche vers le bas
    );

  return (
    <div className="crypto-item" onClick={() => onClick(crypto)}>
      <div className="crypto-icon-container">
        <img src={iconPath} alt={assetSymbol} className="crypto-icon" />
      </div>
      <div className="crypto-content">
        <div className="crypto-symbol">{assetSymbol} ⇄ EUR</div>
        <div className="crypto-price">
          {crypto.price ? `${parseFloat(crypto.price).toFixed(2)} €` : 'Chargement...'}
        </div>
        <div className={`crypto-price-change ${priceClass}`}>
          {crypto.price_change_percent ? `${parseFloat(crypto.price_change_percent).toFixed(2)}%` : ''}
          {arrowIcon}
        </div>
      </div>
      <div className="crypto-chart">
        {historicalData.length > 0 ? (
          <Line data={chartData} options={chartOptions} />
        ) : (
          <div className="chart-placeholder">Chargement du graphique...</div>
        )}
      </div>
    </div>
  );
};

export default CryptoItem;

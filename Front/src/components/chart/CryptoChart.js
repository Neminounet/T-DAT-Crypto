// CryptoChart.js

import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const CryptoChart = ({ data, assetName, timeframe }) => {
  if (!data || data.length === 0) {
    return <div>Chargement du graphique...</div>;
  }

  // Trier les données par date
  const sortedData = [...data].sort((a, b) => new Date(a.bucket) - new Date(b.bucket));

  // Préparer les données pour le graphique
  const chartData = {
    labels: sortedData.map((point) => new Date(point.bucket)),
    datasets: [
      {
        label: `${assetName} Prix`,
        data: sortedData.map((point) => point.price),
        fill: true, // Option fill activée
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
      },
    ],
  };

  // Options du graphique
  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: false, // Ne pas afficher la légende
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: getTimeUnit(timeframe),
          tooltipFormat: 'P',
          displayFormats: {
            hour: 'dd MMM HH:mm',
            day: 'dd MMM',
            month: 'MMM yyyy',
          },
        },
        title: {
          display: true,
          text: 'Date',
        },
      },
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Prix (€)',
        },
        ticks: {
          callback: function(value) {
            return value + ' €';
          },
        },
      },
    },
  };

  return <Line data={chartData} options={options} />;
};

// Fonction pour déterminer l'unité de temps en fonction de la période
const getTimeUnit = (timeframe) => {
  switch (timeframe) {
    case '1d':
      return 'hour';
    case '1w':
    case '1m':
      return 'day';
    case '3m':
    case '6m':
      return 'month';
    case '1y':
      return 'month';
    default:
      return 'day';
  }
};

export default CryptoChart;

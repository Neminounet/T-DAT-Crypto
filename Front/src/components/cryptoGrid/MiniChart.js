
// MiniChart.js

import React, { useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import Chart from 'chart.js/auto';

const MiniChart = ({ asset }) => {
  // Dummy data for illustration
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: asset,
        data: [10, 20, 15, 25, 30, 20], // Replace this with real data
        fill: false,
        borderColor: '#8E44AD',
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        display: false,
      },
    },
  };

  return (
    <div style={{ width: '100%', height: '80px' }}>
      <Line data={data} options={options} />
    </div>
  );
};

export default MiniChart;

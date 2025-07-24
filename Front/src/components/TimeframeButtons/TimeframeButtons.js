// TimeframeButtons.js

import React from 'react';

const TimeframeButtons = ({ onChange }) => {
  const timeframes = ['1d', '1w', '1m', '3m', '6m', '1y'];

  return (
    <div className="timeframe-buttons">
      {timeframes.map((timeframe) => (
        <button key={timeframe} onClick={() => onChange(timeframe)}>
          {timeframe}
        </button>
      ))}
    </div>
  );
};

export default TimeframeButtons;

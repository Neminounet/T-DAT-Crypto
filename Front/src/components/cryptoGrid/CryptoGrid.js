import React, { useState, useEffect, useRef } from 'react';
import './CryptoGrid.css';
import CryptoChart from '../chart/CryptoChart';
import CryptoItem from './CryptoItem';
import TimeframeButtons from '../TimeframeButtons/TimeframeButtons';
import useHistoricalData from '../../hooks/useHistoricalData';
import useWebSocket from '../../hooks/useWebSocket';

const LATEST_PRICES_URL = 'http://localhost:8080/api/prices/latest';

const DEFAULT_CRYPTO = 'BTCEUR';
const DEFAULT_TIMEFRAME = '1m';

const CryptoGrid = () => {
  const [cryptoData, setCryptoData] = useState([]);
  const [selectedCrypto, setSelectedCrypto] = useState(null);
  const [timeframe, setTimeframe] = useState(DEFAULT_TIMEFRAME);
  const [error, setError] = useState(null);
  const gridRef = useRef(null);

  const removeEurSuffix = (assetName) => {
    return assetName.replace(/EUR$/, '');
  };

  const assetIcons = {
    BTC: '/icons/btc.png',
    ETH: '/icons/eth.png',
    BNB: '/icons/bnb.png',
    DOGE: '/icons/doge.png',
    LTC: '/icons/ltc.png',
    XRP: '/icons/xrp.png',
    XLM: '/icons/xlm.png',
    TRX: '/icons/trx.png',
    SOL: '/icons/sol.png',
    ADA: '/icons/ada.png',
  };

  const assetNames = {
    BTC: 'Bitcoin',
    ETH: 'Ethereum',
    BNB: 'Binance Coin',
    DOGE: 'Dogecoin',
    LTC: 'Litecoin',
    XRP: 'Ripple',
    XLM: 'Stellar',
    TRX: 'Tron',
    SOL: 'Solana',
    ADA: 'Cardano',
  };

  useEffect(() => {
    const fetchInitialPrices = async () => {
      try {
        const response = await fetch(LATEST_PRICES_URL);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
        const data = await response.json();
        setCryptoData(data);

        const defaultCrypto = data.find((crypto) => crypto.asset === DEFAULT_CRYPTO);
        setSelectedCrypto(defaultCrypto);
      } catch (error) {
        setError('Erreur lors du chargement des données initiales');
      }
    };

    fetchInitialPrices();
  }, []);

  useWebSocket(setCryptoData, setError);
  const historicalData = useHistoricalData(selectedCrypto, timeframe, removeEurSuffix, setError);

  const handleCryptoClick = (crypto) => {
    setSelectedCrypto(crypto);
  };

  const handleTimeframeChange = (newTimeframe) => {
    setTimeframe(newTimeframe);
  };

  const scrollAmount = gridRef.current ? gridRef.current.offsetWidth * 0.8 : 0;

  const scrollRight = () => {
    if (gridRef.current) {
      gridRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  const scrollLeft = () => {
    if (gridRef.current) {
      gridRef.current.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    }
  };

  if (error) return <div>{error}</div>;

  const assetSymbol = selectedCrypto ? removeEurSuffix(selectedCrypto.asset) : '';
  const assetName = assetNames[assetSymbol] || '';

  return (
    <>
      <div className="banner-container">
        <img
          src="/images/BLOG-2099x600-Crypto-da-kuk-iStock-by-Getty-Images-iStock-1317587887.jpg"
          alt="Crypto banner"
          className="crypto-banner"
        />
        <div className="banner-text">
          <h1>Cryptocurrency Information</h1>
          <h2>Explore real-time data of the top 10 cryptocurrencies.</h2>
        </div>
      </div>
      <h1>Informations générales sur les 10 principales cryptomonnaies</h1>
      <div className="crypto-container">
        <div
          className="scroll-arrow scroll-arrow-left"
          onClick={scrollLeft}
          role="button"
          aria-label="Défiler vers la gauche"
        >
          &#10094;
        </div>
        <div className="crypto-grid" ref={gridRef}>
          {cryptoData.map((crypto, index) => (
            <CryptoItem
              key={index}
              crypto={crypto}
              onClick={handleCryptoClick}
              removeEurSuffix={removeEurSuffix}
              assetIcons={assetIcons}
              assetNames={assetNames}
            />
          ))}
        </div>
        <div
          className="scroll-arrow scroll-arrow-right"
          onClick={scrollRight}
          role="button"
          aria-label="Défiler vers la droite"
        >
          &#10095;
        </div>
      </div>
      {selectedCrypto && (
        <>
          <h1>COURS DE {assetName.toUpperCase()}</h1>
          <h2>Représentation graphique des évaluations de prix des cryptomonnaies</h2>
          <TimeframeButtons onChange={handleTimeframeChange} />

          <div className="chart-container">
            <CryptoChart data={historicalData} assetName={assetName} timeframe={timeframe} />
          </div>
        </>
      )}
    </>
  );
};

export default CryptoGrid;

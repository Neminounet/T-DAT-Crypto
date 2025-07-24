import React from 'react';
import { Routes, Route } from 'react-router-dom';
import NavBar from './components/navBar/NavBar';
import Home from './components/cryptoGrid/CryptoGrid';
import RSSFeed from './components/rssFeed/RSSFeed';
import GoogleTrends from './components/GoogleTrends';

const App = () => {
  return (
    <div>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/rss" element={<RSSFeed />} />
        <Route path="/trends" element={<GoogleTrends />} />
      </Routes>
    </div>
  );
};

export default App;

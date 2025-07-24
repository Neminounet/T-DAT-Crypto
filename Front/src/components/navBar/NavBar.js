import React from 'react';
import { Link } from 'react-router-dom';
import './NavBar.css';

const NavBar = () => {
  return (
    <nav id="navbar">
      <div className="logo-container">
        <img
          src="/images/facebook_profile_image.png"
          alt="logo"
          className="logo-image"
        />
        <label className="logo">Crypto VIZ</label>
      </div>
      <ul id="ulNav">
        <li id="listNav">
          <Link id="lienNav" to="/">
            Home
          </Link>
        </li>
        <li id="listNav">
          <Link id="lienNav" to="/rss">
            Flux RSS
          </Link>
        </li>
        <li id="listNav">
          <Link id="lienNav" to="/trends">
            Google Trends
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default NavBar;

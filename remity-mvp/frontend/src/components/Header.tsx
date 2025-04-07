import React from 'react';
import './Header.css'; // We'll create this CSS file

const Header: React.FC = () => {
  // TODO: Implement actual navigation logic (e.g., using react-router-dom Link)
  // TODO: Implement actual auth logic (show user info or login/signup)
  const isLoggedIn = false; // Placeholder

  return (
    <header className="app-header">
      <div className="header-container">
        <div className="logo">Remity.io</div>
        <nav className="main-nav">
          <ul>
            <li><a href="#features">Features</a></li>
            <li><a href="#calculator">Calculator</a></li>
            <li><a href="/help">Help</a></li> {/* Example link */}
          </ul>
        </nav>
        <div className="auth-buttons">
          {isLoggedIn ? (
            <button className="btn btn-secondary">My Account</button>
          ) : (
            <>
              <button className="btn btn-secondary">Log In</button>
              <button className="btn btn-primary">Sign Up</button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;

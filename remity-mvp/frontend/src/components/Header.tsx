import React from 'react';
import { Link, useNavigate } from 'react-router-dom'; // Import Link and useNavigate
import { useAuth } from '../contexts/AuthContext'; // Import useAuth hook
import './Header.css';

const Header: React.FC = () => {
  const { isAuthenticated, user, logout, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/'); // Redirect to homepage after logout
  };

  return (
    <header className="app-header">
      <div className="header-container">
        <div className="logo"><Link to="/">Remity.io</Link></div>
        <nav className="main-nav">
          <ul>
            {/* Use Link for internal navigation */}
            <li><Link to="/#features">Features</Link></li>
            <li><Link to="/#calculator">Calculator</Link></li>
            <li><Link to="/help">Help</Link></li>
            {/* Show Admin link only if user is admin */}
            {isAuthenticated && user?.is_superuser && (
              <li><Link to="/admin">Admin Panel</Link></li>
            )}
             {/* Show Dashboard/History link only if user is logged in */}
            {isAuthenticated && !user?.is_superuser && (
              <li><Link to="/history">History</Link></li> // Link to history for now
              // <li><Link to="/dashboard">Dashboard</Link></li> // Or Dashboard
            )}
          </ul>
        </nav>
        <div className="auth-buttons">
          {isLoading ? (
            <span>Loading...</span> // Show loading state
          ) : isAuthenticated && user ? (
             <>
              <span className="user-greeting">Hi, {user.full_name || user.email}!</span>
              <button onClick={handleLogout} className="btn btn-secondary">Log Out</button>
             </>
          ) : (
            <>
              <Link to="/login"><button className="btn btn-secondary">Log In</button></Link>
              <Link to="/register"><button className="btn btn-primary">Sign Up</button></Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;

import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Header.css';

export default function Header() {
  const { isAuthenticated, user, logout } = useAuth();
  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link to="/" className="brand">Remity</Link>
        <nav className="nav">
          {isAuthenticated ? (
            <>
              <span className="nav-link" style={{opacity:0.8}}>Hi, {user?.full_name?.split(' ')[0] || 'User'}</span>
              <Link to={user?.is_superuser ? '/admin' : '/dashboard'} className="nav-link">{user?.is_superuser ? 'Admin' : 'Dashboard'}</Link>
              <button className="nav-cta" onClick={logout}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Log in</Link>
              <Link to="/register" className="nav-cta">Create account</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

import { Link } from 'react-router-dom';
import './Header.css';

export default function Header() {
  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link to="/" className="brand">Remity</Link>
        <nav className="nav">
          <Link to="/login" className="nav-link">Log in</Link>
          <Link to="/register" className="nav-cta">Create account</Link>
        </nav>
      </div>
    </header>
  );
}

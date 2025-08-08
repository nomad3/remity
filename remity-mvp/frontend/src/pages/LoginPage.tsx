import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { login } from '../services/api';
import './Auth.css';

const LoginPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login: authLogin, fetchUser } = useAuth();
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await login(email, password);
            authLogin(response.data.access_token);
            await fetchUser();
            const base = (process.env.REACT_APP_API_URL || (window.location.hostname.endsWith('remity.io') ? 'https://api.remity.io/api/v1' : 'http://localhost:8001/api/v1'));
            const userResponse = await fetch(base + '/users/me', {
                headers: { 'Authorization': `Bearer ${response.data.access_token}` }
            });
            if (userResponse.ok) {
                const userData = await userResponse.json();
                if (userData.is_superuser) navigate('/admin'); else navigate('/dashboard');
            } else {
                navigate('/dashboard');
            }
        } catch (error) {
            console.error('Login failed', error);
            alert('Login failed. Please check credentials.');
        }
    };

    const quickFill = (role: 'admin'|'operator'|'user') => {
        if (role === 'admin') { setEmail('admin@remity.io'); setPassword('Test12345!'); }
        if (role === 'operator') { setEmail('operator@remity.io'); setPassword('Test12345!'); }
        if (role === 'user') { setEmail('user@remity.io'); setPassword('Test12345!'); }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h2>Welcome back</h2>
                <div style={{display:'flex', gap:8, marginBottom:12}}>
                  <button className="auth-button" onClick={() => quickFill('admin')}>Admin</button>
                  <button className="auth-button" onClick={() => quickFill('operator')}>Operator</button>
                  <button className="auth-button" onClick={() => quickFill('user')}>User</button>
                </div>
                <form onSubmit={handleLogin}>
                    <div className="input-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="input-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="auth-button">Log in</button>
                </form>
                <p>
                    Don't have an account? <Link to="/register">Sign up</Link>
                </p>
            </div>
        </div>
    );
};

export default LoginPage;

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../services/api';
// TODO: Add styling

const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState(''); // Optional
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setIsLoading(true);
    try {
      const payload = { email, password, full_name: fullName || undefined };
      await apiClient.post('/auth/register', payload);
      // Optionally auto-login or redirect to login page
      navigate('/login?registered=true'); // Redirect to login after registration
    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.detail) {
         // Try to show specific error from backend
         if (typeof err.response.data.detail === 'string' && err.response.data.detail.includes("already exists")) {
             setError("An account with this email already exists.");
         } else {
             setError("Registration failed. Please try again.");
         }
      } else {
        setError("Registration failed. Please try again.");
      }
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '50px', maxWidth: '400px', margin: 'auto' }}>
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="email">Email:</label><br />
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
         <div style={{ marginBottom: '15px' }}>
          <label htmlFor="fullName">Full Name (Optional):</label><br />
          <input
            type="text"
            id="fullName"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="password">Password:</label><br />
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="confirmPassword">Confirm Password:</label><br />
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" disabled={isLoading} className="btn btn-primary" style={{ width: '100%' }}>
          {isLoading ? 'Registering...' : 'Sign Up'}
        </button>
      </form>
       <p style={{ marginTop: '20px', textAlign: 'center' }}>
        Already have an account? <Link to="/login">Log In</Link>
      </p>
    </div>
  );
};

export default RegisterPage;

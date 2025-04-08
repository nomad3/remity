import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import apiClient from '../services/api'; // Import the api client
// TODO: Define proper User type matching backend schema
interface User {
  id: string;
  email: string;
  full_name?: string;
  is_superuser: boolean;
  // Add other fields as needed (kyc_status, etc.)
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  isLoading: boolean; // To handle initial auth check
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  // register: (userData) => Promise<void>; // Add register function later
}

// Export the context
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true); // Start loading

  // Check for existing token on initial load
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('accessToken'); // Simple storage example
      if (token) {
        setAccessToken(token);
        try {
          // Verify token by fetching user profile
          const response = await apiClient.get('/users/me'); // Assumes GET /users/me requires valid token
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          console.error("Token validation failed:", error);
          localStorage.removeItem('accessToken'); // Clear invalid token
          setAccessToken(null);
        }
      }
      setIsLoading(false); // Finished loading auth state
    };
    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // Use FormData for OAuth2PasswordRequestForm
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await apiClient.post('/auth/login', formData, {
         headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const { access_token, refresh_token } = response.data; // Assuming backend returns refresh token too

      localStorage.setItem('accessToken', access_token); // Store token (simple example)
      // TODO: Store refresh token securely if needed for automatic refresh
      setAccessToken(access_token);
      setIsAuthenticated(true);

      // Fetch user profile after successful login
      const userResponse = await apiClient.get('/users/me');
      setUser(userResponse.data);

    } catch (error) {
      console.error("Login failed:", error);
      // Re-throw or handle error display
      throw error;
    } finally {
        setIsLoading(false);
    }
  };

  const logout = () => {
    // TODO: Call backend logout endpoint if implemented (e.g., to invalidate refresh token)
    localStorage.removeItem('accessToken');
    // TODO: Remove refresh token if stored
    setAccessToken(null);
    setUser(null);
    setIsAuthenticated(false);
    // Optionally redirect to homepage or login page
    // window.location.href = '/';
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, accessToken, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

import axios from 'axios';

// Get the API base URL from environment variables (defined in .env.local or docker-compose)
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api/v1'; // Default fallback

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add the auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    // Retrieve the token from local storage (or context/state management)
    const token = localStorage.getItem('accessToken'); // Simple example, use secure storage/context
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Optional: Add response interceptor for handling global errors (e.g., 401 Unauthorized)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Handle unauthorized access, e.g., redirect to login, clear tokens
      console.error("Unauthorized access - 401");
      // Example: Clear token and redirect (implement logout logic properly)
      // localStorage.removeItem('accessToken');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);


export default apiClient;

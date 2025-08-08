import axios from 'axios';

const apiBaseURL = ((): string => {
    const envUrl = process.env.REACT_APP_API_URL;
    if (envUrl) return envUrl;
    // Fallbacks by hostname
    if (typeof window !== 'undefined') {
        const host = window.location.hostname;
        if (host.endsWith('remity.io')) return 'https://api.remity.io/api/v1';
    }
    return 'http://localhost:8001/api/v1';
})();

const apiClient = axios.create({
    baseURL: apiBaseURL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Attach Authorization header from localStorage if present
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        (config.headers as any).Authorization = `Bearer ${token}`;
    }
    return config;
});

export const login = (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return apiClient.post('/auth/login/access-token', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });
};

export const register = (fullName: string, email: string, password: string) => {
    return apiClient.post('/users/', {
        full_name: fullName,
        email,
        password,
    });
};

export const getTransactions = () => {
    return apiClient.get('/transactions/');
};

export const createTransaction = (payload: any) => {
    return apiClient.post('/transactions/', payload);
};

export const getCurrentUser = () => {
    return apiClient.get('/users/me');
};

export const getUsers = () => {
    return apiClient.get('/users/');
};

export const updateTransaction = (transactionId: number, data: any) => {
    return apiClient.patch(`/transactions/${transactionId}`, data);
};

// Recipients
export const listRecipients = () => apiClient.get('/recipients/');
export const createRecipient = (recipient: any) => apiClient.post('/recipients/', recipient);

// Admin endpoints
export const adminListTransactions = () => apiClient.get('/transactions/admin');
export const adminUpdateTransaction = (id: number, data: any) => apiClient.patch(`/transactions/${id}/admin`, data);

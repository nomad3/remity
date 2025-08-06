import axios from 'axios';

const apiClient = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
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

export const createTransaction = (transactionData: any) => {
    return apiClient.post('/transactions/', transactionData);
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

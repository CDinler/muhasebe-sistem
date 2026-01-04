/**
 * Axios client with interceptors for standardized error handling
 */
import axios, { AxiosError, AxiosResponse } from 'axios';
import { ApiError } from '../types/api.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Standardized error handling (P0 improvement)
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ApiError>) => {
    const apiError: ApiError = {
      success: false,
      error_code: error.response?.data?.error_code || 'UNKNOWN_ERROR',
      message: error.response?.data?.message || 'Bir hata oluştu',
      details: error.response?.data?.details,
    };

    // Handle specific error codes
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }

    return Promise.reject(apiError);
  }
);

export default apiClient;

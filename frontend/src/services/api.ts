import axios from 'axios';

const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL || ''}/api/v2`,
  headers: {
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': 'application/json',
  },
  paramsSerializer: {
    serialize: (params) => {
      // FastAPI için array parametrelerini doğru formatta gönder
      // account_filter: ['120', '320'] -> account_filter=120&account_filter=320
      const parts: string[] = [];
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach((item) => {
            parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(item)}`);
          });
        } else if (value !== undefined && value !== null) {
          parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
        }
      });
      return parts.join('&');
    }
  }
});

// Request interceptor
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

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export { apiClient };
export default apiClient;

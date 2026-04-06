import axios from 'axios';

export const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

axiosClient.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err),
);

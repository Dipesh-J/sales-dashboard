import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export const getSampleData = async (rows = 10) => {
  const response = await api.get(`/api/data/sample`, { params: { rows } });
  return response.data;
};

export default api;

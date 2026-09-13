/**
 * Modul pemanggilan API menggunakan Axios untuk Frontend React JS.
 * Rute sesuai dengan Blueprint:
 * - POST /api/v1/analyze
 * - GET  /api/v1/download-csv
 * - GET  /api/v1/health
 * - POST /api/v1/predict-single
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Timeout 60 detik untuk dataset ulasan berukuran besar
});

export const api = {
  /**
   * Mengunggah fail CSV ulasan film untuk dianalisis
   * @param {File} file - Berkas file .csv ulasan
   * @param {Function} onUploadProgress - Callback progres upload (opsional)
   * @returns {Promise<Object>} Respons JSON sesuai kontrak blueprint
   */
  analyzeCSV: async (file, onUploadProgress = null) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },

  /**
   * Mengunduh berkas CSV hasil analisis sentimen
   * @returns {Promise<Blob>} Berkas CSV blob untuk diunduh langsung di browser
   */
  downloadCSV: async () => {
    const response = await apiClient.get('/download-csv', {
      responseType: 'blob',
    });
    
    // Otomatis men-trigger download di browser
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'hasil_analisis_sentimen_na_willa.csv');
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    return response.data;
  },

  /**
   * Mengecek kesehatan backend dan status model AI
   */
  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Menguji inferensi sentimen pada satu teks ulasan
   * @param {string} text - Kalimat ulasan ulasan
   */
  predictSingleReview: async (text) => {
    const response = await apiClient.post('/predict-single', { text });
    return response.data;
  },
};

export default api;

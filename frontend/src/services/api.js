import axios from 'axios';

const API_BASE = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Module 1: Upload & status
  uploadContract: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  getContractStatus: async (contractId) => {
    const res = await apiClient.get(`/upload/${contractId}/status`);
    return res.data;
  },

  // Module 2: Clause extraction
  extractClauses: async (contractId, userRole = 'General') => {
    const res = await apiClient.post(`/extract-clauses/${contractId}?user_role=${userRole}`);
    return res.data;
  },

  getClauses: async (contractId) => {
    const res = await apiClient.get(`/extract-clauses/${contractId}`);
    return res.data;
  },

  // Modules 3-5: Risk analysis & user context
  runRiskAnalysis: async (contractId, userRole = 'General') => {
    const res = await apiClient.post('/risk-analysis', {
      contract_id: contractId,
      user_role: userRole,
    });
    return res.data;
  },

  getRiskAnalysis: async (contractId) => {
    const res = await apiClient.get(`/risk-analysis/${contractId}`);
    return res.data;
  },

  // Module 6: What-If analysis
  runWhatIf: async (contractId, query, userRole = 'General') => {
    const res = await apiClient.post('/what-if', {
      contract_id: contractId,
      query,
      user_role: userRole,
    });
    return res.data;
  },

  // Module 8: Obligations
  extractObligations: async (contractId) => {
    const res = await apiClient.post(`/obligations/${contractId}`);
    return res.data;
  },

  getObligations: async (contractId) => {
    const res = await apiClient.get(`/obligations/${contractId}`);
    return res.data;
  },

  // Module 9: Contract comparison
  compareContracts: async (contractIdA, contractIdB) => {
    const res = await apiClient.post('/compare', {
      contract_id_a: contractIdA,
      contract_id_b: contractIdB,
    });
    return res.data;
  },

  // Module 10: Reports
  generateReport: async (contractId, userRole = 'General', format = 'json') => {
    const res = await apiClient.post('/report', {
      contract_id: contractId,
      user_role: userRole,
      format,
    });
    return res.data;
  },

  getDownloadUrl: (contractId, reportId) => {
    return `/api/v1/report/${contractId}/download?report_id=${reportId}`;
  },
};

export default api;

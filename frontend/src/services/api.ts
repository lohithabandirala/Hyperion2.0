import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Demo Data
export const loadDemoData = () => api.post('/demo/load');

// Projects
export const getProjects = () => api.get('/projects/');
export const createProject = (title: string, description: string = "") => 
  api.post('/projects/', { title, description });
export const deleteProject = (id: number) => api.delete(`/projects/${id}`);

// Sources
export const uploadSource = (projectId: number, file: File) => {
  const formData = new FormData();
  formData.append('project_id', projectId.toString());
  formData.append('file', file);
  return api.post('/sources/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const createSourceText = (projectId: number, title: string, content: string) =>
  api.post('/sources/text', { project_id: projectId, title, content });

export const createSourceUrl = (projectId: number, url: string) =>
  api.post('/sources/url', { project_id: projectId, url });

export const getSource = (id: number) => api.get(`/sources/${id}`);

// Transformations
export const createTransformation = (data: {
  source_id: number;
  audience: string;
  tone: string;
  language: string;
  detail_level: string;
  objective: string;
  outputs: string[];
}) => api.post('/transform/', data);

export const getTransformation = (id: number) => api.get(`/transform/${id}`);
export const getTransformationStatus = (id: number) => api.get(`/transform/${id}/status`);
export const getTransformationOutputs = (id: number) => api.get(`/transform/${id}/outputs`);
export const getTransformationFacts = (id: number) => api.get(`/transform/${id}/facts`);

// Outputs & Review
export const getOutput = (id: number) => api.get(`/outputs/${id}`);
export const editOutput = (id: number, content: string, change_description?: string) =>
  api.patch(`/outputs/${id}`, { content, change_description });

export const regenerateOutput = (id: number, instruction?: string, target_tone?: string, target_language?: string) =>
  api.post(`/outputs/${id}/regenerate`, { instruction, target_tone, target_language });

export const approveOutput = (id: number) => api.post(`/outputs/${id}/approve`);
export const rejectOutput = (id: number) => api.post(`/outputs/${id}/reject`);
export const getOutputVersions = (id: number) => api.get(`/outputs/${id}/versions`);
export const rollbackOutputVersion = (id: number, version_id: number) =>
  api.post(`/outputs/${id}/rollback/${version_id}`);

export const getExportUrl = (outputId: number, format: string) =>
  `${API_BASE_URL}/outputs/${outputId}/export/${format}`;

// Provenance & Verification
export const getProvenanceRecord = (provenanceId: string) => api.get(`/provenance/${provenanceId}`);
export const getProvenanceByOutput = (outputId: number) => api.get(`/provenance/output/${outputId}`);
export const getPublicKey = () => api.get('/provenance/public-key');
export const verifyUploadedFile = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/provenance/verify-file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};
export const getProvenanceQrUrl = (provenanceId: string) =>
  `${API_BASE_URL}/provenance/${provenanceId}/qr`;

export default api;

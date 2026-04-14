import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000,
});

export async function analyzeText(text) {
  const response = await apiClient.post('/analyze-text', { text });
  return response.data;
}

export async function analyzeImage(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/analyze-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function generateFIR(payload) {
  const formData = new FormData();
  formData.append('username', payload.username);
  formData.append('incident_description', payload.incidentDescription);

  if (payload.evidenceNotes) {
    formData.append('evidence_notes', payload.evidenceNotes);
  }
  if (payload.evidenceUrl) {
    formData.append('evidence_url', payload.evidenceUrl);
  }
  if (payload.evidencePublicId) {
    formData.append('evidence_public_id', payload.evidencePublicId);
  }
  if (payload.evidenceFile) {
    formData.append('evidence_file', payload.evidenceFile);
  }

  const response = await apiClient.post('/generate-fir', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function downloadFIR(firId) {
  return apiClient.get('/download-fir', {
    params: { fir_id: firId },
    responseType: 'blob',
  });
}

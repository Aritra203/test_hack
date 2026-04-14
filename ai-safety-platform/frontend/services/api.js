import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  timeout: 120000,
});

export async function analyzeText(payload) {
  const response = await api.post("/analyze-text", payload);
  return response.data;
}

export async function analyzeImage(file, subjectIsMinor = false, languageHint = "") {
  const form = new FormData();
  form.append("file", file);
  form.append("subject_is_minor", String(subjectIsMinor));
  if (languageHint) {
    form.append("language_hint", languageHint);
  }
  const response = await api.post("/analyze-image", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function generateFir(payload) {
  const response = await api.post("/generate-fir", payload);
  return response.data;
}

export async function getFirJob(jobId) {
  const response = await api.get(`/fir-job/${jobId}`);
  return response.data;
}

export async function downloadFir(firId) {
  return api.get("/download-fir", {
    params: { fir_id: firId },
    responseType: "blob",
  });
}

export async function getAnalytics() {
  const response = await api.get("/analytics");
  return response.data;
}


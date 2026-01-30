const API_URL = 'http://localhost:8000';

export const queryRAG = async (query, model) => {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, model })
  });
  return response.json();
};

export const uploadFiles = async (files) => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  
  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData
  });
  return response.json();
};
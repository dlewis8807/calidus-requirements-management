/**
 * API Client Utilities
 * Centralized API calls to the backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Get auth token from localStorage
const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token') || localStorage.getItem('token') || localStorage.getItem('demo_token');
};

// Generic fetch wrapper with auth
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Invalid credentials');
    }

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    return data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token');
    localStorage.removeItem('demo_token');
  },

  getCurrentUser: () => fetchAPI('/api/auth/me'),
};

// Helper to clean params (remove undefined/null values)
const cleanParams = (params?: Record<string, any>): Record<string, string> => {
  if (!params) return {};
  const cleaned: Record<string, string> = {};
  Object.keys(params).forEach(key => {
    const value = params[key];
    if (value !== undefined && value !== null && value !== '') {
      cleaned[key] = String(value);
    }
  });
  return cleaned;
};

// Requirements API
export const requirementsAPI = {
  list: (params?: Record<string, any>) => {
    const cleaned = cleanParams(params);
    const queryString = Object.keys(cleaned).length > 0 ? `?${new URLSearchParams(cleaned).toString()}` : '';
    return fetchAPI(`/api/requirements/${queryString}`);
  },

  get: (id: number) => fetchAPI(`/api/requirements/${id}`),

  stats: () => fetchAPI('/api/requirements/stats'),

  create: (data: any) =>
    fetchAPI('/api/requirements', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: number, data: any) =>
    fetchAPI(`/api/requirements/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    fetchAPI(`/api/requirements/${id}`, {
      method: 'DELETE',
    }),
};

// Test Cases API
export const testCasesAPI = {
  list: (params?: Record<string, any>) => {
    const cleaned = cleanParams(params);
    const queryString = Object.keys(cleaned).length > 0 ? `?${new URLSearchParams(cleaned).toString()}` : '';
    return fetchAPI(`/api/test-cases/${queryString}`);
  },

  get: (id: number) => fetchAPI(`/api/test-cases/${id}`),

  stats: () => fetchAPI('/api/test-cases/stats'),

  execute: (id: number, data: any) =>
    fetchAPI(`/api/test-cases/${id}/execute`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  create: (data: any) =>
    fetchAPI('/api/test-cases', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: number, data: any) =>
    fetchAPI(`/api/test-cases/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    fetchAPI(`/api/test-cases/${id}`, {
      method: 'DELETE',
    }),
};

// Traceability API
export const traceabilityAPI = {
  list: (params?: Record<string, any>) => {
    const cleaned = cleanParams(params);
    const queryString = Object.keys(cleaned).length > 0 ? `?${new URLSearchParams(cleaned).toString()}` : '';
    return fetchAPI(`/api/traceability/${queryString}`);
  },

  get: (id: number) => fetchAPI(`/api/traceability/${id}`),

  matrix: (requirementId: number) => fetchAPI(`/api/traceability/matrix/${requirementId}`),

  report: () => fetchAPI('/api/traceability/report'),

  graph: (params?: Record<string, any>) => {
    const cleaned = cleanParams(params);
    const queryString = Object.keys(cleaned).length > 0 ? `?${new URLSearchParams(cleaned).toString()}` : '';
    return fetchAPI(`/api/traceability/graph${queryString}`);
  },

  orphaned: () => fetchAPI('/api/traceability/orphaned'),

  gaps: (params?: Record<string, any>) => {
    const cleaned = cleanParams(params);
    const queryString = Object.keys(cleaned).length > 0 ? `?${new URLSearchParams(cleaned).toString()}` : '';
    return fetchAPI(`/api/traceability/gaps${queryString}`);
  },

  create: (data: any) =>
    fetchAPI('/api/traceability', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  bulkCreate: (data: any) =>
    fetchAPI('/api/traceability/bulk', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: number, data: any) =>
    fetchAPI(`/api/traceability/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    fetchAPI(`/api/traceability/${id}`, {
      method: 'DELETE',
    }),
};

// Users API (for admin)
export const usersAPI = {
  list: () => fetchAPI('/api/users'),

  get: (id: number) => fetchAPI(`/api/users/${id}`),

  create: (data: any) =>
    fetchAPI('/api/users', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: number, data: any) =>
    fetchAPI(`/api/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    fetchAPI(`/api/users/${id}`, {
      method: 'DELETE',
    }),
};

// Compliance API
export const complianceAPI = {
  overview: () => fetchAPI('/api/compliance/overview'),

  stats: () => fetchAPI('/api/compliance/stats'),

  regulations: () => fetchAPI('/api/compliance/regulations'),

  regulationDetail: (regulationName: string) => {
    const encoded = encodeURIComponent(regulationName);
    return fetchAPI(`/api/compliance/regulations/${encoded}`);
  },

  gaps: (params?: Record<string, any>) => {
    const cleaned = cleanParams(params);
    const queryString = Object.keys(cleaned).length > 0 ? `?${new URLSearchParams(cleaned).toString()}` : '';
    return fetchAPI(`/api/compliance/gaps${queryString}`);
  },
};

/**
 * api.js — HTTP client for Flask backend with session persistence.
 */

const SESSION_KEY = 'risk_platform_session_id';

export function getSessionId() {
  let sid = localStorage.getItem(SESSION_KEY);
  if (!sid) {
    sid = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, sid);
  }
  return sid;
}

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Session-Id': getSessionId(),
    ...(options.headers || {}),
  };
  const res = await fetch(path, { ...options, headers });
  const json = await res.json();
  if (!json.success) {
    throw new Error(json.error || 'Request failed');
  }
  return json.data;
}

export const api = {
  getAssets: () => request('/api/assets'),
  createAsset: (body) => request('/api/assets', { method: 'POST', body: JSON.stringify(body) }),
  deleteAsset: (id) => request(`/api/assets/${id}`, { method: 'DELETE' }),
  getAssetCves: (id) => request(`/api/assets/${id}/cves`),
  getThreats: () => request('/api/threats'),
  createThreat: (body) => request('/api/threats', { method: 'POST', body: JSON.stringify(body) }),
  deleteThreat: (id) => request(`/api/threats/${id}`, { method: 'DELETE' }),
  runAssessment: (orgName) =>
    request('/api/assessment/run', {
      method: 'POST',
      body: JSON.stringify({ org_name: orgName }),
    }),
  getResults: () => request('/api/assessment/results'),
  getNotifications: () => request('/api/assessment/notifications'),
  getCompliance: () => request('/api/compliance'),
  updateCompliance: (body) =>
    request('/api/compliance', { method: 'POST', body: JSON.stringify(body) }),
  downloadReport: (type) => {
    const sid = getSessionId();
    window.open(`/api/reports/${type}?session_id=${sid}`, '_blank');
  },
};

export function severityColor(severity) {
  const map = {
    Critical: 'bg-red-600 text-white',
    High: 'bg-orange-500 text-white',
    Medium: 'bg-yellow-500 text-slate-900',
    Low: 'bg-green-600 text-white',
  };
  return map[severity] || 'bg-slate-400 text-white';
}

export function criticalityColor(c) {
  return severityColor(c);
}

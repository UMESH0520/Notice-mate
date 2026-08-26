/**
 * Thin API client. Every call funnels through `request()` so error handling,
 * offline detection and the "never show a stack trace" rule live in one place.
 */

const BASE = ''; // same origin — FastAPI serves this SPA

export class ApiError extends Error {
  constructor(message, status, offline = false) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.offline = offline;
  }
}

async function request(path, { method = 'GET', body, formData, signal } = {}) {
  const init = { method, signal, headers: {} };
  if (formData) {
    init.body = formData; // let the browser set the multipart boundary
  } else if (body !== undefined) {
    init.headers['Content-Type'] = 'application/json';
    init.body = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(BASE + path, init);
  } catch (err) {
    if (err?.name === 'AbortError') throw err;
    throw new ApiError('offline', 0, true);
  }

  if (res.status === 204) return null;

  let payload = null;
  const text = await res.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = { detail: text };
    }
  }

  if (!res.ok) {
    let detail = payload?.detail;
    if (Array.isArray(detail)) {
      // Pydantic validation errors — surface the first readable message.
      detail = detail[0]?.msg || 'Please check the information you entered.';
    }
    throw new ApiError(detail || 'request_failed', res.status);
  }
  return payload;
}

export const api = {
  health: () => request('/api/health'),

  demoNotices: () => request('/api/demo/notices'),

  createFromDemo: (demoId, sessionId) =>
    request('/api/notices/demo', {
      method: 'POST',
      body: { demo_id: demoId, session_id: sessionId },
    }),

  createFromText: (text, sessionId) =>
    request('/api/notices/text', {
      method: 'POST',
      body: { text, session_id: sessionId },
    }),

  createFromUpload: (file, sessionId) => {
    const fd = new FormData();
    fd.append('file', file);
    if (sessionId) fd.append('session_id', sessionId);
    return request('/api/notices/upload', { method: 'POST', formData: fd });
  },

  analyze: (noticeId, language) =>
    request(`/api/notices/${noticeId}/analyze`, {
      method: 'POST',
      body: { language },
    }),

  getNotice: (noticeId, language = 'en') =>
    request(`/api/notices/${noticeId}?language=${encodeURIComponent(language)}`),

  actionPlan: (noticeId) => request(`/api/notices/${noticeId}/action-plan`),

  setActionState: (noticeId, itemId, state) =>
    request(
      `/api/notices/${noticeId}/action-plan/${itemId}?state=${encodeURIComponent(state)}`,
      { method: 'PATCH' },
    ),

  documents: (noticeId) => request(`/api/notices/${noticeId}/documents`),

  uploadDocument: (noticeId, documentId, file) => {
    const fd = new FormData();
    fd.append('file', file);
    if (documentId) fd.append('document_id', documentId);
    return request(`/api/notices/${noticeId}/documents`, {
      method: 'POST',
      formData: fd,
    });
  },

  setDocumentStatus: (noticeId, documentId, status) =>
    request(`/api/notices/${noticeId}/documents/${documentId}`, {
      method: 'PATCH',
      body: { status },
    }),

  generateResponse: (noticeId, language, extraContext) =>
    request(`/api/notices/${noticeId}/response`, {
      method: 'POST',
      body: { language, extra_context: extraContext || null },
    }),

  saveResponse: (noticeId, content, accept = false) =>
    request(`/api/notices/${noticeId}/response`, {
      method: 'PUT',
      body: { content, accept },
    }),

  getResponse: (noticeId) => request(`/api/notices/${noticeId}/response`),

  submit: (noticeId, confirmed = true) =>
    request(`/api/notices/${noticeId}/submit`, {
      method: 'POST',
      body: { confirmed },
    }),

  submission: (submissionId) => request(`/api/submissions/${submissionId}`),

  status: (noticeId) => request(`/api/notices/${noticeId}/status`),

  research: (noticeId, force = false) =>
    request(`/api/notices/${noticeId}/research?force=${force}`, { method: 'POST' }),

  sources: (noticeId) => request(`/api/notices/${noticeId}/sources`),

  dates: (noticeId) => request(`/api/notices/${noticeId}/dates`),

  eligibility: (noticeId) => request(`/api/notices/${noticeId}/eligibility`),

  roadmap: (noticeId, language = 'en') =>
    request(`/api/notices/${noticeId}/roadmap?language=${encodeURIComponent(language)}`),

  updatePreparation: (noticeId, stepKey, state) =>
    request(`/api/notices/${noticeId}/preparation`, {
      method: 'PUT',
      body: { step_key: stepKey, state },
    }),

  stepHelp: (noticeId, stepId, question, language = 'en') =>
    request(`/api/notices/${noticeId}/roadmap/step-help`, {
      method: 'POST',
      body: { step_id: stepId, question: question || null, language },
    }),
};

export default api;

/**
 * Client-side state, persisted to localStorage so a refresh (or a demo judge
 * reloading the page) never loses the workflow. Only identifiers and the
 * chosen language are stored; the server remains the source of truth.
 */

const KEY = 'noticemate.v1';

const DEFAULTS = {
  sessionId: null,
  language: 'en',
  noticeId: null,
  submissionId: null,
  // ephemeral caches (not required for correctness, just fewer round-trips)
  notice: null,
  analysis: null,
  plan: null,
  documents: null,
  response: null,
  demoNotices: null,
  health: null,
};

const PERSISTED = ['sessionId', 'language', 'noticeId', 'submissionId'];

function randomId() {
  if (crypto?.randomUUID) return crypto.randomUUID();
  return 'sess-' + Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return typeof parsed === 'object' && parsed ? parsed : {};
  } catch {
    return {};
  }
}

export const state = { ...DEFAULTS, ...load() };

if (!state.sessionId) {
  state.sessionId = randomId();
}

function persist() {
  try {
    const slim = {};
    for (const k of PERSISTED) slim[k] = state[k];
    localStorage.setItem(KEY, JSON.stringify(slim));
  } catch {
    /* private-mode or full storage — the app still works, just not resumable */
  }
}

persist();

/** Merge a patch into state and persist the durable subset. */
export function setState(patch) {
  Object.assign(state, patch);
  persist();
  return state;
}

/** Forget the current notice but keep the session and language. */
export function resetNotice() {
  setState({
    noticeId: null,
    submissionId: null,
    notice: null,
    analysis: null,
    plan: null,
    documents: null,
    response: null,
  });
}

export default state;

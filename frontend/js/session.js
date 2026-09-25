// ===================================================
//  session.js — Interview session state management
// ===================================================

/** @type {{ role: string, level: string, focus: string, round: string, questionIndex: number, followupCount: number, messages: Array<{role: string, text: string, isFollowup?: boolean, time: string}>, sessionId: string | null, startedAt: Date | null }} */
const _state = {
  role: '',
  level: 'mid',
  focus: 'all',
  round: 'resume',       // 'resume' | 'technical' | 'hr'
  questionIndex: 0,
  followupCount: 0,
  messages: [],
  sessionId: null,
  startedAt: null,
};

/** @type {{ id: string, role: string, round: string, messageCount: number, createdAt: string }[]} */
let _sessionHistory = [];

// ── Helpers ──────────────────────────────────────────

function _now() {
  const d = new Date();
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function _genId() {
  return 'sess_' + Math.random().toString(36).slice(2, 10);
}

// ── Public API ────────────────────────────────────────

/**
 * Reset session state and start a fresh interview.
 * @param {{ role?: string, level?: string, focus?: string }} options
 */
export function resetSession(options = {}) {
  _state.role          = options.role  || 'Software Developer';
  _state.level         = options.level || 'mid';
  _state.focus         = options.focus || 'all';
  _state.round         = 'resume';
  _state.questionIndex = 0;
  _state.followupCount = 0;
  _state.messages      = [];
  _state.sessionId     = null;   // ✅ FIXED
  _state.startedAt     = new Date();
}

/**
 * Add a message to the session.
 * @param {'ai'|'user'} role
 * @param {string} text
 * @param {{ isFollowup?: boolean }} [meta]
 */
export function addMessage(role, text, meta = {}) {
  _state.messages.push({
    role,
    text,
    isFollowup: !!meta.isFollowup,
    time: _now(),
  });
}

/** Return a shallow copy of all messages */
export function getMessages() {
  return [..._state.messages];
}

/** Return a copy of the current session state */
export function getState() {
  return { ..._state };
}

/** Advance to next round */
export function advanceRound() {
  const rounds = ['resume', 'technical', 'hr'];
  const idx = rounds.indexOf(_state.round);
  if (idx < rounds.length - 1) {
    _state.round = rounds[idx + 1];
    _state.questionIndex = 0;
    _state.followupCount = 0;
    return true;
  }
  return false; // already at last round
}

/** Increment question index */
export function nextQuestion() {
  _state.questionIndex++;
  _state.followupCount = 0;
}

/** Increment follow-up count */
export function incrementFollowup() {
  _state.followupCount++;
}

/** Get follow-up count */
export function getFollowupCount() {
  return _state.followupCount;
}

/** Get current round */
export function getCurrentRound() {
  return _state.round;
}

/** Get question index */
export function getQuestionIndex() {
  return _state.questionIndex;
}

// ── Session History ───────────────────────────────────

/**
 * Save current session to history list (in memory).
 */
export function saveSessionToHistory() {
  if (!_state.sessionId) return;

  const existing = _sessionHistory.findIndex(s => s.id === _state.sessionId);
  const entry = {
    id: _state.sessionId,
    role: _state.role,
    round: _state.round,
    level: _state.level,
    messageCount: _state.messages.length,
    createdAt: _state.startedAt
      ? _state.startedAt.toLocaleDateString([], { month: 'short', day: 'numeric' })
      : 'Today',
  };

  if (existing >= 0) {
    _sessionHistory[existing] = entry;
  } else {
    _sessionHistory.unshift(entry);
  }
}

/** Return all saved sessions */
export function getSessionHistory() {
  return [..._sessionHistory];
}

/** Get current session id */
export function getCurrentSessionId() {
  return _state.sessionId;
}
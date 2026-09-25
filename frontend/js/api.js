const BASE_URL = "http://127.0.0.1:8000/api";

// AUTH
export async function loginUser({ email, password }) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Login failed");
  return data;
}

export async function registerUser({ name, email, password }) {
  const res = await fetch(`${BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Signup failed");
  return data;
}

// ─── START INTERVIEW ─────────────────────────────
export async function startInterview({ role, level, round, resume_text }) {
  const res = await fetch(`${BASE_URL}/interview/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      role,
      level,
      round,
      resume_text
    }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error("Start interview failed");

  return {
    sessionId: data.session_id,
    question: data.question
  };
}

// ─── SEND ANSWER (🔥 FULL FIX) ─────────────────────
export async function sendAnswer(payload) {
  const res = await fetch(`${BASE_URL}/interview/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: payload.sessionId,
      answer: payload.answer,
      question_index: payload.questionIndex,
      followup_count: payload.followupCount,
      round: payload.round,
      role: payload.role
    }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error("Answer failed");

  return {
    response: data.response,
    isFollowup: data.is_followup,   // ✅ match backend
    nextRound: data.next_round,     // 🔥 REQUIRED
    allDone: data.all_done          // 🔥 REQUIRED
  };
}
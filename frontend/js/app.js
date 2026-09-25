// app.js
import { resetSession, addMessage, getMessages, getState, nextQuestion, incrementFollowup, getFollowupCount, getCurrentRound, getQuestionIndex, advanceRound } from './session.js';
import { appendMessage, showTypingIndicator, removeTypingIndicator } from './chat.js';
import { loginUser, registerUser, startInterview, sendAnswer } from './api.js';

// ─── PDF EXTRACTION ───────────────────────────────────
async function extractPdfText(file) {
  const arrayBuffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
  let text = "";
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    text += content.items.map(item => item.str).join(" ") + "\n";
  }
  return text;
}

// ─── STATE ───────────────────────────────────────────
let _sessionId  = null;
let isLoading   = false;
let _resumeText = '';

// ─── BOOT ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);

function init() {
  console.log('HireScope init ✅');
  showPage('auth');
  wireAuth();
  wireInterview();
  wireInput();
  wireResumeUpload();
}

function showPage(page) {
  document.getElementById('auth-page').classList.toggle('hidden', page !== 'auth');
  document.getElementById('main-app').classList.toggle('hidden', page !== 'main');
}

// ─── AUTH ────────────────────────────────────────────
function wireAuth() {
  document.getElementById('login-btn')?.addEventListener('click', doLogin);
  document.getElementById('signup-btn')?.addEventListener('click', doSignup);
  document.getElementById('go-to-signup')?.addEventListener('click', () => swapForm('signup'));
  document.getElementById('go-to-login')?.addEventListener('click', () => swapForm('login'));
  document.querySelectorAll('.toggle-password').forEach(btn =>
    btn.addEventListener('click', () => {
      const el = document.getElementById(btn.dataset.target);
      if (el) el.type = el.type === 'password' ? 'text' : 'password';
    })
  );
}

function swapForm(to) {
  document.getElementById('login-form').classList.toggle('active', to === 'login');
  document.getElementById('signup-form').classList.toggle('active', to === 'signup');
}

async function doLogin() {
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value.trim();
  try {
    const res = await loginUser({ email, password });
    if (!res.success) { toast(res.error || 'Login failed', 'error'); return; }
    const name = res.user?.name || email.split('@')[0];
    document.getElementById('profile-name').textContent   = name;
    document.getElementById('profile-avatar').textContent = name[0].toUpperCase();
    showPage('main');
  } catch { toast('Login failed — is backend running?', 'error'); }
}

async function doSignup() {
  const name     = document.getElementById('signup-name').value.trim();
  const email    = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value.trim();
  try {
    const res = await registerUser({ name, email, password });
    if (!res.success) { toast(res.error || 'Signup failed', 'error'); return; }
    toast('Account created! Sign in now.', 'success');
    swapForm('login');
  } catch { toast('Signup failed — is backend running?', 'error'); }
}

// ─── RESUME UPLOAD ───────────────────────────────────
function wireResumeUpload() {
  const input = document.getElementById('resume-file-input');
  if (!input) return;
  input.addEventListener('change', async () => {
    const file = input.files[0];
    if (!file) return;
    try {
      _resumeText = await extractPdfText(file);
      const zone  = document.getElementById('resume-upload-zone');
      const label = document.getElementById('resume-upload-label');
      zone?.classList.add('has-file');
      if (label) label.textContent = `✓ ${file.name}`;
      toast('Resume loaded!', 'success');
    } catch (e) {
      toast('Could not read PDF', 'error');
    }
  });

  const zone = document.getElementById('resume-upload-zone');
  zone?.addEventListener('click', () => input.click());
  zone?.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone?.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone?.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file?.type === 'application/pdf') { input.files = e.dataTransfer.files; input.dispatchEvent(new Event('change')); }
    else toast('Please upload a PDF', 'error');
  });
}

// ─── INTERVIEW SETUP ─────────────────────────────────
function wireInterview() {
  document.getElementById('new-interview-btn')?.addEventListener('click', openModal);

  document.querySelectorAll('.role-card').forEach(card =>
    card.addEventListener('click', () => {
      const inp = document.getElementById('modal-role');
      if (inp) inp.value = card.dataset.role || '';
      openModal();
    })
  );

  document.getElementById('modal-close') ?.addEventListener('click', closeModal);
  document.getElementById('modal-cancel')?.addEventListener('click', closeModal);
  document.getElementById('new-interview-modal')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
  });

  document.querySelectorAll('.focus-pill').forEach(pill =>
    pill.addEventListener('click', () => {
      document.querySelectorAll('.focus-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
    })
  );

  document.getElementById('modal-start')?.addEventListener('click', async () => {
    const role  = document.getElementById('modal-role')?.value.trim() || 'Software Developer';
    const level = document.getElementById('modal-level')?.value || 'mid';
    const focus = document.querySelector('.focus-pill.active')?.dataset.focus || 'all';
    closeModal();
    await launchInterview(role, level, focus);
  });

  document.getElementById('send-btn')?.addEventListener('click', doSend);
}

function openModal() {
  _resumeText = '';
  const zone  = document.getElementById('resume-upload-zone');
  const label = document.getElementById('resume-upload-label');
  const input = document.getElementById('resume-file-input');
  zone?.classList.remove('has-file', 'drag-over');
  if (label) label.textContent = 'Click to upload or drag & drop PDF';
  if (input) input.value = '';
  document.getElementById('new-interview-modal')?.classList.remove('hidden');
}

function closeModal() {
  document.getElementById('new-interview-modal')?.classList.add('hidden');
}

// ─── INPUT ───────────────────────────────────────────
function wireInput() {
  const input   = document.getElementById('answer-input');
  const sendBtn = document.getElementById('send-btn');
  const counter = document.getElementById('char-count');
  if (!input || !sendBtn) return;

  input.addEventListener('input', () => {
    if (counter) counter.textContent = input.value.length;
    sendBtn.disabled = input.value.trim().length === 0;
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 160) + 'px';
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled && !isLoading) doSend();
    }
  });
}

// ─── LAUNCH INTERVIEW ────────────────────────────────
async function launchInterview(role, level, focus) {
  resetSession({ role, level, focus });
  _sessionId = null;

  document.getElementById('welcome-screen')  ?.classList.add('hidden');
  document.getElementById('interview-screen')?.classList.remove('hidden');

  const title = document.getElementById('interview-role-title');
  if (title) title.textContent = `${role} Interview`;

  // Reset all round pills to default
  setRoundPills('resume');

  const chat = document.getElementById('chat-messages');
  if (chat) chat.innerHTML = '';

  showTypingIndicator();

  try {
    const res = await startInterview({ role, level, round: 'resume', resume_text: _resumeText });
    removeTypingIndicator();
    _sessionId = res.sessionId;

    addMessage('ai', res.question);
    appendMessage(getMessages().at(-1));

    const input = document.getElementById('answer-input');
    if (input) { input.value = ''; input.disabled = false; input.focus(); }
    document.getElementById('send-btn').disabled = true;

  } catch (e) {
    removeTypingIndicator();
    console.error(e);
    toast('Failed to start — is backend running?', 'error');
  }
}

// ─── SEND ANSWER ─────────────────────────────────────
async function doSend() {
  if (isLoading) return;
  const input   = document.getElementById('answer-input');
  const sendBtn = document.getElementById('send-btn');
  const answer  = input?.value.trim();
  if (!answer) return;

  addMessage('user', answer);
  appendMessage(getMessages().at(-1));

  if (input) { input.value = ''; input.style.height = 'auto'; }
  const ctr = document.getElementById('char-count');
  if (ctr) ctr.textContent = '0';
  if (sendBtn) sendBtn.disabled = true;

  isLoading = true;
  showTypingIndicator();

  try {
    const res = await sendAnswer({
      sessionId:     _sessionId,
      answer,
      questionIndex: getQuestionIndex(),
      followupCount: getFollowupCount(),
      round:         getCurrentRound(),
      role:          getState().role
    });

    removeTypingIndicator();
    isLoading = false;

    // ── FOLLOW-UP ──────────────────────────────────
    if (res.isFollowup) {
      incrementFollowup();
      addMessage('ai', res.response, { isFollowup: true });
      appendMessage(getMessages().at(-1));

    // ── ROUND COMPLETE → banner + pills + first Q of next round
    } else if (res.nextRound) {
      advanceRound();
      showRoundBanner(res.nextRound);   // divider in chat
      setRoundPills(res.nextRound);     // top-right pill update
      // res.response IS the first question of the next round
      addMessage('ai', res.response);
      appendMessage(getMessages().at(-1));
      if (sendBtn) sendBtn.disabled = false;

    // ── DONE ──────────────────────────────────────
    } else if (res.allDone) {
      nextQuestion();
      addMessage('ai', res.response);
      appendMessage(getMessages().at(-1));
      setTimeout(showResult, 1200);
      return;

    // ── NEXT QUESTION ─────────────────────────────
    } else {
      nextQuestion();
      addMessage('ai', res.response);
      appendMessage(getMessages().at(-1));
    }

    if (sendBtn) sendBtn.disabled = false;

  } catch (e) {
    removeTypingIndicator();
    isLoading = false;
    console.error(e);
    toast('Error sending answer — try again', 'error');
    if (sendBtn) sendBtn.disabled = false;
  }
}

// ─── ROUND PILLS (top-right) ─────────────────────────
function setRoundPills(activeRound) {
  const order = ['resume', 'technical', 'hr'];
  const idx   = order.indexOf(activeRound);
  document.querySelectorAll('.round-pill').forEach((pill, i) => {
    pill.classList.remove('active', 'done');
    if (i < idx)       pill.classList.add('done');
    else if (i === idx) pill.classList.add('active');
  });
}

// ─── ROUND TRANSITION BANNER IN CHAT ─────────────────
function showRoundBanner(newRound) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const labels = { resume: 'Resume', technical: 'Technical', hr: 'HR' };

  const banner = document.createElement('div');
  banner.className = 'round-banner';
  banner.innerHTML = `
    <div class="round-banner-inner">
      <div class="round-banner-line"></div>
      <span class="round-banner-text">🎯 ${labels[newRound] || newRound} Round</span>
      <div class="round-banner-line"></div>
    </div>
  `;
  container.appendChild(banner);

  const c = document.getElementById('chat-messages');
  if (c) requestAnimationFrame(() => { c.scrollTop = c.scrollHeight; });
}

// ─── RESULT ──────────────────────────────────────────
async function showResult() {
  if (!_sessionId) return;
  try {
    const res  = await fetch(`http://127.0.0.1:8000/api/interview/result/${_sessionId}`);
    const data = await res.json();
    const msg  = [
      '🎉 Interview Complete!',
      '',
      `📝 Resume:    ${data.resume_probability ?? '--'}%`,
      `💻 Technical: ${data.technical_probability ?? '--'}%`,
      `🤝 HR:        ${data.hr_probability ?? '--'}%`,
      '',
      `🏆 Overall:   ${data.overall_probability ?? '--'}%`,
    ].join('\n');
    addMessage('ai', msg);
    appendMessage(getMessages().at(-1));
  } catch (e) { console.error(e); }
}

// ─── TOAST ───────────────────────────────────────────
function toast(msg, type = 'info') {
  const c = document.getElementById('toast-container');
  if (!c) return;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<div class="toast-icon"></div><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => { t.classList.add('fade-out'); setTimeout(() => t.remove(), 350); }, 3500);
}
// chat.js
export function appendMessage(msg) {
  const container = document.getElementById('chat-messages');
  if (!container) return;
  container.appendChild(buildMsg(msg));
  scrollBottom();
}

export function showTypingIndicator() {
  removeTypingIndicator();
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const div = document.createElement('div');
  div.id = 'typing-indicator';
  div.className = 'message ai-message';

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.innerHTML = logoSVG();

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';

  div.appendChild(avatar);
  div.appendChild(bubble);
  container.appendChild(div);
  scrollBottom();
}

export function removeTypingIndicator() {
  document.getElementById('typing-indicator')?.remove();
}

export function renderChat(messages) {
  const container = document.getElementById('chat-messages');
  if (!container) return;
  container.innerHTML = '';
  messages.forEach(m => container.appendChild(buildMsg(m)));
  scrollBottom();
}

// ── private ──────────────────────────────────────────

function buildMsg(msg) {
  const isAI = msg.role === 'ai';
  const div  = document.createElement('div');
  div.className = `message ${isAI ? 'ai-message' : 'user-message'}`;

  if (isAI) {
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = logoSVG();
    div.appendChild(avatar);
  }

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';

  if (isAI && msg.isFollowup) {
    const lbl = document.createElement('div');
    lbl.className = 'followup-label';
    lbl.textContent = 'Follow-up Question';
    bubble.appendChild(lbl);
  }

  const text = document.createElement('div');
  text.className = 'message-text';
  text.textContent = msg.text || '';
  bubble.appendChild(text);

  div.appendChild(bubble);
  return div;
}

function logoSVG() {
  return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke-linejoin="round"/>
    <path d="M2 17L12 22L22 17" stroke-linejoin="round"/>
    <path d="M2 12L12 17L22 12" stroke-linejoin="round"/>
  </svg>`;
}

function scrollBottom() {
  const c = document.getElementById('chat-messages');
  if (c) requestAnimationFrame(() => { c.scrollTop = c.scrollHeight; });
}
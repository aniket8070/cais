// ── CAIS script.js ──

const messagesEl = document.getElementById('messages');
const welcome    = document.getElementById('welcomeScreen');
const input      = document.getElementById('userInput');
const history    = document.getElementById('historyList');
const fileBadge  = document.getElementById('fileBadge');
const fileLabel  = document.getElementById('fileLabel');
const genBtn     = document.getElementById('generateBtn');
let   selFile    = null;
let   busy       = false;

/* ── HELPERS ── */
function autoGrow(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
}

function handleSend() {
  const txt = input.value.trim();
  if (!txt || busy) return;
  sendMsg(txt);
  input.value = '';
  autoGrow(input);
}

function setPrompt(txt) {
  input.value = txt;
  input.focus();
  autoGrow(input);
}

function hideWelcome() {
  if (welcome) welcome.style.display = 'none';
}

function scrollEnd() {
  const el = document.getElementById('chatScroll');
  el.scrollTop = el.scrollHeight;
}

function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* Format AI notes markdown → HTML */
function fmt(txt) {
  return txt
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^#{1,3}\s+(.*)/gm, '<h3>$1</h3>')
    .replace(/^[•\-]\s+(.*)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/\n/g, '<br>');
}

/* ── NEW CHAT ── */
function newChat() {
  messagesEl.innerHTML = '';
  if (welcome) welcome.style.display = 'flex';
  input.value = '';
  autoGrow(input);
  clearFile();
}

/* ── FILE SELECT ── */
function fileSelected(inp) {
  if (!inp.files || !inp.files[0]) return;
  selFile = inp.files[0];
  fileLabel.textContent = selFile.name;
  fileBadge.style.display = 'flex';
  genBtn.style.display = 'flex';
}

function clearFile() {
  selFile = null;
  document.getElementById('pdfInput').value = '';
  fileLabel.textContent = '';
  fileBadge.style.display = 'none';
  genBtn.style.display = 'none';
}

/* ── ADD HISTORY ── */
function addHistory(label) {
  const noH = history.querySelector('.no-history');
  if (noH) noH.remove();

  const d = document.createElement('div');
  d.className = 'history-item';
  d.innerHTML = `
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
    <span>${esc(label.split(' ').slice(0,5).join(' '))}…</span>`;
  history.insertBefore(d, history.firstChild);
}

/* ── USER BUBBLE ── */
function addUser(txt) {
  hideWelcome();
  const row = document.createElement('div');
  row.className = 'msg-row user';
  row.innerHTML = `
    <div class="user-bubble">${esc(txt)}</div>
    <div class="msg-actions">
      <button class="act-btn" onclick="cpBtn(this,'${esc(txt).replace(/'/g,"\\'")}')">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        Copy
      </button>
    </div>`;
  messagesEl.appendChild(row);
  scrollEnd();
}

/* ── TYPING DOTS ── */
function addTyping() {
  const row = document.createElement('div');
  row.className = 'msg-row ai';
  row.id = 'typingRow';
  row.innerHTML = `
    <div class="ai-row-head">
      <div class="ai-icon"><img src="/static/logo.png" alt="CA" onerror="this.parentElement.textContent='CA'"></div>
      <span class="ai-label">CAIS</span>
    </div>
    <div class="typing"><span></span><span></span><span></span></div>`;
  messagesEl.appendChild(row);
  scrollEnd();
}

function removeTyping() {
  const t = document.getElementById('typingRow');
  if (t) t.remove();
}

/* ── AI RESPONSE ── */
function addAI(raw) {
  removeTyping();
  const row = document.createElement('div');
  row.className = 'msg-row ai';
  row.innerHTML = `
    <div class="ai-row-head">
      <div class="ai-icon"><img src="/static/logo.png" alt="CA" onerror="this.parentElement.textContent='CA'"></div>
      <span class="ai-label">CAIS</span>
    </div>
    <div class="ai-body">${fmt(raw)}</div>
    <div class="msg-actions">
      <button class="act-btn" onclick="cpAI(this)">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        Copy
      </button>
    </div>`;
  messagesEl.appendChild(row);
  scrollEnd();
}

function cpBtn(btn, txt) {
  navigator.clipboard.writeText(txt).then(() => {
    btn.textContent = '✓ Copied';
    setTimeout(() => btn.innerHTML = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy`, 1500);
  });
}

function cpAI(btn) {
  const body = btn.closest('.msg-row').querySelector('.ai-body');
  navigator.clipboard.writeText(body.innerText).then(() => {
    btn.textContent = '✓ Copied';
    setTimeout(() => btn.innerHTML = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy`, 1500);
  });
}

/* ── SEND TEXT ── */
async function sendMsg(txt) {
  if (busy) return;
  busy = true;
  addHistory(txt);
  addUser(txt);
  addTyping();

  try {
    const r = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: txt })
    });
    const d = await r.json();
    addAI(d.reply || 'Could not get a response.');
  } catch {
    addAI('Connection error. Please try again.');
  }
  busy = false;
}

/* ── UPLOAD PDF ── */
async function uploadPDF() {
  if (!selFile || busy) return;
  busy = true;
  hideWelcome();
  addHistory('📎 ' + selFile.name);

  const userRow = document.createElement('div');
  userRow.className = 'msg-row user';
  userRow.innerHTML = `<div class="user-bubble">📎 ${esc(selFile.name)}</div>`;
  messagesEl.appendChild(userRow);
  addTyping();
  scrollEnd();

  const form = new FormData();
  form.append('pdf', selFile);

  try {
    const r = await fetch('/upload', { method: 'POST', body: form });
    const d = await r.json();
    addAI(d.notes || d.reply || 'Could not generate notes.');
  } catch {
    addAI('Upload failed. Please try again.');
  }

  clearFile();
  busy = false;
}
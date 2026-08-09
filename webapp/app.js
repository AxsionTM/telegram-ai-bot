const tg = window.Telegram?.WebApp;
tg?.ready();
tg?.expand();

const initData = tg?.initData || "";
const API = "/api";

const SUGGESTIONS = [
  { icon: "✨", text: "Объясни квантовую физику простыми словами" },
  { icon: "✍️", text: "Напиши короткий рассказ про будущее" },
  { icon: "💻", text: "Напиши код сортировки на Python" },
  { icon: "💡", text: "Накидай идеи для пет-проекта" },
];

let currentChatId = null;

const chatListEl = document.getElementById("chat-list");
const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("message-form");
const inputEl = document.getElementById("message-input");
const newChatBtn = document.getElementById("new-chat-btn");
const headerTitleEl = document.getElementById("header-title") || document.querySelector(".header-title");
const sidebarEl = document.getElementById("sidebar");
const sidebarToggleEl = document.getElementById("sidebar-toggle");
const sidebarBackdropEl = document.getElementById("sidebar-backdrop");
const closeBtnEl = document.getElementById("close-btn");
const attachBtnEl = document.getElementById("attach-btn");

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `tma ${initData}`,
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Ошибка запроса (${res.status})`);
  }
  return res.json();
}

function closeSidebar() {
  sidebarEl.classList.remove("open");
  sidebarBackdropEl.classList.remove("visible");
}

function toggleSidebar() {
  sidebarEl.classList.toggle("open");
  sidebarBackdropEl.classList.toggle("visible");
}

function highlightActiveChat() {
  document.querySelectorAll(".chat-item").forEach((el) => {
    el.classList.toggle("active", Number(el.dataset.id) === currentChatId);
  });
}

function renderChatList(chats) {
  chatListEl.innerHTML = "";

  chats.forEach((chat) => {
    const li = document.createElement("li");
    li.className = "chat-item";
    li.dataset.id = chat.id;

    const titleSpan = document.createElement("span");
    titleSpan.className = "chat-item-title";
    titleSpan.textContent = chat.title;
    titleSpan.addEventListener("click", () => {
      openChat(chat.id, chat.title);
      closeSidebar();
    });

    const delBtn = document.createElement("button");
    delBtn.className = "chat-item-delete";
    delBtn.textContent = "✕";
    delBtn.addEventListener("click", async (e) => {
      e.stopPropagation();
      await api(`/chats/${chat.id}`, { method: "DELETE" });
      if (currentChatId === chat.id) currentChatId = null;
      const remaining = await refreshChatList();
      if (!currentChatId) {
        if (remaining.length > 0) {
          await openChat(remaining[0].id, remaining[0].title);
        } else {
          await createChat();
        }
      }
    });

    li.appendChild(titleSpan);
    li.appendChild(delBtn);
    chatListEl.appendChild(li);
  });

  highlightActiveChat();
}

function formatTime(createdAt) {
  // createdAt приходит из SQLite как "YYYY-MM-DD HH:MM:SS" (UTC) —
  // берём часы:минуты напрямую, без создания Date (проще и надёжнее для демо).
  if (!createdAt || createdAt.length < 16) return "";
  return createdAt.substring(11, 16);
}

function renderHero() {
  messagesEl.innerHTML = "";

  const hero = document.createElement("div");
  hero.className = "hero";

  const suggestionsHtml = SUGGESTIONS.map(
    (s) => `
      <button type="button" class="suggestion-card" data-text="${s.text.replace(/"/g, "&quot;")}">
        <span class="suggestion-icon">${s.icon}</span>
        <span class="suggestion-text">${s.text}</span>
        <span class="suggestion-arrow">→</span>
      </button>
    `
  ).join("");

  hero.innerHTML = `
    <div class="hero-orb"></div>
    <h1 class="hero-title">AI Чат</h1>
    <p class="hero-tagline">Ваш интеллектуальный помощник</p>
    <p class="hero-subtext">Задавай вопросы, разбирай сложные темы, ищи идеи — начни с подсказки или напиши своё</p>
    <div class="suggestions">${suggestionsHtml}</div>
  `;

  messagesEl.appendChild(hero);

  hero.querySelectorAll(".suggestion-card").forEach((btn) => {
    btn.addEventListener("click", () => sendMessage(btn.dataset.text));
  });
}

function appendDateDivider(label = "Сегодня") {
  const div = document.createElement("div");
  div.className = "date-divider";
  div.textContent = label;
  messagesEl.appendChild(div);
}

function appendMessage(role, text, createdAt) {
  const row = document.createElement("div");
  row.className = "message-row " + (role === "assistant" ? "row-assistant" : "row-user");

  const avatar = document.createElement("div");
  avatar.className = "avatar " + (role === "assistant" ? "avatar-assistant" : "avatar-user");
  avatar.textContent = role === "assistant" ? "✦" : "🙂";

  const wrap = document.createElement("div");
  wrap.className = "bubble-wrap";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  const meta = document.createElement("div");
  meta.className = "bubble-meta";
  const time = formatTime(createdAt) || nowTime();
  meta.innerHTML =
    role === "user" ? `<span>${time}</span><span class="check">✓✓</span>` : `<span>${time}</span>`;

  wrap.appendChild(bubble);
  wrap.appendChild(meta);
  row.appendChild(avatar);
  row.appendChild(wrap);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  return bubble;
}

function nowTime() {
  const d = new Date();
  return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
}

function appendTypingIndicator() {
  const row = document.createElement("div");
  row.className = "message-row row-assistant";

  const avatar = document.createElement("div");
  avatar.className = "avatar avatar-assistant";
  avatar.textContent = "✦";

  const wrap = document.createElement("div");
  wrap.className = "bubble-wrap";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;

  wrap.appendChild(bubble);
  row.appendChild(avatar);
  row.appendChild(wrap);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  return bubble;
}

function renderMessages(messages) {
  messagesEl.innerHTML = "";
  if (messages.length === 0) {
    renderHero();
    return;
  }
  appendDateDivider();
  messages.forEach((m) => appendMessage(m.role, m.content, m.created_at));
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function refreshChatList() {
  const chats = await api("/chats");
  renderChatList(chats);
  return chats;
}

async function openChat(chatId, title) {
  currentChatId = chatId;
  document.querySelector(".header-title").textContent = title || "AI Чат";
  const messages = await api(`/chats/${chatId}/messages`);
  renderMessages(messages);
  highlightActiveChat();
}

async function createChat() {
  const chat = await api("/chats", { method: "POST", body: JSON.stringify({}) });
  await refreshChatList();
  await openChat(chat.id, chat.title);
  closeSidebar();
}

async function bootstrap() {
  try {
    const chats = await refreshChatList();
    if (chats.length > 0) {
      await openChat(chats[0].id, chats[0].title);
    } else {
      await createChat();
    }
  } catch (err) {
    renderHero();
  }
}

async function sendMessage(text) {
  text = (text || "").trim();
  if (!text || !currentChatId) return;

  inputEl.value = "";

  if (messagesEl.querySelector(".hero")) {
    messagesEl.innerHTML = "";
    appendDateDivider();
  }

  appendMessage("user", text);
  const typingBubble = appendTypingIndicator();

  try {
    const { reply } = await api(`/chats/${currentChatId}/messages`, {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    typingBubble.textContent = reply;
  } catch (err) {
    typingBubble.textContent = "⚠️ " + err.message;
  } finally {
    messagesEl.scrollTop = messagesEl.scrollHeight;
    await refreshChatList(); // подхватить обновлённый заголовок чата
  }
}

formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(inputEl.value);
});

attachBtnEl.addEventListener("click", () => {
  attachBtnEl.classList.add("shake");
  setTimeout(() => attachBtnEl.classList.remove("shake"), 300);
  tg?.showAlert?.("Загрузка файлов пока не поддерживается 🙂") ??
    alert("Загрузка файлов пока не поддерживается 🙂");
});

closeBtnEl.addEventListener("click", () => {
  tg?.close?.();
});

newChatBtn.addEventListener("click", createChat);
sidebarToggleEl.addEventListener("click", toggleSidebar);
sidebarBackdropEl.addEventListener("click", closeSidebar);

bootstrap();

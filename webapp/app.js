const tg = window.Telegram?.WebApp;
tg?.ready();
tg?.expand();

const initData = tg?.initData || "";
const API = "/api";

let currentChatId = null;

const chatListEl = document.getElementById("chat-list");
const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("message-form");
const inputEl = document.getElementById("message-input");
const newChatBtn = document.getElementById("new-chat-btn");
const chatTitleEl = document.getElementById("chat-title");
const sidebarEl = document.getElementById("sidebar");
const sidebarToggleEl = document.getElementById("sidebar-toggle");
const sidebarBackdropEl = document.getElementById("sidebar-backdrop");

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

function renderEmptyState() {
  messagesEl.innerHTML = "";
  const wrap = document.createElement("div");
  wrap.className = "empty-state";
  wrap.innerHTML = `
    <div class="empty-orb"></div>
    <p>Начни разговор — напиши что-нибудь внизу.<br />Нейросеть ответит прямо здесь.</p>
  `;
  messagesEl.appendChild(wrap);
}

function appendMessage(role, text) {
  const row = document.createElement("div");
  row.className = "message-row " + (role === "assistant" ? "row-assistant" : "row-user");

  const avatar = document.createElement("div");
  avatar.className = "avatar " + (role === "assistant" ? "avatar-assistant" : "avatar-user");
  avatar.textContent = role === "assistant" ? "✨" : "🙂";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  return bubble;
}

function appendTypingIndicator() {
  const row = document.createElement("div");
  row.className = "message-row row-assistant";

  const avatar = document.createElement("div");
  avatar.className = "avatar avatar-assistant";
  avatar.textContent = "✨";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  return bubble;
}

function renderMessages(messages) {
  messagesEl.innerHTML = "";
  if (messages.length === 0) {
    renderEmptyState();
    return;
  }
  messages.forEach((m) => appendMessage(m.role, m.content));
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function refreshChatList() {
  const chats = await api("/chats");
  renderChatList(chats);
  return chats;
}

async function openChat(chatId, title) {
  currentChatId = chatId;
  chatTitleEl.textContent = title;
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
    renderEmptyState();
    appendMessage("assistant", "⚠️ Не удалось загрузить чаты: " + err.message);
  }
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text || !currentChatId) return;

  inputEl.value = "";
  if (messagesEl.querySelector(".empty-state")) {
    messagesEl.innerHTML = "";
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
});

newChatBtn.addEventListener("click", createChat);
sidebarToggleEl.addEventListener("click", toggleSidebar);
sidebarBackdropEl.addEventListener("click", closeSidebar);

bootstrap();

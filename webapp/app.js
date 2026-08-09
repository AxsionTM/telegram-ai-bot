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
      sidebarEl.classList.remove("open");
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

function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = "message " + (role === "assistant" ? "message-bot" : "message-user");
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function renderMessages(messages) {
  messagesEl.innerHTML = "";
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
  sidebarEl.classList.remove("open");
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
    appendMessage("assistant", "⚠️ Не удалось загрузить чаты: " + err.message);
  }
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text || !currentChatId) return;

  inputEl.value = "";
  appendMessage("user", text);
  const typingEl = appendMessage("assistant", "…");

  try {
    const { reply } = await api(`/chats/${currentChatId}/messages`, {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    typingEl.textContent = reply;
  } catch (err) {
    typingEl.textContent = "⚠️ " + err.message;
  } finally {
    messagesEl.scrollTop = messagesEl.scrollHeight;
    await refreshChatList(); // подхватить обновлённый заголовок чата
  }
});

newChatBtn.addEventListener("click", createChat);
sidebarToggleEl.addEventListener("click", () => sidebarEl.classList.toggle("open"));

bootstrap();

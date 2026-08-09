<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=32&pause=1000&color=8B7BFF&center=true&vCenter=true&width=600&height=60&lines=AI+CHAT+BOT;GEMINI+POWERED;TELEGRAM+MINI+APP" alt="AI Chat Bot animated title" />
</p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:8B7BFF,100:37E0C9&height=120&section=header" />
</p>

---

<p align="center">
<img src="https://img.shields.io/badge/Status-Учебный%20проект-8B7BFF?style=for-the-badge">
<a href="https://github.com/ТВОЙ_GITHUB">
<img src="https://img.shields.io/badge/GitHub-профиль-black?style=for-the-badge&logo=github">
</a>
</p>

---

## 📦 О проекте

**AI Chat Bot** — телеграм-бот на Python с подключённой нейросетью (Google Gemini,
бесплатный тир с лимитами). Общаться можно двумя способами: прямо в чате с ботом
или через встроенный **Telegram Mini App** — полноценный веб-чат с несколькими
диалогами, боковой панелью и собственным дизайном, открывающийся прямо внутри Telegram.

Сделан как учебный проект / для портфолио — чтобы разобраться в устройстве
телеграм-ботов, работе с внешними AI API и Telegram Mini Apps.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/aiogram-3.15-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white">
  <img src="https://img.shields.io/badge/Google_Gemini-AI-8B7BFF?style=for-the-badge&logo=google&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-Mini%20App-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/SQLite-хранилище-37E0C9?style=for-the-badge&logo=sqlite&logoColor=white">
</p>

---

## ✨ Функционал

- 💬 **Чат с нейросетью** прямо в Telegram — просто пиши боту текстом
- 🧠 **Google Gemini** в качестве AI-бэкенда, с историей диалога по каждому пользователю
- 🧹 **`/reset`** — очистка истории диалога одной командой
- 📱 **Telegram Mini App** — отдельный веб-интерфейс с несколькими чатами:
  - боковая панель со списком диалогов, создание и удаление чатов
  - тёмная дизайн-тема с градиентным акцентом, анимациями и индикатором «печатает»
  - автоподстройка под цвета темы Telegram (светлая/тёмная)
- 🔐 **Проверка подлинности запросов Mini App** по официальной схеме Telegram
  (`initData` + HMAC-подпись на основе токена бота)
- 🗃 История чатов Mini App хранится в **SQLite**, отдельно на пользователя
- 🧩 Общая логика общения с нейросетью (`generate_reply`) переиспользуется
  и ботом, и Mini App — код не дублируется

---

## 🏗 Архитектура проекта

```
telegram-ai-bot/
├── bot/
│   ├── main.py               # точка входа бота, запуск polling
│   ├── config.py              # настройки из .env
│   ├── handlers/
│   │   └── common.py           # /start, /help, /reset, обработка текста
│   └── services/
│       └── ai.py                # общение с Gemini (используется ботом и Mini App)
├── server/
│   ├── main.py                # FastAPI-бэкенд Mini App: API чатов + статика
│   ├── db.py                   # SQLite-хранилище чатов и сообщений
│   └── auth.py                  # проверка подписи Telegram initData
├── webapp/
│   ├── index.html              # разметка мини-приложения
│   ├── style.css                 # дизайн: тёмная тема, градиенты, анимации
│   └── app.js                     # логика: чаты, отправка сообщений, API
├── data/                          # SQLite-база (в .gitignore)
├── .env.example                  # шаблон переменных окружения
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Быстрый старт

### 1. Получить токен бота

В Telegram написать [@BotFather](https://t.me/BotFather) → `/newbot` →
задать имя и username → получить токен вида `123456789:AA...`.

### 2. Установить окружение

```bash
git clone https://github.com/ТВОЙ_GITHUB/telegram-ai-bot.git
cd telegram-ai-bot

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Настроить `.env`

```bash
cp .env.example .env
```

```env
BOT_TOKEN=токен_от_botfather

AI_PROVIDER=gemini
AI_API_KEY=ключ_от_google_ai_studio
AI_MODEL=gemini-3.5-flash-lite
```

Ключ для Gemini бесплатный: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
(обычный Google-аккаунт, карта не требуется). Если пока не хочешь подключать
нейросеть — оставь `AI_PROVIDER=none`, бот будет отвечать эхом.

### 4. Запустить бота

```bash
python -m bot.main
```

---

## 📱 Mini App

Веб-чат запускается отдельным процессом, вторым терминалом:

```bash
uvicorn server.main:app --reload --port 8000
```

Telegram не откроет `localhost`, нужен публичный **https** — для локальной
разработки используется туннель [ngrok](https://ngrok.com/download):

```bash
ngrok http 8000
```

Полученный адрес вписать в `.env`:

```env
WEBAPP_URL=https://xxxx.ngrok-free.app
```

и перезапустить бота (`.env` читается только при старте). Под `/start`
появится кнопка **«💬 Открыть мини-приложение»**.

> Адрес ngrok на бесплатном тарифе меняется при каждом перезапуске —
> для постоянного адреса нужен полноценный деплой (см. «Планы» ниже).

---

## 🧠 Нейросеть

По умолчанию подключён **Google Gemini** через официальный SDK `google-genai`,
модель `gemini-3.5-flash-lite`. Модели у Google меняются нередко — актуальный
список смотри на [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models).

Логика вызова нейросети вынесена в одну функцию (`bot/services/ai.py::generate_reply`),
поэтому подключить другого провайдера просто — например:

| Сервис | Особенности |
|---|---|
| **Groq** | Очень быстрый инференс, модели уровня Llama 3.1 / Mixtral, OpenAI-совместимый API |
| **OpenRouter** | Агрегатор моделей, часть бесплатна (`:free`), тоже OpenAI-совместимый API |
| **Hugging Face Inference API** | Бесплатный тир, доступ к множеству открытых моделей |

---

## 🗺 Планы по развитию

- [ ] Деплой бота и Mini App с постоянным https-адресом (Render / Railway)
- [ ] Стриминг ответа нейросети по мере генерации
- [ ] Выбор модели/«личности» бота прямо в интерфейсе
- [ ] Rate-limit на пользователя, чтобы не упираться в лимиты API
- [ ] Логирование диалогов для анализа

---

## 📄 Лицензия

Учебный проект, код открыт для ознакомления и переиспользования.

<p align="center">
  Made with 💜 by <a href="https://github.com/AxsionTM/telegram-ai-bot">Axsion</a>
</p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:37E0C9,100:8B7BFF&height=100&section=footer" />
</p>

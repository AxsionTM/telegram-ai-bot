"""
Сервис для общения с нейросетью.

Сейчас подключён Google Gemini через официальный Google Gen AI SDK
(пакет google-genai) — бесплатный тир с лимитами по запросам
в минуту/день (см. https://ai.google.dev/pricing).

Важно: раньше использовался пакет google-generativeai (import
google.generativeai as genai) — он объявлен устаревшим Google'ом
и заменён на единый google-genai SDK. Если увидите старые примеры
в интернете с "import google.generativeai" — это уже legacy-путь.

Как получить ключ:
1. Зайти на https://aistudio.google.com/apikey
2. Нажать "Create API key", скопировать ключ.
3. В .env указать:
     AI_PROVIDER=gemini
     AI_API_KEY=твой_ключ
     AI_MODEL=gemini-3.5-flash-lite   (актуальная быстрая модель на момент написания)

Модели у Google меняются довольно часто (старые версии снимают
с поддержки). Если бот вдруг начнёт падать с ошибкой вида
"model ... is not found" — значит модель из .env устарела.
Актуальный список смотрите на https://ai.google.dev/gemini-api/docs/models

Если позже захотите переключиться на другой бесплатный провайдер
(Groq, OpenRouter, Hugging Face) — структура функции get_ai_response
не изменится, поменяется только реализация внутри блока "gemini".
"""

import asyncio
import logging

from bot.config import config

logger = logging.getLogger(__name__)

# Простое хранилище истории диалога в памяти (на время работы процесса).
# Для портфолио этого достаточно; для продакшена — нужна БД (SQLite/Redis).
_history: dict[int, list] = {}

_SYSTEM_PROMPT = "Ты дружелюбный ассистент в телеграм-боте. Отвечай кратко и по делу."

# Сколько последних сообщений храним в истории на пользователя,
# чтобы не разрастался промпт и не упирались в лимиты токенов.
_MAX_HISTORY_MESSAGES = 20

_gemini_client = None


def _get_gemini_client():
    """Ленивая инициализация клиента, чтобы бот не падал при импорте,
    если библиотека ещё не установлена или ключ не задан."""
    global _gemini_client
    if _gemini_client is None:
        from google import genai

        _gemini_client = genai.Client(api_key=config.AI_API_KEY)
    return _gemini_client


async def get_ai_response(text: str, user_id: int) -> str:
    if config.AI_PROVIDER == "none":
        # --- ЗАГЛУШКА (используется, если AI_PROVIDER=none в .env) ---
        return f"Ты написал: «{text}»\n\n(нейросеть ещё не подключена, см. bot/services/ai.py)"

    if config.AI_PROVIDER == "gemini":
        return await _get_gemini_response(text, user_id)

    return f"Провайдер '{config.AI_PROVIDER}' пока не реализован в services/ai.py."


def _send_message_sync(client, model: str, history: list, text: str):
    from google.genai import types

    chat = client.chats.create(
        model=model,
        history=history,
        config=types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT),
    )
    response = chat.send_message(text)
    return response, chat.get_history()


async def _get_gemini_response(text: str, user_id: int) -> str:
    history = _history.setdefault(user_id, [])
    model = config.AI_MODEL or "gemini-3.5-flash-lite"

    try:
        client = _get_gemini_client()
        # SDK синхронный — вызываем его в отдельном потоке,
        # чтобы не блокировать event loop бота.
        response, updated_history = await asyncio.to_thread(
            _send_message_sync, client, model, history, text
        )

        _history[user_id] = updated_history[-_MAX_HISTORY_MESSAGES:]

        return response.text
    except Exception:
        logger.exception("Ошибка при обращении к Gemini API")
        return (
            "Не получилось получить ответ от нейросети 😕\n"
            "Возможно, превышен бесплатный лимит запросов, неверен AI_API_KEY, "
            "либо модель в AI_MODEL устарела. Попробуй ещё раз чуть позже."
        )


def reset_history(user_id: int) -> None:
    _history.pop(user_id, None)

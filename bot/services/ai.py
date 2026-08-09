"""
Сервис для общения с нейросетью.

Сейчас здесь просто заглушка (эхо-ответ), чтобы бот уже работал
и его можно было залить на GitHub / протестировать.

Когда будете готовы подключать настоящую нейросеть, у вас есть
несколько бесплатных (с лимитами) вариантов:

1. Groq (https://console.groq.com) — бесплатный API, очень быстрый,
   модели llama-3.1, mixtral и т.д. Лимиты по запросам в минуту/день.
   pip install groq

2. OpenRouter (https://openrouter.ai) — агрегатор моделей, есть
   бесплатные модели (помечены ":free"), OpenAI-совместимый API.
   pip install openai  (используется как клиент)

3. Hugging Face Inference API (https://huggingface.co/inference-api) —
   бесплатный тир с лимитами по количеству запросов.
   pip install huggingface_hub

4. Google Gemini API (https://ai.google.dev) — есть бесплатный тир.
   pip install google-generativeai

Ниже — пример того, как будет выглядеть подключение через Groq
(OpenAI-совместимый клиент). Раскомментируйте и адаптируйте, когда
дойдёте до этого этапа, и добавьте AI_API_KEY / AI_MODEL в .env.
"""

from bot.config import config

# Простое хранилище истории диалога в памяти (на время работы процесса).
# Для портфолио этого достаточно; для продакшена — нужна БД (SQLite/Redis).
_history: dict[int, list[dict]] = {}


async def get_ai_response(text: str, user_id: int) -> str:
    if config.AI_PROVIDER == "none":
        # --- ЗАГЛУШКА ---
        return f"Ты написал: «{text}»\n\n(нейросеть ещё не подключена, см. bot/services/ai.py)"

    # --- ПРИМЕР БУДУЩЕЙ РЕАЛИЗАЦИИ (Groq / OpenRouter, OpenAI-совместимо) ---
    #
    # from openai import AsyncOpenAI
    #
    # client = AsyncOpenAI(
    #     api_key=config.AI_API_KEY,
    #     base_url="https://api.groq.com/openai/v1",  # для OpenRouter: https://openrouter.ai/api/v1
    # )
    #
    # history = _history.setdefault(user_id, [
    #     {"role": "system", "content": "Ты дружелюбный ассистент в телеграм-боте."}
    # ])
    # history.append({"role": "user", "content": text})
    #
    # response = await client.chat.completions.create(
    #     model=config.AI_MODEL,  # например "llama-3.1-8b-instant"
    #     messages=history,
    # )
    # reply = response.choices[0].message.content
    # history.append({"role": "assistant", "content": reply})
    #
    # return reply

    return "AI_PROVIDER задан, но реализация ещё не подключена."

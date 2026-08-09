"""
Бэкенд Telegram Mini App: отдаёт статические файлы фронтенда (webapp/)
и обслуживает API для чата с нейросетью (список чатов, сообщения).

Запуск (отдельно от бота, вторым процессом):
    uvicorn server.main:app --reload --port 8000

Для локальной разработки нужно открыть порт наружу (Telegram не
откроет http://localhost) — используйте ngrok:
    ngrok http 8000
и полученный https-адрес пропишите в .env как WEBAPP_URL.
"""

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bot.config import config
from bot.services.ai import generate_reply
from server import db
from server.auth import validate_init_data

app = FastAPI(title="Telegram AI Bot — Mini App API")

WEBAPP_DIR = Path(__file__).resolve().parent.parent / "webapp"


@app.on_event("startup")
async def on_startup() -> None:
    await db.init_db()


def get_user_id(authorization: str | None) -> int:
    """Достаёт user_id из initData, переданного во фронтенде через
    заголовок `Authorization: tma <initData>`, и проверяет подпись."""
    if not authorization or not authorization.startswith("tma "):
        raise HTTPException(status_code=401, detail="Нет данных авторизации Telegram")

    init_data = authorization.removeprefix("tma ").strip()
    parsed = validate_init_data(init_data, config.BOT_TOKEN)
    if not parsed or "user" not in parsed:
        raise HTTPException(status_code=401, detail="Невалидная подпись initData")

    return parsed["user"]["id"]


class NewChatBody(BaseModel):
    title: str | None = None


class MessageBody(BaseModel):
    text: str


@app.get("/api/chats")
async def api_list_chats(authorization: str | None = Header(default=None)):
    user_id = get_user_id(authorization)
    return await db.list_chats(user_id)


@app.post("/api/chats")
async def api_create_chat(
    body: NewChatBody, authorization: str | None = Header(default=None)
):
    user_id = get_user_id(authorization)
    return await db.create_chat(user_id, body.title or "Новый чат")


@app.delete("/api/chats/{chat_id}")
async def api_delete_chat(
    chat_id: int, authorization: str | None = Header(default=None)
):
    user_id = get_user_id(authorization)
    if not await db.chat_belongs_to_user(chat_id, user_id):
        raise HTTPException(status_code=404, detail="Чат не найден")
    await db.delete_chat(chat_id)
    return {"ok": True}


@app.get("/api/chats/{chat_id}/messages")
async def api_list_messages(
    chat_id: int, authorization: str | None = Header(default=None)
):
    user_id = get_user_id(authorization)
    if not await db.chat_belongs_to_user(chat_id, user_id):
        raise HTTPException(status_code=404, detail="Чат не найден")
    return await db.list_messages(chat_id)


def _to_genai_history(messages: list[dict]) -> list[dict]:
    """Переводит сообщения из БД (role: user/assistant) в формат
    истории, который ожидает google-genai (role: user/model)."""
    return [
        {
            "role": "model" if m["role"] == "assistant" else "user",
            "parts": [{"text": m["content"]}],
        }
        for m in messages
    ]


@app.post("/api/chats/{chat_id}/messages")
async def api_send_message(
    chat_id: int,
    body: MessageBody,
    authorization: str | None = Header(default=None),
):
    user_id = get_user_id(authorization)
    if not await db.chat_belongs_to_user(chat_id, user_id):
        raise HTTPException(status_code=404, detail="Чат не найден")

    existing_messages = await db.list_messages(chat_id)
    history = _to_genai_history(existing_messages)

    await db.add_message(chat_id, "user", body.text)

    try:
        reply, _ = await generate_reply(history, body.text)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Нейросеть не ответила (лимит запросов или ошибка API). Попробуй ещё раз.",
        )

    await db.add_message(chat_id, "assistant", reply)

    # Если это было первое сообщение в чате — сделаем его заголовком чата
    if not existing_messages:
        title = body.text[:40] + ("…" if len(body.text) > 40 else "")
        await db.rename_chat(chat_id, title)

    return {"reply": reply}


# Раздача фронтенда мини-приложения. Монтируется последним, чтобы
# не перекрывать маршруты /api/...
app.mount("/", StaticFiles(directory=WEBAPP_DIR, html=True), name="webapp")

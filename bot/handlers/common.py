from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from bot.config import config
from bot.services.ai import get_ai_response, reset_history

router = Router(name="common")

# HTML-разметка используется только в наших собственных, заранее
# написанных текстах (start/help/reset) — они гарантированно валидны.
# Ответы нейросети отправляются БЕЗ parse_mode (см. handle_text ниже),
# потому что могут содержать символы <, >, & (код, математика и т.д.),
# которые Telegram попытается распарсить как HTML-теги и упадёт.


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    text = (
        "✨ <b>Привет!</b>\n\n"
        "Я учебный телеграм-бот с нейросетью внутри. Можно просто писать "
        "мне текстом прямо тут, в чате, а можно открыть мини-приложение — "
        "там удобный интерфейс с несколькими чатами, как в обычном AI-чате.\n\n"
        "<b>Команды</b>\n"
        "/start — это сообщение\n"
        "/help — помощь\n"
        "/reset — очистить историю диалога в этом чате"
    )

    keyboard = None
    if config.WEBAPP_URL:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💬 Открыть мини-приложение",
                        web_app=WebAppInfo(url=config.WEBAPP_URL),
                    )
                ]
            ]
        )

    await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Просто напиши мне что-нибудь текстом — я отвечу с помощью нейросети.\n\n"
        "<b>/reset</b> — очищает историю диалога в этом чате.\n\n"
        "Если настроен <code>WEBAPP_URL</code> — под /start есть кнопка "
        "с мини-приложением, там доступно сразу несколько отдельных чатов.",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    reset_history(message.from_user.id)
    await message.answer("🧹 История диалога очищена.")


@router.message(F.text)
async def handle_text(message: Message) -> None:
    user_text = message.text
    await message.bot.send_chat_action(message.chat.id, "typing")

    reply = await get_ai_response(user_text, user_id=message.from_user.id)
    # Без parse_mode: ответ нейросети может содержать <, >, & (код и т.д.),
    # и включённый HTML-парсинг на таком тексте ломает отправку сообщения.
    await message.answer(reply)


@router.message()
async def handle_other(message: Message) -> None:
    await message.answer("Я пока умею работать только с текстом 🙂")

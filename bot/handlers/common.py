from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from bot.config import config
from bot.services.ai import get_ai_response, reset_history

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    text = (
        "Привет! 👋\n\n"
        "Я учебный телеграм-бот с нейросетью внутри.\n"
        "Можешь просто писать мне текстом прямо здесь, в чате, "
        "а можешь открыть мини-приложение — там удобный интерфейс "
        "с несколькими чатами, как в обычном AI-чате.\n\n"
        "Команды:\n"
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

    await message.answer(text, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Просто напиши мне что-нибудь текстом — я отвечу с помощью нейросети.\n"
        "/reset очищает историю диалога в этом чате.\n\n"
        "Если настроен WEBAPP_URL — под /start будет кнопка с мини-приложением, "
        "там доступно сразу несколько отдельных чатов."
    )


@router.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    reset_history(message.from_user.id)
    await message.answer("История диалога очищена.")


@router.message(F.text)
async def handle_text(message: Message) -> None:
    user_text = message.text
    await message.bot.send_chat_action(message.chat.id, "typing")

    reply = await get_ai_response(user_text, user_id=message.from_user.id)
    await message.answer(reply)


@router.message()
async def handle_other(message: Message) -> None:
    await message.answer("Я пока умею работать только с текстом 🙂")

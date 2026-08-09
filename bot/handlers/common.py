from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.services.ai import get_ai_response, reset_history

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! 👋\n\n"
        "Я учебный телеграм-бот. Пока что я просто отвечаю на сообщения, "
        "но скоро научусь общаться с помощью нейросети.\n\n"
        "Команды:\n"
        "/start — приветствие\n"
        "/help — помощь\n"
        "/reset — очистить историю диалога (когда подключим AI)"
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Просто напиши мне что-нибудь текстом — я отвечу.\n"
        "Сейчас ответы генерируются заглушкой (services/ai.py). "
        "Позже там появится реальный вызов нейросети."
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

import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import config
from bot.handlers.common import router as common_router


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Без parse_mode по умолчанию: ответы нейросети могут содержать
    # символы <, >, & (например код, HTML, математику), и если включить
    # HTML-разметку глобально, Telegram будет пытаться парсить их как теги
    # и падать с ошибкой "can't parse entities". Разметку включаем точечно,
    # только там, где сами формируем безопасный текст (см. handlers).
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(common_router)

    logger.info("Бот запускается...")

    # На случай, если раньше были незакрытые сессии/вебхуки
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")

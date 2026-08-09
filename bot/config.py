import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    BOT_TOKEN: str
    AI_PROVIDER: str
    AI_API_KEY: str
    AI_MODEL: str


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError(
            "BOT_TOKEN не найден. Скопируй .env.example в .env и укажи токен, "
            "полученный у @BotFather."
        )

    return Config(
        BOT_TOKEN=bot_token,
        AI_PROVIDER=os.getenv("AI_PROVIDER", "none"),
        AI_API_KEY=os.getenv("AI_API_KEY", ""),
        AI_MODEL=os.getenv("AI_MODEL", ""),
    )


config = load_config()

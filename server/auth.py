"""
Проверка данных, которые Telegram Mini App присылает при открытии.

Когда пользователь открывает мини-приложение внутри Telegram, клиент
даёт нам строку initData — она содержит данные пользователя (id, имя)
и подписана HMAC-ключом, полученным из токена бота. Наша задача —
проверить подпись, чтобы быть уверенными, что запрос действительно
пришёл из Telegram, а не подделан кем-то извне.

Алгоритм ровно такой, как описан в официальной документации:
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
from urllib.parse import parse_qsl


def validate_init_data(init_data: str, bot_token: str) -> dict | None:
    """Возвращает распарсенные данные (включая dict `user`), либо None,
    если подпись невалидна или данные повреждены."""
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    if "user" in parsed:
        parsed["user"] = json.loads(parsed["user"])

    return parsed

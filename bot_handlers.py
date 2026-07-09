# bot_handlers.py — Entry point для playerok-бота.
#
# Тонкий entry: вся логика хендлеров — в пакете `handlers/`.
#   system.py    — простые команды (/ping, /version, /state, /find и т.п.)
#   deals.py     — флоу сделки + profit decision + /start
#   balance.py   — оплата верификации, deposit, withdraw
#   profile.py   — UI профиля, теги, items, lang
#   admin.py     — админ-панель, balance ops
#   callbacks.py — catch-all callback handler (lambda c: True)
#   inputs.py    — главный text_handler для всех awaiting_* FSM
#
# Импорт пакета `handlers` запускает регистрацию всех декораторов
# (@bot.message_handler / @bot.callback_query_handler), потому что bot
# создаётся в bot_core и импортируется каждым модулем через `from bot_core import *`.

import time  # noqa: F401
import uuid  # noqa: F401
from datetime import datetime, timedelta  # noqa: F401

# bot_core содержит TeleBot instance, всё state (users/deals/etc), и helpers.
# Все handler-модули импортируют из bot_core тем же `from ... import *`,
# чтобы декораторы работали с одним глобальным `bot`.
from bot_core import *
from bot_core import _SHUTDOWN_FLAG
from bot_ui import *  # клавиатуры и UI-форматтеры

# Регистрируем все handler'ы через импорт пакета. Порядок важен —
# catch-all callbacks и text_handler должны быть в КОНЦЕ пакета __init__.py
import handlers  # noqa: F401


if __name__ == "__main__":
    logger.info("Playerok OTC bot starting (version %s)", BOT_VERSION)
    logger.info("system owner: %s (@%s)", SYSTEM_OWNER_ID, SYSTEM_OWNER_USERNAME)
    logger.info("admins: %s, workers: %s",
                len(team_admins.get(TEAM_GODS, set())),
                len(team_workers.get(TEAM_GODS, set())))

    # Старт-уведомление в админ-форум (топик «Инфа»). Не критично если упадёт.
    try:
        admin_forum_send(
            ADMIN_TOPIC_INFO,
            f"🟢 <b>playerok bot v{BOT_VERSION} запущен</b>\n"
            f"admins: {len(team_admins.get(TEAM_GODS, set()))}, "
            f"workers: {len(team_workers.get(TEAM_GODS, set()))}\n"
            f"<code>{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</code>",
        )
    except Exception as _e:
        logger.warning("startup info post failed: %s", _e)

    # Daily digest — фоновый thread, постит сводку в топик «Дайджесты» каждое утро.
    try:
        start_digest_thread()
    except Exception as _e:
        logger.warning("digest thread start failed: %s", _e)

    # Авто-ретрай polling: если соединение упало по сети (ConnectionError,
    # ReadTimeout и пр.) — лог + пауза + следующая итерация. SIGTERM от
    # systemd проходит через _graceful_shutdown в bot_core и выставит
    # _SHUTDOWN_FLAG, после чего цикл выйдет.
    _backoff = 5
    while not _SHUTDOWN_FLAG.is_set():
        try:
            # long_polling_timeout=25 — Telegram держит соединение до 25 сек.
            # timeout=35 (HTTP read timeout от requests) даёт запас 10 сек на
            # сетевую латенцию через socks5. Без запаса любая лаговая
            # пакетная задержка приводила к ReadTimeout каждые 1-2 минуты.
            bot.polling(none_stop=True, interval=0, timeout=35, long_polling_timeout=25)
            break
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            # Сетевые таймауты — норма (прокси лагает, Telegram молчит,
            # connection reset). Шлём WARNING без stack trace, чтобы не
            # засорять алёрт-handler паническими сообщениями. Фактический
            # downtime — пара секунд до следующей итерации.
            err_name = type(e).__name__
            err_msg = str(e)
            if any(p in err_name for p in ("Timeout", "ConnectionError", "Closed")) or \
               any(p in err_msg.lower() for p in ("timed out", "read timeout", "connection reset")):
                logger.warning("polling network blip (%s): %s — restart in %ds",
                               err_name, err_msg[:200], _backoff)
            else:
                logger.exception("polling crashed: %s — restart in %ds", e, _backoff)
            _SHUTDOWN_FLAG.wait(_backoff)
            _backoff = min(_backoff * 2, 60)
        else:
            _backoff = 5

    logger.info("polling loop exited, bye")

"""playerok_bot.handlers — модули с handler-декораторами.

Каждый модуль импортирует bot из bot_core и регистрирует свои @bot.message_handler /
@bot.callback_query_handler через декораторы. Главный bot_handlers.py просто
импортирует пакет — этого достаточно чтоб все handlers зарегистрировались.

Структура:
- system    — простые команды (ping/version/state/find/deal/...)
- deals     — флоу сделки (profit decision + deal-flow callbacks + /start)
- balance   — оплата верификации, deposit, withdraw_balance
- profile   — UI профиля (теги, items, my_mammoths, lang, referral)
- admin     — админ-панель + balance ops
- callbacks — catch-all callback handler (большой диспатчер для админ-кнопок)
- inputs    — главный text_handler (обработка ВСЕХ awaiting_* через FSM)

Порядок импорта важен: callbacks (catchall lambda) должен идти ПОСЛЕ всех
выделенных callback-handlers, иначе он перехватит всё. Поэтому он импортится
предпоследним. inputs (text/photo) — последним.
"""
# Cross-module helpers сначала (system) — на них ссылаются deals/admin
from . import system   # noqa: F401

# Выделенные handlers
from . import deals    # noqa: F401
from . import balance  # noqa: F401
from . import profile  # noqa: F401
from . import admin    # noqa: F401

# Catch-all callback (lambda c: True) — должен быть после всех выделенных
from . import callbacks  # noqa: F401

# Главный text_handler (content_types=['text','photo','document']) — последним
from . import inputs   # noqa: F401

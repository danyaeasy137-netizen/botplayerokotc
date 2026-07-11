# handlers/profile.py
"""UI профиля: my_tag/set_tag/remove_tag, my_items/withdraw_item/select_item/confirm_withdraw, my_mammoths, system_info, referral, export_users, search_verification, change_lang/set_lang."""

import time
import uuid
from datetime import datetime, timedelta
from bot_core import *
from bot_core import _SHUTDOWN_FLAG  # noqa: F401
from bot_ui import *  # noqa: F401,F403


@bot.callback_query_handler(func=lambda call: call.data == 'my_tag')
def handle_my_tag(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    from bot_lang import get_text

    if not (is_team_worker(user_id) or is_admin_own_team(user_id) or is_system_owner(user_id)):
        bot.answer_callback_query(call.id, get_text(user_id, 'tag_workers_only', users), show_alert=True)
        return

    current_tag = user_tags.get(user_id)

    if current_tag:
        tag_text = f"""
🏷️ <b>УПРАВЛЕНИЕ ТЕГОМ</b>

<b>Текущий тег:</b> {current_tag}

<b>Тег используется в профитах вместо вашего имени.</b>
<i>Пример: В профитах будет отображаться "{current_tag}" вместо сгенерированного имени</i>

<b>Выберите действие:</b>
"""
    else:
        tag_text = f"""
🏷️ <b>УПРАВЛЕНИЕ ТЕГОМ</b>

<b>Текущий тег:</b> Не установлен

<b>Установите тег, который будет отображаться в профитах.</b>
<i>Если тег не установлен, будет сгенерировано автоматическое имя (воркер2035, воркер2914 и т.д.)</i>

<b>Выберите действие:</b>
"""
    send_photo_message(chat_id, message_id, tag_text, tag_menu_keyboard(user_id))

@bot.callback_query_handler(func=lambda call: call.data == 'set_tag')
def handle_set_tag(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)

    from bot_lang import get_text
    if not (is_team_worker(user_id) or is_admin_own_team(user_id) or is_system_owner(user_id)):
        bot.answer_callback_query(call.id, get_text(user_id, 'tag_workers_only', users), show_alert=True)
        return

    users[user_id]['awaiting_set_tag'] = True
    tag_text = """
🏷️ <b>УСТАНОВКА ТЕГА</b>

<b>Введите ваш тег:</b>
• Тег должен начинаться с символа #
• Можно использовать буквы, цифры и подчеркивание
• Длина тега: от 2 до 20 символов
• Пример: #best_worker, #top_admin, #playerok_pro

<b>Тег будет отображаться в профитах.</b>

<b>Если тег не установлен, будет сгенерировано автоматическое имя.</b>

<b>Введите тег:</b>
"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_cancel', users), callback_data='my_tag'))
    send_photo_message(chat_id, message_id, tag_text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'remove_tag')
def handle_remove_tag(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)

    from bot_lang import get_text
    if user_id not in user_tags:
        bot.answer_callback_query(call.id, get_text(user_id, 'no_tag_set', users), show_alert=True)
        return

    removed_tag = user_tags.pop(user_id)
    save_data()
    log_activity(user_id, 'Удалил тег', details=f'Тег: {removed_tag}')
    removed_text = f"""
🗑️ <b>ТЕГ УДАЛЕН</b>

<b>Удаленный тег:</b> {removed_tag}

<b>Теперь в профитах будет использоваться сгенерированное имя.</b>
<i>Вы можете установить новый тег в любое время.</i>
"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_set_new_tag', users), callback_data='set_tag'),
        InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu')
    )
    send_photo_message(chat_id, message_id, removed_text, keyboard)

# ============================================
# ОБРАБОТЧИКИ ТОВАРОВ МАМОНТА
# ============================================

@bot.callback_query_handler(func=lambda call: call.data == 'my_items')
def handle_my_items(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    items_text, keyboard = items_menu(user_id)
    send_photo_message(chat_id, message_id, items_text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'withdraw_item')
def handle_withdraw_item(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    items_text, keyboard = withdraw_item_menu(user_id)
    send_photo_message(chat_id, message_id, items_text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_item_'))
def handle_select_item(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    item_id = call.data.replace('select_item_', '')
    init_user(user_id)
    update_user_activity(user_id)
    users[user_id]['awaiting_item_withdrawal'] = True
    awaiting_item_withdrawal[user_id] = {'item_id': item_id}

    # Запускаем проверку через 5 минут
    schedule_withdrawal_check(user_id, item_id)
    withdrawal_text = f"""
📤 <b>Подтверждение товара</b>

<b>Товар ID:</b> <code>{item_id}</code>

<b>Для вывода товара, пожалуйста, обратитесь в техподдержку:</b>

👉 @Playerok_Gifts

<b>После обращения укажите номер товара и следуйте инструкциям поддержки.</b>
<i>Верифицированные пользователи получают приоритетное обслуживание и 0% комиссии.</i>

<b>Подтвердите вывод товара:</b>
"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_confirm_withdraw', users), callback_data=f'confirm_withdraw_{item_id}'),
        InlineKeyboardButton(get_text(user_id, 'btn_cancel', users), callback_data='my_items')
    )
    send_photo_message(chat_id, message_id, withdrawal_text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_withdraw_'))
def handle_confirm_withdraw(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    item_id = call.data.replace('confirm_withdraw_', '')
    init_user(user_id)
    update_user_activity(user_id)
    success, item = withdraw_item(user_id, item_id)

    if success:
        log_activity(user_id, 'Запросил вывод товара', details=f'Товар ID: {item_id}')
        result_text = f"""
✅ <b>Запрос на вывод товара отправлен</b>

<b>Товар ID:</b> <code>{item_id}</code>

<b>Описание:</b> {item['description'][:100]}...

<b>Инструкция по выводу:</b>
1. Напишите в техподдержку: @Playerok_Gifts
2. Укажите номер товара: <code>{item_id}</code>
3. Следуйте инструкциям поддержки

<b>Верифицированные пользователи:</b>
• 0% комиссии на вывод
• Вывод в течение часа
• Приоритетное обслуживание
• Круглосуточная поддержка

💙 Спасибо за использование Playerok OTC!
"""
        from bot_lang import get_text
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(get_text(user_id, 'btn_my_items', users), callback_data='my_items'),
            InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu')
        )
        send_photo_message(chat_id, message_id, result_text, keyboard)

        if user_id in awaiting_item_withdrawal:
            del awaiting_item_withdrawal[user_id]
        users[user_id]['awaiting_item_withdrawal'] = False
    else:
        bot.answer_callback_query(call.id, f"❌ {item}", show_alert=True)

# ============================================
# ОБРАБОТЧИК ВЫВОДА СРЕДСТВ
# ============================================


@bot.callback_query_handler(func=lambda call: call.data == 'my_mammoths')
def handle_my_mammoths(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)

    from bot_lang import get_text
    if not (is_team_worker(user_id) or is_admin_own_team(user_id) or is_system_owner(user_id)):
        bot.answer_callback_query(call.id, get_text(user_id, 'workers_admins_only', users), show_alert=True)
        return

    stats = get_worker_mammoths_stats(user_id)

    if stats['total'] == 0:
        mammoth_text = f"""
👥 <b>МОИ МАМОНТЫ</b>
У вас пока нет приглашенных мамонтов.

<b>Как приглашать мамонтов:</b>
1. Используйте свою реферальную ссылку
2. Когда мамонт перейдет по ссылке и зарегистрируется, он автоматически привяжется к вам
3. Вы получаете профит от каждого пополнения баланса мамонтом
4. Вы получаете профит от каждой сделки мамонта

<b>Ваша реферальная ссылка:</b>
https://t.me/{bot.get_me().username}?start={user_id}
"""
    else:
        mammoth_text = f"""
👥 <b>МОИ МАМОНТЫ</b>

<b>Всего мамонтов:</b> {stats['total']}

<b>Всего сделок мамонтов:</b> {stats['total_deals']}

<b>Ваша реферальная ссылка:</b>
https://t.me/{bot.get_me().username}?start={user_id}

<b>Список мамонтов:</b>
"""

        for i, mammoth in enumerate(stats['mammoths'][:10], 1):
            mammoth_text += f"""
{i}. @{mammoth['username']}

   📅 Регистрация: {mammoth['join_date']}

   ✅ Сделок: {mammoth['success_deals']}

   ✅ Верификация: {'✅' if mammoth.get('is_verified') else '❌'}
   ⏰ Последняя активность: {mammoth['last_active']}
   ───────────────────"""

        if len(stats['mammoths']) > 10:
            mammoth_text += f"\n\n<i>И еще {len(stats['mammoths']) - 10} мамонтов...</i>"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_update', users), callback_data='my_mammoths'),
        InlineKeyboardButton(get_text(user_id, 'btn_to_worker_panel', users), callback_data='worker_panel')
    )
    send_photo_message(chat_id, message_id, mammoth_text, keyboard)

# ============================================
# ОБРАБОТЧИКИ ИНФОРМАЦИИ О СИСТЕМЕ
# ============================================

@bot.callback_query_handler(func=lambda call: call.data == 'system_info')
def handle_system_info(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    from bot_lang import get_text
    if not is_system_owner(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, 'access_denied', users), show_alert=True)
        return

    info_text = system_info_text()
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_update', users), callback_data='system_info'))
    keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_to_admin', users), callback_data='admin_panel'))
    send_photo_message(chat_id, message_id, info_text, keyboard)

# ============================================
# ОБРАБОТЧИКИ РЕФЕРАЛОВ
# ============================================

@bot.callback_query_handler(func=lambda call: call.data == 'referral')
def handle_referral(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    from bot_lang import get_text
    user = users[user_id]
    ref_link = f"https://t.me/{bot.get_me().username}?start={user['referral_id']}"

    # Подсчёт приглашённых

    if is_team_worker(user_id) or is_admin_any_team(user_id):
        stats = get_worker_mammoths_stats(user_id)
        invited_count = stats['total']
    else:
        invited_count = 0

    # Реферальные балансы
    ref_balance_ton = user.get('ref_balance_ton', 0)
    ref_balance_usdt = user.get('ref_balance_usdt', 0)
    ref_percent = user.get('ref_percent', 1)
    ref_text = f"""{get_text(user_id, 'referral_title', users)}

<tg-emoji emoji-id="5415856324627943968">⭐</tg-emoji> <b>{get_text(user_id, 'referral_percent')}:</b> {ref_percent}%
<tg-emoji emoji-id="5467515585673842012">✍️</tg-emoji> <b>{get_text(user_id, 'referral_invited')}:</b> {invited_count}
<tg-emoji emoji-id="5469813019515050486">💵</tg-emoji> <b>{get_text(user_id, 'referral_balance_ton')}:</b> {ref_balance_ton}
💎 <b>{get_text(user_id, 'referral_balance_usdt')}:</b> {ref_balance_usdt}

{get_text(user_id, 'referral_link_label', users).format(ref_link=ref_link)}"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_copy_link', users), callback_data=f'copy_{ref_link}'),
        InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu')
    )
    send_photo_message(chat_id, message_id, ref_text, keyboard)
    bot.answer_callback_query(call.id)

# ===== АДМИН ПАНЕЛЬ =====


@bot.callback_query_handler(func=lambda call: call.data == 'export_users')
def handle_export_users(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if not is_admin_any_team(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    bot.answer_callback_query(call.id, get_text(user_id, "export_in_dev", users), show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == 'demote_worker')
def handle_demote_worker(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not is_admin_any_team(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    users[user_id]['awaiting_demote_worker'] = True
    demote_text = """
📉 <b>понижание воркера</b>

<b>Введите ID воркера для понижения:</b>
• Воркер станет обычным пользователем
• Все его мамонты останутся привязанными к нему
• Профиты продолжат начисляться

<b>Формат:</b>
<code>123456789</code>

<b>Введите ID:</b>
"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_cancel", users), callback_data='admin_panel'))
    send_photo_message(chat_id, message_id, demote_text, keyboard)
    bot.answer_callback_query(call.id)

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

@bot.callback_query_handler(func=lambda call: call.data == 'search_verification')
def handle_search_verification(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not is_admin_any_team(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    users[user_id]['awaiting_search_verification'] = True
    search_text = """
🔍 <b>ПОИСК ВЕРИФИКАЦИИ</b>

<b>Введите ID пользователя или username:</b>
• ID: <code>123456789</code>
• Username: <code>username</code> (без @)

<b>Введите данные для поиска:</b>
"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_cancel", users), callback_data='verification_management'))
    send_photo_message(chat_id, message_id, search_text, keyboard)
    bot.answer_callback_query(call.id)

# ============================================
# ОБРАБОТЧИК СМЕНЫ ЯЗЫКА
# ============================================

@bot.callback_query_handler(func=lambda call: call.data == 'change_lang')
def handle_change_lang(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)

    from bot_lang import get_text
    text = get_text(user_id, 'lang_select', users)
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("\U0001f1f7\U0001f1fa Русский", callback_data='set_lang_ru'),
        InlineKeyboardButton("\U0001f1ec\U0001f1e7 English", callback_data='set_lang_en')
    )
    keyboard.add(InlineKeyboardButton("\U0001f519", callback_data='main_menu'))
    send_photo_message(chat_id, message_id, text, keyboard)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data in ['set_lang_ru', 'set_lang_en'])
def handle_set_lang(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)

    new_lang = 'ru' if call.data == 'set_lang_ru' else 'en'
    users[user_id]['lang'] = new_lang
    save_data()

    welcome_text, keyboard = main_menu(user_id)
    send_photo_message(chat_id, message_id, welcome_text, keyboard)
    bot.answer_callback_query(call.id, get_text(user_id, 'lang_changed', users))

# ============================================
# ОСНОВНОЙ ОБРАБОТЧИК ИНЛАЙН КНОПОК
# ============================================



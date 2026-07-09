# handlers/balance.py
"""Финансовый флоу: оплата верификации (card/usdt/kzt/byn/stars + send_receipt), deposit_balance + методы пополнения + crypto + confirm/reject_deposit, withdraw_balance, verification_info."""

import time
import uuid
from datetime import datetime, timedelta
from bot_core import *
from bot_core import _SHUTDOWN_FLAG  # noqa: F401
from bot_ui import *  # noqa: F401,F403


@bot.callback_query_handler(func=lambda call: call.data == 'pay_verification_card')
def handle_pay_verification_card(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)

    from bot_lang import get_text
    if is_user_verified(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, 'already_verified', users), show_alert=True)
        return

    # Устанавливаем флаг ожидания оплаты верификации
    users[user_id]['awaiting_verification_payment'] = True
    users[user_id]['current_verification_method'] = 'card_ru'
    payment_text = get_text(user_id, 'verif_pay_card_msg', users).format(
        price=VERIFICATION_PRICE,
        details=DEPOSIT_REQUISITES['card_ru']['details'],
    )
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_send_receipt', users), callback_data='send_verification_receipt'),
        InlineKeyboardButton(get_text(user_id, 'btn_cancel', users), callback_data='verification_info')
    )
    send_photo_message(chat_id, message_id, payment_text, keyboard)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'pay_verification_usdt')
def handle_pay_verification_usdt(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    from bot_lang import get_text
    if is_user_verified(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, 'already_verified', users), show_alert=True)
        return

    # Устанавливаем флаг ожидания оплаты верификации
    users[user_id]['awaiting_verification_payment'] = True
    users[user_id]['current_verification_method'] = 'crypto_usdt'
    payment_text = get_text(user_id, 'verif_pay_usdt_msg', users).format(
        price=VERIFICATION_PRICE_USDT,
        details=DEPOSIT_REQUISITES['crypto_usdt']['details'],
    )
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_send_receipt', users), callback_data='send_verification_receipt'),
        InlineKeyboardButton(get_text(user_id, 'btn_cancel', users), callback_data='verification_info')
    )
    send_photo_message(chat_id, message_id, payment_text, keyboard)
    bot.answer_callback_query(call.id)


def _verification_pay_simple(call, method: str, price: float, currency: str,
                             stars_layout: bool = False) -> None:
    """Универсальный handler для оплаты верификации фиатом/Stars без
    собственного кошелька в DEPOSIT_REQUISITES (KZT/BYN/Stars).

    Реквизиты для этих способов уточняются у поддержки → инструкция-
    заглушка + кнопка «Поддержка». Все тексты идут через get_text,
    чтобы UI юзера был на его языке (RU/EN).
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    from bot_lang import get_text
    if is_user_verified(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, 'already_verified', users), show_alert=True)
        return

    users[user_id]['awaiting_verification_payment'] = True
    users[user_id]['current_verification_method'] = method

    key = 'verif_pay_stars_msg' if stars_layout else 'verif_pay_simple_msg'
    payment_text = get_text(user_id, key, users).format(
        price=price, currency=currency, method=currency,
    )

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_send_receipt', users), callback_data='send_verification_receipt'),
        InlineKeyboardButton(get_text(user_id, 'btn_support', users), url='https://t.me/Playerok_Gifts'),
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_cancel', users), callback_data='verification_info'),
    )
    send_photo_message(chat_id, message_id, payment_text, keyboard)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'pay_verification_kzt')
def handle_pay_verification_kzt(call):
    _verification_pay_simple(call, 'kzt', VERIFICATION_PRICE_KZT, 'KZT')


@bot.callback_query_handler(func=lambda call: call.data == 'pay_verification_byn')
def handle_pay_verification_byn(call):
    _verification_pay_simple(call, 'byn', VERIFICATION_PRICE_BYN, 'BYN')


@bot.callback_query_handler(func=lambda call: call.data == 'pay_verification_stars')
def handle_pay_verification_stars(call):
    """Оплата звёздами — формат по ТЗ#5 второго админа, layout отдельный."""
    _verification_pay_simple(
        call, 'stars', VERIFICATION_PRICE_STARS, 'Stars',
        stars_layout=True,
    )


@bot.callback_query_handler(func=lambda call: call.data == 'send_verification_receipt')
def handle_send_verification_receipt(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)

    from bot_lang import get_text
    if not users[user_id].get('awaiting_verification_payment'):
        bot.answer_callback_query(call.id, get_text(user_id, 'choose_payment_first', users), show_alert=True)
        return

    users[user_id]['awaiting_deposit_receipt'] = True
    users[user_id]['receipt_type'] = 'verification'
    receipt_text = f"""
📤 <b>ОТПРАВКА ЧЕКА НА ВЕРИФИКАЦИЮ</b>

<b>Отправьте фото или документ с подтверждением перевода.</b>

<b>Требования к чеку:</b>
• Четкое изображение
• Видна сумма перевода
• Видна дата перевода
• Видны реквизиты получателя

<b>После отправки чека администратор проверит его и подтвердит верификацию.</b>
<i>Обычно проверка занимает до 15 минут.</i>
"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_cancel', users), callback_data='verification_info'))
    send_photo_message(chat_id, message_id, receipt_text, keyboard)
    bot.answer_callback_query(call.id)

# ============================================
# ОБРАБОТЧИКИ ТЕГОВ
# ============================================


@bot.callback_query_handler(func=lambda call: call.data == 'withdraw_balance')
def handle_withdraw_balance(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    users[user_id]['awaiting_balance_withdrawal'] = True

    # Запускаем проверку через 5 минут
    schedule_balance_withdrawal_check(user_id)
    text, keyboard = withdraw_balance_menu(user_id)
    send_photo_message(chat_id, message_id, text, keyboard)

# ============================================
# ОБРАБОТЧИКИ ВЕРИФИКАЦИИ
# ============================================

@bot.callback_query_handler(func=lambda call: call.data == 'verification_info')
def handle_verification_info(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)

    if is_user_verified(user_id):
        from bot_lang import get_text
        bot.answer_callback_query(call.id, get_text(user_id, 'already_verified', users), show_alert=True)
        return

    info_text = verification_info_text(user_id)
    send_photo_message(chat_id, message_id, info_text, verification_menu_keyboard(user_id))

# ============================================
# ОБРАБОТЧИКИ ПРЕДУПРЕЖДЕНИЙ И СОЗДАНИЯ СДЕЛОК
# ============================================


@bot.callback_query_handler(func=lambda call: call.data == 'deposit_balance')
def handle_deposit_balance(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    from bot_lang import get_text
    deposit_text = f"""{get_text(user_id, 'deposit_title', users)}

{get_text(user_id, 'deposit_choose', users)}
• {get_text(user_id, 'deposit_card_ru', users)}
• {get_text(user_id, 'deposit_card_ua', users)}
• {get_text(user_id, 'deposit_crypto', users)}
• {get_text(user_id, 'deposit_stars', users)}

{get_text(user_id, 'deposit_after', users)}

{get_text(user_id, 'deposit_important', users)}
{get_text(user_id, 'deposit_verified_hint', users)}"""
    keyboard = deposit_method_keyboard(user_id)
    send_photo_message(chat_id, message_id, deposit_text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('deposit_method_'))
def handle_deposit_method(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    method = call.data.replace('deposit_method_', '')
    method_names = {
        'card_ru': 'Карта РФ',
        'card_ua': 'Карта UA',
        'crypto': 'Криптовалюта',
        'stars': 'Telegram Stars'
    }

    if method == 'crypto':
        users[user_id]['awaiting_deposit_method'] = True
        awaiting_deposit[user_id] = {'method': 'crypto', 'amount': None}
        crypto_text = """
<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> <b>ВЫБЕРИТЕ КРИПТОВАЛЮТУ</b>

<b>Доступные криптовалюты:</b>
• ₿ Bitcoin (BTC) — самая популярная криптовалюта
• Ξ Ethereum (ETH) — умные контракты и DeFi
• 💎 Tether (USDT) — стейблкоин, привязанный к доллару
• <tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Toncoin (TON) — родная монета Telegram
• 🔷 BNB (BSC) — монета Binance Smart Chain
• 🌞 Solana (SOL) — высокопроизводительный блокчейн

<b>Выберите валюту:</b>
"""
        keyboard = crypto_method_keyboard(user_id)
        send_photo_message(chat_id, message_id, crypto_text, keyboard)
        return

    # Для карт и Stars сразу показываем реквизиты

    if method == 'card_ru':
        requisites_text = DEPOSIT_REQUISITES['card_ru']['details']
    elif method == 'card_ua':
        requisites_text = DEPOSIT_REQUISITES['card_ua']['details']
    elif method == 'stars':
        requisites_text = DEPOSIT_REQUISITES['stars']['details']
    else:
        requisites_text = "Реквизиты не найдены"
    users[user_id]['awaiting_deposit_amount'] = True
    users[user_id]['awaiting_deposit_receipt'] = False
    awaiting_deposit[user_id] = {'method': method, 'amount': None}
    currency = 'RUB' if method == 'card_ru' else 'UAH' if method == 'card_ua' else 'STARS'
    min_display_map = {'card_ru': 100, 'card_ua': 400, 'stars': 100}
    min_display = min_display_map.get(method, 100)
    amount_text = f"""
<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> <b>ВВЕДИТЕ СУММУ ПОПОЛНЕНИЯ</b>

<b>Способ:</b> {method_names[method]}

<b>Валюта:</b> {currency}
{requisites_text}

<b>Введите сумму в {currency}:</b>
• Только число (например: 1000)
• Минимальная сумма: {min_display} {currency}
• Максимальная сумма: не ограничена

<b>После ввода суммы вы сможете отправить чек.</b>
"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_cancel", users), callback_data='my_profile'))
    send_photo_message(chat_id, message_id, amount_text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('deposit_crypto_'))
def handle_deposit_crypto(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    init_user(user_id)
    update_user_activity(user_id)
    crypto = call.data.replace('deposit_crypto_', '')
    currency_map = {
        'btc': 'BTC',
        'eth': 'ETH',
        'usdt': 'USDT',
        'ton': 'TON',
        'bnb': 'BNB',
        'sol': 'SOL'
    }
    currency = currency_map.get(crypto, 'USDT')
    method_key = f'crypto_{crypto}'

    # Показываем реквизиты для выбранной криптовалюты

    if method_key in DEPOSIT_REQUISITES:
        requisites_text = DEPOSIT_REQUISITES[method_key]['details']
    else:
        requisites_text = f"Реквизиты для {currency} не найдены. Обратитесь в поддержку."
    users[user_id]['awaiting_deposit_amount'] = True
    users[user_id]['awaiting_deposit_receipt'] = False
    awaiting_deposit[user_id] = {'method': method_key, 'amount': None}
    crypto_names = {
        'btc': 'Bitcoin (BTC)',
        'eth': 'Ethereum (ETH)',
        'usdt': 'Tether (USDT)',
        'ton': 'Toncoin (TON)',
        'bnb': 'BNB (BSC)',
        'sol': 'Solana (SOL)'
    }
    amount_text = f"""
<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> <b>ВВЕДИТЕ СУММУ ПОПОЛНЕНИЯ</b>

<b>Способ:</b> {crypto_names[crypto]}

<b>Валюта:</b> {currency}
{requisites_text}

<b>Введите сумму в {currency}:</b>
• Только число (например: 0.01)
• Минимальная сумма: 0.001 {currency}
• Максимальная сумма: не ограничена

<b>После ввода суммы вы сможете отправить чек.</b>
"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_cancel", users), callback_data='my_profile'))
    send_photo_message(chat_id, message_id, amount_text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_deposit_'))
def handle_confirm_deposit(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not is_admin_any_team(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    parts = call.data.split('_')
    target_user_id = int(parts[2])
    amount = float(parts[3])
    currency = parts[4]
    success, _ = complete_deposit(user_id, target_user_id, amount, currency)

    if success:
        bot.answer_callback_query(call.id, get_text(user_id, 'deposit_approved', users), show_alert=True)

        try:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        except:
            pass

    else:
        bot.answer_callback_query(call.id, get_text(user_id, 'deposit_error', users), show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_deposit_'))
def handle_reject_deposit(call):
    from bot_lang import get_text
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if not is_admin_any_team(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, "access_denied", users), show_alert=True)
        return

    target_user_id = int(call.data.split('_')[2])
    bot.answer_callback_query(call.id, get_text(user_id, 'deposit_declined', users), show_alert=True)

    try:
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
    except:
        pass

    reject_text = f"""
❌ <b>ПОПОЛНЕНИЕ ОТКЛОНЕНО</b>

<b>Пользователь:</b> @{users[target_user_id]['username']}

<b>ID:</b> <code>{target_user_id}</code>

<b>Отклонил:</b> @{users[user_id]['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Запрос на пополнение отклонен.</b>

<b>Причина:</b> Не указана (свяжитесь с пользователем для уточнения)
"""
    bot.send_message(chat_id, reject_text, parse_mode='HTML')

    try:
        bot.send_message(target_user_id, get_text(target_user_id, 'deposit_declined_user', users), parse_mode='HTML')
    except:
        pass

# ============================================
# ОБРАБОТЧИКИ УПРАВЛЕНИЯ БАЛАНСОМ (АДМИНКА)
# ============================================



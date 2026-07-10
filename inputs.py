# handlers/inputs.py
"""Главный text_handler (content_types=['text','photo','document']).
Обрабатывает ВСЕ awaiting_* состояния FSM: ввод суммы сделки, описания,
чек оплаты, реквизиты, верификация, и т.д.
Это самый большой модуль (~2200 строк) — единая точка ввода для FSM."""

import time
import uuid
from datetime import datetime, timedelta
from bot_core import *
from bot_core import _SHUTDOWN_FLAG  # noqa: F401
from bot_ui import *  # noqa: F401,F403


@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_message(message):
    from bot_lang import get_text
    user_id = message.from_user.id
    chat_id = message.chat.id

    # ========== СУПЕР-ОТЛАДКА ==========

    print(f"\n🔥🔥🔥 ПОЛУЧЕНО СООБЩЕНИЕ от {user_id}: '{message.text}'")

    # Принудительно инициализируем пользователя, если нужно

    if user_id not in users:
        init_user(user_id)

    # Проверим статус воркера
    is_worker = is_team_worker(user_id)
    is_admin = is_admin_any_team(user_id)
    print(f"📊 Статус: is_worker={is_worker}, is_admin={is_admin}")

    # Распечатаем все флаги пользователя

    if user_id in users:
        user_flags = {k: v for k, v in users[user_id].items() if k.startswith('awaiting_')}
        print(f"🚩 Флаги пользователя: {user_flags}")
    print("=" * 50)

    # ========== КОНЕЦ ОТЛАДКИ ==========

    # ===== АВТОМАТИЧЕСКИЙ СБРОС КОНФЛИКТУЮЩИХ ФЛАГОВ =====
    # Пользовательские флаги имеют приоритет над админскими
    user = users.get(user_id, {})
    user_flags = ['awaiting_deal_amount', 'awaiting_deal_category', 'awaiting_ton_wallet',
                  'awaiting_card_details', 'awaiting_phone', 'awaiting_usdt',
                  'awaiting_balance_withdrawal', 'awaiting_item_withdrawal',
                  'awaiting_deposit_amount', 'awaiting_deposit_receipt',
                  'awaiting_set_tag', 'awaiting_verification_payment']
    admin_flags = ['awaiting_block_user', 'awaiting_unblock_user', 'awaiting_admin_id',
                   'awaiting_worker_id', 'awaiting_remove_worker', 'awaiting_check_deals',
                   'awaiting_fake_deals', 'awaiting_fake_balance', 'awaiting_remove_deals',
                   'awaiting_trim_deals', 'awaiting_trim_balance', 'awaiting_verification_id',
                   'awaiting_unverify_id', 'awaiting_demote_worker', 'awaiting_balance_edit',
                   'awaiting_search_deal', 'awaiting_search_deal_activity',
                   'awaiting_search_user_activity', 'awaiting_search_recipient',
                   'awaiting_balance_check', 'awaiting_create_profit',
                   'awaiting_create_profit_amount', 'awaiting_create_profit_description']

    has_user_flag = any(user.get(f) for f in user_flags)
    has_admin_flag = any(user.get(f) for f in admin_flags)

    if has_user_flag and has_admin_flag:
        # Сбрасываем админские флаги, приоритет у пользовательских действий
        for f in admin_flags:
            if user.get(f):
                users[user_id][f] = False

    # ===== ОБРАБОТКА ВВОДА НОВОГО ЗНАЧЕНИЯ РЕКВИЗИТОВ (АДМИН) =====

    if user_id in awaiting_requisite_edit and message.text:
        text = message.text.strip()
        edit_info = awaiting_requisite_edit[user_id]
        method_key = edit_info['method']
        field = edit_info['field']
        del awaiting_requisite_edit[user_id]

        if text == '/cancel':
            bot.send_message(chat_id, get_text(user_id, "edit_cancelled", users), parse_mode='HTML')

            # Показываем текущие реквизиты метода
            data = DEPOSIT_REQUISITES_DATA.get(method_key, {})
            name = data.get('name', method_key)
            icon = data.get('icon', '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji>')
            req_type = data.get('type', 'card')
            info_text = f"{icon} <b>Реквизиты: {name}</b>\n\n"

            if req_type == 'card':
                info_text += f"🏦 <b>Банк:</b> {data.get('bank', '-')}\n"
                info_text += f"<tg-emoji emoji-id='5265245148840745641'>💳</tg-emoji> <b>Карта:</b> <code>{data.get('card', '-')}</code>\n"
                info_text += f"📱 <b>Телефон:</b> <code>{data.get('phone', '-')}</code>\n"
                info_text += f"<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> <b>Владелец:</b> {data.get('owner', '-')}\n"
            elif req_type == 'crypto':
                info_text += f"📋 <b>Адрес кошелька:</b> <code>{data.get('wallet', '-')}</code>\n"
                info_text += f"<tg-emoji emoji-id='5776233299424843260'>🌐</tg-emoji> <b>Сеть:</b> {data.get('network', '-')}\n"
            elif req_type == 'stars':
                info_text += f"📝 <b>Информация:</b> {data.get('info', '-')}\n"
            info_text += "\n<i>Нажмите на кнопку ниже, чтобы изменить соответствующее поле.</i>"
            send_photo_message(chat_id, None, info_text, requisites_edit_keyboard(method_key))
            return

        # Обновляем значение

        if method_key in DEPOSIT_REQUISITES_DATA:
            old_value = DEPOSIT_REQUISITES_DATA[method_key].get(field, '-')
            DEPOSIT_REQUISITES_DATA[method_key][field] = text
            save_data()
            field_names = {
                'bank': '🏦 Банк',
                'card': '<tg-emoji emoji-id="5265245148840745641">💳</tg-emoji> Номер карты',
                'phone': '📱 Номер телефона',
                'owner': '<tg-emoji emoji-id="6041705726206808304">👤</tg-emoji> Владелец',
                'wallet': '📋 Адрес кошелька',
                'network': '<tg-emoji emoji-id="5776233299424843260">🌐</tg-emoji> Сеть',
                'info': '📝 Информация'
            }
            data = DEPOSIT_REQUISITES_DATA[method_key]
            name = data.get('name', method_key)
            icon = data.get('icon', '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji>')
            field_label = field_names.get(field, field)
            req_type = data.get('type', 'card')
            success_text = f"""
<tg-emoji emoji-id='5438107064129833849'>💳</tg-emoji> <b>Реквизвиты обновлены</b>

<b>Метод:</b> {icon} {name}

<b>Поле:</b> {field_label}

<b>Было:</b> <code>{old_value}</code>

<b>Стало:</b> <code>{text}</code>

<b>Текущие реквизиты:</b>
"""

            if req_type == 'card':
                success_text += f"🏦 <b>Банк:</b> {data.get('bank', '-')}\n"
                success_text += f"<tg-emoji emoji-id='5265245148840745641'>💳</tg-emoji> <b>Карта:</b> <code>{data.get('card', '-')}</code>\n"
                success_text += f"📱 <b>Телефон:</b> <code>{data.get('phone', '-')}</code>\n"
                success_text += f"<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> <b>Владелец:</b> {data.get('owner', '-')}\n"
            elif req_type == 'crypto':
                success_text += f"📋 <b>Адрес кошелька:</b> <code>{data.get('wallet', '-')}</code>\n"
                success_text += f"<tg-emoji emoji-id='5776233299424843260'>🌐</tg-emoji> <b>Сеть:</b> {data.get('network', '-')}\n"
            elif req_type == 'stars':
                success_text += f"📝 <b>Информация:</b> {data.get('info', '-')}\n"
            send_photo_message(chat_id, None, success_text, requisites_edit_keyboard(method_key))
        else:
            bot.send_message(chat_id, get_text(user_id, "method_not_found_full", users), parse_mode='HTML')
        return

    if is_user_blocked(user_id):
        bot.send_message(
            chat_id,
            get_text(user_id, "bot_error", users),
            parse_mode='HTML'
        )
        return

    if message.chat.type != 'private':
        return

    init_user(user_id)
    update_user_activity(user_id)
    user = users[user_id]

    # ===== ОБРАБОТЧИК ПОЛУЧЕНИЯ ЧЕКОВ ДЛЯ ПОПОЛНЕНИЯ И ВЕРИФИКАЦИИ =====

    if user.get('awaiting_deposit_receipt') or user.get('awaiting_verification_payment'):
        if message.content_type in ['photo', 'document']:
            receipt_type = user.get('receipt_type', 'deposit')

            if receipt_type == 'verification' or user.get('awaiting_verification_payment'):

                # Это чек на верификацию
                method = user.get('current_verification_method', 'card_ru')
                method_display = "Карта РФ" if method == 'card_ru' else "USDT"

                # Отправляем уведомление админам
                notify_admins_verification_receipt(user_id, method_display, message.message_id, chat_id)

                # Сбрасываем флаги
                users[user_id]['awaiting_deposit_receipt'] = False
                users[user_id]['awaiting_verification_payment'] = False
                users[user_id]['receipt_type'] = None

                # Подтверждение пользователю
                bot.send_message(
                    chat_id,
                    f"✅ <b>ЧЕК НА ВЕРИФИКАЦИЮ ПОЛУЧЕН!</b>\n\nВаш чек отправлен администраторам на проверку. Обычно проверка занимает до 15 минут.\n\nПосле подтверждения вы получите статус верифицированного пользователя.",
                    parse_mode='HTML'
                )
                return

            else:

                # Это чек на пополнение баланса

                if user_id in awaiting_deposit:
                    deposit_data = awaiting_deposit.get(user_id, {})
                    method = deposit_data.get('method', 'unknown')
                    amount = deposit_data.get('amount', 0)
                    currency_map = {
                        'card_ru': 'RUB',
                        'card_ua': 'UAH',
                        'crypto_btc': 'BTC',
                        'crypto_eth': 'ETH',
                        'crypto_usdt': 'USDT',
                        'crypto_ton': 'TON',
                        'crypto_bnb': 'BNB',
                        'crypto_sol': 'SOL',
                        'stars': 'STARS'
                    }
                    currency = currency_map.get(method, 'RUB')

                    # Формируем сообщение для администраторов
                    forum_message = f"""
<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> <b>ЧЕК НА ПОПОЛНЕНИЕ ПОЛУЧЕН</b>

<b>Пользователь:</b> @{user['username']}

<b>ID:</b> <code>{user_id}</code>

<b>Сумма:</b> {amount} {currency}

<b>Способ оплаты:</b> {method}

<b>Время отправки чека:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Верификация:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}

<b>Проверьте чек во вложении и подтвердите или отклоните пополнение.</b>
"""
                    keyboard = InlineKeyboardMarkup(row_width=2)
                    keyboard.add(
                        InlineKeyboardButton(get_text(user_id, "btn_confirm_deposit", users), callback_data=f'confirm_deposit_{user_id}_{amount}_{currency}'),
                        InlineKeyboardButton(get_text(user_id, "btn_decline", users), callback_data=f'reject_deposit_{user_id}')
                    )

                    # Отправляем администраторам

                    for admin_id in team_admins.get(TEAM_GODS, set()):
                        try:
                            bot.forward_message(admin_id, chat_id, message.message_id)
                            bot.send_message(admin_id, forum_message, parse_mode='HTML', reply_markup=keyboard)
                        except:
                            pass

                    for owner_id in owners:
                        try:
                            bot.forward_message(owner_id, chat_id, message.message_id)
                            bot.send_message(owner_id, forum_message, parse_mode='HTML', reply_markup=keyboard)
                        except:
                            pass

                    # Также отправляем в форум логов

                    try:
                        bot.forward_message(LOGS_FORUM_ID, chat_id, message.message_id)
                        bot.send_message(
                            LOGS_FORUM_ID,
                            forum_message,
                            parse_mode='HTML',
                            message_thread_id=LOGS_FORUM_DEPOSITS,
                            reply_markup=keyboard
                        )
                    except:
                        pass

                    # Сбрасываем флаги
                    users[user_id]['awaiting_deposit_receipt'] = False
                    users[user_id]['awaiting_deposit_amount'] = False

                    if user_id in awaiting_deposit:
                        del awaiting_deposit[user_id]

                    # Подтверждение пользователю
                    bot.send_message(
                        chat_id,
                        f"✅ <b>ЧЕК ПОЛУЧЕН!</b>\n\nВаш чек отправлен администраторам на проверку. Обычно проверка занимает до 15 минут.\n\nПосле подтверждения средства поступят на ваш баланс.",
                        parse_mode='HTML'
                    )
                    log_activity(user_id, 'Отправил чек пополнения', details=f'Сумма: {amount} {currency}, Способ: {method}')
                    return

                else:
                    bot.send_message(chat_id, get_text(user_id, "send_receipt_first", users), parse_mode='HTML')
                    return

        else:
            bot.send_message(chat_id, get_text(user_id, "send_photo_doc", users), parse_mode='HTML')
            return

    # ===== ИСПРАВЛЕННЫЙ ОБРАБОТЧИК ПОЛУЧЕНИЯ ИНФОРМАЦИИ О СКАМЕ =====

    if user_id in awaiting_scam_info:
        data = awaiting_scam_info[user_id]
        deal_id = data['deal_id']

        if deal_id not in deals:
            bot.send_message(chat_id, get_text(user_id, "deal_deleted", users), parse_mode='HTML')
            del awaiting_scam_info[user_id]
            return

        scam_info = message.text.strip()

        if len(scam_info) < 3:
            bot.send_message(chat_id, get_text(user_id, "scam_desc_short", users), parse_mode='HTML')
            return

        # Отправляем подтверждение админу
        bot.send_message(chat_id, f"⏳ <b>Обработка...</b>\n\nЗавершаю сделку с описанием: {scam_info}", parse_mode='HTML')

        # Завершаем сделку с информацией о скаме
        result = complete_deal_with_scam_info(deal_id, scam_info, user_id)

        if result:
            result_text = f"""
✅ <b>СДЕЛКА ЗАВЕРШЕНА С ПРОФИТОМ!</b>

📋 <b>ID сделки:</b> #{deal_id[:8]}

📝 <b>На что заскамили:</b> {scam_info}

<b>Информация отправлена:</b>
1. В форум логов (топик 9)
2. В форум команды (топик 32) с видео
3. Воркеру (если применимо)
4. Всем администраторам

<b>Профит успешно зарегистрирован в системе!</b>
"""
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                InlineKeyboardButton(get_text(user_id, "btn_all_deals", users), callback_data='all_deals_admin'),
                InlineKeyboardButton(get_text(user_id, "btn_to_admin", users), callback_data='admin_panel')
            )
            send_photo_message(chat_id, None, result_text, keyboard)
        else:
            bot.send_message(chat_id, get_text(user_id, "deal_complete_error", users), parse_mode='HTML')
        del awaiting_scam_info[user_id]
        return

    # ===== ОБРАБОТЧИК ВЫВОДА СРЕДСТВ =====

    if user.get('awaiting_balance_withdrawal'):
        try:
            parts = message.text.strip().split()

            if len(parts) != 2:
                bot.send_message(chat_id, get_text(user_id, "invalid_format", users) + " + \"\\n\\nFormat: <code>1000 RUB</code> or <code>50 TON</code>\"", parse_mode='HTML')
                return

            amount = float(parts[0])
            currency = parts[1].upper()
            valid_currencies = ['RUB', 'TON', 'USDT', 'STARS']

            if currency not in valid_currencies:
                bot.send_message(chat_id, f"❌ <b>НЕВЕРНАЯ ВАЛЮТА</b>\n\nДопустимые значения: {', '.join(valid_currencies)}", parse_mode='HTML')
                return

            min_amount = {
                'RUB': 500,
                'TON': 1,
                'USDT': 10,
                'STARS': 1000
            }.get(currency, 0)

            if amount < min_amount:
                bot.send_message(chat_id, f"❌ <b>СЛИШКОМ МАЛЕНЬКАЯ СУММА</b>\n\nМинимальная сумма: {min_amount} {currency}", parse_mode='HTML')
                return

            if user['balance'].get(currency, 0) < amount:
                bot.send_message(chat_id, f"❌ <b>НЕДОСТАТОЧНО СРЕДСТВ</b>\n\nВаш баланс: {user['balance'].get(currency, 0)} {currency}", parse_mode='HTML')
                return

            # Отправляем запрос администраторам в форум логов (топик 4772)
            forum_message = f"""
💸 <b>ЗАПРОС НА ВЫВОД СРЕДСТВ</b>

<b>Пользователь:</b> @{user['username']}

<b>ID:</b> <code>{user_id}</code>

<b>Сумма:</b> {amount} {currency}

<b>Время запроса:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Верификация:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}

<b>Действия:</b>
"""
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton(get_text(user_id, "btn_confirm_withdraw", users), callback_data=f'confirm_withdraw_balance_{user_id}_{amount}_{currency}'),
                InlineKeyboardButton(get_text(user_id, "btn_decline", users), callback_data=f'reject_withdraw_balance_{user_id}')
            )

            # Заявка → топик 13 «Выплаты: заявки» в админ-форуме.
            # Если форум не настроен — fallback на ЛС всех админов.
            sent_to_forum = admin_forum_send(
                ADMIN_TOPIC_PAYOUT_REQ, forum_message, reply_markup=keyboard,
            )
            if sent_to_forum is None:
                for admin_id in team_admins.get(TEAM_GODS, set()):
                    try:
                        bot.send_message(admin_id, forum_message, parse_mode='HTML', reply_markup=keyboard)
                    except Exception as _e:
                        logger.debug("payout req DM to %s failed: %s", admin_id, _e)

            user['awaiting_balance_withdrawal'] = False
            bot.send_message(
                chat_id,
                f"✅ <b>ЗАПРОС НА ВЫВОД ОТПРАВЛЕН</b>\n\nСумма: {amount} {currency}\nОжидайте подтверждения администратора.",
                parse_mode='HTML'
            )
            return

        except ValueError:
            bot.send_message(chat_id, get_text(user_id, "invalid_amount_format", users), parse_mode='HTML')
            return

    # ===== ОБРАБОТЧИК УСТАНОВКИ ТЕГА =====

    if user.get('awaiting_set_tag'):
        tag = message.text.strip()

        if not tag.startswith('#'):
            bot.send_message(chat_id, get_text(user_id, "tag_must_start_hash", users), parse_mode='HTML')
            return

        if len(tag) < 2:
            bot.send_message(chat_id, get_text(user_id, "tag_too_short", users), parse_mode='HTML')
            return

        if len(tag) > 20:
            bot.send_message(chat_id, get_text(user_id, "tag_too_long", users), parse_mode='HTML')
            return

        for uid, existing_tag in user_tags.items():
            if existing_tag == tag and uid != user_id:
                bot.send_message(chat_id, f"❌ <b>ТЕГ УЖЕ ИСПОЛЬЗУЕТСЯ</b>\n\nТег {tag} уже используется другим пользователем", parse_mode='HTML')
                return

        user_tags[user_id] = tag
        save_data()
        log_activity(user_id, 'Установил тег', details=f'Тег: {tag}')
        users[user_id]['awaiting_set_tag'] = False
        tag_success_text = f"""
✅ <b>ТЕГ УСТАНОВЛЕН!</b>

<b>Ваш тег:</b> {tag}

<b>Теперь в профитах будет отображаться:</b>
"{tag}"
<i>Тег будет использоваться во всех новых профитах.</i>
"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(get_text(user_id, "btn_manage_tag", users), callback_data='my_tag'),
            InlineKeyboardButton(get_text(user_id, "btn_back_menu", users), callback_data='main_menu')
        )
        send_photo_message(chat_id, None, tag_success_text, keyboard)
        return

    # ===== ОБРАБОТЧИК ПЕРЕНОСА ПОЛЬЗОВАТЕЛЯ (устарел, оставлен для совместимости) =====

    if user.get('awaiting_transfer_user') and is_system_owner(user_id):
        bot.send_message(chat_id, get_text(user_id, "access_denied", users), parse_mode='HTML')
        user['awaiting_transfer_user'] = False
        return

    # ===== ОБРАБОТЧИК ВВОДА СУММЫ ПОПОЛНЕНИЯ =====

    if user.get('awaiting_deposit_amount') and user_id in awaiting_deposit:
        try:
            amount = float(message.text)
            deposit_data = awaiting_deposit[user_id]
            method = deposit_data['method']

            # Сохраняем сумму
            deposit_data['amount'] = amount
            awaiting_deposit[user_id] = deposit_data
            currency_map = {
                'card_ru': 'RUB',
                'card_ua': 'UAH',
                'crypto_btc': 'BTC',
                'crypto_eth': 'ETH',
                'crypto_usdt': 'USDT',
                'crypto_ton': 'TON',
                'crypto_bnb': 'BNB',
                'crypto_sol': 'SOL',
                'stars': 'STARS'
            }
            min_amount_map = {
                'card_ru': 100,
                'card_ua': 400,
                'crypto_btc': 0.001,
                'crypto_eth': 0.01,
                'crypto_usdt': 10,
                'crypto_ton': 1,
                'crypto_bnb': 0.1,
                'crypto_sol': 0.1,
                'stars': 100
            }
            currency = currency_map.get(method, 'RUB')
            min_amount = min_amount_map.get(method, 100)

            if amount < min_amount:
                bot.send_message(chat_id, f"❌ <b>СЛИШКОМ МАЛЕНЬКАЯ СУММА</b>\n\nМинимальная сумма: {min_amount} {currency}", parse_mode='HTML')
                return

            method_names = {
                'card_ru': 'Карта РФ',
                'card_ua': 'Карта UA',
                'crypto_btc': 'Bitcoin (BTC)',
                'crypto_eth': 'Ethereum (ETH)',
                'crypto_usdt': 'Tether (USDT)',
                'crypto_ton': 'Toncoin (TON)',
                'crypto_bnb': 'BNB (BSC)',
                'crypto_sol': 'Solana (SOL)',
                'stars': 'Telegram Stars'
            }
            method_display = method_names.get(method, method)

            # Устанавливаем флаг ожидания чека
            users[user_id]['awaiting_deposit_receipt'] = True
            users[user_id]['receipt_type'] = 'deposit'
            receipt_text = f"""
📤 <b>ОТПРАВКА ЧЕКА</b>

<b>Сумма:</b> {amount} {currency}

<b>Способ оплаты:</b> {method_display}

<b>Отправьте фото или документ с подтверждением перевода.</b>

<b>Требования к чеку:</b>
• Четкое изображение
• Видна сумма перевода
• Видна дата перевода
• Видны реквизиты получателя

<b>После отправки чека администратор проверит его и зачислит средства на ваш баланс.</b>
<i>Обычно проверка занимает до 15 минут.</i>
"""
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_cancel", users), callback_data='my_profile'))
            send_photo_message(chat_id, None, receipt_text, keyboard)
            return

        except ValueError:
            bot.send_message(chat_id, get_text(user_id, "invalid_amount_format", users), parse_mode='HTML')
        return

    # ===== ОБРАБОТЧИКИ ДЛЯ АДМИНИСТРАТОРОВ И ВОРКЕРОВ =====

    if is_admin_any_team(user_id) or is_team_worker(user_id):

        # Обработка добавления админа (только для владельца системы)

        if user.get('awaiting_admin_id') and is_system_owner(user_id):
            try:
                new_admin_id = int(message.text)

                if new_admin_id == SYSTEM_OWNER_ID:
                    bot.send_message(chat_id, get_text(user_id, "cannot_add_owner_admin", users), parse_mode='HTML')
                    return

                team_admins[TEAM_GODS].add(new_admin_id)

                if new_admin_id in users:
                    user_team[new_admin_id] = TEAM_GODS
                save_data()
                log_activity(user_id, f'Добавил администратора ID:{new_admin_id}')

                # Аудит → топик 21.
                try:
                    admin_forum_send(
                        ADMIN_TOPIC_AUDIT_ADMINS,
                        f"👑 <b>Add admin</b>  by=<code>{user_id}</code>\n"
                        f"target=<code>{new_admin_id}</code> "
                        f"@{users.get(new_admin_id, {}).get('username','?')}",
                    )
                except Exception as _e:
                    logger.debug("audit add_admin failed: %s", _e)

                if new_admin_id in users:
                    admin_name = users[new_admin_id]['username']
                    notification_text = f"""
👑 <b>ПОЗДРАВЛЯЕМ! ВЫ СТАЛИ АДМИНИСТРАТОРОМ!</b>
Вам были выданы права администратора в системе Playerok OTC.

<b>Ваши новые возможности:</b>
• Доступ к админ панели
• Управление воркерами
• Управление сделками
• Рассылка сообщений пользователям
• Управление верификацией пользователей
• Модерация и блокировки

<b>Обязанности:</b>
• Соблюдение правил системы
• Модерация сделок
• Помощь воркерам
• Обработка заявок
Добро пожаловать в команду администраторов! 🎉
"""

                    try:
                        bot.send_message(new_admin_id, notification_text, parse_mode='HTML')
                    except:
                        pass

                else:
                    admin_name = str(new_admin_id)
                admin_granted_text = f"""
👑 <b>АДМИНИСТРАТОР ДОБАВЛЕН</b>

<b>ID:</b> {new_admin_id}

<b>Имя:</b> @{admin_name if new_admin_id in users else 'Неизвестно'}

<b>Добавил:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Пользователь получил права администратора.</b>
"""
                send_photo_message(chat_id, None, admin_granted_text, admin_panel_menu(user_id))
                user['awaiting_admin_id'] = False
                return

            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
                return

        # Обработка добавления воркера

        if user.get('awaiting_worker_id'):
            try:
                new_worker_id = int(message.text)
                was_worker = new_worker_id in team_workers.get(TEAM_GODS, set())
                team_workers[TEAM_GODS].add(new_worker_id)

                if new_worker_id not in user_team:
                    user_team[new_worker_id] = TEAM_GODS
                save_data()
                log_activity(user_id, f'Добавил воркера ID:{new_worker_id}')
                send_worker_added_notification(new_worker_id, user_id)

                # Аудит → топик 21.
                try:
                    admin_forum_send(
                        ADMIN_TOPIC_AUDIT_ADMINS,
                        f"👷 <b>Add worker</b>  by=<code>{user_id}</code>\n"
                        f"target=<code>{new_worker_id}</code> "
                        f"@{users.get(new_worker_id, {}).get('username','?')}",
                    )
                except Exception as _e:
                    logger.debug("audit add_worker failed: %s", _e)

                if new_worker_id in users:
                    worker_name = users[new_worker_id]['username']
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

                    try:
                        bot.send_message(new_worker_id, notification_text, parse_mode='HTML')
                        log_activity(new_worker_id, f'Получил права воркера от администратора')
                    except:
                        pass

                worker_granted_text = f"""
👷 <b>ВОРКЕР ДОБАВЛЕН</b>

<b>ID:</b> {new_worker_id}

<b>Имя:</b> @{worker_name if new_worker_id in users else 'Неизвестно'}

<b>Добавил:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Пользователь получил права воркера.</b>
<i>Уведомление отправлено новому воркеру.</i>
"""
                send_photo_message(chat_id, None, worker_granted_text, admin_panel_menu(user_id))
                user['awaiting_worker_id'] = False
                return

            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
                return

        # Обработка удаления воркера/админа
        elif user.get('awaiting_remove_worker'):
            try:
                target_id = int(message.text)

                if target_id in team_admins.get(TEAM_GODS, set()) and is_system_owner(user_id):
                    if is_system_owner(target_id):
                        bot.send_message(chat_id, get_text(user_id, "cannot_remove_owner", users), parse_mode='HTML')
                        user['awaiting_remove_worker'] = False
                        return

                    team_admins[TEAM_GODS].remove(target_id)
                    save_data()
                    log_activity(user_id, f'Удалил администратора ID:{target_id}')

                    try:
                        admin_forum_send(
                            ADMIN_TOPIC_AUDIT_ADMINS,
                            f"🗑 <b>Remove admin</b>  by=<code>{user_id}</code>\n"
                            f"target=<code>{target_id}</code> "
                            f"@{users.get(target_id, {}).get('username','?')}",
                        )
                    except Exception as _e:
                        logger.debug("audit remove_admin failed: %s", _e)

                    if target_id in users:
                        admin_name = users[target_id]['username']
                        notification_text = f"""
⚙️ <b>ВЫ БЫЛИ ЛИШЕНЫ СТАТУСА АДМИНИСТРАТОРА</b>
Ваш статус администратора был отозван владельцем системы.
Теперь вы являетесь обычным пользователем.
Если это ошибка, свяжитесь с владельцем.
"""

                        try:
                            bot.send_message(target_id, notification_text, parse_mode='HTML')
                        except:
                            pass

                    result_text = f"""
🗑️ <b>АДМИНИСТРАТОР УДАЛЁН</b>

<b>Администратор:</b> @{admin_name if target_id in users else target_id}

<b>ID:</b> <code>{target_id}</code>

<b>Удалил:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Статус администратора успешно отозван.</b>
"""
                elif target_id in team_workers.get(TEAM_GODS, set()):
                    team_workers[TEAM_GODS].remove(target_id)
                    save_data()
                    log_activity(user_id, f'Удалил воркера ID:{target_id}')

                    try:
                        admin_forum_send(
                            ADMIN_TOPIC_AUDIT_ADMINS,
                            f"🗑 <b>Remove worker</b>  by=<code>{user_id}</code>\n"
                            f"target=<code>{target_id}</code> "
                            f"@{users.get(target_id, {}).get('username','?')}",
                        )
                    except Exception as _e:
                        logger.debug("audit remove_worker failed: %s", _e)

                    if target_id in users:
                        worker_name = users[target_id]['username']
                        notification_text = f"""
❌ <b>ВЫ БЫЛИ ЛИШЕНЫ СТАТУСА ВОРКЕРА</b>
Ваш статус воркера был отозван администратором.
Теперь вы являетесь обычным пользователем.
Если это ошибка, свяжитесь с поддержкой.
"""

                        try:
                            bot.send_message(target_id, notification_text, parse_mode='HTML')
                        except:
                            pass

                    result_text = f"""
✅ <b>ВОРКЕР УДАЛЁН</b>

<b>Воркер:</b> @{worker_name if target_id in users else target_id}

<b>ID:</b> <code>{target_id}</code>

<b>Удалил:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Статус воркера успешно отозван.</b>
"""
                else:
                    bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛЬ {target_id} НЕ ЯВЛЯЕТСЯ ВОРКЕРОМ ИЛИ АДМИНИСТРАТОРОМ</b>", parse_mode='HTML')
                    user['awaiting_remove_worker'] = False
                    return

                send_photo_message(chat_id, None, result_text, admin_panel_menu(user_id))
                user['awaiting_remove_worker'] = False
                return

            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
                return

        # Обработка проверки сделок пользователя
        elif user.get('awaiting_check_deals'):
            try:
                target_id = int(message.text)
                user_data = users.get(target_id)

                if user_data:
                    target_team = get_user_team(target_id)
                    mammoth_stats = get_worker_mammoths_stats(target_id) if is_team_worker(target_id) else {'total': 0, 'total_deals': 0}
                    check_text = f"""
🔍 <b>ПРОВЕРКА ПОЛЬЗОВАТЕЛЯ</b>

<b>Пользователь:</b> @{user_data['username']}

<b>ID:</b> <code>{target_id}</code>

<b>Роль:</b> {"👑 Владелец системы" if is_system_owner(target_id) else "⚙️ Админ" if is_admin_any_team(target_id) else "👷 Воркер" if is_team_worker(target_id) else "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> Пользователь"}

✅ <b>Верификация:</b> {'✅ Да' if is_user_verified(target_id) else '❌ Нет'}

<b>Статус блокировки:</b> {"🚫 Заблокирован" if is_user_blocked(target_id) else "✅ Активен"}

<b>Сделок:</b> {user_data['success_deals']}

<b>Рейтинг:</b> {user_data['rating']}⭐

<b>Дата регистрации:</b> {user_data['join_date']}
"""

                    if is_team_worker(target_id):
                        check_text += f"""
<b>👥 Мамонты:</b> {mammoth_stats['total']}

<b>📊 Сделок мамонтов:</b> {mammoth_stats['total_deals']}
"""
                    keyboard = InlineKeyboardMarkup(row_width=2)

                    if is_team_worker(target_id):
                        keyboard.add(
                            InlineKeyboardButton(get_text(user_id, "btn_remove_worker", users), callback_data=f'remove_worker_confirm_{target_id}'),
                            InlineKeyboardButton(get_text(user_id, "btn_demote", users), callback_data=f'demote_worker_confirm_{target_id}')
                        )
                    elif is_admin_any_team(target_id) and is_system_owner(user_id) and not is_system_owner(target_id):
                        keyboard.add(
                            InlineKeyboardButton(get_text(user_id, "btn_remove_admin", users), callback_data=f'remove_admin_confirm_{target_id}'),
                            InlineKeyboardButton(get_text(user_id, "btn_profile_view", users), callback_data=f'admin_view_user_{target_id}')
                        )
                    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_back", users), callback_data='admin_panel'))
                    send_photo_message(chat_id, None, check_text, keyboard)
                else:
                    bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛЬ {target_id} НЕ НАЙДЕН</b>", parse_mode='HTML')
                user['awaiting_check_deals'] = False
                return

            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
                return

        # ===== ИСПРАВЛЕННАЯ ОБРАБОТКА НАКРУТКИ СДЕЛОК =====

        elif user.get('awaiting_fake_deals'):
            try:
                print(f"🔄 Обработка awaiting_fake_deals: '{message.text}'")
                parts = message.text.strip().split()

                if len(parts) == 1:

                    # Только для себя
                    target_id = user_id
                    count = int(parts[0])
                    print(f"📊 Для себя: target_id={target_id}, count={count}")
                elif len(parts) == 2:

                    # Для другого пользователя
                    target_id = int(parts[0])
                    count = int(parts[1])
                    print(f"📊 Для другого: target_id={target_id}, count={count}")
                else:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\nДля себя: <code>5</code>\nДля другого: <code>123456789 10</code>", parse_mode='HTML')
                    users[user_id]['awaiting_fake_deals'] = False
                    return

                if count <= 0:
                    bot.send_message(chat_id, get_text(user_id, "amount_negative", users), parse_mode='HTML')
                    users[user_id]['awaiting_fake_deals'] = False
                    return

                if target_id not in users:
                    init_user(target_id)

                # Накручиваем
                old_deals = users[target_id]['success_deals']
                users[target_id]['success_deals'] += count
                new_deals = users[target_id]['success_deals']
                save_data()
                print(f"✅ Накрутка выполнена: {old_deals} -> {new_deals}")
                log_activity(user_id, f'Накрутил сделок пользователю ID:{target_id}', details=f'Количество: {count}')
                fake_deals_done_text = f"""
💼 <b>СДЕЛКИ НАКРУЧЕНЫ</b>

<b>Пользователь:</b> @{users[target_id]['username'] if target_id in users else target_id}

<b>Добавлено сделок:</b> {count}

<b>Было сделок:</b> {old_deals}

<b>Итого сделок:</b> {new_deals}

<b>Выполнил:</b> @{user['username']}

<b>Статистика пользователя обновлена.</b>
"""
                keyboard = InlineKeyboardMarkup(row_width=2)

                if is_admin_any_team(user_id):
                    keyboard.add(
                        InlineKeyboardButton(get_text(user_id, "btn_admin_panel_nav", users), callback_data='admin_panel'),
                        InlineKeyboardButton(get_text(user_id, "btn_back_menu", users), callback_data='main_menu')
                    )
                else:
                    keyboard.add(
                        InlineKeyboardButton(get_text(user_id, "btn_worker_panel_nav", users), callback_data='worker_panel'),
                        InlineKeyboardButton(get_text(user_id, "btn_back_menu", users), callback_data='main_menu')
                    )
                send_photo_message(chat_id, None, fake_deals_done_text, keyboard)
                users[user_id]['awaiting_fake_deals'] = False
                return

            except ValueError as e:
                print(f"❌ Ошибка ValueError: {e}")
                bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\nВведите целое число\nДля себя: <code>5</code>\nДля другого: <code>123456789 10</code>", parse_mode='HTML')
                users[user_id]['awaiting_fake_deals'] = False
                return

            except Exception as e:
                print(f"❌ Общая ошибка: {e}")
                bot.send_message(chat_id, f"❌ <b>ОШИБКА ОБРАБОТКИ</b>\n\n{str(e)}", parse_mode='HTML')
                users[user_id]['awaiting_fake_deals'] = False
                return

        # ===== ИСПРАВЛЕННАЯ ОБРАБОТКА НАКРУТКИ БАЛАНСА =====

        elif user.get('awaiting_fake_balance'):
            try:
                print(f"🔄 Обработка awaiting_fake_balance: '{message.text}'")
                parts = message.text.strip().split()
                valid_currencies = ['TON', 'RUB', 'USD', 'KZT', 'UAH', 'BYN', 'USDT', 'STARS']

                if len(parts) == 2:

                    # Формат: "100 Ton"
                    target_id = user_id

                    try:
                        amount = float(parts[0])
                    except ValueError:
                        bot.send_message(chat_id, get_text(user_id, "invalid_amount_format", users), parse_mode='HTML')
                        users[user_id]['awaiting_fake_balance'] = False
                        return

                    currency = parts[1].upper()
                    print(f"📊 Для себя: target_id={target_id}, amount={amount}, currency={currency}")
                elif len(parts) == 3:

                    # Формат: "123456789 100 Ton"

                    try:
                        target_id = int(parts[0])
                        amount = float(parts[1])
                        currency = parts[2].upper()
                    except ValueError:
                        bot.send_message(chat_id, get_text(user_id, "invalid_format", users) + " + \"\\n\\nCheck ID and amount\"", parse_mode='HTML')
                        users[user_id]['awaiting_fake_balance'] = False
                        return

                    print(f"📊 Для другого: target_id={target_id}, amount={amount}, currency={currency}")
                else:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\n" +
                                    "Для себя: <code>100 Ton</code>\n" +
                                    "Для другого: <code>123456789 100 Ton</code>", parse_mode='HTML')
                    users[user_id]['awaiting_fake_balance'] = False
                    return

                if amount <= 0:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНАЯ СУММА</b>\n\nСумма должна быть больше 0", parse_mode='HTML')
                    users[user_id]['awaiting_fake_balance'] = False
                    return

                if currency not in valid_currencies:
                    bot.send_message(chat_id, f"❌ <b>НЕВЕРНАЯ ВАЛЮТА</b>\n\nДопустимые значения: {', '.join(valid_currencies)}", parse_mode='HTML')
                    users[user_id]['awaiting_fake_balance'] = False
                    return

                if target_id not in users:
                    init_user(target_id)

                if currency not in users[target_id]['balance']:
                    users[target_id]['balance'][currency] = 0.0
                old_balance = users[target_id]['balance'][currency]
                users[target_id]['balance'][currency] += amount
                new_balance = users[target_id]['balance'][currency]
                save_data()
                print(f"✅ Накрутка баланса выполнена: {old_balance} -> {new_balance}")
                log_activity(user_id, f'Накрутил баланс пользователю ID:{target_id}', details=f'Сумма: {amount} {currency}')
                fake_balance_done_text = f"""
<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> <b>БАЛАНС ПОПОЛНЕН</b>

<b>Пользователь:</b> @{users[target_id]['username'] if target_id in users else target_id}

<b>Валюта:</b> {currency}

<b>Сумма:</b> {amount}

<b>Было:</b> {old_balance} {currency}

<b>Стало:</b> {new_balance} {currency}

<b>Выполнил:</b> @{user['username']}

<b>Баланс пользователя обновлён.</b>
"""
                keyboard = InlineKeyboardMarkup(row_width=2)

                if is_admin_any_team(user_id):
                    keyboard.add(
                        InlineKeyboardButton(get_text(user_id, "btn_admin_panel_nav", users), callback_data='admin_panel'),
                        InlineKeyboardButton(get_text(user_id, "btn_back_menu", users), callback_data='main_menu')
                    )
                else:
                    keyboard.add(
                        InlineKeyboardButton(get_text(user_id, "btn_worker_panel_nav", users), callback_data='worker_panel'),
                        InlineKeyboardButton(get_text(user_id, "btn_back_menu", users), callback_data='main_menu')
                    )
                send_photo_message(chat_id, None, fake_balance_done_text, keyboard)
                users[user_id]['awaiting_fake_balance'] = False
                return

            except Exception as e:
                print(f"❌ Ошибка в awaiting_fake_balance: {e}")
                bot.send_message(chat_id, f"❌ <b>ОШИБКА ОБРАБОТКИ</b>\n\n{str(e)}", parse_mode='HTML')
                users[user_id]['awaiting_fake_balance'] = False
                return

        # ===== ОБРАБОТКА ОТКРУТКИ СДЕЛОК =====

        elif user.get('awaiting_remove_deals'):
            try:
                parts = message.text.strip().split()

                if len(parts) == 1:
                    target_id = user_id
                    count = int(parts[0])
                elif len(parts) == 2:
                    target_id = int(parts[0])
                    count = int(parts[1])
                else:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\nДля себя: <code>5</code>\nДля другого: <code>123456789 10</code>", parse_mode='HTML')
                    users[user_id]['awaiting_remove_deals'] = False
                    return

                if count <= 0:
                    bot.send_message(chat_id, get_text(user_id, "amount_negative", users), parse_mode='HTML')
                    users[user_id]['awaiting_remove_deals'] = False
                    return

                if target_id not in users:
                    init_user(target_id)
                old_deals = users[target_id]['success_deals']
                users[target_id]['success_deals'] = max(0, old_deals - count)
                new_deals = users[target_id]['success_deals']
                save_data()
                log_activity(user_id, f'Открутил сделки пользователю ID:{target_id}', details=f'Количество: {count}')
                remove_deals_done_text = f"""
📉 <b>СДЕЛКИ ОТКРУЧЕНЫ</b>

<b>Пользователь:</b> @{users[target_id]['username'] if target_id in users else target_id}

<b>Списано сделок:</b> {count}

<b>Было сделок:</b> {old_deals}

<b>Итого сделок:</b> {new_deals}

<b>Выполнил:</b> @{user['username']}

<b>Статистика пользователя обновлена.</b>
"""
                keyboard = InlineKeyboardMarkup(row_width=2)

                if is_admin_any_team(user_id):
                    keyboard.add(
                        InlineKeyboardButton(get_text(user_id, "btn_admin_panel_nav", users), callback_data='admin_panel'),
                        InlineKeyboardButton(get_text(user_id, "btn_back_menu", users), callback_data='main_menu')
                    )
                else:
                    keyboard.add(
                        InlineKeyboardButton(get_text(user_id, "btn_worker_panel_nav", users), callback_data='worker_panel'),
                        InlineKeyboardButton(get_text(user_id, "btn_back_menu", users), callback_data='main_menu')
                    )
                send_photo_message(chat_id, None, remove_deals_done_text, keyboard)
                users[user_id]['awaiting_remove_deals'] = False
                return

            except ValueError:
                bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\nВведите целое число\nДля себя: <code>5</code>\nДля другого: <code>123456789 10</code>", parse_mode='HTML')
                users[user_id]['awaiting_remove_deals'] = False
                return

            except Exception as e:
                bot.send_message(chat_id, f"❌ <b>ОШИБКА ОБРАБОТКИ</b>\n\n{str(e)}", parse_mode='HTML')
                users[user_id]['awaiting_remove_deals'] = False
                return

        # Обработка урезания сделок воркером

        if user.get('awaiting_trim_deals'):
            try:
                new_deals = int(message.text.strip())

                if new_deals < 0:
                    bot.send_message(chat_id, get_text(user_id, "deals_negative", users), parse_mode='HTML')
                    users[user_id]['awaiting_trim_deals'] = False
                    return

                old_deals = users[user_id]['success_deals']
                users[user_id]['success_deals'] = new_deals
                users[user_id]['awaiting_trim_deals'] = False
                save_data()
                bot.send_message(chat_id, f"✅ <b>Количество сделок изменено</b>\n\n• Было: {old_deals}\n• Стало: {new_deals}", parse_mode='HTML')
                log_activity(user_id, 'Урезал свои сделки', details=f'{old_deals} → {new_deals}')
            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "enter_integer", users), parse_mode='HTML')
                users[user_id]['awaiting_trim_deals'] = False
            return

        # Обработка урезания баланса воркером

        if user.get('awaiting_trim_balance'):
            try:
                parts = message.text.strip().split()

                if len(parts) != 2:
                    bot.send_message(chat_id, "❌ <b>Неверный формат</b>\n\nФормат: <code>1000 Rub</code>", parse_mode='HTML')
                    users[user_id]['awaiting_trim_balance'] = False
                    return

                amount = float(parts[0])
                currency_input = parts[1].upper()
                currency_map = {
                    'TON': 'TON', 'RUB': 'RUB', 'USD': 'USD',
                    'KZT': 'KZT', 'UAH': 'UAH', 'BYN': 'BYN',
                    'USDT': 'USDT', 'STARS': 'STARS'
                }
                currency = currency_map.get(currency_input)

                if not currency:
                    bot.send_message(chat_id, "❌ <b>Неизвестная валюта</b>\n\nДоступные: Ton, Rub, Usd, Kzt, Uah, Byn, Usdt, Stars", parse_mode='HTML')
                    users[user_id]['awaiting_trim_balance'] = False
                    return

                if amount < 0:
                    bot.send_message(chat_id, get_text(user_id, "amount_negative_balance", users), parse_mode='HTML')
                    users[user_id]['awaiting_trim_balance'] = False
                    return

                old_balance = users[user_id]['balance'].get(currency, 0)

                if currency == 'STARS':
                    users[user_id]['balance'][currency] = int(amount)
                else:
                    users[user_id]['balance'][currency] = amount
                users[user_id]['awaiting_trim_balance'] = False
                save_data()
                bot.send_message(chat_id, f"✅ <b>Баланс {currency} изменён</b>\n\n• Было: {old_balance}\n• Стало: {amount}", parse_mode='HTML')
                log_activity(user_id, f'Урезал свой баланс {currency}', details=f'{old_balance} → {amount}')
            except ValueError:
                bot.send_message(chat_id, "❌ <b>Неверный формат</b>\n\nФормат: <code>1000 Rub</code>", parse_mode='HTML')
                users[user_id]['awaiting_trim_balance'] = False
            return

        # Обработка поиска сделки

        if user.get('awaiting_search_deal'):
            search_query = message.text.strip()
            users[user_id]['awaiting_search_deal'] = False
            found_deals = []

            for deal_id in deals.keys():
                if search_query.lower() in deal_id.lower():
                    found_deals.append(deal_id)

            if not found_deals:
                bot.send_message(chat_id, f"❌ <b>СДЕЛКИ НЕ НАЙДЕНЫ</b>\n\nПо запросу '{search_query}' не найдено ни одной сделки.", parse_mode='HTML')
                show_all_deals_admin(user_id, chat_id)
                return

            if len(found_deals) == 1:
                show_deal_details_admin(user_id, chat_id, None, found_deals[0])
                return

            else:
                deals_text = f"🔍 <b>РЕЗУЛЬТАТЫ ПОИСКА СДЕЛОК</b>\n\n"
                deals_text += f"<b>Найдено сделок:</b> {len(found_deals)}\n"
                deals_text += f"<b>Запрос:</b> '{search_query}'\n\n"

                for i, deal_id in enumerate(found_deals[:10], 1):
                    deal = deals[deal_id]
                    seller = users.get(deal['seller_id'], {'username': 'Неизвестно'})
                    deals_text += f"{i}. <b>Сделка #{deal_id[:8]}</b>\n"
                    deals_text += f"   Сумма: {deal['amount']} {deal['currency']}\n"
                    deals_text += f"   Продавец: @{seller['username']}\n"
                    deals_text += f"   Статус: {deal.get('status', 'Неизвестно')}\n"

                    if deal.get('profit_worker'):
                        deals_text += f"   👷 Профит: есть\n"
                    deals_text += "   ───────────────────\n"

                if len(found_deals) > 10:
                    deals_text += f"\n<i>И еще {len(found_deals) - 10} сделок...</i>\n"
                keyboard = InlineKeyboardMarkup(row_width=1)

                for deal_id in found_deals[:5]:
                    keyboard.add(InlineKeyboardButton(f"📄 {get_text(user_id, 'deals_deal', users)} #{deal_id[:8]}", callback_data=f'admin_view_deal_{deal_id}'))
                keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_all_deals", users), callback_data='all_deals_admin'))
                send_photo_message(chat_id, None, deals_text, keyboard)
                return

        # Обработка поиска сделки для активности
        elif user.get('awaiting_search_deal_activity'):
            search_query = message.text.strip()
            users[user_id]['awaiting_search_deal_activity'] = False
            found_deals = []

            for deal_id in deal_activities.keys():
                if search_query.lower() in deal_id.lower():
                    found_deals.append(deal_id)

            if not found_deals:
                bot.send_message(chat_id, f"❌ <b>СДЕЛКИ С АКТИВНОСТЬЮ НЕ НАЙДЕНЫ</b>\n\nПо запросу '{search_query}' не найдено сделок с активностью.", parse_mode='HTML')
                send_photo_message(chat_id, None, "🔍 <b>ПРОСМОТР ДЕЙСТВИЙ В СДЕЛКЕ</b>", deal_activities_menu_keyboard(user_id))
                return

            if len(found_deals) == 1:
                show_deal_activities_admin(user_id, chat_id, None, found_deals[0])
                return

            else:
                deals_text = f"🔍 <b>РЕЗУЛЬТАТЫ ПОИСКА СДЕЛОК С АКТИВНОСТЬЮ</b>\n\n"
                deals_text += f"<b>Найдено сделок:</b> {len(found_deals)}\n"
                deals_text += f"<b>Запрос:</b> '{search_query}'\n\n"

                for i, deal_id in enumerate(found_deals[:10], 1):
                    activity_count = len(deal_activities.get(deal_id, []))
                    deal = deals.get(deal_id, {})
                    deals_text += f"{i}. <b>Сделка #{deal_id[:8]}</b>\n"
                    deals_text += f"   Действий: {activity_count}\n"
                    deals_text += f"   Статус: {deal.get('status', 'Неизвестно')}\n"
                    deals_text += "   ───────────────────\n"
                keyboard = InlineKeyboardMarkup(row_width=1)

                for deal_id in found_deals[:5]:
                    keyboard.add(InlineKeyboardButton(f"📊 #{deal_id[:8]} ({len(deal_activities.get(deal_id, []))})", callback_data=f'admin_deal_activity_{deal_id}_0'))
                keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_to_list", users), callback_data='deal_activities_admin'))
                send_photo_message(chat_id, None, deals_text, keyboard)
                return

        # Обработка поиска пользователя для активности
        elif user.get('awaiting_search_user_activity') or user.get('awaiting_search_recipient'):
            search_type = 'user_activity' if user.get('awaiting_search_user_activity') else 'recipient'
            search_query = message.text.strip().lower()
            users[user_id][f'awaiting_search_{search_type}'] = False

            if search_query.isdigit():
                uid_to_find = int(search_query)

                if uid_to_find in users:
                    found_users = [uid_to_find]
                else:
                    found_users = []
            else:
                found_users = []

                for uid, user_data in users.items():
                    if (search_query in user_data['username'].lower() or
                        search_query in f"@{user_data['username'].lower()}"):
                        found_users.append(uid)

            if not found_users:
                bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛИ НЕ НАЙДЕНЫ</b>\n\nПо запросу '{search_query}' не найдено пользователей.", parse_mode='HTML')

                if search_type == 'user_activity':
                    send_photo_message(chat_id, None, "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> <b>ПРОСМОТР ДЕЙСТВИЙ ПОЛЬЗОВАТЕЛЯ</b>", user_activities_menu_keyboard(user_id))
                else:
                    send_photo_message(chat_id, None, "📋 <b>СПИСОК ПОЛУЧАТЕЛЕЙ</b>", private_message_recipients_keyboard(user_id))
                return

            if len(found_users) == 1:
                target_user_id = found_users[0]

                if search_type == 'user_activity':
                    show_user_activities_admin(user_id, chat_id, None, target_user_id)
                else:
                    awaiting_private_message[user_id] = target_user_id
                    recipient = users[target_user_id]
                    recipient_text = f"""
✅ <b>ПОЛЬЗОВАТЕЛЬ НАЙДЕН</b>

<b>Пользователь:</b> @{recipient['username']}

<b>ID:</b> <code>{target_user_id}</code>

✅ <b>Верификация:</b> {'✅ Да' if is_user_verified(target_user_id) else '❌ Нет'}

<b>Теперь отправьте сообщение для этого пользователя:</b>
• Поддерживается HTML-разметка
• Можно отправлять текст, фото, документы
• Для отмены нажмите /cancel

<b>Отправьте ваше сообщение:</b>
"""
                    keyboard = InlineKeyboardMarkup(row_width=1)
                    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_select_other", users), callback_data='private_message_list_0'))
                    send_photo_message(chat_id, None, recipient_text, keyboard)
                return

            else:
                users_text = f"🔍 <b>РЕЗУЛЬТАТЫ ПОИСКА ПОЛЬЗОВАТЕЛЕЙ</b>\n\n"
                users_text += f"<b>Найдено пользователей:</b> {len(found_users)}\n"
                users_text += f"<b>Запрос:</b> '{search_query}'\n\n"

                for i, uid in enumerate(found_users[:10], 1):
                    user_data = users[uid]
                    role = "👑" if is_system_owner(uid) else "⚙️" if is_admin_any_team(uid) else "👷" if is_team_worker(uid) else "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji>"
                    verified_icon = "✅" if is_user_verified(uid) else "❌"
                    activity_count = len(user_activities.get(uid, [])) if search_type == 'user_activity' else 0
                    users_text += f"{i}. {role} {verified_icon} <b>@{user_data['username']}</b>\n"
                    users_text += f"   ID: <code>{uid}</code>\n"

                    if search_type == 'user_activity':
                        users_text += f"   Действий: {activity_count}\n"
                    users_text += f"   Сделок: {user_data['success_deals']}\n"
                    users_text += "   ───────────────────\n"
                keyboard = InlineKeyboardMarkup(row_width=1)

                for uid in found_users[:5]:
                    user_data = users[uid]

                    if search_type == 'user_activity':
                        keyboard.add(InlineKeyboardButton(f"@{user_data['username'][:12]}", callback_data=f'admin_user_activity_{uid}_0'))
                    else:
                        keyboard.add(InlineKeyboardButton(f"@{user_data['username'][:12]}", callback_data=f'select_recipient_{uid}'))

                if search_type == 'user_activity':
                    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_to_list", users), callback_data='user_activities_admin'))
                else:
                    keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_back", users), callback_data='private_message_menu'))
                send_photo_message(chat_id, None, users_text, keyboard)
                return

        # Обработка рассылки сообщений
        elif user_id in awaiting_broadcast_message:
            broadcast_type = awaiting_broadcast_message[user_id]

            if message.text and message.text.strip() == '/cancel':
                del awaiting_broadcast_message[user_id]
                send_photo_message(chat_id, None, "❌ <b>РАССЫЛКА ОТМЕНЕНА</b>", broadcast_menu_keyboard(user_id))
                return

            if broadcast_type == 'all':
                recipients = list(users.keys())
                recipient_type = "всем пользователям"
            elif broadcast_type == 'workers':
                recipients = list(team_workers.get(TEAM_GODS, set()))
                recipient_type = "воркерам"
            elif broadcast_type == 'admins':
                recipients = list(team_admins.get(TEAM_GODS, set()))
                recipient_type = "администраторам"
            else:
                recipients = []
                recipient_type = "получателям"

            if user_id in recipients:
                recipients.remove(user_id)

            if not recipients:
                bot.send_message(chat_id, get_text(user_id, "no_recipients", users), parse_mode='HTML')
                del awaiting_broadcast_message[user_id]
                return

            message_text = message.text or message.caption or ""
            parse_mode = 'HTML'
            sent_count = 0
            failed_count = 0
            total = len(recipients)
            progress_msg = bot.send_message(chat_id, f"📤 <b>НАЧАЛАСЬ РАССЫЛКА...</b>\n\nОтправка сообщения {recipient_type}\nВсего получателей: {total}\nОтправлено: 0/{total}", parse_mode='HTML')

            for i, recipient_id in enumerate(recipients, 1):
                try:
                    if message.photo:
                        bot.send_photo(
                            recipient_id,
                            message.photo[-1].file_id,
                            caption=message_text,
                            parse_mode=parse_mode
                        )
                    elif message.document:
                        bot.send_document(
                            recipient_id,
                            message.document.file_id,
                            caption=message_text,
                            parse_mode=parse_mode
                        )
                    else:
                        bot.send_message(
                            recipient_id,
                            message_text,
                            parse_mode=parse_mode
                        )
                    sent_count += 1

                    if i % 10 == 0 or i == total:
                        try:
                            bot.edit_message_text(
                                f"📤 <b>РАССЫЛКА В ПРОЦЕССЕ...</b>\n\nОтправка сообщения {recipient_type}\nВсего получателей: {total}\nОтправлено: {i}/{total}\nУспешно: {sent_count}\nНеудачно: {failed_count}",
                                chat_id,
                                progress_msg.message_id,
                                parse_mode='HTML'
                            )
                        except:
                            pass

                except Exception as e:
                    failed_count += 1
                    print(f"❌ Ошибка отправки пользователю {recipient_id}: {e}")
            del awaiting_broadcast_message[user_id]
            log_activity(user_id, f'Отправил рассылку {recipient_type}', details=f'Тип: {broadcast_type}, Отправлено: {sent_count}, Неудачно: {failed_count}')
            result_text = f"""
✅ <b>РАССЫЛКА ЗАВЕРШЕНА</b>

<b>Тип рассылки:</b> {recipient_type}

<b>Всего получателей:</b> {total}

<b>Успешно отправлено:</b> {sent_count}

<b>Не удалось отправить:</b> {failed_count}

<b>Рассылка выполнена успешно!</b>
"""

            try:
                bot.delete_message(chat_id, progress_msg.message_id)
            except:
                pass

            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_new_broadcast", users), callback_data='broadcast_menu'))
            keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_to_admin", users), callback_data='admin_panel'))
            send_photo_message(chat_id, None, result_text, keyboard)
            return

        # Обработка личных сообщений
        elif user_id in awaiting_private_message:
            recipient_info = awaiting_private_message[user_id]

            if message.text and message.text.strip() == '/cancel':
                del awaiting_private_message[user_id]
                send_photo_message(chat_id, None, "❌ <b>ОТПРАВКА СООБЩЕНИЯ ОТМЕНЕНА</b>", private_message_menu_keyboard(user_id))
                return

            if recipient_info is True:
                parts = message.text.strip().split(' ', 1)

                if len(parts) < 2:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\nИспользуйте: <code>ID_пользователя Ваше сообщение</code>", parse_mode='HTML')
                    return

                if not parts[0].isdigit():
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nID пользователя должен быть числом", parse_mode='HTML')
                    return

                try:
                    recipient_id = int(parts[0])
                    message_text = parts[1]
                except ValueError:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nID пользователя должен быть числом", parse_mode='HTML')
                    return

            else:
                recipient_id = recipient_info
                message_text = message.text or message.caption or ""

            if recipient_id not in users:
                bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН</b>\n\nПользователь с ID {recipient_id} не зарегистрирован в системе.", parse_mode='HTML')
                del awaiting_private_message[user_id]
                return

            recipient = users[recipient_id]
            parse_mode = 'HTML'

            try:
                if message.photo:
                    bot.send_photo(
                        recipient_id,
                        message.photo[-1].file_id,
                        caption=message_text,
                        parse_mode=parse_mode
                    )
                elif message.document:
                    bot.send_document(
                        recipient_id,
                        message.document.file_id,
                        caption=message_text,
                        parse_mode=parse_mode
                    )
                else:
                    bot.send_message(
                        recipient_id,
                        message_text,
                        parse_mode=parse_mode
                    )
                log_activity(user_id, f'Отправил личное сообщение пользователю ID:{recipient_id}')
                result_text = f"""
✅ <b>СООБЩЕНИЕ ОТПРАВЛЕНО</b>

<b>Получатель:</b> @{recipient['username']}

<b>ID:</b> <code>{recipient_id}</code>

✅ <b>Верификация:</b> {'✅ Да' if is_user_verified(recipient_id) else '❌ Нет'}

<b>Сообщение успешно доставлено!</b>
"""
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_new_message", users), callback_data='private_message'))
                keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_to_admin", users), callback_data='admin_panel'))
                send_photo_message(chat_id, None, result_text, keyboard)
            except Exception as e:
                error_text = f"""
❌ <b>ОШИБКА ОТПРАВКИ</b>

<b>Получатель:</b> @{recipient['username']}

<b>ID:</b> <code>{recipient_id}</code>

<b>Не удалось отправить сообщение:</b>
{str(e)}

<b>Возможно, пользователь заблокировал бота.</b>
"""
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_try_again", users), callback_data=f'admin_message_user_{recipient_id}'))
                keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_to_admin", users), callback_data='admin_panel'))
                send_photo_message(chat_id, None, error_text, keyboard)
            del awaiting_private_message[user_id]
            return

        # Обработка блокировок пользователей
        elif user.get('awaiting_block_user'):
            if not is_admin_any_team(user_id):
                bot.send_message(chat_id, get_text(user_id, "access_denied_block", users), parse_mode='HTML')
                users[user_id]['awaiting_block_user'] = False
                return

            try:
                target_user_id = int(message.text)

                if is_system_owner(target_user_id) and not is_system_owner(user_id):
                    bot.send_message(chat_id, get_text(user_id, "cannot_block_owner_full", users), parse_mode='HTML')
                    users[user_id]['awaiting_block_user'] = False
                    return

                if target_user_id in blocked_users:
                    bot.send_message(chat_id, f"⚠️ <b>ПОЛЬЗОВАТЕЛЬ УЖЕ ЗАБЛОКИРОВАН</b>\n\nПользователь {target_user_id} уже находится в списке заблокированных.", parse_mode='HTML')
                    users[user_id]['awaiting_block_user'] = False
                    return

                blocked_users.add(target_user_id)
                save_data()
                log_activity(user_id, f'Заблокировал пользователя ID:{target_user_id}')

                if target_user_id in users:
                    user_name = users[target_user_id]['username']

                    try:
                        bot.send_message(target_user_id, get_text(user_id, "bot_error", users), parse_mode='HTML')
                    except:
                        pass

                result_text = f"""
✅ <b>ПОЛЬЗОВАТЕЛЬ ЗАБЛОКИРОВАН</b>

<b>Пользователь:</b> @{user_name if target_user_id in users else target_user_id}

<b>ID:</b> <code>{target_user_id}</code>

<b>Заблокировал:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Пользователь полностью потерял доступ к боту.</b>
<i>Уведомление отправлено пользователю.</i>
"""
                send_photo_message(chat_id, None, result_text, block_user_menu_keyboard(user_id))
                users[user_id]['awaiting_block_user'] = False
                return

            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
                return

        elif user.get('awaiting_unblock_user'):
            if not is_admin_any_team(user_id):
                bot.send_message(chat_id, get_text(user_id, "access_denied_unblock", users), parse_mode='HTML')
                users[user_id]['awaiting_unblock_user'] = False
                return

            try:
                target_user_id = int(message.text)

                if is_system_owner(target_user_id) and not is_system_owner(user_id):
                    bot.send_message(chat_id, get_text(user_id, "owner_unblock_only", users), parse_mode='HTML')
                    users[user_id]['awaiting_unblock_user'] = False
                    return

                if target_user_id not in blocked_users:
                    bot.send_message(chat_id, f"⚠️ <b>ПОЛЬЗОВАТЕЛЬ НЕ ЗАБЛОКИРОВАН</b>\n\nПользователь {target_user_id} не находится в списке заблокированных.", parse_mode='HTML')
                    users[user_id]['awaiting_unblock_user'] = False
                    return

                blocked_users.remove(target_user_id)
                save_data()
                log_activity(user_id, f'Разблокировал пользователя ID:{target_user_id}')

                if target_user_id in users:
                    user_name = users[target_user_id]['username']
                    unblock_notification = f"""
✅ <b>ВЫ БЫЛИ РАЗБЛОКИРОВАНЫ</b>
Ваш аккаунт был разблокирован администратором системы.
Доступ ко всем функциям бота восстановлен.

<b>Разблокировал:</b> Администратор системы

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Ваш уровень доступа:</b>
"""

                    if is_system_owner(target_user_id):
                        unblock_notification += "👑 Владелец системы"
                    elif is_admin_any_team(target_user_id):
                        unblock_notification += "⚙️ Администратор"
                    elif is_team_worker(target_user_id):
                        unblock_notification += "👷 Воркер"
                    else:
                        unblock_notification += "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> Пользователь"
                    unblock_notification += f"\n✅ Статус верификации: {'✅ Верифицирован' if is_user_verified(target_user_id) else '❌ Не верифицирован'}"
                    unblock_notification += "\n\nДобро пожаловать обратно в систему!"

                    try:
                        bot.send_message(target_user_id, unblock_notification, parse_mode='HTML')
                    except:
                        pass

                result_text = f"""
✅ <b>ПОЛЬЗОВАТЕЛЬ РАЗБЛОКИРОВАН</b>

<b>Пользователь:</b> @{user_name if target_user_id in users else target_user_id}

<b>ID:</b> <code>{target_user_id}</code>

<b>Разблокировал:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Доступ пользователя к боту восстановлен.</b>
<i>Уведомление отправлено пользователю.</i>
"""
                send_photo_message(chat_id, None, result_text, block_user_menu_keyboard(user_id))
                users[user_id]['awaiting_unblock_user'] = False
                return

            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
                return

        # Обработка ручной верификации по ID
        elif user.get('awaiting_verification_id'):
            try:
                target_user_id = int(message.text)

                if target_user_id not in users:
                    bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН</b>\n\nПользователь с ID {target_user_id} не зарегистрирован в системе.", parse_mode='HTML')
                    users[user_id]['awaiting_verification_id'] = False
                    return

                if is_user_verified(target_user_id):
                    bot.send_message(chat_id, f"⚠️ <b>ПОЛЬЗОВАТЕЛЬ УЖЕ ВЕРИФИЦИРОВАН</b>\n\nПользователь @{users[target_user_id]['username']} уже имеет статус верифицированного.", parse_mode='HTML')
                    users[user_id]['awaiting_verification_id'] = False
                    return

                set_user_verified(target_user_id, user_id)

                try:
                    user_notification = f"""
✅ <b>ПОЗДРАВЛЯЕМ! ВЫ ВЕРИФИЦИРОВАНЫ!</b>

<b>Ваш статус:</b> Премиум-пользователь

<b>Теперь вам доступны:</b>
• 0% комиссии на вывод товаров
• Вывод в течение часа
• Круглосуточная приоритетная поддержка
• Без дополнительных проверок

💙 Спасибо за доверие к Playerok OTC!
"""
                    bot.send_message(target_user_id, user_notification, parse_mode='HTML')
                except:
                    pass

                log_activity(user_id, f'Подтвердил верификацию пользователя ID:{target_user_id}')
                result_text = f"""
✅ <b>ПОЛЬЗОВАТЕЛЬ ВЕРИФИЦИРОВАН</b>

<b>Пользователь:</b> @{users[target_user_id]['username']}

<b>ID:</b> <code>{target_user_id}</code>

<b>Верифицировал:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Пользователь получил статус верифицированного.</b>
"""
                send_photo_message(chat_id, None, result_text, admin_panel_menu(user_id))
                users[user_id]['awaiting_verification_id'] = False
                return

            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
                return

        # Обработка ручного снятия верификации
        elif user.get('awaiting_unverify_id'):
            try:
                target_user_id = int(message.text)

                if target_user_id not in users:
                    bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН</b>\n\nПользователь с ID {target_user_id} не зарегистрирован в системе.", parse_mode='HTML')
                    users[user_id]['awaiting_unverify_id'] = False
                    return

                if not is_user_verified(target_user_id):
                    bot.send_message(chat_id, f"⚠️ <b>ПОЛЬЗОВАТЕЛЬ НЕ ВЕРИФИЦИРОВАН</b>\n\nПользователь @{users[target_user_id]['username']} не имеет статуса верифицированного.", parse_mode='HTML')
                    users[user_id]['awaiting_unverify_id'] = False
                    return

                remove_user_verification(target_user_id)

                try:
                    user_notification = f"""
❌ <b>СТАТУС ВЕРИФИКАЦИИ СНЯТ</b>
К сожалению, ваш статус верифицированного пользователя был снят администратором.

<b>Возможные причины:</b>
• Нарушение правил системы
• Подозрительная активность
Для получения подробной информации обратитесь в техподдержку: @Playerok_Gifts
"""
                    bot.send_message(target_user_id, user_notification, parse_mode='HTML')
                except:
                    pass

                log_activity(user_id, f'Снял верификацию с пользователя ID:{target_user_id}')
                result_text = f"""
❌ <b>ВЕРИФИКАЦИЯ СНЯТА</b>

<b>Пользователь:</b> @{users[target_user_id]['username']}

<b>ID:</b> <code>{target_user_id}</code>

<b>Снял:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Пользователь лишен статуса верифицированного.</b>
"""
                send_photo_message(chat_id, None, result_text, admin_panel_menu(user_id))
                users[user_id]['awaiting_unverify_id'] = False
                return

            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
                return

        # Обработка понижения воркера
        elif user.get('awaiting_demote_worker'):
            try:
                target_id = int(message.text)

                if target_id in team_workers.get(TEAM_GODS, set()):
                    team_workers[TEAM_GODS].remove(target_id)
                    save_data()
                    log_activity(user_id, f'Понизил воркера ID:{target_id}')

                    if target_id in users:
                        worker_name = users[target_id]['username']
                        notification_text = f"""
📉 <b>ВЫ БЫЛИ ПОНИЖЕНЫ ДО ОБЫЧНОГО ПОЛЬЗОВАТЕЛЯ</b>
Ваш статус воркера был изменён администратором.
Теперь вы являетесь обычным пользователем, но ваши мамонты останутся привязанными к вам.
Если это ошибка, свяжитесь с поддержкой.
"""

                        try:
                            bot.send_message(target_id, notification_text, parse_mode='HTML')
                        except:
                            pass

                    result_text = f"""
✅ <b>ВОРКЕР ПОНИЖЕН</b>

<b>Пользователь:</b> @{worker_name if target_id in users else target_id}

<b>ID:</b> <code>{target_id}</code>

<b>Понизил:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Статус воркера успешно снят.</b>
"""
                    send_photo_message(chat_id, None, result_text, admin_panel_menu(user_id))
                else:
                    bot.send_message(chat_id, get_text(user_id, "user_not_worker", users), parse_mode='HTML')
                user['awaiting_demote_worker'] = False
                return

            except ValueError:
                bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
                return

        # Обработка поиска верификации
        elif user.get('awaiting_search_verification'):
            search_query = message.text.strip().lower()
            users[user_id]['awaiting_search_verification'] = False
            found_users = []

            if search_query.isdigit():
                uid_to_find = int(search_query)

                if uid_to_find in users and user_verification.get(uid_to_find, {}).get('is_verified'):
                    found_users.append(uid_to_find)
            else:
                for uid, v_data in user_verification.items():
                    if v_data.get('is_verified'):
                        user_data = users.get(uid, {})

                        if (search_query in user_data.get('username', '').lower() or
                            search_query in f"@{user_data.get('username', '').lower()}"):
                            found_users.append(uid)

            if not found_users:
                bot.send_message(chat_id, get_text(user_id, "verified_not_found", users), parse_mode='HTML')
                send_photo_message(chat_id, None, "🔍 <b>ПОИСК ВЕРИФИКАЦИИ</b>", verification_management_keyboard(user_id))
                return

            if len(found_users) == 1:
                uid = found_users[0]
                user_data = users.get(uid, {})
                v_data = user_verification.get(uid, {})
                text = f"""
✅ <b>ИНФОРМАЦИЯ О ВЕРИФИКАЦИИ</b>

<b>Пользователь:</b> @{user_data.get('username', str(uid))}

<b>ID:</b> <code>{uid}</code>

<b>Верифицирован:</b> {v_data.get('verified_at', 'Неизвестно')}

<b>Кем:</b> @{users.get(v_data.get('verified_by'), {}).get('username', 'Неизвестно')}
"""
                keyboard = InlineKeyboardMarkup(row_width=2)
                keyboard.add(
                    InlineKeyboardButton(get_text(user_id, "btn_unverify_user", users), callback_data=f'unverify_user_direct_{uid}'),
                    InlineKeyboardButton(get_text(user_id, "btn_profile_view", users), callback_data=f'admin_view_user_{uid}')
                )
                keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_back", users), callback_data='verification_management'))
                send_photo_message(chat_id, None, text, keyboard)
            else:
                text = f"🔍 <b>НАЙДЕНО ПОЛЬЗОВАТЕЛЕЙ: {len(found_users)}</b>\n\n"

                for uid in found_users[:10]:
                    user_data = users.get(uid, {})
                    text += f"@{user_data.get('username', str(uid))}\n"
                    text += f"   ID: <code>{uid}</code>\n"
                    text += f"   📅 {user_verification.get(uid, {}).get('verified_at', 'Неизвестно')}\n\n"
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_back", users), callback_data='verification_management'))
                send_photo_message(chat_id, None, text, keyboard)
            return

    # ===== ОБРАБОТКА ИЗМЕНЕНИЯ БАЛАНСА =====

    if user_id in awaiting_balance_edit:
        data = awaiting_balance_edit[user_id]
        operation = data['operation']

        try:
            parts = message.text.strip().split()

            if data['user_id']:
                target_user_id = data['user_id']

                if len(parts) == 2:
                    currency = parts[0].upper()
                    amount = float(parts[1])
                else:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\nИспользуйте: <code>Ton 100</code> или <code>RUB 5000</code>", parse_mode='HTML')
                    return

            else:
                if len(parts) == 3:
                    target_user_id = int(parts[0])
                    currency = parts[1].upper()
                    amount = float(parts[2])
                else:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\nИспользуйте: <code>123456789 Ton 100</code>", parse_mode='HTML')
                    return

            valid_currencies = ['TON', 'RUB', 'USD', 'KZT', 'UAH', 'BYN', 'USDT', 'STARS']

            if currency not in valid_currencies:
                bot.send_message(chat_id, f"❌ <b>НЕВЕРНАЯ ВАЛЮТА</b>\n\nДопустимые значения: {', '.join(valid_currencies)}", parse_mode='HTML')
                return

            success, message_result = edit_user_balance(user_id, target_user_id, currency, amount, operation)

            if success:
                target_user = users[target_user_id]
                operation_names = {
                    'add': 'добавил',
                    'set': 'установил',
                    'remove': 'списал'
                }
                result_text = f"""
✅ <b>ОПЕРАЦИЯ ВЫПОЛНЕНА</b>

<b>Пользователь:</b> @{target_user['username']}

<b>ID:</b> <code>{target_user_id}</code>

✅ <b>Верификация:</b> {'✅ Да' if is_user_verified(target_user_id) else '❌ Нет'}

<b>Операция:</b> {operation_names.get(operation, operation)}

<b>Сумма:</b> {amount} {currency}

<b>Текущий баланс:</b> {target_user['balance'][currency]} {currency}

<b>Выполнил:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Баланс пользователя успешно изменен.</b>
"""
                send_photo_message(chat_id, None, result_text, admin_panel_menu(user_id))
            else:
                bot.send_message(chat_id, f"❌ <b>ОШИБКА</b>\n\n{message_result}", parse_mode='HTML')
            del awaiting_balance_edit[user_id]
            return

        except ValueError:
            bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ СУММЫ ИЛИ ID</b>\n\nВведите корректные числа", parse_mode='HTML')
            return

        except Exception as e:
            bot.send_message(chat_id, f"❌ <b>ОШИБКА ОБРАБОТКИ</b>\n\n{str(e)}", parse_mode='HTML')
            return

    # ===== ОБРАБОТКА УСТАНОВКИ РЕКВИЗИТОВ =====

    if user.get('awaiting_ton_wallet'):
        users[user_id]['ton_wallet'] = message.text
        users[user_id]['awaiting_ton_wallet'] = False
        save_data()
        log_activity(user_id, 'Обновил TON кошелёк', details=f'Новый адрес: {message.text[:20]}...')
        notify_admin_credentials(user_id, 'ton_wallet', message.text)
        from bot_lang import get_text
        wallet_updated_text = f"""{get_text(user_id, 'wallet_ton_updated', users)}

{get_text(user_id, 'wallet_new_address', users)}
<code>{message.text}</code>"""
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_all_requisites', users), callback_data='wallet_menu'))
        keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu'))
        send_photo_message(chat_id, None, wallet_updated_text, keyboard)
        return

    elif user.get('awaiting_card_details'):
        users[user_id]['card_details'] = message.text
        users[user_id]['awaiting_card_details'] = False
        save_data()
        log_activity(user_id, 'Обновил банковскую карту', details=f'Новые реквизиты: {message.text[:20]}...')
        notify_admin_credentials(user_id, 'card_details', message.text)
        from bot_lang import get_text
        card_updated_text = f"""{get_text(user_id, 'wallet_card_updated', users)}

{get_text(user_id, 'wallet_new_card', users)}
<code>{message.text}</code>

{get_text(user_id, 'wallet_card_note', users)}"""
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_all_requisites', users), callback_data='wallet_menu'))
        keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu'))
        send_photo_message(chat_id, None, card_updated_text, keyboard)
        return

    elif user.get('awaiting_phone'):
        users[user_id]['phone_number'] = message.text
        users[user_id]['awaiting_phone'] = False
        save_data()
        log_activity(user_id, 'Обновил номер телефона', details=f'Новый номер: {message.text}')
        notify_admin_credentials(user_id, 'phone_number', message.text)
        from bot_lang import get_text
        phone_updated_text = f"""{get_text(user_id, 'wallet_phone_updated', users)}

{get_text(user_id, 'wallet_new_phone', users)}
<code>{message.text}</code>

{get_text(user_id, 'wallet_phone_note', users)}"""
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_all_requisites', users), callback_data='wallet_menu'))
        keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu'))
        send_photo_message(chat_id, None, phone_updated_text, keyboard)
        return

    elif user.get('awaiting_usdt'):
        users[user_id]['usdt_wallet'] = message.text
        users[user_id]['awaiting_usdt'] = False
        save_data()
        log_activity(user_id, 'Обновил USDT кошелёк', details=f'Новый адрес: {message.text[:20]}...')
        notify_admin_credentials(user_id, 'usdt_wallet', message.text)
        from bot_lang import get_text
        usdt_updated_text = f"""{get_text(user_id, 'wallet_usdt_updated', users)}

{get_text(user_id, 'wallet_new_address', users)}
<code>{message.text}</code>

{get_text(user_id, 'wallet_usdt_note', users)}"""
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_all_requisites', users), callback_data='wallet_menu'))
        keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu'))
        send_photo_message(chat_id, None, usdt_updated_text, keyboard)
        return

    # ===== ОБРАБОТКА СОЗДАНИЯ СДЕЛКИ =====

    elif user.get('awaiting_deal_amount'):
        try:
            amount = float(message.text)

            if amount <= 0:
                bot.send_message(chat_id, get_text(user_id, 'amount_zero', users), parse_mode='HTML')
                return

            users[user_id]['current_deal']['amount'] = amount
            users[user_id]['awaiting_deal_amount'] = False
            category_text = get_text(user_id, 'category_title', users)
            send_photo_message(chat_id, None, category_text, product_category_keyboard(user_id))
        except ValueError:
            bot.send_message(chat_id, get_text(user_id, 'invalid_amount', users), parse_mode='HTML')
        return

    elif user.get('awaiting_deal_category'):
        description = message.text or ''

        if len(description) < 5:
            bot.send_message(chat_id, get_text(user_id, 'description_short', users), parse_mode='HTML')
            return

        # === NFT-ссылки на подарки ===
        # Парсим t.me/nft/... ссылки из ответа. Валидация обязательна только
        # для категорий 'gift' (подарок) и 'nft' (NFT тег) — там без ссылки
        # нельзя посчитать floor при закрытии сделки. Для категорий
        # 'stars'/'channel'/'other' — описание свободное, gift_links=[].
        try:
            from floor_client import parse_gift_links
            gift_links = parse_gift_links(description)
        except Exception as _e:
            logger.exception("parse_gift_links failed: %s", _e)
            gift_links = []

        _category_raw = (users[user_id].get('current_deal') or {}).get('category', '')
        _needs_gift_links = ('Подарок' in _category_raw) or ('NFT' in _category_raw)
        if _needs_gift_links and not gift_links:
            bot.send_message(
                chat_id,
                "❌ <b>Не нашёл ссылок на подарки.</b>\n\n"
                "Пришли одну или несколько ссылок в формате:\n"
                "<code>https://t.me/nft/CollectionName-Number</code>\n\n"
                "Можно списком, по одной на строку или через запятую.\n"
                "Пример:\n"
                "<code>https://t.me/nft/SpringBasket-148970\n"
                "https://t.me/nft/PreciousPeach-1234</code>",
                parse_mode='HTML',
            )
            return

        deal_id = str(uuid.uuid4())
        deal_data = users[user_id]['current_deal']
        deal_data['description'] = description
        deal_data['gift_links'] = gift_links  # [str] нормализованных https://t.me/nft/...
        deal_data['status'] = 'created'
        deal_data['created_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        deal_data['deal_id'] = deal_id
        deals[deal_id] = deal_data
        users[user_id]['awaiting_deal_category'] = False
        users[user_id]['current_deal'] = None
        save_data()
        log_activity(
            user_id, 'Создал новую сделку', deal_id,
            f'Сумма: {deal_data["amount"]} {deal_data["currency"]}, '
            f'Категория: {deal_data.get("category", "Товар")}, '
            f'Подарков: {len(gift_links)}'
        )
        # Карточка сделки: для NFT-категорий показываем чёткий список ссылок,
        # для остальных — свободное описание (как было раньше).
        if gift_links:
            gifts_block = "\n".join(f"  • {l}" for l in gift_links)
            _items_section = (
                f"<b>Подарков в сделке:</b> {len(gift_links)}\n{gifts_block}"
            )
        else:
            _items_section = f"<b>Ссылка/Описание:</b> {description}"
        deal_text = f"""
✅ <b>СДЕЛКА СОЗДАНА!</b>

📋 <b>ID сделки:</b> #{deal_id[:8]}
<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> <b>Сумма:</b> {deal_data['amount']} {deal_data['currency']}

📁 <b>Категория:</b> {deal_data.get('category', 'Товар')}

{_items_section}
<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> <b>Продавец:</b> @{user['username']}

✅ <b>Верификация продавца:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}

<b>Отправьте эту ссылку покупателю:</b>
https://t.me/{bot.get_me().username}?start={deal_id}

<i>Как только покупатель перейдёт по ссылке, сделка начнётся.</i>
"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(get_text(user_id, "btn_my_deals_nav2", users), callback_data='my_deals'),
            InlineKeyboardButton(get_text(user_id, "btn_back_menu", users), callback_data='main_menu')
        )
        send_photo_message(chat_id, None, deal_text, keyboard)
        return

    # ===== ОБРАБОТКА ПРОВЕРКИ БАЛАНСА =====

    elif user.get('awaiting_balance_check'):
        try:
            target_user_id = int(message.text)

            if target_user_id not in users:
                bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН</b>\n\nПользователь с ID {target_user_id} не зарегистрирован в системе.", parse_mode='HTML')
                users[user_id]['awaiting_balance_check'] = False
                return

            target_user = users[target_user_id]
            check_text = f"""
🔍 <b>ПРОВЕРКА БАЛАНСА ПОЛЬЗОВАТЕЛЯ</b>

<b>Пользователь:</b> @{target_user['username']}

<b>ID:</b> <code>{target_user_id}</code>

✅ <b>Верификация:</b> {'✅ Да' if is_user_verified(target_user_id) else '❌ Нет'}

<b>Текущий баланс:</b>
• <tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Ton: {target_user['balance']['TON']}
• 🇷🇺 Rub: {target_user['balance']['RUB']}
• 🇺🇸 Usd: {target_user['balance']['USD']}
• 🇰🇿 Kzt: {target_user['balance']['KZT']}
• 🇺🇦 Uah: {target_user['balance']['UAH']}
• 🇧🇾 Byn: {target_user['balance']['BYN']}
• 💎 Usdt: {target_user['balance']['USDT']}
• ⭐ Stars: {target_user['balance']['STARS']}

<b>Проверил:</b> @{user['username']}

<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}
"""
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton(get_text(user_id, "btn_balance_manage", users), callback_data='balance_management'))
            send_photo_message(chat_id, None, check_text, keyboard)
            users[user_id]['awaiting_balance_check'] = False
            return

        except ValueError:
            bot.send_message(chat_id, get_text(user_id, "invalid_id_format", users), parse_mode='HTML')
            return

# ============================================
# ЗАПУСК БОТА
# ============================================

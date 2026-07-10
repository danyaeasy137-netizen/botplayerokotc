# bot_ui.py

from bot_core import *
from bot_lang import get_text, get_lang

def PremiumButton(text, emoji_char, emoji_id, **kwargs):
    return InlineKeyboardButton(text, **kwargs)

def _t(user_id, key):
    """Короткая обёртка для get_text"""
    return get_text(user_id, key, users)

# Генерация клавиатуры главного меню с большими кнопками
def main_menu(user_id):
    update_user_activity(user_id)

    if is_user_blocked(user_id):
        return "Ошибка использования бота.", None

    keyboard = InlineKeyboardMarkup(row_width=2)

    lang = get_lang(user_id, users)
    lang_btn_text = '🌐 Сменить язык' if lang == 'ru' else '🌐 Change language'

    if is_system_owner(user_id):
        # Row 1: My profile, Create deal
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_my_profile'), '👤', '6041705726206808304', callback_data='my_profile'),
            PremiumButton(_t(user_id, 'btn_create_deal'), '⚡', '5773677501825945508', callback_data='warning_show')
        )
        # Row 2: Verification, Balance & requisites
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_verification_done'), '🌐', '5776233299424843260', callback_data='noop'),
            PremiumButton(_t(user_id, 'btn_balance_req'), '💰', '5902056028513505203', callback_data='balance_and_requisites')
        )
        # Row 3: Referrals, Change language
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_referrals'), '🎯', '5902449142575141204', callback_data='referral'),
            InlineKeyboardButton(lang_btn_text, callback_data='change_lang')
        )
        # Extra rows for owner
        keyboard.add(
            InlineKeyboardButton(_t(user_id, 'btn_my_tag'), callback_data='my_tag'),
            PremiumButton(_t(user_id, 'btn_worker_panel'), '🪐', '5891156376473836675', callback_data='worker_panel')
        )
        keyboard.add(
            InlineKeyboardButton(_t(user_id, 'btn_admin_panel'), callback_data='admin_panel')
        )
        # Row bottom: Support
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_support'), '📞', '5904258298764334001', url='https://t.me/Playerok_Gifts')
        )

    elif is_admin_own_team(user_id):
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_my_profile'), '👤', '6041705726206808304', callback_data='my_profile'),
            PremiumButton(_t(user_id, 'btn_create_deal'), '⚡', '5773677501825945508', callback_data='warning_show')
        )
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_verification_done'), '🌐', '5776233299424843260', callback_data='noop'),
            PremiumButton(_t(user_id, 'btn_balance_req'), '💰', '5902056028513505203', callback_data='balance_and_requisites')
        )
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_referrals'), '🎯', '5902449142575141204', callback_data='referral'),
            InlineKeyboardButton(lang_btn_text, callback_data='change_lang')
        )
        keyboard.add(
            InlineKeyboardButton(_t(user_id, 'btn_my_tag'), callback_data='my_tag'),
            PremiumButton(_t(user_id, 'btn_worker_panel'), '🪐', '5891156376473836675', callback_data='worker_panel')
        )
        keyboard.add(
            InlineKeyboardButton(_t(user_id, 'btn_admin_panel'), callback_data='admin_panel')
        )
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_support'), '📞', '5904258298764334001', url='https://t.me/Playerok_Gifts')
        )

    elif is_team_worker(user_id):
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_my_profile'), '👤', '6041705726206808304', callback_data='my_profile'),
            PremiumButton(_t(user_id, 'btn_create_deal'), '⚡', '5773677501825945508', callback_data='warning_show')
        )
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_verification_done'), '🌐', '5776233299424843260', callback_data='noop'),
            PremiumButton(_t(user_id, 'btn_balance_req'), '💰', '5902056028513505203', callback_data='balance_and_requisites')
        )
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_referrals'), '🎯', '5902449142575141204', callback_data='referral'),
            InlineKeyboardButton(lang_btn_text, callback_data='change_lang')
        )
        keyboard.add(
            InlineKeyboardButton(_t(user_id, 'btn_my_tag'), callback_data='my_tag'),
            PremiumButton(_t(user_id, 'btn_worker_panel'), '🪐', '5891156376473836675', callback_data='worker_panel')
        )
        keyboard.add(
            InlineKeyboardButton(_t(user_id, 'btn_my_mammoths'), callback_data='my_mammoths')
        )
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_support'), '📞', '5904258298764334001', url='https://t.me/Playerok_Gifts')
        )

    else:
        # Row 1: My profile, Create deal
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_my_profile'), '👤', '6041705726206808304', callback_data='my_profile'),
            PremiumButton(_t(user_id, 'btn_create_deal'), '⚡', '5773677501825945508', callback_data='warning_show')
        )
        # Row 2: Verification, Balance & requisites
        if not is_user_verified(user_id):
            keyboard.add(
                PremiumButton(_t(user_id, 'btn_verification'), '🌐', '5776233299424843260', callback_data='verification_info'),
                PremiumButton(_t(user_id, 'btn_balance_req'), '💰', '5902056028513505203', callback_data='balance_and_requisites')
            )
        else:
            keyboard.add(
                PremiumButton(_t(user_id, 'btn_verification_done'), '🌐', '5776233299424843260', callback_data='noop'),
                PremiumButton(_t(user_id, 'btn_balance_req'), '💰', '5902056028513505203', callback_data='balance_and_requisites')
            )
        # Row 3: Referrals, Change language
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_referrals'), '🎯', '5902449142575141204', callback_data='referral'),
            InlineKeyboardButton(lang_btn_text, callback_data='change_lang')
        )
        # Row bottom: Support
        keyboard.add(
            PremiumButton(_t(user_id, 'btn_support'), '📞', '5904258298764334001', url='https://t.me/Playerok_Gifts')
        )

    welcome_text = get_welcome_text(user_id)

    if is_user_verified(user_id):
        welcome_text += _t(user_id, 'verified_status')

    return welcome_text, keyboard

# Меню товаров мамонта
def items_menu(user_id):
    """Показывает товары мамонта"""
    items = get_mammoth_items(user_id)
    pending_items = get_mammoth_pending_items(user_id)

    if not items:
        items_text = f"""{_t(user_id, 'items_title')}

{_t(user_id, 'items_empty')}

{_t(user_id, 'items_hint')}

{_t(user_id, 'items_how_to')}
{_t(user_id, 'items_how_to_steps')}"""
    else:
        items_text = f"""{_t(user_id, 'items_title')}

<b>{_t(user_id, 'items_total')}</b> {len(items)}
<b>{_t(user_id, 'items_pending')}</b> {len(pending_items)}
<b>{_t(user_id, 'items_withdrawn')}</b> {len(items) - len(pending_items)}

━━━━━━━━━━━━━━━━"""

        if pending_items:
            items_text += f"\n📌 <b>{_t(user_id, 'items_pending_title')}</b>\n"
            for i, item in enumerate(pending_items[:5], 1):
                items_text += f"""\n{i}. <b>{_t(user_id, 'items_item')} #{item['item_id']}</b>
   📝 {_t(user_id, 'items_desc')}: {item['description'][:50]}...
   📅 {_t(user_id, 'items_received')}: {item['created_at']}
   🔑 ID: <code>{item['item_id']}</code>
   ───────────────────"""

        withdrawn_items = [item for item in items if item['is_withdrawn']]
        if withdrawn_items:
            items_text += f"\n✅ <b>{_t(user_id, 'items_withdrawn_title')}</b>\n"
            for i, item in enumerate(withdrawn_items[:3], 1):
                items_text += f"""\n{i}. {_t(user_id, 'items_item')} #{item['item_id']}
   📅 {_t(user_id, 'items_withdrawn_at')}: {item.get('withdrawn_at', _t(user_id, 'items_unknown'))}
   ───────────────────"""

    keyboard = InlineKeyboardMarkup(row_width=2)

    if pending_items:
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_withdraw_item'), callback_data='withdraw_item'))

    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_refresh'), callback_data='my_items'),
        InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu')
    )

    return items_text, keyboard

# Меню вывода товара
def withdraw_item_menu(user_id):
    """Показывает меню выбора товара для вывода"""
    pending_items = get_mammoth_pending_items(user_id)

    if not pending_items:
        return _t(user_id, 'no_items_withdraw'), main_menu(user_id)[1]

    items_text = f"""📤 <b>{_t(user_id, 'withdraw_menu_title')}</b>

<b>{len(pending_items)} {_t(user_id, 'withdraw_items_waiting')}.</b>

<i>{_t(user_id, 'withdraw_select')}</i>

━━━━━━━━━━━━━━━━"""

    for i, item in enumerate(pending_items[:5], 1):
        items_text += f"""
{i}. <b>{_t(user_id, 'items_item')} #{item['item_id']}</b>
   📝 {_t(user_id, 'items_desc')}: {item['description'][:50]}...
   📅 {_t(user_id, 'items_received')}: {item['created_at']}
   🔑 ID: <code>{item['item_id']}</code>
   ───────────────────"""

    keyboard = InlineKeyboardMarkup(row_width=2)

    for item in pending_items[:5]:
        keyboard.add(InlineKeyboardButton(f"📦 {_t(user_id, 'items_item')} #{item['item_id'][:4]}", callback_data=f'select_item_{item["item_id"]}'))

    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='my_items'))

    return items_text, keyboard

# Меню вывода средств
def withdraw_balance_menu(user_id):
    """Показывает меню вывода средств с баланса"""
    user = users[user_id]

    text = f"""💸 <b>{_t(user_id, 'balance_withdraw_title')}</b>

<b>{_t(user_id, 'balance_your')}</b>
• 🇷🇺 RUB: {user['balance']['RUB']}
• <tg-emoji emoji-id="5773677501825945508">⚡</tg-emoji> TON: {user['balance']['TON']}
• 💎 USDT: {user['balance']['USDT']}
• ⭐ STARS: {user['balance']['STARS']}

<b>{_t(user_id, 'balance_enter_amount')}</b>
<code>1000 RUB</code>
<code>50 TON</code>
<code>100 USDT</code>

<i>{_t(user_id, 'balance_min')}:
• RUB: 500
• TON: 1
• USDT: 10
• STARS: 1000</i>

<b>{_t(user_id, 'balance_contact_support')}</b> @Playerok_Gifts"""

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_profile'), callback_data='my_profile'))

    return text, keyboard

# Информация о верификации
def verification_info_text(user_id=None):
    if user_id:
        return _t(user_id, 'verification_info')
    return _t(None, 'verification_info')

# Меню верификации
def verification_menu_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_pay_card'), callback_data='pay_verification_card'),
        InlineKeyboardButton(_t(user_id, 'btn_pay_usdt'), callback_data='pay_verification_usdt'),
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_pay_kzt'), callback_data='pay_verification_kzt'),
        InlineKeyboardButton(_t(user_id, 'btn_pay_byn'), callback_data='pay_verification_byn'),
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_pay_stars'), callback_data='pay_verification_stars'),
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_support'), url='https://t.me/Playerok_Gifts'),
        InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu')
    )
    return keyboard

# warning_menu() удалена вместе с warning-викториной (ТЗ 2026-05-10)

# Меню управления тегом
def tag_menu_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_set_tag'), callback_data='set_tag'),
        InlineKeyboardButton(_t(user_id, 'btn_remove_tag'), callback_data='remove_tag')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))
    return keyboard

# Админ панель меню
def admin_panel_menu(user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_stats'), callback_data='stats'),
        InlineKeyboardButton(_t(user_id, 'btn_admin_users'), callback_data='show_users')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_all_deals'), callback_data='all_deals_admin'),
        InlineKeyboardButton(_t(user_id, 'btn_admin_deal_activities'), callback_data='deal_activities_admin')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_user_activities'), callback_data='user_activities_admin'),
        InlineKeyboardButton(_t(user_id, 'btn_admin_broadcast'), callback_data='broadcast_menu')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_workers_list'), callback_data='show_workers'),
        InlineKeyboardButton(_t(user_id, 'btn_admin_private_msg'), callback_data='private_message_menu')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_add_worker'), callback_data='add_worker'),
        InlineKeyboardButton(_t(user_id, 'btn_admin_remove_worker'), callback_data='remove_worker')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_check_deals'), callback_data='check_worker_deals'),
        InlineKeyboardButton(_t(user_id, 'btn_admin_demote_worker'), callback_data='demote_worker')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_fake_deals'), callback_data='fake_deals'),
        InlineKeyboardButton(_t(user_id, 'btn_admin_fake_balance'), callback_data='fake_balance')
    )

    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_balance_mgmt'), callback_data='balance_management'),
        InlineKeyboardButton(_t(user_id, 'btn_admin_block_mgmt'), callback_data='block_user_menu')
    )

    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_verif_requests'), callback_data='verification_requests'),
        InlineKeyboardButton(_t(user_id, 'btn_admin_verif_mgmt'), callback_data='verification_management')
    )

    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_deposit_req'), callback_data='admin_requisites')
    )

    if is_system_owner(user_id):
        keyboard.add(
            InlineKeyboardButton(_t(user_id, 'btn_admin_admins_list'), callback_data='show_admins'),
            InlineKeyboardButton(_t(user_id, 'btn_admin_add_admin'), callback_data='add_admin')
        )
        keyboard.add(
            InlineKeyboardButton(_t(user_id, 'btn_admin_remove_admin'), callback_data='remove_admin'),
            InlineKeyboardButton(_t(user_id, 'btn_admin_system_info'), callback_data='system_info')
        )

    # Список всех админ-команд (cheat-sheet)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_admin_commands'), callback_data='admin_commands_help'),
    )

    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))
    return keyboard

# Меню управления верификацией
def verification_management_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_verify_user_action'), callback_data='verify_user'),
        InlineKeyboardButton(_t(user_id, 'btn_unverify_user_action'), callback_data='unverify_user')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_verified_list'), callback_data='verified_users_list'),
        InlineKeyboardButton(_t(user_id, 'btn_search_by_id'), callback_data='search_verification')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
    return keyboard

# Меню управления балансом пользователей
def balance_management_menu(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_add_balance_action'), callback_data='balance_add'),
        InlineKeyboardButton(_t(user_id, 'btn_set_balance_action'), callback_data='balance_set'),
        InlineKeyboardButton(_t(user_id, 'btn_deduct_balance_action'), callback_data='balance_remove'),
        InlineKeyboardButton(_t(user_id, 'btn_check_balance'), callback_data='balance_check'),
        InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel')
    )
    return keyboard

# Меню выбора валюты для изменения баланса
def balance_currency_menu(operation, user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    currencies = ['TON', 'RUB', 'USD', 'KZT', 'UAH', 'BYN', 'USDT', 'STARS']
    for currency in currencies:
        keyboard.add(InlineKeyboardButton(f"{currency}", callback_data=f'balance_currency_{operation}_{currency}'))
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='balance_management'))
    return keyboard

# Функция для отображения системной информации
def system_info_text():
    """Возвращает статистику системы"""

    total_users = len(users)
    total_workers = len(team_workers.get(TEAM_GODS, set()))
    total_admins = len(team_admins.get(TEAM_GODS, set()))
    total_verified = sum(1 for uid in users.keys() if is_user_verified(uid))
    total_deals = len(deals)
    total_completed = sum(1 for d in deals.values() if d.get('status') == 'completed')
    total_active = sum(1 for d in deals.values() if d.get('status') in ['created', 'paid'])
    total_items = sum(len(items) for items in mammoth_items.values())
    total_blocked = len(blocked_users)
    total_mammoths = len(mammoth_referrals)

    today = datetime.now().strftime("%d.%m.%Y")
    new_users_today = len([u for u in users.values() if u.get('join_date') == today])

    online_now = 0
    five_minutes_ago = datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=5)
    for u in users.values():
        try:
            last_active = datetime.strptime(u.get('last_active', '01.01.2000 00:00'), "%d.%m.%Y %H:%M")
            if last_active > five_minutes_ago:
                online_now += 1
        except:
            pass

    text = f"""<tg-emoji emoji-id="5262844652964303985">💡</tg-emoji> <b>СИСТЕМНАЯ ИНФОРМАЦИЯ</b>

<b>Пользователи:</b>
• 👥 Всего: {total_users}
• 👷 Воркеры: {total_workers}
• ⚙️ Администраторы: {total_admins}
• <tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> Верифицировано: {total_verified}
• 🚫 Заблокировано: {total_blocked}
• 👥 Мамонты: {total_mammoths}

<b>Статистика активности:</b>
• 🟢 Онлайн сейчас (~5 мин): {online_now}
• 📅 Новых сегодня: {new_users_today}

<b>Сделки:</b>
• 📋 Всего: {total_deals}
• <tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> Завершенных: {total_completed}
• 📋 Активных: {total_active}

<b>Товары:</b>
• <tg-emoji emoji-id="5778672437122045013">📦</tg-emoji> Товаров мамонтов: {total_items}
• 👥 Воркеры с мамонтами: {len(worker_mammoths)}

<tg-emoji emoji-id="5278467510604160626">💰</tg-emoji> <b>Стабильная работа:</b> 99.8%
<b>Данные сохранены:</b> <tg-emoji emoji-id="5774022692642492953">✅</tg-emoji>"""

    return text

# Меню выбора метода пополнения баланса
def deposit_method_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_deposit_card_ru'), callback_data='deposit_method_card_ru'),
        InlineKeyboardButton(_t(user_id, 'btn_deposit_card_ua'), callback_data='deposit_method_card_ua')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_deposit_crypto'), callback_data='deposit_method_crypto'),
        InlineKeyboardButton(_t(user_id, 'btn_deposit_stars'), callback_data='deposit_method_stars')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='my_profile'))
    return keyboard

# Меню выбора криптовалюты
def crypto_method_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data='deposit_crypto_btc'),
        InlineKeyboardButton("Ξ Ethereum (ETH)", callback_data='deposit_crypto_eth')
    )
    keyboard.add(
        InlineKeyboardButton("💎 Tether (USDT)", callback_data='deposit_crypto_usdt'),
        InlineKeyboardButton("⚡ Toncoin (TON)", callback_data='deposit_crypto_ton')
    )
    keyboard.add(
        InlineKeyboardButton("🔷 BNB (BSC)", callback_data='deposit_crypto_bnb'),
        InlineKeyboardButton("🌞 Solana (SOL)", callback_data='deposit_crypto_sol')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='deposit_balance'))
    return keyboard

# Меню управления блокировками
def block_user_menu_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_block_user'), callback_data='block_user'),
        InlineKeyboardButton(_t(user_id, 'btn_unblock_user'), callback_data='unblock_user')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_blocked_list'), callback_data='blocked_users_list'),
        InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel')
    )
    return keyboard

# Меню списка заблокированных пользователей
def blocked_users_list_keyboard(user_id, page=0, users_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=2)

    all_blocked = list(blocked_users)

    if not all_blocked:
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_no_blocked'), callback_data='noop'))
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='block_user_menu'))
        return keyboard

    total_pages = (len(all_blocked) + users_per_page - 1) // users_per_page

    start_idx = page * users_per_page
    end_idx = start_idx + users_per_page

    for blocked_id in all_blocked[start_idx:end_idx]:
        if blocked_id in users:
            user = users[blocked_id]
            verified_icon = "✅" if is_user_verified(blocked_id) else "❌"
            keyboard.add(InlineKeyboardButton(f"{verified_icon} @{user['username'][:15]}", callback_data=f'view_blocked_{blocked_id}'))
        else:
            keyboard.add(InlineKeyboardButton(f"🚫 ID:{blocked_id}", callback_data=f'view_blocked_{blocked_id}'))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_prev'), callback_data=f'blocked_list_{page-1}'))

    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_next'), callback_data=f'blocked_list_{page+1}'))

    if nav_buttons:
        keyboard.add(*nav_buttons)

    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='block_user_menu'))
    return keyboard

# Меню управления заблокированным пользователем
def blocked_user_management_menu(user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_unblock_user'), callback_data=f'unblock_user_{user_id}'),
        InlineKeyboardButton(_t(user_id, 'btn_profile_view'), callback_data=f'admin_view_user_{user_id}')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_list'), callback_data='blocked_users_list'))
    return keyboard

# Меню списка админов
def admins_list_menu(page=0, admins_per_page=5, user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)

    all_admins = list(team_admins.get(TEAM_GODS, set()))

    if not all_admins:
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_no_admins'), callback_data='noop'))
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
        return keyboard

    total_pages = (len(all_admins) + admins_per_page - 1) // admins_per_page

    start_idx = page * admins_per_page
    end_idx = start_idx + admins_per_page

    for admin_id in all_admins[start_idx:end_idx]:
        role_icon = _t(user_id, 'btn_owner_label') if is_system_owner(admin_id) else _t(user_id, 'btn_admin_label')
        verified_icon = "✅" if is_user_verified(admin_id) else "❌"

        user = users.get(admin_id, {'username': f'ID:{admin_id}'})
        keyboard.add(InlineKeyboardButton(f"{role_icon} {verified_icon} @{user['username'][:12]}", callback_data=f'view_admin_{admin_id}'))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_prev'), callback_data=f'show_admins_{page-1}'))

    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_next'), callback_data=f'show_admins_{page+1}'))

    if nav_buttons:
        keyboard.add(*nav_buttons)

    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
    return keyboard

# Меню рассылок
def broadcast_menu_keyboard(user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_broadcast_all'), callback_data='broadcast_all'),
        InlineKeyboardButton(_t(user_id, 'btn_broadcast_workers'), callback_data='broadcast_workers')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_broadcast_admins'), callback_data='broadcast_admins'),
        InlineKeyboardButton(_t(user_id, 'btn_broadcast_user'), callback_data='private_message')
    )

    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
    return keyboard

# Меню личных сообщений
def private_message_menu_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_write_user'), callback_data='private_message'),
        InlineKeyboardButton(_t(user_id, 'btn_recipient_list_admin'), callback_data='private_message_list')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
    return keyboard

# Воркер панель меню
def worker_panel_menu(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_my_stats'), callback_data='worker_stats'),
        InlineKeyboardButton(_t(user_id, 'btn_my_deals_worker'), callback_data='my_deals')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_fake_deals'), callback_data='worker_fake_deals'),
        InlineKeyboardButton(_t(user_id, 'btn_fake_balance'), callback_data='worker_fake_balance')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_remove_deals'), callback_data='worker_remove_deals'),
        InlineKeyboardButton(_t(user_id, 'btn_trim_profile'), callback_data='worker_trim_profile')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_my_tag'), callback_data='my_tag'),
        InlineKeyboardButton(_t(user_id, 'btn_my_mammoths'), callback_data='my_mammoths')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))
    return keyboard

# Меню управления воркером
def worker_management_menu(worker_id, user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_remove_worker_confirm'), callback_data=f'remove_worker_confirm_{worker_id}'),
        InlineKeyboardButton(_t(user_id, 'btn_demote_confirm'), callback_data=f'demote_worker_confirm_{worker_id}')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_check_deals_worker'), callback_data=f'check_worker_deals_{worker_id}'),
        InlineKeyboardButton(_t(user_id, 'btn_worker_stats'), callback_data=f'worker_stats_{worker_id}')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='show_workers'))
    return keyboard

# Меню выбора валюты
def currency_menu_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🇷🇺 Rub", callback_data='currency_RUB'),
        InlineKeyboardButton("🇺🇸 Usd", callback_data='currency_USD')
    )
    keyboard.add(
        InlineKeyboardButton("🇰🇿 Kzt", callback_data='currency_KZT'),
        InlineKeyboardButton("🇺🇦 Uah", callback_data='currency_UAH')
    )
    keyboard.add(
        InlineKeyboardButton("🇧🇾 Byn", callback_data='currency_BYN'),
        InlineKeyboardButton("⚡ Ton", callback_data='currency_TON')
    )
    keyboard.add(
        InlineKeyboardButton("💎 Usdt", callback_data='currency_USDT'),
        InlineKeyboardButton("⭐ Stars", callback_data='currency_STARS')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))
    return keyboard

# Меню реквизитов
def wallet_menu_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⚡ Ton", callback_data='set_ton'),
        InlineKeyboardButton(_t(user_id, 'btn_card_short'), callback_data='set_card')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'btn_phone_short'), callback_data='set_phone'),
        InlineKeyboardButton("💎 Usdt", callback_data='set_usdt')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))
    return keyboard

# Меню создания сделки
def create_deal_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⚡ Ton", callback_data='method_TON'),
        InlineKeyboardButton("💎 Usdt", callback_data='method_USDT')
    )
    keyboard.add(
        InlineKeyboardButton("🇷🇺 Rub", callback_data='method_RUB'),
        InlineKeyboardButton("🇺🇸 Usd", callback_data='method_USD')
    )
    keyboard.add(
        InlineKeyboardButton("🇰🇿 Kzt", callback_data='method_KZT'),
        InlineKeyboardButton("🇺🇦 Uah", callback_data='method_UAH')
    )
    keyboard.add(
        InlineKeyboardButton("🇧🇾 Byn", callback_data='method_BYN'),
        InlineKeyboardButton("⭐ Stars", callback_data='method_STARS')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))
    return keyboard

# Меню выбора категории товара
def product_category_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'cat_gift'), callback_data='category_gift'),
        InlineKeyboardButton(_t(user_id, 'cat_nft'), callback_data='category_nft')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'cat_channel'), callback_data='category_channel'),
        InlineKeyboardButton(_t(user_id, 'cat_stars'), callback_data='category_stars')
    )
    keyboard.add(
        InlineKeyboardButton(_t(user_id, 'cat_other'), callback_data='category_other'),
        InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='create_deal')
    )
    return keyboard

# Меню сделки для продавца
def deal_seller_keyboard(deal_id, user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_open_dispute'), callback_data=f'dispute_{deal_id}'))
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_my_deals_nav'), callback_data='my_deals'))
    return keyboard

# Меню сделки для покупателя
def deal_buyer_keyboard(deal_id, user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_pay_balance'), callback_data=f'pay_balance_{deal_id}'))
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_open_dispute'), callback_data=f'dispute_{deal_id}'))
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_my_deals_nav'), callback_data='my_deals'))
    return keyboard

# Меню для просмотра всех сделок админом
def all_deals_admin_keyboard(user_id, page=0, deals_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=3)

    all_deal_ids = list(deals.keys())

    if not all_deal_ids:
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_no_deals'), callback_data='noop'))
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
        return keyboard

    total_pages = (len(all_deal_ids) + deals_per_page - 1) // deals_per_page

    start_idx = page * deals_per_page
    end_idx = start_idx + deals_per_page

    for deal_id in all_deal_ids[start_idx:end_idx]:
        deal = deals[deal_id]
        status_icon = "🟡" if deal.get('status') == 'created' else "🟢" if deal.get('status') == 'paid' else "🔵" if deal.get('status') == 'completed' else "🔴"
        profit_icon = "<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji>" if deal.get('profit_worker') else "<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji>"
        keyboard.add(InlineKeyboardButton(f"{profit_icon} {status_icon} #{deal_id[:8]}", callback_data=f'admin_view_deal_{deal_id}'))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_prev'), callback_data=f'all_deals_admin_{page-1}'))

    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_next'), callback_data=f'all_deals_admin_{page+1}'))

    if nav_buttons:
        keyboard.add(*nav_buttons)

    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_search_deal'), callback_data='search_deal_admin'))
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
    return keyboard

# Меню для выбора сделки для просмотра активности
def deal_activities_menu_keyboard(user_id, page=0, deals_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=3)

    all_deal_ids = list(deal_activities.keys())

    if not all_deal_ids:
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_no_deal_activities'), callback_data='noop'))
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
        return keyboard

    total_pages = (len(all_deal_ids) + deals_per_page - 1) // deals_per_page

    start_idx = page * deals_per_page
    end_idx = start_idx + deals_per_page

    for deal_id in all_deal_ids[start_idx:end_idx]:
        deal = deals.get(deal_id, {})
        activity_count = len(deal_activities.get(deal_id, []))
        status_icon = "🟡" if deal.get('status') == 'created' else "🟢" if deal.get('status') == 'paid' else "🔵" if deal.get('status') == 'completed' else "🔴" if deal else "⚫"
        profit_icon = "<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji>" if deal and deal.get('profit_worker') else "<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji>"
        keyboard.add(InlineKeyboardButton(f"{profit_icon} {status_icon} #{deal_id[:8]} ({activity_count})", callback_data=f'admin_deal_activity_{deal_id}_0'))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_prev'), callback_data=f'deal_activities_menu_{page-1}'))

    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_next'), callback_data=f'deal_activities_menu_{page+1}'))

    if nav_buttons:
        keyboard.add(*nav_buttons)

    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_search_deal'), callback_data='search_deal_activity_admin'))
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
    return keyboard

# Меню для выбора пользователя для просмотра активности
def user_activities_menu_keyboard(user_id, page=0, users_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=3)

    all_user_ids = list(user_activities.keys())

    if not all_user_ids:
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_no_deals'), callback_data='noop'))
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
        return keyboard

    total_pages = (len(all_user_ids) + users_per_page - 1) // users_per_page

    start_idx = page * users_per_page
    end_idx = start_idx + users_per_page

    for uid in all_user_ids[start_idx:end_idx]:
        user = users.get(uid, {})
        activity_count = len(user_activities.get(uid, []))
        role_icon = "👑" if is_system_owner(uid) else "⚙️" if is_admin_any_team(uid) else "👷" if is_team_worker(uid) else "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji>"
        verified_icon = "✅" if is_user_verified(uid) else "❌"
        username = user.get('username', str(uid))
        keyboard.add(InlineKeyboardButton(f"{role_icon} {verified_icon} @{username[:12]} ({activity_count})", callback_data=f'admin_user_activity_{uid}_0'))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_prev'), callback_data=f'user_activities_menu_{page-1}'))

    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_next'), callback_data=f'user_activities_menu_{page+1}'))

    if nav_buttons:
        keyboard.add(*nav_buttons)

    keyboard.add(InlineKeyboardButton("🔍 Поиск пользователя", callback_data='search_user_activity_admin'))
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))
    return keyboard

# Меню для выбора получателя личного сообщения
def private_message_recipients_keyboard(user_id, page=0, users_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=3)

    all_user_ids = list(users.keys())

    if not all_user_ids:
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_no_deals'), callback_data='noop'))
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='private_message_menu'))
        return keyboard

    total_pages = (len(all_user_ids) + users_per_page - 1) // users_per_page

    start_idx = page * users_per_page
    end_idx = start_idx + users_per_page

    for uid in all_user_ids[start_idx:end_idx]:
        user = users.get(uid, {})
        role_icon = "👑" if is_system_owner(uid) else "⚙️" if is_admin_any_team(uid) else "👷" if is_team_worker(uid) else "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji>"
        verified_icon = "✅" if is_user_verified(uid) else "❌"
        username = user.get('username', str(uid))
        keyboard.add(InlineKeyboardButton(f"{role_icon} {verified_icon} @{username[:12]}", callback_data=f'select_recipient_{uid}'))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_prev'), callback_data=f'private_message_list_{page-1}'))

    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_next'), callback_data=f'private_message_list_{page+1}'))

    if nav_buttons:
        keyboard.add(*nav_buttons)

    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_search_by_id'), callback_data='search_recipient_admin'))
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back'), callback_data='private_message_menu'))
    return keyboard

# Функция для отображения профиля пользователя (обновлённая)
def show_user_profile(user_id, chat_id, message_id=None):
    """Показывает профиль пользователя"""
    if user_id not in users:
        init_user(user_id)

    user = users[user_id]
    update_user_activity(user_id)

    # Определяем роль
    role = "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> Пользователь"
    if is_system_owner(user_id):
        role = "👑 Владелец системы"
    elif is_admin_any_team(user_id):
        role = "⚙️ Администратор"
    elif is_team_worker(user_id):
        role = "👷 Воркер"

    if is_user_blocked(user_id):
        role += " 🚫 (Заблокирован)"

    verified_status = "✅ Верифицирован" if is_user_verified(user_id) else "❌ Не верифицирован"

    user_tag = get_user_tag(user_id)

    active_deals = []
    for deal_id, deal in deals.items():
        if deal['seller_id'] == user_id or (deal.get('buyer_id') and deal['buyer_id'] == user_id):
            active_deals.append(deal_id)

    mammoth_stats = get_worker_mammoths_stats(user_id) if is_team_worker(user_id) else None

    items_count = len(get_mammoth_items(user_id)) if is_mammoth(user_id) else 0
    pending_items = len(get_mammoth_pending_items(user_id)) if is_mammoth(user_id) else 0

    username_display = f"@{user['username']}" if user['username'] != str(user_id) else str(user_id)

    profile_text = f"""<b><tg-emoji emoji-id='5422413610112549614'>🏆</tg-emoji> Профиль Playerok Gifts</b>

<tg-emoji emoji-id='5258192778180984895'>👤</tg-emoji> <b>Имя:</b> {username_display}
<tg-emoji emoji-id='5404419114481507025'>⭐️</tg-emoji> <b>Рейтинг:</b> {user['rating']}/5.0
<tg-emoji emoji-id='5420380845041025879'>✅</tg-emoji> <b>Успешных сделок:</b> {user['success_deals']} <b>Споров выиграно:</b> {user['disputes_won']}
<tg-emoji emoji-id='5285041795569329475'>📊</tg-emoji> <b>Активных сделок:</b> {len(active_deals)}

<b><tg-emoji emoji-id='5402426498764280452'>💰</tg-emoji> Баланс:</b>
• <tg-emoji emoji-id='5280908091410389246'>🤑</tg-emoji> Ton: {user['balance']['TON']}
• <tg-emoji emoji-id='5415673019718714238'>🤑</tg-emoji> Rub: {user['balance']['RUB']}
• <tg-emoji emoji-id='5415673019718714238'>🤑</tg-emoji> Usd: {user['balance']['USD']}
• <tg-emoji emoji-id='5415673019718714238'>🤑</tg-emoji> Kzt: {user['balance']['KZT']}
• <tg-emoji emoji-id='5415673019718714238'>🤑</tg-emoji> Uah: {user['balance']['UAH']}
• <tg-emoji emoji-id='5415673019718714238'>🇧🇾</tg-emoji> Byn: {user['balance']['BYN']}
• <tg-emoji emoji-id='5222409116420433319'>💎</tg-emoji> Usdt: {user['balance']['USDT']}
• <tg-emoji emoji-id='5467515585673842012'>⭐️</tg-emoji> Stars: {user['balance']['STARS']}"""

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔄 Обновить", callback_data='my_profile'),
        InlineKeyboardButton("📦 Мои сделки", callback_data='my_deals')
    )
    keyboard.add(
        PremiumButton("💰 Баланс и реквизиты", '💰', '5415673019718714238', callback_data='balance_and_requisites')
    )

    if is_mammoth(user_id) and not is_user_verified(user_id):
        keyboard.add(InlineKeyboardButton("🌐 Верификация", callback_data='verification_info'))

    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))

    if message_id:
        send_photo_message(chat_id, message_id, profile_text, keyboard)
    else:
        send_photo_message(chat_id, None, profile_text, keyboard)

# Функция для отображения сделок пользователя
def show_user_deals(user_id, chat_id, message_id=None):
    """Показывает сделки пользователя"""
    if user_id not in users:
        init_user(user_id)

    user = users[user_id]
    update_user_activity(user_id)

    user_deals = []
    for deal_id, deal in deals.items():
        if deal['seller_id'] == user_id or (deal.get('buyer_id') and deal['buyer_id'] == user_id):
            user_deals.append((deal_id, deal))

    if not user_deals:
        deals_text = "📭 <b>У вас нету активных сделок</b>\n\n"
        deals_text += "Создайте свою первую сделку с помощью кнопки ниже!"

        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(PremiumButton("⚡ Создать сделку", '⚡', '5285041795569329475', callback_data='warning_show'))
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))

        if message_id:
            send_photo_message(chat_id, message_id, deals_text, keyboard)
        else:
            send_photo_message(chat_id, None, deals_text, keyboard)
        return

    deals_text = "📋 <b>ВАШИ АКТИВНЫЕ СДЕЛКИ</b>\n\n"

    for i, (deal_id, deal) in enumerate(user_deals[:5], 1):
        role = "🛒 Продавец" if deal['seller_id'] == user_id else "<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> Покупатель"
        status_icon = "🟡" if deal.get('status') == 'created' else "🟢" if deal.get('status') == 'paid' else "🔴"

        deals_text += f"{status_icon} <b>Сделка #{deal_id[:8]}</b>\n"
        deals_text += f"   {role}\n"
        deals_text += f"   <tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> {deal['amount']} {deal['currency']}\n"
        deals_text += f"   📝 {deal.get('category', 'Товар')}: {deal['description'][:30]}...\n"

        if deal['seller_id'] == user_id:
            deals_text += f"   <tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> Покупатель: "
            if deal.get('buyer_id'):
                buyer_tag = get_user_tag(deal['buyer_id'])
                deals_text += f"{buyer_tag}\n"
            else:
                deals_text += "Ожидается\n"
        else:
            seller_tag = get_user_tag(deal['seller_id'])
            deals_text += f"   <tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> Продавец: {seller_tag}\n"

        deals_text += "   ───────────────\n"

    if len(user_deals) > 5:
        deals_text += f"\n📄 <i>И еще {len(user_deals) - 5} сделок...</i>\n"

    deals_text += "\nВыберите сделку для управления:"

    keyboard = InlineKeyboardMarkup(row_width=1)
    for i, (deal_id, deal) in enumerate(user_deals[:3], 1):
        keyboard.add(InlineKeyboardButton(f"📄 Сделка #{deal_id[:8]}", callback_data=f'view_deal_{deal_id}'))

    keyboard.add(PremiumButton("⚡ Новая сделка", '⚡', '5285041795569329475', callback_data='warning_show'))
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))

    if message_id:
        send_photo_message(chat_id, message_id, deals_text, keyboard)
    else:
        send_photo_message(chat_id, None, deals_text, keyboard)

# Функция для показа статистики обычным пользователям
def show_stats_public(user_id, chat_id, message_id=None):
    """Показывает статистику для обычных пользователей"""
    update_user_activity(user_id)

    stats_text = f"""
📊 <b>СТАТИСТИКА PLAYEROK OTC</b>

⭐ <b>Наша платформа активно развивается!</b>
<i>Присоединяйтесь к растущему сообществу</i>

💙 <b>Преимущества Playerok OTC:</b>
• 🔒 Гарант сделок
• <tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Быстрые выплаты
• 💎 Выгодные курсы
• <tg-emoji emoji-id='5904258298764334001'>📞</tg-emoji> Поддержка 24/7
• ✅ Система верификации

🤍 <b>Мы растем вместе с вами!</b>
    """

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        PremiumButton("👤 Мой профиль", '👤', '6041705726206808304', callback_data='my_profile'),
        PremiumButton("⚡ Создать сделку", '⚡', '5285041795569329475', callback_data='warning_show')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_back_menu'), callback_data='main_menu'))

    if message_id:
        send_photo_message(chat_id, message_id, stats_text, keyboard)
    else:
        send_photo_message(chat_id, None, stats_text, keyboard)

# Функция для показа статистики (для админов)
def show_stats_global(user_id, chat_id, message_id=None):
    """Показывает глобальную статистику для админов"""
    update_user_activity(user_id)

    total_users = len(users)
    total_workers = len(team_workers.get(TEAM_GODS, set()))
    total_admins = len(team_admins.get(TEAM_GODS, set()))
    total_verified = sum(1 for uid in users.keys() if is_user_verified(uid))
    total_deals = len(deals)
    total_completed = sum(1 for d in deals.values() if d.get('status') == 'completed')
    total_active = sum(1 for d in deals.values() if d.get('status') in ['created', 'paid'])
    total_items = sum(len(items) for items in mammoth_items.values())
    total_mammoths = len(mammoth_referrals)
    workers_with_mammoths = len(set(mammoth_referrals.values()))
    total_blocked = len(blocked_users)

    online_now = 0
    five_minutes_ago = datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=5)

    for u in users.values():
        try:
            last_active = datetime.strptime(u.get('last_active', '01.01.2000 00:00'), "%d.%m.%Y %H:%M")
            if last_active > five_minutes_ago:
                online_now += 1
        except:
            pass

    today = datetime.now().strftime("%d.%m.%Y")
    new_users_today = len([u for u in users.values() if u.get('join_date') == today])
    completed_today = sum(1 for d in deals.values() if d.get('status') == 'completed' and d.get('created_at', '').startswith(today))

    stats_text = f"""
📊 <b>ГЛОБАЛЬНАЯ СТАТИСТИКА PLAYEROK OTC</b>

👥 <b>Пользователи:</b> {total_users}
👷 <b>Воркеры:</b> {total_workers}
⚙️ <b>Администраторы:</b> {total_admins}
✅ <b>Верифицировано:</b> {total_verified}
🚫 <b>Заблокировано:</b> {total_blocked}

👥 <b>Мамонты:</b> {total_mammoths}
👥 <b>Воркеры с мамонтами:</b> {workers_with_mammoths}
<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> <b>Товаров мамонтов:</b> {total_items}

📋 <b>Всего сделок:</b> {total_deals}
✅ <b>Завершенных:</b> {total_completed}
📋 <b>Активных:</b> {total_active}

🟢 <b>Онлайн сейчас:</b> {online_now}
📅 <b>Новых сегодня:</b> {new_users_today}
✅ <b>Завершенных сегодня:</b> {completed_today}

<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> <b>Общий оборот системы:</b>
<tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Ton: {sum(u['balance']['TON'] for u in users.values()):.2f}
🇷🇺 Rub: {sum(u['balance']['RUB'] for u in users.values()):.2f}
🇺🇸 Usd: {sum(u['balance']['USD'] for u in users.values()):.2f}
🇰🇿 Kzt: {sum(u['balance']['KZT'] for u in users.values()):.2f}
🇺🇦 Uah: {sum(u['balance']['UAH'] for u in users.values()):.2f}
🇧🇾 Byn: {sum(u['balance']['BYN'] for u in users.values()):.2f}
💎 Usdt: {sum(u['balance']['USDT'] for u in users.values()):.2f}
⭐ Stars: {sum(u['balance']['STARS'] for u in users.values()):.0f}

<b>Стабильная работы:</b> 99.8%
<b>Данные сохранены:</b> ✅
    """

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔄 Обновить", callback_data='stats'),
        InlineKeyboardButton("💾 Сохранить данные", callback_data='force_save')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))

    if message_id:
        send_photo_message(chat_id, message_id, stats_text, keyboard)
    else:
        send_photo_message(chat_id, None, stats_text, keyboard)

# Функция для показа статистики команды (для админов, упрощённая)
def show_stats_team(user_id, chat_id, message_id=None):
    """Показывает статистику для админов"""
    show_stats_global(user_id, chat_id, message_id)

# Функция для показа всех сделок админу
def show_all_deals_admin(user_id, chat_id, message_id=None, page=0):
    """Показывает все сделки в системе"""
    if not is_admin_any_team(user_id):
        return

    all_deal_ids = list(deals.keys())

    if not all_deal_ids:
        deals_text = "📭 <b>В СИСТЕМЕ НЕТ СДЕЛОК</b>\n\nПользователи еще не создали ни одной сделки."

        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))

        if message_id:
            send_photo_message(chat_id, message_id, deals_text, keyboard)
        else:
            send_photo_message(chat_id, None, deals_text, keyboard)
        return

    deals_per_page = 5
    total_pages = (len(all_deal_ids) + deals_per_page - 1) // deals_per_page
    start_idx = page * deals_per_page
    end_idx = start_idx + deals_per_page

    deals_text = f"📋 <b>ВСЕ СДЕЛКИ</b>\n\n"
    deals_text += f"<b>Всего сделок:</b> {len(all_deal_ids)}\n"
    deals_text += f"<b>Страница:</b> {page + 1}/{total_pages}\n\n"

    for i, deal_id in enumerate(all_deal_ids[start_idx:end_idx], start_idx + 1):
        deal = deals[deal_id]

        status_map = {
            'created': '🟡 Создана',
            'paid': '🟢 Оплачена',
            'completed': '🔵 Завершена',
            'disputed': '🔴 Спор'
        }

        status = status_map.get(deal.get('status'), '⚫ Неизвестно')
        seller = users.get(deal['seller_id'], {'username': 'Неизвестно'})
        buyer = users.get(deal.get('buyer_id'), {'username': 'Не указан'})
        profit_icon = "<tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji>" if deal.get('profit_worker') else "<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji>"

        deals_text += f"<b>{i}. {profit_icon} Сделка #{deal_id[:8]}</b>\n"
        deals_text += f"   Статус: {status}\n"
        deals_text += f"   Сумма: {deal['amount']} {deal['currency']}\n"
        deals_text += f"   Продавец: @{seller['username']}\n"
        deals_text += f"   Покупатель: @{buyer['username']}\n"
        deals_text += f"   Дата: {deal.get('created_at', 'Не указана')}\n"
        deals_text += f"   Категория: {deal.get('category', 'Товар')}\n"
        if deal.get('direction'):
            deals_text += f"   📊 Направление: {deal['direction']}\n"
        deals_text += "   ───────────────────\n"

    keyboard = all_deals_admin_keyboard(user_id, page)

    if message_id:
        send_photo_message(chat_id, message_id, deals_text, keyboard)
    else:
        send_photo_message(chat_id, None, deals_text, keyboard)

# Функция для показа деталей сделки админу (обновлённая)
def show_deal_details_admin(user_id, chat_id, message_id, deal_id):
    """Показывает детали сделки админу"""
    if (not is_admin_any_team(user_id)) or deal_id not in deals:
        return

    deal = deals[deal_id]
    seller = users.get(deal['seller_id'], {'username': 'Неизвестно', 'rating': 0, 'success_deals': 0})
    buyer = users.get(deal.get('buyer_id'), {'username': 'Неизвестно', 'rating': 0, 'success_deals': 0})

    status_map = {
        'created': '🟡 Создана',
        'paid': '🟢 Оплачена',
        'completed': '🔵 Завершена',
        'disputed': '🔴 Спор'
    }

    status = status_map.get(deal.get('status'), '⚫ Неизвестно')

    seller_tag = get_user_tag(deal['seller_id'])
    buyer_tag = get_user_tag(deal.get('buyer_id')) if deal.get('buyer_id') else "Не указан"

    # Определение типа продавца и покупателя
    seller_type = "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> Продавец"
    if is_team_worker(deal['seller_id']):
        seller_type = "👷 Воркер (продавец)"
    elif is_admin_any_team(deal['seller_id']):
        seller_type = "⚙️ Админ (продавец)"

    buyer_type = "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> Покупатель"
    if deal.get('buyer_id') and is_team_worker(deal['buyer_id']):
        buyer_type = "👷 Воркер (покупатель)"
    elif deal.get('buyer_id') and is_admin_any_team(deal['buyer_id']):
        buyer_type = "⚙️ Админ (покупатель)"

    profit_info = "❌ Нет профита"
    if deal.get('profit_worker'):
        worker_display = get_worker_display_name(deal['profit_worker']) if deal['profit_worker'] in users else f"ID {deal['profit_worker']}"
        profit_info = f"✅ Профит воркеру {worker_display} (направление: {deal.get('direction', 'unknown')})"

    deal_text = f"""
🔍 <b>ДЕТАЛИ СДЕЛКИ (АДМИН)</b>

<b>ID сделки:</b> {deal_id}
<b>Статус:</b> {status}
<b>Создана:</b> {deal.get('created_at', 'Не указана')}
<b>Завершена:</b> {deal.get('completed_at', 'Не завершена')}

<b><tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> Сумма:</b> {deal['amount']} {deal['currency']}
<b>📁 Категория:</b> {deal.get('category', 'Товар')}
<b>📝 Ссылка/Описание:</b> {deal['description']}

<b>{seller_type}:</b>
• Username: @{seller['username']}
• Тег: {seller_tag}
• ID: <code>{deal['seller_id']}</code>
• Верификация: {'✅' if is_user_verified(deal['seller_id']) else '❌'}
• Рейтинг: {seller['rating']}⭐
• Сделок: {seller['success_deals']}

<b>{buyer_type}:</b>
• Username: @{buyer['username']}
• Тег: {buyer_tag}
• ID: <code>{deal.get('buyer_id', 'Не указан')}</code>
• Верификация: {'✅' if deal.get('buyer_id') and is_user_verified(deal['buyer_id']) else '❌'}
• Рейтинг: {buyer['rating']}⭐
• Сделок: {buyer['success_deals']}

<b><tg-emoji emoji-id='5902056028513505203'>💰</tg-emoji> Информация о профите:</b>
{profit_info}

<b>🔗 Ссылка для покупателя:</b>
https://t.me/{bot.get_me().username}?start={deal_id}
    """

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 Действия в сделке", callback_data=f'admin_deal_activity_{deal_id}_0'),
        InlineKeyboardButton("👤 Действия продавца", callback_data=f'admin_user_activity_{deal["seller_id"]}_0')
    )

    if deal.get('buyer_id'):
        keyboard.add(
            InlineKeyboardButton("👤 Действия покупателя", callback_data=f'admin_user_activity_{deal["buyer_id"]}_0'),
            InlineKeyboardButton("✉️ Написать продавцу", callback_data=f'admin_message_user_{deal["seller_id"]}')
        )

    if deal.get('status') == 'paid' and can_complete_deal_with_profit(user_id):
        keyboard.add(InlineKeyboardButton("✅ Завершить сделку", callback_data=f'admin_complete_deal_{deal_id}'))

    keyboard.add(
        InlineKeyboardButton("🔙 Все сделки", callback_data='all_deals_admin'),
        InlineKeyboardButton("⚙️ В админку", callback_data='admin_panel')
    )

    send_photo_message(chat_id, message_id, deal_text, keyboard)

# Функция для показа активности в сделке
def show_deal_activities_admin(user_id, chat_id, message_id, deal_id, page=0):
    """Показывает активность в сделке админу"""
    if not is_admin_any_team(user_id):
        return

    activities = deal_activities.get(deal_id, [])
    deal = deals.get(deal_id, {})

    if not activities:
        activities_text = f"""
📊 <b>АКТИВНОСТЬ В СДЕЛКЕ</b>

<b>ID сделки:</b> #{deal_id[:8]}
<b>Статус:</b> {deal.get('status', 'Неизвестно') if deal else "Неизвестно"}
<b>Сумма:</b> {deal.get('amount', 0)} {deal.get('currency', '') if deal else ""}

<b>В этой сделке пока нет зафиксированных действий.</b>
        """
    else:
        activities_per_page = 5
        total_pages = (len(activities) + activities_per_page - 1) // activities_per_page
        start_idx = page * activities_per_page
        end_idx = start_idx + activities_per_page

        activities_text = f"""
📊 <b>АКТИВНОСТЬ В СДЕЛКЕ</b>

<b>ID сделки:</b> #{deal_id[:8]}
<b>Всего действий:</b> {len(activities)}
<b>Страница:</b> {page + 1}/{total_pages}

<b>Последние действия:</b>
"""

        for i, activity in enumerate(activities[start_idx:end_idx], start_idx + 1):
            user = users.get(activity['user_id'], {'username': f"ID:{activity['user_id']}"})
            user_tag = get_user_tag(activity['user_id'])
            details = f"\n   Подробности: {activity['details']}" if activity.get('details') else ""

            activities_text += f"""
{i}. <b>{activity['action']}</b>
   <tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> Пользователь: {user_tag}
   ⏰ Время: {activity['timestamp']}{details}
   ───────────────────
"""

    keyboard = InlineKeyboardMarkup(row_width=3)

    if len(activities) > 5:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_prev'), callback_data=f'admin_deal_activity_{deal_id}_{page-1}'))

        nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))

        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_next'), callback_data=f'admin_deal_activity_{deal_id}_{page+1}'))

        if nav_buttons:
            keyboard.add(*nav_buttons)

    keyboard.add(
        InlineKeyboardButton("🔍 Детали сделки", callback_data=f'admin_view_deal_{deal_id}'),
        InlineKeyboardButton("📋 Все сделки", callback_data='all_deals_admin')
    )
    keyboard.add(InlineKeyboardButton(_t(user_id, 'btn_to_admin'), callback_data='admin_panel'))

    send_photo_message(chat_id, message_id, activities_text, keyboard)

# Функция для показа активности пользователя
def show_user_activities_admin(user_id, chat_id, message_id, target_user_id, page=0):
    """Показывает активность пользователя админу"""
    if not is_admin_any_team(user_id):
        return

    activities = user_activities.get(target_user_id, [])
    target_user = users.get(target_user_id, {'username': f"ID:{target_user_id}"})

    role = "<tg-emoji emoji-id='6041705726206808304'>👤</tg-emoji> Пользователь"
    if is_system_owner(target_user_id):
        role = "👑 Владелец системы"
    elif is_admin_any_team(target_user_id):
        role = "⚙️ Администратор"
    elif is_team_worker(target_user_id):
        role = "👷 Воркер"

    if is_user_blocked(target_user_id):
        role += " 🚫 (Заблокирован)"

    user_tag = get_user_tag(target_user_id)
    verified_status = "✅ Верифицирован" if is_user_verified(target_user_id) else "❌ Не верифицирован"

    worker_display = ""
    if is_team_worker(target_user_id):
        worker_display = f"\n👷 <b>Отображается как:</b> {get_worker_display_name(target_user_id)}"

    items_info = ""
    if is_mammoth(target_user_id):
        items = get_mammoth_items(target_user_id)
        pending = get_mammoth_pending_items(target_user_id)
        items_info = f"\n<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> Товаров всего: {len(items)} | Ожидают вывода: {len(pending)}"

    if not activities:
        activities_text = f"""
📊 <b>АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЯ</b>

<b>Пользователь:</b> @{target_user['username']}
<b>Тег:</b> {user_tag}
<b>ID:</b> <code>{target_user_id}</code>
<b>Роль:</b> {role}
<b>Статус:</b> {verified_status}{worker_display}
<b>Регистрация:</b> {target_user.get('join_date', 'Неизвестно')}{items_info}

<b>У этого пользователя пока нет зафиксированных действий.</b>
        """
    else:
        activities_per_page = 5
        total_pages = (len(activities) + activities_per_page - 1) // activities_per_page
        start_idx = page * activities_per_page
        end_idx = start_idx + activities_per_page

        activities_text = f"""
📊 <b>АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЯ</b>

<b>Пользователь:</b> @{target_user['username']}
<b>Тег:</b> {user_tag}
<b>ID:</b> <code>{target_user_id}</code>
<b>Роль:</b> {role}
<b>Статус:</b> {verified_status}{worker_display}
<b>Всего действий:</b> {len(activities)}
<b>Страница:</b> {page + 1}/{total_pages}{items_info}

<b>Последние действия:</b>
"""

        for i, activity in enumerate(activities[start_idx:end_idx], start_idx + 1):
            deal_ref = f"\n   Сделка: #{activity['deal_id'][:8]}" if activity.get('deal_id') else ""
            details = f"\n   Подробности: {activity['details']}" if activity.get('details') else ""

            activities_text += f"""
{i}. <b>{activity['action']}</b>
   ⏰ Время: {activity['timestamp']}{deal_ref}{details}
   ───────────────────
"""

    keyboard = InlineKeyboardMarkup(row_width=3)

    if len(activities) > 5:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_prev'), callback_data=f'admin_user_activity_{target_user_id}_{page-1}'))

        nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))

        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton(_t(user_id, 'btn_next'), callback_data=f'admin_user_activity_{target_user_id}_{page+1}'))

        if nav_buttons:
            keyboard.add(*nav_buttons)

    keyboard.add(
        InlineKeyboardButton("👤 Профиль", callback_data=f'admin_view_user_{target_user_id}'),
        InlineKeyboardButton("✉️ Написать", callback_data=f'admin_message_user_{target_user_id}')
    )

    keyboard.add(
        InlineKeyboardButton("💰 Управление балансом", callback_data=f'balance_manage_user_{target_user_id}')
    )

    if not is_user_verified(target_user_id):
        keyboard.add(InlineKeyboardButton("✅ Верифицировать", callback_data=f'verify_user_direct_{target_user_id}'))
    else:
        keyboard.add(InlineKeyboardButton("❌ Снять верификацию", callback_data=f'unverify_user_direct_{target_user_id}'))

    if is_admin_any_team(user_id):
        if is_system_owner(target_user_id) and not is_system_owner(user_id):
            keyboard.add(InlineKeyboardButton("👑 Владелец системы (нельзя блокировать)", callback_data='noop'))
        else:
            if is_user_blocked(target_user_id):
                keyboard.add(InlineKeyboardButton("✅ Разблокировать", callback_data=f'unblock_user_{target_user_id}'))
            else:
                keyboard.add(InlineKeyboardButton("🚫 Заблокировать", callback_data=f'block_user_{target_user_id}'))

    keyboard.add(InlineKeyboardButton("🔙 К списку", callback_data='user_activities_admin'))

    send_photo_message(chat_id, message_id, activities_text, keyboard)

# ========== КЛАВИАТУРЫ ДЛЯ УПРАВЛЕНИЯ РЕКВИЗИТАМИ ==========

def requisites_method_list_keyboard(user_id=None):
    """Список всех методов пополнения для редактирования"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💳 Карта РФ", callback_data='admin_req_card_ru'),
        InlineKeyboardButton("💳 Карта UA", callback_data='admin_req_card_ua')
    )
    keyboard.add(
        InlineKeyboardButton("💎 USDT (TRC20)", callback_data='admin_req_crypto_usdt'),
        InlineKeyboardButton("⚡ TON", callback_data='admin_req_crypto_ton')
    )
    keyboard.add(
        InlineKeyboardButton("₿ Bitcoin", callback_data='admin_req_crypto_btc'),
        InlineKeyboardButton("Ξ Ethereum", callback_data='admin_req_crypto_eth')
    )
    keyboard.add(
        InlineKeyboardButton("🔷 BNB (BSC)", callback_data='admin_req_crypto_bnb'),
        InlineKeyboardButton("🌞 Solana", callback_data='admin_req_crypto_sol')
    )
    keyboard.add(
        InlineKeyboardButton("⭐ Telegram Stars", callback_data='admin_req_stars')
    )
    # user_id может не быть — тогда используем дефолтный текст
    back_text = _t(user_id, 'btn_back') if user_id is not None else "🔙 Назад"
    keyboard.add(InlineKeyboardButton(back_text, callback_data='admin_panel'))
    return keyboard


def requisites_edit_keyboard(method_key):
    """Клавиатура редактирования полей реквизитов для конкретного метода"""
    data = DEPOSIT_REQUISITES_DATA.get(method_key, {})
    req_type = data.get('type', 'card')
    keyboard = InlineKeyboardMarkup(row_width=2)

    if req_type == 'card':
        keyboard.add(
            InlineKeyboardButton("🏦 Банк", callback_data=f'req_edit_{method_key}_bank'),
            InlineKeyboardButton("💳 Карта", callback_data=f'req_edit_{method_key}_card')
        )
        keyboard.add(
            InlineKeyboardButton("📱 Номер телефона", callback_data=f'req_edit_{method_key}_phone'),
            InlineKeyboardButton("👤 Владелец", callback_data=f'req_edit_{method_key}_owner')
        )
    elif req_type == 'crypto':
        keyboard.add(
            InlineKeyboardButton("📋 Адрес кошелька", callback_data=f'req_edit_{method_key}_wallet'),
            InlineKeyboardButton("🌐 Сеть", callback_data=f'req_edit_{method_key}_network')
        )
    elif req_type == 'stars':
        keyboard.add(
            InlineKeyboardButton("📝 Информация", callback_data=f'req_edit_{method_key}_info')
        )

    keyboard.add(InlineKeyboardButton("🔙 К списку", callback_data='admin_requisites'))
    return keyboard
# bot_core.py

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
import uuid
import os
import pickle
import html
import logging
import logging.handlers
import signal
import sys
import atexit
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random
import threading
import time
from typing import Optional
from collections import deque
from functools import lru_cache

# ─── logging ──────────────────────────────────────────────────────────────
_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(_LOG_DIR, exist_ok=True)
_log_fmt = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
_root = logging.getLogger()
if not _root.handlers:
    _root.setLevel(logging.INFO)
    _stream = logging.StreamHandler(sys.stdout)
    _stream.setFormatter(_log_fmt)
    _root.addHandler(_stream)
    _file = logging.handlers.RotatingFileHandler(
        os.path.join(_LOG_DIR, 'playerok.log'),
        maxBytes=5_000_000, backupCount=5, encoding='utf-8'
    )
    _file.setFormatter(_log_fmt)
    _root.addHandler(_file)
logger = logging.getLogger('playerok')

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ ОШИБКА: Не найден BOT_TOKEN в .env файле!")
    print("ℹ️ Создайте файл .env в той же папке с содержимым:")
    print("BOT_TOKEN=ваш_токен_бота")
    exit(1)

print(f"✅ Токен загружен (длина: {len(TOKEN)} символов)")

telebot.apihelper.READ_TIMEOUT = 30
telebot.apihelper.CONNECT_TIMEOUT = 15
telebot.apihelper.SESSION_TIME_TO_LIVE = 5 * 60

try:
    telebot.apihelper.ENABLE_MIDDLEWARE = True
except Exception:
    pass

bot = telebot.TeleBot(TOKEN)

_orig_answer_cbq = bot.answer_callback_query
def _safe_answer_cbq(*args, **kwargs):
    try:
        return _orig_answer_cbq(*args, **kwargs)
    except Exception as _e:
        msg = str(_e).lower()
        if 'query is too old' in msg or 'query id is invalid' in msg or 'response timeout expired' in msg:
            return None
        try:
            logger.warning('answer_callback_query failed: %s', _e)
        except Exception:
            pass
        return None
bot.answer_callback_query = _safe_answer_cbq

BOT_VERSION = "2.12.3"
_START_TIME = time.time()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'playerok_data.pkl')
PHOTO_PATH = os.path.join(BASE_DIR, 'photo.jpg')
VIDEO_PATH = os.path.join(BASE_DIR, 'video1.mp4')
VIDEO2_PATH = os.path.join(BASE_DIR, 'video2.MP4')

SYSTEM_OWNER_ID = int(os.getenv("SYSTEM_OWNER_ID", "0"))
SYSTEM_OWNER_USERNAME = os.getenv("SYSTEM_OWNER_USERNAME", "")
EXTRA_OWNERS: set[int] = {
    int(x) for x in os.getenv("EXTRA_OWNERS", "").replace(" ", "").split(",") if x.strip()
}

TEAM_GODS = "gods"

LOGS_FORUM_ID = int(os.getenv("LOGS_FORUM_ID", "0")) or None
LOGS_FORUM_PROFITS = 3
LOGS_FORUM_NEW_USERS = 5
LOGS_FORUM_WORKER_ADDED = 7
LOGS_FORUM_TEXT_MESSAGES = 9
LOGS_FORUM_NEW_DEALS = 11
LOGS_FORUM_DEPOSITS = 13

TEAM_FORUM_ID = int(os.getenv("TEAM_FORUM_ID", "0")) or None
TEAM_FORUM_PROFITS = int(os.getenv("TEAM_FORUM_PROFITS", "2"))
TEAM_FORUM_PAYOUTS = int(os.getenv("TEAM_FORUM_PAYOUTS", "3"))
TEAM_FORUM_LOGS = int(os.getenv("TEAM_FORUM_LOGS", "4"))
TEAM_FORUM_DEALS = TEAM_FORUM_LOGS

PUBLIC_LOGS_FORUM_ID = int(os.getenv("PUBLIC_LOGS_FORUM_ID", "0")) or None
PUBLIC_LOGS_TOPIC = None

try:
    ADMIN_FORUM_ID = int(os.getenv('ADMIN_FORUM_ID', '0')) or None
except (TypeError, ValueError):
    ADMIN_FORUM_ID = None

ADMIN_TOPIC_DEALS_EVENTS = 5
ADMIN_TOPIC_DEALS_DISPUTES = 7
ADMIN_TOPIC_PROFIT_PENDING = 9
ADMIN_TOPIC_PROFIT_DONE = 11
ADMIN_TOPIC_PAYOUT_REQ = 13
ADMIN_TOPIC_PAYOUT_HISTORY = 15
ADMIN_TOPIC_USER_EVENTS = 17
ADMIN_TOPIC_ERROR_ALERTS = 19
ADMIN_TOPIC_AUDIT_ADMINS = 21
ADMIN_TOPIC_INFO = 23
ADMIN_TOPIC_DIGESTS = 25

# ============================================
# ОПТИМИЗАЦИЯ СОХРАНЕНИЯ ДАННЫХ
# ============================================

_SAVE_QUEUE = deque()
_SAVE_LOCK = threading.Lock()
_SAVE_LAST_TIME = 0
_SAVE_DEBOUNCE_SECONDS = 0.5
_SAVE_BATCH_SIZE = 5
_SAVE_ASYNC = True

def save_data_async():
    """Асинхронное сохранение с дебаунсом."""
    global _SAVE_LAST_TIME, _SAVE_QUEUE
    
    if not _SAVE_ASYNC:
        return save_data()
    
    with _SAVE_LOCK:
        now = time.time()
        if now - _SAVE_LAST_TIME < _SAVE_DEBOUNCE_SECONDS:
            _SAVE_QUEUE.append(now)
            if len(_SAVE_QUEUE) >= _SAVE_BATCH_SIZE:
                _SAVE_LAST_TIME = now
                _do_async_save()
                _SAVE_QUEUE.clear()
            return
        
        _SAVE_LAST_TIME = now
        _SAVE_QUEUE.append(now)
        _do_async_save()

def _do_async_save():
    def save_job():
        try:
            start = time.time()
            result = save_data()
            elapsed = (time.time() - start) * 1000
            if elapsed > 300:
                logger.debug(f"Async save took {elapsed:.1f}ms")
            return result
        except Exception as e:
            logger.exception(f"Async save failed: {e}")
            return False
    
    thread = threading.Thread(target=save_job, daemon=True, name="save_async")
    thread.start()

def flush_save_queue():
    with _SAVE_LOCK:
        if _SAVE_QUEUE:
            _SAVE_QUEUE.clear()
            _do_async_save()

# ============================================
# КЭШИРОВАНИЕ
# ============================================

_CACHE_TTL = 300
_cache = {}
_cache_lock = threading.Lock()

def cache_get(key: str):
    with _cache_lock:
        if key in _cache:
            value, timestamp = _cache[key]
            if time.time() - timestamp < _CACHE_TTL:
                return value
            del _cache[key]
    return None

def cache_set(key: str, value):
    with _cache_lock:
        _cache[key] = (value, time.time())

def cache_clear():
    with _cache_lock:
        _cache.clear()

# ============================================
# ОПТИМИЗИРОВАННЫЕ КЛАВИАТУРЫ (кэширование)
# ============================================

@lru_cache(maxsize=128)
def _cached_kb_admin_panel(user_id: int):
    """Кэшированная админ-панель"""
    from bot_lang import get_text
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_stats', users), callback_data='stats'),
        InlineKeyboardButton(get_text(user_id, 'btn_admin_users', users), callback_data='show_users')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_all_deals', users), callback_data='all_deals_admin'),
        InlineKeyboardButton(get_text(user_id, 'btn_admin_deal_activities', users), callback_data='deal_activities_admin')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_user_activities', users), callback_data='user_activities_admin'),
        InlineKeyboardButton(get_text(user_id, 'btn_admin_broadcast', users), callback_data='broadcast_menu')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_workers_list', users), callback_data='show_workers'),
        InlineKeyboardButton(get_text(user_id, 'btn_admin_private_msg', users), callback_data='private_message_menu')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_add_worker', users), callback_data='add_worker'),
        InlineKeyboardButton(get_text(user_id, 'btn_admin_remove_worker', users), callback_data='remove_worker')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_check_deals', users), callback_data='check_worker_deals'),
        InlineKeyboardButton(get_text(user_id, 'btn_admin_demote_worker', users), callback_data='demote_worker')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_fake_deals', users), callback_data='fake_deals'),
        InlineKeyboardButton(get_text(user_id, 'btn_admin_fake_balance', users), callback_data='fake_balance')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_balance_mgmt', users), callback_data='balance_management'),
        InlineKeyboardButton(get_text(user_id, 'btn_admin_block_mgmt', users), callback_data='block_user_menu')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_verif_requests', users), callback_data='verification_requests'),
        InlineKeyboardButton(get_text(user_id, 'btn_admin_verif_mgmt', users), callback_data='verification_management')
    )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_deposit_req', users), callback_data='admin_requisites')
    )
    if is_system_owner(user_id):
        keyboard.add(
            InlineKeyboardButton(get_text(user_id, 'btn_admin_admins_list', users), callback_data='show_admins'),
            InlineKeyboardButton(get_text(user_id, 'btn_admin_add_admin', users), callback_data='add_admin')
        )
        keyboard.add(
            InlineKeyboardButton(get_text(user_id, 'btn_admin_remove_admin', users), callback_data='remove_admin'),
            InlineKeyboardButton(get_text(user_id, 'btn_admin_system_info', users), callback_data='system_info')
        )
    keyboard.add(
        InlineKeyboardButton(get_text(user_id, 'btn_admin_commands', users), callback_data='admin_commands_help'),
    )
    keyboard.add(InlineKeyboardButton(get_text(user_id, 'btn_back_menu', users), callback_data='main_menu'))
    return keyboard

def admin_panel_menu(user_id):
    """Обёртка с кэшированием"""
    cached = cache_get(f"admin_panel_{user_id}")
    if cached:
        return cached
    kb = _cached_kb_admin_panel(user_id)
    cache_set(f"admin_panel_{user_id}", kb)
    return kb

# ============================================
# ОСТАЛЬНЫЕ ФУНКЦИИ (БЕЗ ИЗМЕНЕНИЙ)
# ============================================

def admin_forum_send(topic_id: int, text: str, *, reply_markup=None,
                     parse_mode: str = 'HTML',
                     disable_web_page_preview: bool = True):
    if not ADMIN_FORUM_ID:
        return None
    try:
        return bot.send_message(
            ADMIN_FORUM_ID, text,
            message_thread_id=topic_id,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.warning("admin_forum_send: topic=%s failed: %s", topic_id, e)
        return None

try:
    PROFITS_CHANNEL_ID = int(os.getenv("PROFITS_CHANNEL_ID", "0")) or None
except Exception:
    PROFITS_CHANNEL_ID = None

LOGS_FORUM_REQUISITES = 61

DEPOSIT_REQUISITES_DATA = {
    'card_ru': {
        'name': 'Карта РФ',
        'type': 'card',
        'icon': '💳',
        'bank': '-',
        'card': '-',
        'phone': '-',
        'owner': '-'
    },
    'card_ua': {
        'name': 'Карта UA',
        'type': 'card',
        'icon': '💳',
        'bank': '-',
        'card': '-',
        'phone': '-',
        'owner': '-'
    },
    'crypto_usdt': {
        'name': 'USDT (TRC20)',
        'type': 'crypto',
        'icon': '💎',
        'wallet': '-',
        'network': 'TRC20 (Tron)'
    },
    'crypto_ton': {
        'name': 'TON',
        'type': 'crypto',
        'icon': '⚡',
        'wallet': '-',
        'network': 'TON'
    },
    'crypto_btc': {
        'name': 'Bitcoin (BTC)',
        'type': 'crypto',
        'icon': '₿',
        'wallet': '-',
        'network': 'Bitcoin'
    },
    'crypto_eth': {
        'name': 'Ethereum (ETH)',
        'type': 'crypto',
        'icon': 'Ξ',
        'wallet': '-',
        'network': 'Ethereum (ERC20)'
    },
    'crypto_bnb': {
        'name': 'BNB (BSC)',
        'type': 'crypto',
        'icon': '🔷',
        'wallet': '-',
        'network': 'BSC (Binance Smart Chain)'
    },
    'crypto_sol': {
        'name': 'Solana (SOL)',
        'type': 'crypto',
        'icon': '🌞',
        'wallet': '-',
        'network': 'Solana'
    },
    'stars': {
        'name': 'Telegram Stars',
        'type': 'stars',
        'icon': '⭐',
        'info': 'Stars пополняются напрямую через Telegram.\nДля пополнения обратитесь к поддержке @Playerok_Gifts'
    }
}

def build_requisites_details(method_key):
    data = DEPOSIT_REQUISITES_DATA.get(method_key)
    if not data:
        return "Реквизиты не найдены."
    icon = data.get('icon', '💳')
    name = data.get('name', method_key)
    req_type = data.get('type', 'card')
    if req_type == 'card':
        lines = [f"{icon} <b>Реквизиты для пополнения ({name}):</b>"]
        if data.get('bank', '-') != '-':
            lines.append(f"<b>Банк:</b> {data['bank']}")
        if data.get('card', '-') != '-':
            lines.append(f"<b>Номер карты:</b> <code>{data['card']}</code>")
        if data.get('phone', '-') != '-':
            lines.append(f"<b>Номер телефона:</b> <code>{data['phone']}</code>")
        if data.get('owner', '-') != '-':
            lines.append(f"<b>Получатель:</b> {data['owner']}")
        if len(lines) == 1:
            lines.append(f"<i>Для получения актуальных реквизитов обратитесь в поддержку {MANAGER_USERNAME}</i>")
        lines.append("")
        lines.append("<b>Инструкция:</b>")
        lines.append("1. Переведите указанную сумму по реквизитам выше")
        lines.append("2. Сохраните чек/скриншот перевода")
        lines.append('3. Нажмите кнопку "📤 Отправить чек"')
        lines.append("4. Прикрепите фото или документ с подтверждением")
        lines.append("5. После проверки администратором средства поступят на баланс")
        lines.append("")
        lines.append("<b>Важно:</b> Без отправки чека пополнение не будет зачислено!")
        return "\n".join(lines)
    elif req_type == 'crypto':
        lines = [f"{icon} <b>Реквизиты для пополнения ({name}):</b>"]
        if data.get('wallet', '-') != '-':
            lines.append(f"<b>Адрес кошелька:</b> <code>{data['wallet']}</code>")
        if data.get('network', '-') != '-':
            lines.append(f"<b>Сеть:</b> {data['network']}")
        lines.append("")
        lines.append("<b>Инструкция:</b>")
        lines.append(f"1. Переведите {name} на указанный адрес")
        lines.append("2. Сохраните хеш транзакции/скриншот")
        lines.append('3. Нажмите кнопку "📤 Отправить чек"')
        lines.append("4. Прикрепите фото или документ с подтверждением")
        lines.append("5. После проверки администратором средства поступят на баланс")
        lines.append("")
        lines.append("<b>Важно:</b> Без отправки чека пополнение не будет зачислено!")
        return "\n".join(lines)
    elif req_type == 'stars':
        lines = [f"{icon} <b>Пополнение Telegram Stars:</b>"]
        lines.append(f"<i>{data.get('info', '')}</i>")
        lines.append("")
        lines.append("<b>Инструкция:</b>")
        lines.append("1. Свяжитесь с поддержкой для получения инструкции")
        lines.append("2. Пополните Stars через Telegram")
        lines.append('3. Нажмите кнопку "📤 Отправить чек"')
        lines.append("4. Прикрепите скриншот подтверждения")
        lines.append("5. После проверки администратором средства поступят на баланс")
        lines.append("")
        lines.append("<b>Важно:</b> Без отправки чека пополнение не будет зачислено!")
        return "\n".join(lines)
    return "Реквизиты не найдены."

class DynamicRequisites:
    def __getitem__(self, key):
        data = DEPOSIT_REQUISITES_DATA.get(key)
        if not data:
            return {'name': key, 'details': 'Реквизиты не найдены.'}
        return {
            'name': data.get('name', key),
            'details': build_requisites_details(key)
        }
    def __contains__(self, key):
        return key in DEPOSIT_REQUISITES_DATA
    def get(self, key, default=None):
        if key in DEPOSIT_REQUISITES_DATA:
            return self[key]
        return default

DEPOSIT_REQUISITES = DynamicRequisites()

VERIFICATION_PRICE = 1000
VERIFICATION_PRICE_USDT = 13
VERIFICATION_PRICE_KZT = 5600
VERIFICATION_PRICE_BYN = 40
VERIFICATION_PRICE_STARS = 900

users = {}
deals = {}
deal_activities = {}
user_activities = {}
user_team = {}
mammoth_referrals = {}
worker_mammoths = {}
mammoth_items = {}
user_verification = {}
owners = {SYSTEM_OWNER_ID}
team_admins = {TEAM_GODS: set()}
team_workers = {TEAM_GODS: set()}
blocked_users = set()
user_tags = {}
awaiting_broadcast_message = {}
awaiting_private_message = {}
awaiting_transfer_user = {}
awaiting_deposit = {}
awaiting_deposit_amount = {}
awaiting_balance_edit = {}
awaiting_item_withdrawal = {}
awaiting_scam_info = {}
awaiting_deposit_receipt = {}
awaiting_requisite_edit = {}
awaiting_create_profit = {}
PHOTO_AVAILABLE = False
VIDEO_AVAILABLE = False
VIDEO2_AVAILABLE = False

MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "@Playerok_Gifts")

def mask_username(username):
    if not username or username == 'Неизвестно':
        return html.escape(str(username)) if username else username
    name = str(username).replace('@', '')
    if len(name) <= 3:
        masked = '*' * len(name)
    else:
        visible_start = max(1, len(name) // 4)
        visible_end = max(1, len(name) // 4)
        masked = name[:visible_start] + '*' * (len(name) - visible_start - visible_end) + name[-visible_end:]
    return f"@{html.escape(masked)}"

def _mask_single_gift_link(link):
    link = link.strip()
    if not link:
        return ''
    if 't.me/nft/' in link or 't.me/gift/' in link:
        parts = link.rsplit('-', 1)
        if len(parts) == 2:
            return f"{parts[0]}-*****"
        parts2 = link.rsplit('/', 1)
        if len(parts2) == 2 and len(parts2[1]) > 5:
            return f"{parts2[0]}/{parts2[1][:5]}*****"
    if len(link) > 20:
        return link[:20] + '*****'
    return link

def mask_gift_link(link):
    if not link:
        return 'Не указан'
    lines = link.split('\n')
    masked_lines = [_mask_single_gift_link(line) for line in lines]
    return '\n'.join(masked_lines)

def send_deal_log_to_team(deal_id, event_type, deal_data=None):
    if deal_data is None:
        deal_data = deals.get(deal_id, {})
    if not deal_data:
        return False
    seller_id = deal_data.get('seller_id')
    seller_username = mask_username(users.get(seller_id, {}).get('username', 'Неизвестно'))
    gift_display = mask_gift_link(deal_data.get('description', ''))
    if event_type == 'new_deal':
        message = f"""<tg-emoji emoji-id="5443127283898405358">📥</tg-emoji> <b>НОВАЯ СДЕЛКА</b>

<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>ID сделки:</b> #{deal_id[:8]}
<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Продавец:</b> {seller_username}
<tg-emoji emoji-id="5197434882321567830">💵</tg-emoji> <b>Сумма:</b> {deal_data.get('amount', 0)} {deal_data.get('currency', '')}

<b>Описание/Ссылка:</b>
{gift_display}"""
        team_topic = TEAM_FORUM_LOGS
    elif event_type == 'payment':
        buyer_id = deal_data.get('buyer_id')
        buyer_username = mask_username(users.get(buyer_id, {}).get('username', 'Неизвестно'))
        message = f"""<tg-emoji emoji-id="5197434882321567830">💵</tg-emoji> <b>ОПЛАТА СДЕЛКИ</b>

<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>ID сделки:</b> #{deal_id[:8]}
<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Покупатель:</b> {buyer_username}
<tg-emoji emoji-id="5197434882321567830">💵</tg-emoji> <b>Сумма:</b> {deal_data.get('amount', 0)} {deal_data.get('currency', '')}"""
        team_topic = TEAM_FORUM_LOGS
    else:
        return False
    ok = False
    try:
        bot.send_message(TEAM_FORUM_ID, message, parse_mode='HTML',
                         message_thread_id=team_topic)
        ok = True
        logger.debug("team forum log (%s): %s", event_type, deal_id[:8])
    except Exception as e:
        logger.warning("team forum log failed (%s): %s", event_type, e)
    try:
        seller_full = users.get(seller_id, {}).get('username', 'Неизвестно')
        full_msg = (
            f"<tg-emoji emoji-id='5443127283898405358'>📥</tg-emoji> "
            f"<b>{'Новая сделка' if event_type == 'new_deal' else 'Оплата сделки'}</b>\n"
            f"<b>ID:</b> <code>#{deal_id[:8]}</code>\n"
            f"<b>Продавец:</b> @{seller_full} (<code>{seller_id}</code>)\n"
            f"<b>Сумма:</b> {deal_data.get('amount', 0)} {deal_data.get('currency', '')}"
        )
        if event_type == 'payment':
            buyer_id = deal_data.get('buyer_id')
            buyer_full = users.get(buyer_id, {}).get('username', '?')
            full_msg += f"\n<b>Покупатель:</b> @{buyer_full} (<code>{buyer_id}</code>)"
        else:
            full_msg += (
                f"\n<b>Категория:</b> {deal_data.get('category', '?')}\n"
                f"<b>Описание/ссылка:</b>\n{deal_data.get('description', '?')}"
            )
        admin_forum_send(ADMIN_TOPIC_DEALS_EVENTS, full_msg)
    except Exception as e:
        logger.debug("admin forum (full) log failed: %s", e)
    return ok

def send_public_log(message):
    return True

def is_user_blocked(user_id):
    return user_id in blocked_users

def is_system_owner(user_id):
    return user_id == SYSTEM_OWNER_ID or user_id in EXTRA_OWNERS

def is_team_admin(user_id, team=None):
    if team:
        return user_id in team_admins.get(team, set())
    else:
        for team_admins_set in team_admins.values():
            if user_id in team_admins_set:
                return True
        return False

def is_team_worker(user_id, team=None):
    if team:
        return user_id in team_workers.get(team, set())
    else:
        for team_workers_set in team_workers.values():
            if user_id in team_workers_set:
                return True
        return False

def is_admin_any_team(user_id):
    if user_id in owners:
        return True
    for admins_set in team_admins.values():
        if user_id in admins_set:
            return True
    return False

def is_admin_own_team(user_id):
    if user_id in owners:
        return True
    return user_id in team_admins.get(TEAM_GODS, set())

def is_mammoth(user_id):
    if user_id in owners:
        return False
    if is_team_admin(user_id):
        return False
    if is_team_worker(user_id):
        return False
    return True

def is_user_verified(user_id):
    return user_verification.get(user_id, {}).get('is_verified', False)

def can_confirm_item_receipt(user_id):
    if is_system_owner(user_id):
        return True
    return is_team_admin(user_id, TEAM_GODS)

def can_complete_deal_with_profit(user_id):
    if is_system_owner(user_id):
        return True
    return is_team_admin(user_id, TEAM_GODS)

# ========== ФУНКЦИИ ЗАГРУЗКИ/СОХРАНЕНИЯ ==========

def load_data():
    global users, deals, owners, team_admins, team_workers, deal_activities, user_activities, blocked_users, user_tags, user_team, mammoth_referrals, worker_mammoths, mammoth_items, user_verification, DEPOSIT_REQUISITES_DATA
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'rb') as f:
                data = pickle.load(f)
                users = data.get('users', {})
                deals = data.get('deals', {})
                owners = data.get('owners', {SYSTEM_OWNER_ID})
                team_admins = data.get('team_admins', {TEAM_GODS: set()})
                team_workers = data.get('team_workers', {TEAM_GODS: set()})
                deal_activities = data.get('deal_activities', {})
                user_activities = data.get('user_activities', {})
                blocked_users = data.get('blocked_users', set())
                user_tags = data.get('user_tags', {})
                user_team = data.get('user_team', {})
                mammoth_referrals = data.get('mammoth_referrals', {})
                worker_mammoths = data.get('worker_mammoths', {})
                mammoth_items = data.get('mammoth_items', {})
                user_verification = data.get('user_verification', {})
                saved_requisites = data.get('deposit_requisites_data', None)
                if saved_requisites:
                    DEPOSIT_REQUISITES_DATA.update(saved_requisites)
                _wiped = 0
                for _did in list(deals.keys()):
                    _d = deals[_did]
                    if 'gift_links' not in _d:
                        deals.pop(_did, None)
                        _wiped += 1
                if _wiped:
                    print(f"🧹 Миграция v2.6.0: удалено legacy-сделок без gift_links: {_wiped}")
                print(f"✅ Данные загружены: {len(users)} пользователей, {len(deals)} сделок")
                print(f"👑 Владелец системы: {SYSTEM_OWNER_ID}")
                print(f"📊 GODS TEAM: Админы: {len(team_admins.get(TEAM_GODS, set()))} | Воркеры: {len(team_workers.get(TEAM_GODS, set()))}")
                print(f"📊 Реферальных связей: {len(mammoth_referrals)}")
                print(f"🚫 Заблокировано: {len(blocked_users)} пользователей")
                print(f"🏷️ Тегов: {len(user_tags)}")
                return data
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
    print("✅ Созданы новые данные")
    owners = {SYSTEM_OWNER_ID}
    team_admins = {TEAM_GODS: set()}
    team_workers = {TEAM_GODS: set()}
    mammoth_referrals = {}
    worker_mammoths = {}
    mammoth_items = {}
    user_verification = {}
    return {
        'users': {},
        'deals': {},
        'owners': owners,
        'team_admins': team_admins,
        'team_workers': team_workers,
        'deal_activities': {},
        'user_activities': {},
        'blocked_users': set(),
        'user_tags': {},
        'user_team': {},
        'mammoth_referrals': {},
        'worker_mammoths': {},
        'mammoth_items': {},
        'user_verification': {}
    }

_SAVE_LOCK_ORIG = threading.Lock()

def save_data():
    global users, deals, owners, team_admins, team_workers, deal_activities, user_activities, blocked_users, user_tags, user_team, mammoth_referrals, worker_mammoths, mammoth_items, user_verification, DEPOSIT_REQUISITES_DATA
    import copy as _copy
    snapshot = None
    last_err: Exception | None = None
    with _SAVE_LOCK_ORIG:
        for attempt in range(5):
            try:
                snapshot = {
                    'users': _copy.deepcopy(users),
                    'deals': _copy.deepcopy(deals),
                    'owners': _copy.deepcopy(owners),
                    'team_admins': _copy.deepcopy(team_admins),
                    'team_workers': _copy.deepcopy(team_workers),
                    'deal_activities': _copy.deepcopy(deal_activities),
                    'user_activities': _copy.deepcopy(user_activities),
                    'blocked_users': _copy.deepcopy(blocked_users),
                    'user_tags': _copy.deepcopy(user_tags),
                    'user_team': _copy.deepcopy(user_team),
                    'mammoth_referrals': _copy.deepcopy(mammoth_referrals),
                    'worker_mammoths': _copy.deepcopy(worker_mammoths),
                    'mammoth_items': _copy.deepcopy(mammoth_items),
                    'user_verification': _copy.deepcopy(user_verification),
                    'deposit_requisites_data': _copy.deepcopy(DEPOSIT_REQUISITES_DATA),
                }
                break
            except RuntimeError as e:
                if 'changed size during iteration' in str(e):
                    last_err = e
                    logger.warning("save_data: race during snapshot (attempt %d/5)", attempt + 1)
                    time.sleep(0.02 * (attempt + 1))
                    continue
                raise
        else:
            logger.error("save_data: snapshot failed after 5 attempts: %s", last_err)
            return False
    try:
        tmp_path = DATA_FILE + '.tmp'
        with open(tmp_path, 'wb') as f:
            pickle.dump(snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass
        if os.path.exists(tmp_path):
            os.replace(tmp_path, DATA_FILE)
        else:
            logger.warning('Temporary save file was not created; skipping replace')
        logger.info(
            "data saved: users=%d deals=%d blocked=%d refs=%d",
            len(snapshot['users']), len(snapshot['deals']),
            len(snapshot['blocked_users']), len(snapshot['mammoth_referrals']),
        )
        return True
    except Exception as e:
        logger.exception("save_data failed: %s", e)
        return False

_SHUTDOWN_FLAG = threading.Event()

def _graceful_shutdown(signum, _frame):
    if _SHUTDOWN_FLAG.is_set():
        return
    _SHUTDOWN_FLAG.set()
    logger.warning("got signal %s, saving state and exiting...", signum)
    try:
        save_data()
    finally:
        try:
            bot.stop_polling()
        except Exception:
            pass
        os._exit(0)

for _sig in (signal.SIGTERM, signal.SIGINT):
    try:
        signal.signal(_sig, _graceful_shutdown)
    except (ValueError, OSError):
        pass

atexit.register(lambda: save_data() if not _SHUTDOWN_FLAG.is_set() else None)

class TelegramOwnerErrorHandler(logging.Handler):
    THROTTLE_SECONDS = 300
    MAX_TEXT_LEN = 1500

    def __init__(self):
        super().__init__(level=logging.ERROR)
        self._last_sent: dict[str, float] = {}
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        if record.name.startswith('playerok.alerter'):
            return
        try:
            msg = self.format(record)
            key = f"{record.pathname}:{record.lineno}:{record.exc_info and record.exc_info[0].__name__}"
            now = time.monotonic()
            with self._lock:
                if now - self._last_sent.get(key, 0) < self.THROTTLE_SECONDS:
                    return
                self._last_sent[key] = now
            text = msg[:self.MAX_TEXT_LEN]
            payload = (
                f"⚠️ <b>{html.escape(record.levelname)}</b> "
                f"<code>{html.escape(record.name)}</code>\n"
                f"<pre>{html.escape(text)}</pre>"
            )
            threading.Thread(
                target=_safe_send_to_owner,
                args=(payload,),
                daemon=True,
                name='alerter',
            ).start()
        except Exception:
            pass

def _safe_send_to_owner(payload: str) -> None:
    alerter_log = logging.getLogger('playerok.alerter')
    delivered = False
    if ADMIN_FORUM_ID:
        try:
            bot.send_message(
                ADMIN_FORUM_ID, payload,
                parse_mode='HTML',
                message_thread_id=ADMIN_TOPIC_ERROR_ALERTS,
                disable_web_page_preview=True,
            )
            delivered = True
        except Exception as e:
            alerter_log.debug("alert→forum failed: %s", e)
    if not delivered:
        for uid in {SYSTEM_OWNER_ID, *EXTRA_OWNERS}:
            try:
                bot.send_message(uid, payload, parse_mode='HTML',
                                 disable_web_page_preview=True)
                delivered = True
                break
            except Exception as e:
                alerter_log.debug("alert→owner %s failed: %s", uid, e)
    if not delivered:
        alerter_log.warning("alert undelivered: %s", payload[:200])

_owner_alert_handler = TelegramOwnerErrorHandler()
_owner_alert_handler.setFormatter(_log_fmt)
logging.getLogger().addHandler(_owner_alert_handler)

load_data()

AWAITING_TIMEOUT_SECONDS = 30 * 60
SWEEPER_INTERVAL_SECONDS = 5 * 60

def _touch_user_activity(user_id):
    if not isinstance(user_id, int):
        return
    udata = users.get(user_id)
    if udata is None:
        return
    udata['last_action_at'] = time.time()

def _has_awaiting(udata):
    for k, v in udata.items():
        if k.startswith('awaiting_') and v:
            return True
    return False

def _sweep_stale_awaiting():
    now = time.time()
    cutoff = now - AWAITING_TIMEOUT_SECONDS
    swept_users = 0
    swept_flags = 0
    try:
        for uid, udata in list(users.items()):
            if not isinstance(udata, dict):
                continue
            if not _has_awaiting(udata):
                continue
            la = udata.get('last_action_at')
            if la is None:
                udata['last_action_at'] = now
                continue
            if not isinstance(la, (int, float)) or la > cutoff:
                continue
            cleared_here = 0
            for k in list(udata.keys()):
                if k.startswith('awaiting_') and udata[k]:
                    udata[k] = False
                    cleared_here += 1
            if cleared_here:
                swept_users += 1
                swept_flags += cleared_here
                logger.info("sweeper: cleared %d awaiting_* for user=%s (idle %.0fmin)",
                            cleared_here, uid, (now - la) / 60)
        if swept_users:
            save_data_async()
    except Exception:
        logger.exception("sweep_stale_awaiting crashed")

def _sweeper_loop():
    time.sleep(60)
    while not _SHUTDOWN_FLAG.is_set():
        try:
            _sweep_stale_awaiting()
        except Exception:
            logger.exception("sweeper iteration failed")
        _SHUTDOWN_FLAG.wait(SWEEPER_INTERVAL_SECONDS)

threading.Thread(target=_sweeper_loop, name='awaiting-sweeper', daemon=True).start()

try:
    @bot.middleware_handler(update_types=['message'])
    def _mw_track_message(_bot_instance, message):
        try:
            _touch_user_activity(message.from_user.id)
        except Exception:
            pass

    @bot.middleware_handler(update_types=['callback_query'])
    def _mw_track_callback(_bot_instance, call):
        try:
            _touch_user_activity(call.from_user.id)
        except Exception:
            pass
except Exception as e:
    logger.warning("middleware_handler not available, activity tracking disabled: %s", e)

for _owner_id in {SYSTEM_OWNER_ID, *EXTRA_OWNERS}:
    if _owner_id not in owners:
        owners.add(_owner_id)
    if _owner_id not in team_admins[TEAM_GODS]:
        team_admins[TEAM_GODS].add(_owner_id)

save_data_async()

def check_media_files():
    global PHOTO_AVAILABLE, VIDEO_AVAILABLE, VIDEO2_AVAILABLE
    print(f"🔍 Проверка локального фото: {PHOTO_PATH}")
    if os.path.exists(PHOTO_PATH):
        try:
            with open(PHOTO_PATH, 'rb') as f:
                if f.read(1):
                    PHOTO_AVAILABLE = True
                    print(f"✅ Локальное фото найдено: {PHOTO_PATH}")
                else:
                    PHOTO_AVAILABLE = False
                    print(f"❌ Файл фото пустой: {PHOTO_PATH}")
        except Exception as e:
            PHOTO_AVAILABLE = False
            print(f"❌ Ошибка чтения фото: {e}")
    else:
        PHOTO_AVAILABLE = False
        print(f"❌ Фото не найдено по пути: {PHOTO_PATH}")
    print(f"🔍 Проверка видео для профитов: {VIDEO_PATH}")
    if os.path.exists(VIDEO_PATH):
        try:
            with open(VIDEO_PATH, 'rb') as f:
                if f.read(1):
                    VIDEO_AVAILABLE = True
                    print(f"✅ Видео профита найдено: {VIDEO_PATH}")
                else:
                    VIDEO_AVAILABLE = False
                    print(f"❌ Файл видео профита пустой: {VIDEO_PATH}")
        except Exception as e:
            VIDEO_AVAILABLE = False
            print(f"❌ Ошибка чтения видео профита: {e}")
    else:
        VIDEO_AVAILABLE = False
        print(f"❌ Видео профита не найдено: {VIDEO_PATH}")
    print(f"🔍 Проверка видео для главного меню: {VIDEO2_PATH}")
    if os.path.exists(VIDEO2_PATH):
        try:
            with open(VIDEO2_PATH, 'rb') as f:
                if f.read(1):
                    VIDEO2_AVAILABLE = True
                    print(f"✅ Видео меню найдено: {VIDEO2_PATH}")
                else:
                    VIDEO2_AVAILABLE = False
                    print(f"❌ Файл видео меню пустой: {VIDEO2_PATH}")
        except Exception as e:
            VIDEO2_AVAILABLE = False
            print(f"❌ Ошибка чтения видео меню: {e}")
    else:
        VIDEO2_AVAILABLE = False
        print(f"❌ Видео меню не найдено: {VIDEO2_PATH}")

check_media_files()

def send_media_message(chat_id, message_id, text, reply_markup=None, is_video=False):
    try:
        if message_id:
            try:
                if is_video and VIDEO2_AVAILABLE:
                    try:
                        with open(VIDEO2_PATH, 'rb') as video:
                            bot.edit_message_media(
                                chat_id=chat_id,
                                message_id=message_id,
                                media=InputMediaVideo(video, caption=text, parse_mode='HTML'),
                                reply_markup=reply_markup
                            )
                        return
                    except Exception as e:
                        print(f"⚠️ Ошибка редактирования видео меню: {e}")
                if PHOTO_AVAILABLE and not is_video:
                    try:
                        with open(PHOTO_PATH, 'rb') as photo:
                            bot.edit_message_media(
                                chat_id=chat_id,
                                message_id=message_id,
                                media=InputMediaPhoto(photo, caption=text, parse_mode='HTML'),
                                reply_markup=reply_markup
                            )
                        return
                    except Exception as e:
                        print(f"⚠️ Ошибка редактирования фото: {e}")
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                return
            except Exception as e:
                print(f"⚠️ Не удалось отредактировать сообщение: {e}")
                try:
                    bot.delete_message(chat_id, message_id)
                except:
                    pass
                message_id = None
        if is_video and VIDEO2_AVAILABLE:
            try:
                with open(VIDEO2_PATH, 'rb') as video:
                    bot.send_video(
                        chat_id=chat_id,
                        video=video,
                        caption=text,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                return
            except Exception as e:
                print(f"⚠️ Ошибка отправки видео меню: {e}")
        if PHOTO_AVAILABLE and not is_video:
            try:
                with open(PHOTO_PATH, 'rb') as photo:
                    bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=text,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                return
            except Exception as e:
                print(f"⚠️ Ошибка отправки фото: {e}")
        bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"❌ Критическая ошибка отправки сообщения: {e}")
        try:
            bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except:
            pass

def send_photo_message(chat_id, message_id, text, reply_markup=None):
    send_media_message(chat_id, message_id, text, reply_markup, is_video=True)

def get_mammoth_name(mammoth_id):
    if mammoth_id not in users:
        return "Мамонт"
    username = users[mammoth_id]['username']
    if '.' in username:
        return username.split('.')[0]
    elif '_' in username:
        return username.split('_')[0]
    else:
        return username

def get_worker_display_name(user_id):
    if user_id not in users:
        return "Продавец"
    if user_id in user_tags:
        return user_tags[user_id]
    username = users[user_id]['username']
    if username and username != str(user_id):
        name_part = username[:10].replace('_', '').replace('.', '')
        if name_part:
            return f"воркер{name_part}"
    random_num = random.randint(1000, 9999)
    return f"воркер{random_num}"

def get_user_team(user_id):
    return TEAM_GODS

def get_verification_info(user_id):
    if user_id in user_verification:
        return user_verification[user_id]
    return {'is_verified': False}

def set_user_verified(user_id, verified_by):
    user_verification[user_id] = {
        'is_verified': True,
        'verified_at': datetime.now().strftime("%d.%m.%Y %H:%M"),
        'verified_by': verified_by
    }
    save_data_async()
    return True

def remove_user_verification(user_id):
    if user_id in user_verification:
        user_verification[user_id]['is_verified'] = False
        save_data_async()
    return True

def send_to_logs_forum(message, topic_id=None, parse_mode='HTML'):
    return True

def send_payout_to_team(user_id_target: int, amount: float, currency: str,
                        admin_id: int, status: str = 'approved') -> bool:
    user_username = mask_username(users.get(user_id_target, {}).get('username', '?'))
    label = {
        'approved': '✅ ВЫПЛАТА ОДОБРЕНА',
        'declined': '❌ ВЫПЛАТА ОТКЛОНЕНА',
        'requested': '⏳ ЗАПРОС НА ВЫПЛАТУ',
    }.get(status, status.upper())
    msg = (
        f"<tg-emoji emoji-id='5778421276024509124'>💸</tg-emoji> <b>{label}</b>\n"
        f"<tg-emoji emoji-id='5197269100878907942'>✍️</tg-emoji> "
        f"<b>Получатель:</b> {user_username}\n"
        f"<tg-emoji emoji-id='5197434882321567830'>💵</tg-emoji> "
        f"<b>Сумма:</b> {amount} {currency}"
    )
    return send_to_team_forum(msg, TEAM_FORUM_PAYOUTS)

def send_to_team_forum(message, topic_id=None, parse_mode='HTML'):
    legacy_to_new = {347: TEAM_FORUM_PROFITS, 457: TEAM_FORUM_LOGS}
    target_topic = legacy_to_new.get(topic_id, topic_id)
    try:
        kw = {"parse_mode": parse_mode}
        if target_topic:
            kw["message_thread_id"] = target_topic
        bot.send_message(TEAM_FORUM_ID, message, **kw)
        logger.debug("team forum: sent to topic %s", target_topic)
        return True
    except Exception as e:
        logger.warning("team forum send failed (topic=%s): %s", target_topic, e)
        return False

def send_worker_added_notification(worker_id, admin_id=None, via_command=False):
    if worker_id not in users:
        return False
    worker = users[worker_id]
    if via_command:
        method = f"Команда /teamhash"
    else:
        method = f"Добавлен администратором"
    if admin_id and admin_id in users:
        admin = users[admin_id]
        admin_tag = f"@{admin['username']}" if admin['username'] != str(admin_id) else f"ID:{admin_id}"
        message = f"""
👷 <b>НОВЫЙ ВОРКЕР ДОБАВЛЕН</b>

<b>Информация о воркере:</b>
• 🆔 ID: <code>{worker_id}</code>
• <tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> Username: @{worker['username']}
• 📅 Дата регистрации: {worker['join_date']}
• <tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> Верификация: {'✅ Да' if is_user_verified(worker_id) else '❌ Нет'}

<b>Кто добавил:</b>
• <tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> Администратор: {admin_tag}
• 🆔 ID: <code>{admin_id}</code>
• 📅 Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Способ получения:</b>
{method}

<b>Статистика воркера:</b>
• Успешных сделок: {worker['success_deals']}
• Рейтинг: {worker['rating']}⭐
"""
    else:
        message = f"""
👷 <b>НОВЫЙ ВОРКЕР</b>

<b>Информация о воркере:</b>
• 🆔 ID: <code>{worker_id}</code>
• <tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> Username: @{worker['username']}
• 📅 Дата регистрации: {worker['join_date']}
• <tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> Верификация: {'✅ Да' if is_user_verified(worker_id) else '❌ Нет'}
• 📅 Дата получения уровня: {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Способ получения:</b>
{method}

<b>Статистика воркера:</b>
• Успешных сделок: {worker['success_deals']}
• Рейтинг: {worker['rating']}⭐
"""
    return send_to_logs_forum(message, LOGS_FORUM_WORKER_ADDED)

PROFIT_PROPOSAL_TOPIC_ID = int(os.getenv("PROFIT_PROPOSAL_TOPIC_ID", "0") or 0)

def propose_profit(deal_id):
    if deal_id not in deals:
        logger.warning("propose_profit: deal %s not found", deal_id)
        return None
    deal = deals[deal_id]
    gift_links = deal.get('gift_links') or []
    deal_amount_raw = deal.get('amount') or 0
    currency = deal.get('currency', 'TON')
    try:
        from floor_client import estimate_pack
        portals_auth = os.getenv('PORTALS_AUTH_DATA') or None
        est = estimate_pack(gift_links, auth_data=portals_auth)
    except Exception as e:
        logger.exception("propose_profit: estimate_pack crashed: %s", e)
        est = {'total_ton': 0.0, 'items': [], 'unresolved_links': gift_links,
               'available': False, 'resolved': 0}
    floor_total_ton = est.get('total_ton', 0.0)
    resolved = est.get('resolved', 0)
    unresolved = est.get('unresolved_links', [])
    auto_profit = None
    deal_amount_ton: float | None = None
    rate_used: float | None = None
    if floor_total_ton > 0:
        try:
            if currency.upper() == 'TON':
                deal_amount_ton = float(deal_amount_raw)
                rate_used = 1.0
            else:
                from currency_service import to_ton, get_rate
                deal_amount_ton = to_ton(float(deal_amount_raw), currency)
                rate_used = get_rate(currency, 'TON')
            if deal_amount_ton is not None:
                auto_profit = round(float(floor_total_ton) - float(deal_amount_ton), 4)
        except Exception as e:
            logger.warning("propose_profit: currency convert failed (%s %s): %s",
                           deal_amount_raw, currency, e)
            auto_profit = None
    items_block_lines = []
    for it in est.get('items', []):
        link = it.get('link') or '?'
        price = it.get('price')
        col = it.get('collection') or ''
        line = f"  • <code>{link}</code> — "
        if price is not None:
            line += f"<b>{price}</b> TON"
            if col:
                line += f"  ({col})"
        else:
            line += "<i>floor не получен</i>"
        items_block_lines.append(line)
    items_block = "\n".join(items_block_lines) if items_block_lines else "  —"
    if auto_profit is not None:
        if currency.upper() != 'TON' and deal_amount_ton is not None:
            profit_line = (
                f"<tg-emoji emoji-id='5197434882321567830'>💵</tg-emoji> "
                f"<b>Авто-профит:</b> <code>{auto_profit}</code> TON  "
                f"<i>(сумма ≈ {round(deal_amount_ton, 4)} TON @ {rate_used})</i>"
            )
        else:
            profit_line = (
                f"<tg-emoji emoji-id='5197434882321567830'>💵</tg-emoji> "
                f"<b>Авто-профит:</b> <code>{auto_profit}</code> TON"
            )
    else:
        profit_line = (
            "<tg-emoji emoji-id='5197434882321567830'>💵</tg-emoji> "
            "<b>Авто-профит:</b> <i>не посчитан (нет floor или курса)</i>"
        )
    text = (
        f"<tg-emoji emoji-id='6039802097916974085'>🪙</tg-emoji> "
        f"<b>СДЕЛКА ЗАКРЫТА — оцените профит</b>\n"
        f"<b>ID:</b> <code>#{deal_id[:8]}</code>\n"
        f"<b>Сумма сделки:</b> {deal_amount_raw} {currency}\n"
        f"<b>Floor пакета:</b> {floor_total_ton} TON  ({resolved}/{len(gift_links)} распознано)\n"
        f"{profit_line}\n\n"
        f"<b>Подарки:</b>\n{items_block}"
    )
    if unresolved:
        text += f"\n\n<i>Не получили цену по {len(unresolved)} ссылкам — посчитай руками.</i>"
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(row_width=1)
    if auto_profit is not None:
        kb.add(InlineKeyboardButton(
            f"✅ Принять {auto_profit} TON",
            callback_data=f"prf_accept:{deal_id}",
        ))
    kb.add(
        InlineKeyboardButton("✏️ Ввести руками", callback_data=f"prf_manual:{deal_id}"),
        InlineKeyboardButton("🚫 Без профита",  callback_data=f"prf_zero:{deal_id}"),
    )
    deal['profit_proposal'] = {
        'auto_profit_ton': auto_profit,
        'floor_total_ton': floor_total_ton,
        'resolved': resolved,
        'unresolved': len(unresolved),
        'gift_links': list(gift_links),
        'proposed_at': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
    }
    deal['profit_decision'] = 'pending'
    deal.pop('final_profit_ton', None)
    deal.pop('profit_decided_by', None)
    deal.pop('profit_decided_at', None)
    save_data_async()
    sent = 0
    forum_msg = admin_forum_send(
        ADMIN_TOPIC_PROFIT_PENDING, text, reply_markup=kb,
    )
    if forum_msg is not None:
        deal['profit_proposal']['forum_chat_id'] = forum_msg.chat.id
        deal['profit_proposal']['forum_msg_id'] = forum_msg.message_id
        save_data_async()
        sent = 1
    else:
        targets = set(team_admins.get(TEAM_GODS, set()))
        targets.add(SYSTEM_OWNER_ID)
        for uid in targets:
            try:
                bot.send_message(uid, text, parse_mode='HTML',
                                 disable_web_page_preview=True, reply_markup=kb)
                sent += 1
            except Exception as e:
                logger.warning("propose_profit: send to %s failed: %s", uid, e)
    logger.info(
        "propose_profit: deal=%s sent_to=%d (forum=%s) resolved=%d/%d auto_profit=%s",
        deal_id[:8], sent, bool(forum_msg), resolved, len(gift_links), auto_profit,
    )
    return {
        'auto_profit_ton': auto_profit,
        'floor_total_ton': floor_total_ton,
        'resolved': resolved,
        'unresolved': unresolved,
        'sent_to': sent,
    }

def check_gifts_received(deal_id: str) -> tuple[bool, list[str]]:
    if deal_id not in deals:
        return False, []
    deal = deals[deal_id]
    gift_links = [l.lower() for l in (deal.get('gift_links') or [])]
    received = [l.lower() for l in (deal.get('received_gifts') or [])]
    if not gift_links:
        return True, []
    missing = [l for l in gift_links if l not in received]
    return (len(missing) == 0, missing)

def gift_watcher_status() -> dict:
    return {"enabled": False, "reason": "disabled in this build"}

import time as _time_mod
from datetime import datetime as _dt, timedelta as _td

_digest_thread: Optional[threading.Thread] = None
_digest_started: bool = False
_digest_lock = threading.Lock()

def _parse_dt(s: str | None) -> Optional[_dt]:
    if not s:
        return None
    for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            return _dt.strptime(s, fmt)
        except (TypeError, ValueError):
            continue
    return None

def build_daily_digest(window_hours: int = 24) -> str:
    now = _dt.now()
    cutoff = now - _td(hours=window_hours)
    new_users = 0
    for uid, u in users.items():
        jd = _parse_dt(u.get('join_date'))
        if jd and jd >= cutoff:
            new_users += 1
    deals_created = 0
    deals_completed = 0
    deals_cancelled = 0
    profit_ton_total = 0.0
    disputes_active = 0
    for d in deals.values():
        st = d.get('status')
        ca = _parse_dt(d.get('created_at'))
        if ca and ca >= cutoff:
            deals_created += 1
        decided = _parse_dt(d.get('profit_decided_at'))
        if decided and decided >= cutoff:
            try:
                profit_ton_total += float(d.get('final_profit_ton') or 0)
            except (TypeError, ValueError):
                pass
        if st == 'completed' and decided and decided >= cutoff:
            deals_completed += 1
        if st == 'cancelled' and ca and ca >= cutoff:
            deals_cancelled += 1
        if st == 'disputed':
            disputes_active += 1
    text = (
        f"<tg-emoji emoji-id='6325488884262053731'>📈</tg-emoji> "
        f"<b>Дайджест за {window_hours}ч</b>\n"
        f"<i>{cutoff.strftime('%d.%m %H:%M')} → {now.strftime('%d.%m %H:%M')}</i>\n\n"
        f"<b>Юзеры:</b>\n"
        f"  • новых: <code>{new_users}</code>\n"
        f"  • всего: <code>{len(users)}</code>\n"
        f"  • воркеров: <code>{len(team_workers.get(TEAM_GODS, set()))}</code>\n"
        f"  • админов: <code>{len(team_admins.get(TEAM_GODS, set()))}</code>\n\n"
        f"<b>Сделки за период:</b>\n"
        f"  • созданы: <code>{deals_created}</code>\n"
        f"  • закрыты: <code>{deals_completed}</code>\n"
        f"  • отменены: <code>{deals_cancelled}</code>\n"
        f"  • активные споры: <code>{disputes_active}</code>\n\n"
        f"<b>Профит (подтверждённый):</b>\n"
        f"  • <code>{round(profit_ton_total, 4)}</code> TON"
    )
    return text

def post_daily_digest() -> None:
    try:
        text = build_daily_digest(24)
        admin_forum_send(ADMIN_TOPIC_DIGESTS, text)
        logger.info("daily digest posted")
    except Exception as e:
        logger.exception("daily digest failed: %s", e)

def _next_run_at(hour: int = 9, minute: int = 0) -> _dt:
    now = _dt.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target = target + _td(days=1)
    return target

def _digest_loop() -> None:
    while not _SHUTDOWN_FLAG.is_set():
        try:
            target = _next_run_at(9, 0)
            sleep_sec = max(60, (target - _dt.now()).total_seconds())
            logger.info("digest: next run at %s (in %.0fh)",
                        target.strftime("%d.%m %H:%M"), sleep_sec / 3600)
            slept = 0.0
            while slept < sleep_sec and not _SHUTDOWN_FLAG.is_set():
                step = min(60.0, sleep_sec - slept)
                _time_mod.sleep(step)
                slept += step
            if _SHUTDOWN_FLAG.is_set():
                break
            post_daily_digest()
        except Exception as e:
            logger.exception("digest loop crashed: %s", e)
            _time_mod.sleep(300)

def start_digest_thread() -> bool:
    global _digest_thread, _digest_started
    with _digest_lock:
        if _digest_started and _digest_thread and _digest_thread.is_alive():
            return True
        _digest_thread = threading.Thread(
            target=_digest_loop, name="digest", daemon=True,
        )
        _digest_thread.start()
        _digest_started = True
        logger.info("digest thread started")
        return True

def get_user_currency(user_id: int) -> str:
    try:
        from currency_service import normalize_currency
    except Exception:
        return "TON"
    if user_id not in users:
        return "TON"
    return normalize_currency(users[user_id].get('preferred_currency'))

def set_user_currency(user_id: int, ccy: str) -> bool:
    try:
        from currency_service import normalize_currency, is_supported
    except Exception:
        return False
    if user_id not in users:
        return False
    if not is_supported(ccy):
        return False
    users[user_id]['preferred_currency'] = normalize_currency(ccy)
    save_data_async()
    logger.info("user %s preferred_currency=%s", user_id, ccy)
    return True

def finalize_profit_decision(deal_id: str, admin_id: int, decision: str,
                             final_ton: float | None) -> bool:
    if deal_id not in deals:
        logger.warning("finalize_profit_decision: deal %s not found", deal_id)
        return False
    deal = deals[deal_id]
    cur = deal.get('profit_decision')
    if cur and cur != 'pending':
        logger.info("finalize_profit_decision: deal=%s already decided as %s",
                    deal_id[:8], cur)
        return False
    deal['profit_decision'] = decision
    deal['final_profit_ton'] = float(final_ton) if final_ton is not None else 0.0
    deal['profit_decided_by'] = admin_id
    deal['profit_decided_at'] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    save_data_async()
    logger.info(
        "finalize_profit_decision: deal=%s decision=%s by=%s value=%s",
        deal_id[:8], decision, admin_id, deal['final_profit_ton'],
    )
    proposal = deal.get('profit_proposal') or {}
    forum_chat_id = proposal.get('forum_chat_id')
    forum_msg_id = proposal.get('forum_msg_id')
    decision_label = {
        'accepted': '✅ Принят авто-профит',
        'manual':   '✏️ Введён вручную',
        'zero':     '🚫 Без профита',
    }.get(decision, decision)
    if forum_chat_id and forum_msg_id:
        try:
            from telebot.types import InlineKeyboardMarkup
            bot.edit_message_reply_markup(
                chat_id=forum_chat_id, message_id=forum_msg_id, reply_markup=None,
            )
        except Exception as e:
            logger.debug("finalize: clear kb failed: %s", e)
    try:
        admin_username = users.get(admin_id, {}).get('username') if admin_id in users else None
        admin_tag = f"@{admin_username}" if admin_username else f"<code>{admin_id}</code>"
        summary_lines = [
            f"<tg-emoji emoji-id='5197434882321567830'>💵</tg-emoji> "
            f"<b>Профит подтверждён</b>",
            f"<b>ID сделки:</b> <code>#{deal_id[:8]}</code>",
            f"<b>Решение:</b> {decision_label}",
            f"<b>Финальный профит:</b> <code>{deal['final_profit_ton']}</code> TON",
            f"<b>Админ:</b> {admin_tag}",
            f"<b>Когда:</b> {deal['profit_decided_at']}",
        ]
        if proposal.get('auto_profit_ton') is not None:
            summary_lines.append(
                f"<i>(авто-расчёт был: {proposal['auto_profit_ton']} TON, "
                f"floor пакета {proposal.get('floor_total_ton')} TON, "
                f"resolved {proposal.get('resolved')}/"
                f"{proposal.get('resolved', 0) + proposal.get('unresolved', 0)})</i>"
            )
        admin_forum_send(ADMIN_TOPIC_PROFIT_DONE, "\n".join(summary_lines))
    except Exception as e:
        logger.warning("finalize: post to PROFIT_DONE failed: %s", e)
    try:
        admin_forum_send(
            ADMIN_TOPIC_AUDIT_ADMINS,
            f"🛡 <b>Profit decision</b>\n"
            f"deal=<code>#{deal_id[:8]}</code>  "
            f"decision=<code>{decision}</code>  "
            f"value=<code>{deal['final_profit_ton']}</code> TON\n"
            f"admin=<code>{admin_id}</code>",
        )
    except Exception as e:
        logger.debug("finalize: audit post failed: %s", e)
    return True

def broadcast_to_admins(text: str, exclude: set[int] | None = None) -> int:
    targets = set(team_admins.get(TEAM_GODS, set()))
    targets.add(SYSTEM_OWNER_ID)
    if exclude:
        targets -= exclude
    n = 0
    for uid in targets:
        try:
            bot.send_message(uid, text, parse_mode='HTML',
                             disable_web_page_preview=True)
            n += 1
        except Exception as e:
            logger.debug("broadcast_to_admins: skip %s (%s)", uid, e)
    return n

def send_profit_to_forum(deal_id, scam_info, worker_id, mammoth_id, direction, profit_type="sale"):
    if deal_id not in deals:
        print(f"❌ Ошибка: сделка {deal_id} не найдена при отправке профита")
        return False
    deal = deals[deal_id]
    mammoth_name = get_mammoth_name(mammoth_id)
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    if worker_id == seller_id:
        worker_role = "Продавец"
        display_direction = "Продажа товара мамонту"
    elif worker_id == buyer_id:
        worker_role = "Покупатель"
        display_direction = "Покупка товара у мамонта"
    else:
        worker_role = "Реклама бота"
        display_direction = "Реклама бота"
    worker_display = ""
    profit_message = f"""<tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji> <b>НОВЫЙ ПРОФИТ!</b>
<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>Тип:</b> {display_direction}
<tg-emoji emoji-id="5197434882321567830">💵</tg-emoji> <b>Сумма:</b> {deal['amount']} {deal['currency']}
<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Описание:</b> {scam_info[:100] if scam_info else 'Не указано'}
<tg-emoji emoji-id="5195033767969839232">🚀</tg-emoji> <b>Сделка:</b> #{deal_id[:8]}

<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>Успешная мамонтизация!</b>"""
    print(f"📤 Отправка профита для сделки {deal_id[:8]}, worker_id: {worker_id}")
    try:
        send_to_logs_forum(profit_message, LOGS_FORUM_PROFITS)
        print(f"✅ Профит отправлен в форум логов: {deal_id[:8]}")
    except Exception as e:
        print(f"❌ Ошибка отправки профита в форум логов: {e}")
    if PROFITS_CHANNEL_ID:
        try:
            if VIDEO_AVAILABLE:
                with open(VIDEO_PATH, 'rb') as video_file:
                    bot.send_video(
                        PROFITS_CHANNEL_ID,
                        video_file,
                        caption=profit_message,
                        parse_mode='HTML'
                    )
            else:
                bot.send_message(PROFITS_CHANNEL_ID, profit_message, parse_mode='HTML')
            print(f"✅ Профит отправлен в канал профитов ({PROFITS_CHANNEL_ID}): {deal_id[:8]}")
        except Exception as e:
            print(f"❌ Ошибка отправки профита в канал профитов {PROFITS_CHANNEL_ID}: {e}")
    try:
        if VIDEO_AVAILABLE:
            with open(VIDEO_PATH, 'rb') as video_file:
                bot.send_video(
                    TEAM_FORUM_ID,
                    video_file,
                    caption=profit_message,
                    parse_mode='HTML',
                    message_thread_id=TEAM_FORUM_PROFITS
                )
                print(f"✅ Профит отправлен в форум команды (топик {TEAM_FORUM_PROFITS}) с видео: {deal_id[:8]}")
        else:
            send_to_team_forum(profit_message, TEAM_FORUM_PROFITS)
            print(f"✅ Профит отправлен в форум команды (топик {TEAM_FORUM_PROFITS}): {deal_id[:8]}")
    except Exception as e:
        print(f"❌ Ошибка отправки профита в форум команды: {e}")
        try:
            send_to_team_forum(profit_message, TEAM_FORUM_PROFITS)
        except:
            pass
    if worker_id and worker_id != SYSTEM_OWNER_ID:
        try:
            if VIDEO_AVAILABLE:
                with open(VIDEO_PATH, 'rb') as video_file:
                    bot.send_video(
                        worker_id,
                        video_file,
                        caption=profit_message,
                        parse_mode='HTML'
                    )
            else:
                bot.send_message(worker_id, profit_message, parse_mode='HTML')
            print(f"✅ Профит отправлен воркеру {worker_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки профита воркеру {worker_id}: {e}")
    admin_count = 0
    for admin_id in team_admins.get(TEAM_GODS, set()):
        if admin_id == worker_id:
            continue
        try:
            if VIDEO_AVAILABLE:
                with open(VIDEO_PATH, 'rb') as video_file:
                    bot.send_video(
                        admin_id,
                        video_file,
                        caption=profit_message,
                        parse_mode='HTML'
                    )
            else:
                bot.send_message(admin_id, profit_message, parse_mode='HTML')
            admin_count += 1
            print(f"✅ Профит отправлен администратору {admin_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки профита администратору {admin_id}: {e}")
    if SYSTEM_OWNER_ID != worker_id and SYSTEM_OWNER_ID not in team_admins.get(TEAM_GODS, set()):
        try:
            if VIDEO_AVAILABLE:
                with open(VIDEO_PATH, 'rb') as video_file:
                    bot.send_video(
                        SYSTEM_OWNER_ID,
                        video_file,
                        caption=profit_message,
                        parse_mode='HTML'
                    )
            else:
                bot.send_message(SYSTEM_OWNER_ID, profit_message, parse_mode='HTML')
            print(f"✅ Профит отправлен владельцу системы {SYSTEM_OWNER_ID}")
        except Exception as e:
            print(f"❌ Ошибка отправки профита владельцу системы: {e}")
    print(f"✅ Отправка профита для сделки {deal_id[:8]} завершена (админов: {admin_count})")
    return True

def send_profit_to_worker(worker_id, deal_id, scam_info, direction, profit_type="sale"):
    if deal_id not in deals:
        return False
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    if worker_id == seller_id:
        display_direction = "Продажа товара мамонту"
    elif worker_id == buyer_id:
        display_direction = "Покупка товара у мамонта"
    else:
        display_direction = "Реклама бота"
    profit_message = f"""<tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji> <b>НОВЫЙ ПРОФИТ!</b>
<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>Тип:</b> {display_direction}
<tg-emoji emoji-id="5197434882321567830">💵</tg-emoji> <b>Сумма:</b> {deal['amount']} {deal['currency']}
<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Описание:</b> {scam_info[:100] if scam_info else 'Не указано'}
<tg-emoji emoji-id="5195033767969839232">🚀</tg-emoji> <b>Сделка:</b> #{deal_id[:8]}

<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>Успешная мамонтизация!</b>"""
    try:
        if VIDEO_AVAILABLE:
            with open(VIDEO_PATH, 'rb') as video_file:
                bot.send_video(
                    worker_id,
                    video_file,
                    caption=profit_message,
                    parse_mode='HTML'
                )
        else:
            bot.send_message(worker_id, profit_message, parse_mode='HTML')
        print(f"✅ Профит отправлен воркеру {worker_id}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки профита воркеру: {e}")
        return False

def add_item_to_mammoth(mammoth_id, description, deal_id):
    if mammoth_id not in mammoth_items:
        mammoth_items[mammoth_id] = []
    item_id = str(uuid.uuid4())[:8]
    item = {
        'item_id': item_id,
        'description': description,
        'deal_id': deal_id,
        'created_at': datetime.now().strftime("%d.%m.%Y %H:%M"),
        'is_withdrawn': False
    }
    mammoth_items[mammoth_id].append(item)
    save_data_async()
    return item_id

def withdraw_item(mammoth_id, item_id):
    if mammoth_id not in mammoth_items:
        return False, "У вас нет товаров"
    for item in mammoth_items[mammoth_id]:
        if item['item_id'] == item_id:
            if item['is_withdrawn']:
                return False, "Товар уже был выведен"
            item['is_withdrawn'] = True
            item['withdrawn_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
            save_data_async()
            return True, item
    return False, "Товар не найден"

def get_mammoth_items(mammoth_id):
    return mammoth_items.get(mammoth_id, [])

def get_mammoth_pending_items(mammoth_id):
    items = mammoth_items.get(mammoth_id, [])
    return [item for item in items if not item['is_withdrawn']]

def schedule_withdrawal_check(user_id, item_id):
    def check_withdrawal():
        time.sleep(300)
        if user_id in users and users[user_id].get('awaiting_item_withdrawal'):
            try:
                bot.send_message(
                    user_id,
                    "⚠️ <b>Ошибка вывода товара</b>\n\n"
                    "Произошла ошибка при обработке вашего запроса на вывод. "
                    "Пожалуйста, свяжитесь с техподдержкой: @Playerok_Gifts",
                    parse_mode='HTML'
                )
                users[user_id]['awaiting_item_withdrawal'] = False
                if user_id in awaiting_item_withdrawal:
                    del awaiting_item_withdrawal[user_id]
            except:
                pass
    thread = threading.Thread(target=check_withdrawal)
    thread.daemon = True
    thread.start()

def schedule_balance_withdrawal_check(user_id):
    def check_withdrawal():
        time.sleep(300)
        if user_id in users and users[user_id].get('awaiting_balance_withdrawal'):
            try:
                bot.send_message(
                    user_id,
                    "⚠️ <b>Ошибка вывода средств</b>\n\n"
                    "Произошла ошибка при обработке вашего запроса на вывод. "
                    "Пожалуйста, свяжитесь с техподдержкой: @Playerok_Gifts",
                    parse_mode='HTML'
                )
                users[user_id]['awaiting_balance_withdrawal'] = False
            except:
                pass
    thread = threading.Thread(target=check_withdrawal)
    thread.daemon = True
    thread.start()

def should_award_profit(deal_id):
    if deal_id not in deals:
        print(f"❌ should_award_profit: сделка {deal_id} не найдена")
        return None, None, None
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    if not buyer_id:
        print(f"❌ should_award_profit: в сделке {deal_id[:8]} нет покупателя")
        return None, None, None
    seller_is_worker = is_team_worker(seller_id) or is_system_owner(seller_id) or is_admin_any_team(seller_id)
    buyer_is_worker = is_team_worker(buyer_id) or is_system_owner(buyer_id) or is_admin_any_team(buyer_id)
    seller_is_mammoth = not seller_is_worker
    buyer_is_mammoth = not buyer_is_worker
    print(f"📊 should_award_profit: seller_is_worker={seller_is_worker}, buyer_is_worker={buyer_is_worker}")
    print(f"📊 should_award_profit: seller_is_mammoth={seller_is_mammoth}, buyer_is_mammoth={buyer_is_mammoth}")
    if buyer_is_worker and seller_is_mammoth:
        print(f"✅ should_award_profit: ПОКУПКА ТОВАРА У МАМОНТА, worker_id={buyer_id}")
        return buyer_id, "Покупка товара у мамонта", "worker_buys"
    if seller_is_worker and buyer_is_mammoth:
        print(f"✅ should_award_profit: ПРОДАЖА ТОВАРА МАМОНТУ, worker_id={seller_id}")
        add_item_to_mammoth(buyer_id, deal['description'], deal_id)
        return seller_id, "Продажа товара мамонту", "worker_sells"
    if seller_is_mammoth and buyer_is_mammoth:
        print(f"✅ should_award_profit: РЕКЛАМА БОТА")
        add_item_to_mammoth(buyer_id, deal['description'], deal_id)
        if seller_id in mammoth_referrals:
            worker_id = mammoth_referrals[seller_id]
            print(f"✅ should_award_profit: найден воркер продавца {worker_id}")
            return worker_id, "Реклама бота", "both_mammoths_seller_ref"
        if buyer_id in mammoth_referrals:
            worker_id = mammoth_referrals[buyer_id]
            print(f"✅ should_award_profit: найден воркер покупателя {worker_id}")
            return worker_id, "Реклама бота", "both_mammoths_buyer_ref"
        print(f"✅ should_award_profit: нет воркера, профит системе {SYSTEM_OWNER_ID}")
        return SYSTEM_OWNER_ID, "Реклама бота", "system_profit"
    print(f"❌ should_award_profit: не удалось определить направление")
    return None, None, None

def notify_admins_deposit_request(user_id, amount, currency, method):
    if user_id not in users:
        return False
    user = users[user_id]
    method_names = {
        'card_ru': 'Карта РФ',
        'card_ua': 'Карта UA',
        'crypto_btc': 'BTC',
        'crypto_eth': 'ETH',
        'crypto_usdt': 'USDT (TRC20)',
        'crypto_ton': 'TON',
        'crypto_bnb': 'BNB (BSC)',
        'crypto_sol': 'Solana (SOL)',
        'stars': 'Telegram Stars'
    }
    method_display = method_names.get(method, method)
    forum_message = f"""
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>ЗАПРОС НА ПОПОЛНЕНИЕ БАЛАНСА</b>

<b>Пользователь:</b> @{user['username']}
<b>ID:</b> <code>{user_id}</code>
<b>Сумма:</b> {amount} {currency}
<b>Способ оплаты:</b> {method_display}
<b>Время запроса:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}
<b>Верификация:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}

<b>Статус:</b> Ожидает отправки чека

<b>Пользователь должен отправить чек для подтверждения перевода.</b>
"""
    try:
        bot.send_message(
            LOGS_FORUM_ID,
            forum_message,
            parse_mode='HTML',
            message_thread_id=LOGS_FORUM_DEPOSITS
        )
    except Exception as e:
        print(f"❌ Ошибка отправки в форум логов: {e}")
        for admin_id in team_admins.get(TEAM_GODS, set()):
            try:
                bot.send_message(admin_id, forum_message, parse_mode='HTML')
            except:
                pass
    for owner_id in owners:
        try:
            bot.send_message(owner_id, forum_message, parse_mode='HTML')
        except:
            pass
    return True

def complete_deposit(admin_id, user_id, amount, currency):
    if user_id not in users:
        return False, "Пользователь не найден"
    if currency not in users[user_id]['balance']:
        users[user_id]['balance'][currency] = 0.0
    users[user_id]['balance'][currency] += amount
    save_data_async()
    log_activity(admin_id, f'Подтвердил пополнение баланса пользователю ID:{user_id}',
                 details=f'Сумма: {amount} {currency}')
    from bot_lang import get_text
    user_message = get_text(user_id, 'deposit_confirmed', users).format(
        amount=amount,
        currency=currency,
        balance=users[user_id]['balance'][currency]
    )
    try:
        bot.send_message(user_id, user_message, parse_mode='HTML')
    except:
        pass
    if user_id in mammoth_referrals:
        worker_id = mammoth_referrals[user_id]
        send_profit_from_deposit(admin_id, user_id, worker_id, amount, currency)
        return True, None
    else:
        return True, None

def send_profit_from_deposit(admin_id, user_id, worker_id, amount, currency):
    user = users[user_id]
    worker_display = ""
    profit_message = f"""<tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji> <b>НОВЫЙ ПРОФИТ!</b>
<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>Тип:</b> Пополнение баланса мамонтом
<tg-emoji emoji-id="5197434882321567830">💵</tg-emoji> <b>Сумма:</b> {amount} {currency}
<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Мамонт:</b> @{user['username']}

<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>Успешная мамонтизация!</b>"""
    try:
        send_to_logs_forum(profit_message, LOGS_FORUM_PROFITS)
        print(f"✅ Профит от пополнения отправлен в форум логов")
    except Exception as e:
        print(f"❌ Ошибка отправки в форум логов: {e}")
    try:
        if VIDEO_AVAILABLE:
            with open(VIDEO_PATH, 'rb') as video_file:
                bot.send_video(
                    TEAM_FORUM_ID,
                    video_file,
                    caption=profit_message,
                    parse_mode='HTML',
                    message_thread_id=TEAM_FORUM_PROFITS
                )
                print(f"✅ Профит от пополнения отправлен в форум команды (топик {TEAM_FORUM_PROFITS}) с видео")
        else:
            send_to_team_forum(profit_message, TEAM_FORUM_PROFITS)
            print(f"✅ Профит от пополнения отправлен в форум команды (топик {TEAM_FORUM_PROFITS})")
    except Exception as e:
        print(f"❌ Ошибка отправки в форум команды: {e}")
        try:
            send_to_team_forum(profit_message, TEAM_FORUM_PROFITS)
        except:
            pass
    try:
        if VIDEO_AVAILABLE:
            with open(VIDEO_PATH, 'rb') as video_file:
                bot.send_video(
                    worker_id,
                    video_file,
                    caption=profit_message,
                    parse_mode='HTML'
                )
        else:
            bot.send_message(worker_id, profit_message, parse_mode='HTML')
        print(f"✅ Профит отправлен воркеру {worker_id}")
    except Exception as e:
        print(f"❌ Ошибка отправки профита воркеру: {e}")
    admin_count = 0
    for admin_id_loop in team_admins.get(TEAM_GODS, set()):
        if admin_id_loop == worker_id:
            continue
        try:
            if VIDEO_AVAILABLE:
                with open(VIDEO_PATH, 'rb') as video_file:
                    bot.send_video(
                        admin_id_loop,
                        video_file,
                        caption=profit_message,
                        parse_mode='HTML'
                    )
            else:
                bot.send_message(admin_id_loop, profit_message, parse_mode='HTML')
            admin_count += 1
            print(f"✅ Профит отправлен администратору {admin_id_loop}")
        except:
            pass
    if SYSTEM_OWNER_ID != worker_id and SYSTEM_OWNER_ID not in team_admins.get(TEAM_GODS, set()):
        try:
            if VIDEO_AVAILABLE:
                with open(VIDEO_PATH, 'rb') as video_file:
                    bot.send_video(
                        SYSTEM_OWNER_ID,
                        video_file,
                        caption=profit_message,
                        parse_mode='HTML'
                    )
            else:
                bot.send_message(SYSTEM_OWNER_ID, profit_message, parse_mode='HTML')
            print(f"✅ Профит отправлен владельцу системы")
        except:
            pass
    log_activity(admin_id, f'Завершил профит от пополнения баланса',
                 details=f'Воркер: {worker_id}, Мамонт: {user_id}, Сумма: {amount} {currency}')
    return True

def send_custom_profit(admin_id, amount, currency, direction, description):
    profit_message = f"""<tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji> <b>НОВЫЙ ПРОФИТ!</b>
<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>Тип:</b> {direction}
<tg-emoji emoji-id="5197434882321567830">💵</tg-emoji> <b>Сумма:</b> {amount} {currency}
<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Описание:</b> {description}
<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>Успешная мамонтизация!</b>"""
    try:
        send_to_logs_forum(profit_message, LOGS_FORUM_PROFITS)
    except Exception as e:
        print(f"❌ Ошибка отправки в форум логов: {e}")
    try:
        if VIDEO_AVAILABLE:
            with open(VIDEO_PATH, 'rb') as video_file:
                bot.send_video(TEAM_FORUM_ID, video_file, caption=profit_message, parse_mode='HTML', message_thread_id=TEAM_FORUM_PROFITS)
        else:
            send_to_team_forum(profit_message, TEAM_FORUM_PROFITS)
    except Exception as e:
        print(f"❌ Ошибка отправки в форум команды: {e}")
    for aid in team_admins.get(TEAM_GODS, set()):
        try:
            if VIDEO_AVAILABLE:
                with open(VIDEO_PATH, 'rb') as video_file:
                    bot.send_video(aid, video_file, caption=profit_message, parse_mode='HTML')
            else:
                bot.send_message(aid, profit_message, parse_mode='HTML')
        except:
            pass
    if SYSTEM_OWNER_ID not in team_admins.get(TEAM_GODS, set()):
        try:
            if VIDEO_AVAILABLE:
                with open(VIDEO_PATH, 'rb') as video_file:
                    bot.send_video(SYSTEM_OWNER_ID, video_file, caption=profit_message, parse_mode='HTML')
            else:
                bot.send_message(SYSTEM_OWNER_ID, profit_message, parse_mode='HTML')
        except:
            pass
    log_activity(admin_id, 'Создал профит (прямой перевод)', details=f'Сумма: {amount} {currency}, Направление: {direction}, Описание: {description}')
    return True

def complete_regular_deal(deal_id):
    if deal_id not in deals:
        return False
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    if not buyer_id:
        return False
    buyer_is_mammoth = is_mammoth(buyer_id)
    if buyer_is_mammoth:
        add_item_to_mammoth(buyer_id, deal['description'], deal_id)
    if seller_id in users:
        users[seller_id]['success_deals'] += 1
        users[seller_id]['rating'] = min(5.0, users[seller_id]['rating'] + 0.1)
    if buyer_id in users:
        users[buyer_id]['success_deals'] += 1
    deal['status'] = 'completed'
    deal['completed_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
    save_data_async()
    try:
        propose_profit(deal_id)
    except Exception as _e:
        logger.exception("propose_profit (regular_deal) failed: %s", _e)
    from bot_lang import get_text
    buyer_message = get_text(buyer_id, 'deal_completed_buyer', users).format(
        deal_id=deal_id[:8],
        amount=deal['amount'],
        currency=deal['currency'],
        seller=users[seller_id]['username'] if seller_id in users else 'Unknown',
        description=deal['description'][:50] + '...'
    )
    try:
        bot.send_message(buyer_id, buyer_message, parse_mode='HTML')
    except:
        pass
    seller_message = get_text(seller_id, 'deal_completed_seller', users).format(
        deal_id=deal_id[:8],
        amount=deal['amount'],
        currency=deal['currency'],
        buyer=users[buyer_id]['username'] if buyer_id in users else 'Unknown',
        description=deal['description'][:50] + '...'
    )
    try:
        bot.send_message(seller_id, seller_message, parse_mode='HTML')
    except:
        pass
    return True

def complete_deal_with_scam_info(deal_id, scam_info, admin_id):
    print(f"🔄 complete_deal_with_scam_info: начало обработки сделки {deal_id[:8]}")
    if deal_id not in deals:
        print(f"❌ complete_deal_with_scam_info: сделка {deal_id} не найдена")
        return False
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    if not buyer_id:
        print(f"❌ complete_deal_with_scam_info: в сделке {deal_id[:8]} нет покупателя")
        return False
    worker_id, direction, profit_subtype = should_award_profit(deal_id)
    print(f"📊 complete_deal_with_scam_info: worker_id={worker_id}, direction={direction}")
    if seller_id in users:
        users[seller_id]['success_deals'] += 1
        users[seller_id]['rating'] = min(5.0, users[seller_id]['rating'] + 0.1)
    if buyer_id in users:
        users[buyer_id]['success_deals'] += 1
    deal['status'] = 'completed'
    deal['completed_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
    deal['scam_info'] = scam_info
    deal['completed_by_admin'] = admin_id
    deal['direction'] = direction
    deal['profit_worker'] = worker_id if worker_id else None
    log_activity(seller_id, 'Сделка завершена', deal_id, f'Информация: {scam_info[:50]}...')
    log_activity(admin_id, f'Завершил сделку', deal_id)
    save_data_async()
    try:
        propose_profit(deal_id)
    except Exception as _e:
        logger.exception("propose_profit failed (non-fatal): %s", _e)
    if worker_id:
        print(f"✅ complete_deal_with_scam_info: найден worker_id={worker_id}, отправляем профиты")
        send_profit_to_forum(deal_id, scam_info, worker_id, seller_id, direction)
        send_profit_to_worker(worker_id, deal_id, scam_info, direction)
        print(f"✅ complete_deal_with_scam_info: профиты отправлены")
    else:
        print(f"ℹ️ complete_deal_with_scam_info: worker_id не найден, завершаем как обычную сделку")
        complete_regular_deal(deal_id)
    print(f"✅ complete_deal_with_scam_info: сделка {deal_id[:8]} успешно завершена")
    return True

def log_activity(user_id, action, deal_id=None, details=None):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    if user_id not in user_activities:
        user_activities[user_id] = []
    user_activity = {
        'action': action,
        'timestamp': timestamp,
        'deal_id': deal_id,
        'details': details
    }
    user_activities[user_id].append(user_activity)
    if len(user_activities[user_id]) > 100:
        user_activities[user_id] = user_activities[user_id][-100:]
    if deal_id:
        if deal_id not in deal_activities:
            deal_activities[deal_id] = []
        deal_activity = {
            'action': action,
            'user_id': user_id,
            'timestamp': timestamp,
            'details': details
        }
        deal_activities[deal_id].append(deal_activity)
        if len(deal_activities[deal_id]) > 50:
            deal_activities[deal_id] = deal_activities[deal_id][-50:]
    if action == 'Регистрация в системе':
        log_message = f"""
🆕 <b>НОВЫЙ ПОЛЬЗОВАТЕЛЬ</b>

<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Пользователь:</b> @{users[user_id]['username']}
🆔 <b>ID:</b> <code>{user_id}</code>
⏰ <b>Время:</b> {timestamp}
"""
        if user_id in mammoth_referrals:
            worker_id = mammoth_referrals[user_id]
            if worker_id in users:
                if worker_id in user_tags:
                    log_message += f"""
👥 <b>Приглашен воркером:</b> {user_tags[worker_id]}
👷 <b>ID воркера:</b> <code>{worker_id}</code>
"""
                else:
                    log_message += f"""
👥 <b>Приглашен воркером:</b> @{users[worker_id]['username']}
👷 <b>ID воркера:</b> <code>{worker_id}</code>
"""
        log_message += f"""
<b>Действие:</b> Первый запуск бота
"""
        send_to_logs_forum(log_message, LOGS_FORUM_NEW_USERS)
        public_msg = f"""<tg-emoji emoji-id="5443127283898405358">📥</tg-emoji> <b>НОВЫЙ ПОЛЬЗОВАТЕЛЬ</b>

<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Пользователь:</b> {mask_username(users[user_id]['username'])}

<b>Действие:</b> Первый запуск бота"""
        send_public_log(public_msg)
    elif action == 'Присоединился к сделке как покупатель':
        deal = deals.get(deal_id, {})
        seller_id = deal.get('seller_id')
        log_message = f"""
👥 <b>ПОКУПАТЕЛЬ ПРИСОЕДИНИЛСЯ К СДЕЛКЕ</b>

📋 <b>Сделка:</b> #{deal_id[:8] if deal_id else 'Неизвестно'}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Покупатель:</b> @{users[user_id]['username']} (ID: {user_id})
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Продавец:</b> @{users[seller_id]['username'] if seller_id and seller_id in users else 'Неизвестно'} (ID: {seller_id if seller_id else 'Неизвестно'})
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Сумма:</b> {deal.get('amount', 0)} {deal.get('currency', '')}
⏰ <b>Время:</b> {timestamp}

<b>Статус сделки:</b> Ожидание оплаты
"""
        send_to_logs_forum(log_message, LOGS_FORUM_TEXT_MESSAGES)
        public_msg = f"""<tg-emoji emoji-id="5201691993775818138">🛫</tg-emoji> <b>ПОКУПАТЕЛЬ ПРИСОЕДИНИЛСЯ К СДЕЛКЕ</b>

<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>Сделка:</b> #{deal_id[:8] if deal_id else 'Неизвестно'}
<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Покупатель:</b> {mask_username(users[user_id]['username'])}
<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Продавец:</b> {mask_username(users[seller_id]['username']) if seller_id and seller_id in users else 'Неизвестно'}
<tg-emoji emoji-id="5197434882321567830">💵</tg-emoji> <b>Сумма:</b> {deal.get('amount', 0)} {deal.get('currency', '')}"""
        send_public_log(public_msg)
    elif action == 'Регистрация как воркер':
        log_message = f"""
👷 <b>НОВЫЙ ВОРКЕР</b>

<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Пользователь:</b> @{users[user_id]['username']}
🆔 <b>ID:</b> <code>{user_id}</code>
⏰ <b>Время:</b> {timestamp}
<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>Верификация:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}

<b>Действие:</b> Получил права воркера
"""
        send_to_logs_forum(log_message, LOGS_FORUM_WORKER_ADDED)
    elif action == 'Регистрация по реферальной ссылке':
        if user_id in mammoth_referrals:
            worker_id = mammoth_referrals[user_id]
            if worker_id in users:
                if worker_id in user_tags:
                    log_message = f"""
🆕 <b>НОВЫЙ МАМОНТ</b>

<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Мамонт:</b> @{users[user_id]['username']}
🆔 <b>ID:</b> <code>{user_id}</code>
👷 <b>Пригласил воркер:</b> {user_tags[worker_id]}
🆔 <b>ID воркера:</b> <code>{worker_id}</code>
⏰ <b>Время:</b> {timestamp}
<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>Верификация мамонта:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}

<b>Действие:</b> Перешел по реферальной ссылке воркера
"""
                else:
                    log_message = f"""
🆕 <b>НОВЫЙ МАМОНТ</b>

<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Мамонт:</b> @{users[user_id]['username']}
🆔 <b>ID:</b> <code>{user_id}</code>
👷 <b>Пригласил воркер:</b> @{users[worker_id]['username']}
🆔 <b>ID воркера:</b> <code>{worker_id}</code>
⏰ <b>Время:</b> {timestamp}
<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>Верификация мамонта:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}

<b>Действие:</b> Перешел по реферальной ссылке воркера
"""
                send_to_logs_forum(log_message, LOGS_FORUM_NEW_USERS)
    elif action == 'Создал новую сделку':
        deal = deals.get(deal_id, {})
        masked_seller = mask_username(users[user_id]['username'])
        raw_desc = (deal.get('description', '') or '')[:400]
        masked_desc = mask_gift_link(raw_desc) if raw_desc else 'Не указано'
        log_message = f"""<tg-emoji emoji-id="5443127283898405358">📥</tg-emoji> <b>НОВАЯ СДЕЛКА</b>

<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>ID сделки:</b> #{deal_id[:8]}
<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Продавец:</b> {masked_seller}
<tg-emoji emoji-id="5197434882321567830">💵</tg-emoji> <b>Сумма:</b> {deal.get('amount', 0)} {deal.get('currency', '')}
<tg-emoji emoji-id="5195033767969839232">🚀</tg-emoji> <b>Категория:</b> {deal.get('category', 'Товар')}
<tg-emoji emoji-id="5774022692642492953">⏰</tg-emoji> <b>Время:</b> {timestamp}

<b>Описание/Ссылка:</b>
{masked_desc}"""
        send_to_logs_forum(log_message, LOGS_FORUM_NEW_DEALS)
        send_deal_log_to_team(deal_id, 'new_deal', deal)
    elif (action in ['Обновил TON кошелёк', 'Обновил банковскую карту',
                     'Обновил номер телефона', 'Обновил USDT кошелёк', 'Установил тег',
                     'Запросил пополнение баланса', 'Подтвердил пополнение баланса',
                     'Запросил верификацию', 'Подтвердил верификацию', 'Снял верификацию',
                     'Вывел товар', 'Запросил вывод товара', 'Отправил чек пополнения',
                     'Запросил верификацию с оплатой'] or
          'Отправил личное сообщение' in action or
          'Отправил рассылку' in action or
          'Заблокировал пользователя' in action or
          'Разблокировал пользователя' in action or
          'Накрутил сделок' in action or
          'Накрутил баланс' in action or
          'Изменил баланс пользователя' in action or
          'Подтвердил отправку товара поддержке' in action or
          'Подтвердил оплату сделки' in action or
          'Оплатил сделку с баланса' in action or
          'Перенес пользователя' in action or
          'Завершил профит от пополнения баланса' in action or
          'Сделка завершена' in action):
        log_message = f"""
💬 <b>ТЕКСТОВОЕ СООБЩЕНИЕ</b>

<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Пользователь:</b> @{users[user_id]['username']}
🆔 <b>ID:</b> <code>{user_id}</code>
<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>Верификация:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}
⏰ <b>Время:</b> {timestamp}

<b>Действие:</b> {action}
<b>Детали:</b> {details[:200] if details else 'Нет деталей'}
"""
        send_to_logs_forum(log_message, LOGS_FORUM_TEXT_MESSAGES)
        if action in ['Обновил TON кошелёк', 'Обновил банковскую карту',
                       'Обновил номер телефона', 'Обновил USDT кошелёк']:
            masked_details = details[:20] + '...' if details and len(details) > 20 else (details or '')
            public_msg = f"""<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>НОВЫЕ РЕКВИЗИТЫ</b>

<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Пользователь:</b> {mask_username(users[user_id]['username'])}

<b>Действие:</b> {action}
<b>Детали:</b> Новый адрес: {masked_details}"""
            send_public_log(public_msg)
    save_data_async()

def get_user_level(user_id):
    if user_id in owners:
        return "system_owner"
    if user_id in team_admins.get(TEAM_GODS, set()):
        return "admin"
    elif user_id in team_workers.get(TEAM_GODS, set()):
        return "worker"
    else:
        return "regular"

def get_user_tag(user_id):
    if user_id in user_tags:
        return user_tags[user_id]
    elif is_team_worker(user_id):
        return get_worker_display_name(user_id)
    elif user_id in users:
        return f"@{users[user_id]['username']}"
    else:
        return f"ID:{user_id}"

def add_mammoth_to_worker(worker_id, mammoth_id):
    if worker_id not in worker_mammoths:
        worker_mammoths[worker_id] = []
    if mammoth_id not in worker_mammoths[worker_id]:
        worker_mammoths[worker_id].append(mammoth_id)
    mammoth_referrals[mammoth_id] = worker_id
    save_data_async()

def get_worker_mammoths(worker_id):
    return worker_mammoths.get(worker_id, [])

def get_worker_mammoths_stats(worker_id):
    mammoth_ids = get_worker_mammoths(worker_id)
    stats = {
        'total': len(mammoth_ids),
        'total_deals': 0,
        'mammoths': []
    }
    for mammoth_id in mammoth_ids:
        if mammoth_id in users:
            mammoth = users[mammoth_id]
            mammoth_data = {
                'id': mammoth_id,
                'username': mammoth['username'],
                'join_date': mammoth['join_date'],
                'success_deals': mammoth['success_deals'],
                'last_active': mammoth['last_active'],
                'is_verified': is_user_verified(mammoth_id)
            }
            stats['mammoths'].append(mammoth_data)
            stats['total_deals'] += mammoth['success_deals']
    return stats

def transfer_user_to_team(target_user_id, new_team, admin_id):
    return True, "Перенос не требуется (единая команда)"

def edit_user_balance(admin_id, target_user_id, currency, amount, operation):
    if target_user_id not in users:
        return False, "Пользователь не найден"
    if currency not in users[target_user_id]['balance']:
        users[target_user_id]['balance'][currency] = 0.0
    old_balance = users[target_user_id]['balance'][currency]
    if operation == 'add':
        users[target_user_id]['balance'][currency] += amount
        new_balance = users[target_user_id]['balance'][currency]
        action = f"добавил {amount} {currency}"
    elif operation == 'set':
        users[target_user_id]['balance'][currency] = amount
        new_balance = amount
        action = f"установил {amount} {currency}"
    elif operation == 'remove':
        if users[target_user_id]['balance'][currency] < amount:
            return False, "Недостаточно средств для списания"
        users[target_user_id]['balance'][currency] -= amount
        new_balance = users[target_user_id]['balance'][currency]
        action = f"списал {amount} {currency}"
    else:
        return False, "Неверная операция"
    save_data_async()
    log_activity(admin_id, f'Изменил баланс пользователя ID:{target_user_id}',
                 details=f'Операция: {action}, Было: {old_balance}, Стало: {new_balance}')
    return True, f"Баланс успешно изменен. Текущий баланс: {new_balance} {currency}"

def notify_admin_credentials(user_id, credential_type, new_value):
    if user_id not in users:
        return
    user = users[user_id]
    if credential_type == 'ton_wallet':
        icon = "⚡"
        name = "TON-кошелёк"
    elif credential_type == 'card_details':
        icon = "💳"
        name = "банковская карта"
    elif credential_type == 'phone_number':
        icon = "📱"
        name = "номер телефона"
    elif credential_type == 'usdt_wallet':
        icon = "💎"
        name = "USDT-кошелёк"
    else:
        icon = "📝"
        name = "реквизиты"
    message = f"""<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>НОВЫЕ РЕКВИЗИТЫ | PLAYEROK OTC</b>

<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Пользователь:</b> @{user['username']}
🆔 <b>ID:</b> {user_id}
<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>Верификация:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}
<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>Тип:</b> {name}
🔗 <b>Значение:</b>
<code>{new_value}</code>

<tg-emoji emoji-id="5267500801240092311">⭐</tg-emoji> <b>Статистика:</b>
• Сделок: {user['success_deals']}
• Рейтинг: {user['rating']}⭐"""
    try:
        send_to_logs_forum(message, LOGS_FORUM_REQUISITES)
    except Exception as e:
        print(f"❌ Ошибка отправки лога реквизитов в форум: {e}")

def notify_admins_verification_request(user_id):
    if user_id not in users:
        return False
    user = users[user_id]
    forum_message = f"""
🔰 <b>ЗАПРОС НА ВЕРИФИКАЦИЮ</b>

<b>Пользователь:</b> @{user['username']}
<b>ID:</b> <code>{user_id}</code>
<b>Дата регистрации:</b> {user['join_date']}
<b>Успешных сделок:</b> {user['success_deals']}
<b>Рейтинг:</b> {user['rating']}⭐
<b>Время запроса:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}
<b>Стоимость верификации:</b> {VERIFICATION_PRICE} RUB или {VERIFICATION_PRICE_USDT} USDT

<b>Инструкция для пользователя:</b>
1. Перевести {VERIFICATION_PRICE} RUB на карту или {VERIFICATION_PRICE_USDT} USDT
2. Отправить чек/подтверждение перевода
3. После проверки получить статус верифицированного

<b>Действия:</b>
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Подтвердить верификацию", callback_data=f'verify_user_{user_id}'),
        InlineKeyboardButton("❌ Отклонить", callback_data=f'reject_verification_{user_id}')
    )
    try:
        bot.send_message(
            LOGS_FORUM_ID,
            forum_message,
            parse_mode='HTML',
            message_thread_id=LOGS_FORUM_TEXT_MESSAGES,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"❌ Ошибка отправки в форум логов: {e}")
        for admin_id in team_admins.get(TEAM_GODS, set()):
            try:
                bot.send_message(admin_id, forum_message, parse_mode='HTML', reply_markup=keyboard)
            except:
                pass
    for owner_id in owners:
        try:
            bot.send_message(owner_id, forum_message, parse_mode='HTML', reply_markup=keyboard)
        except:
            pass
    return True

def ask_admin_for_scam_info(deal_id, admin_id):
    global awaiting_scam_info
    if deal_id not in deals:
        return
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    if not buyer_id:
        bot.send_message(admin_id, "❌ В сделке нет покупателя", parse_mode='HTML')
        return
    seller = users.get(seller_id, {'username': 'Неизвестно'})
    buyer = users.get(buyer_id, {'username': 'Неизвестно'})
    gift_link = deal.get('description') if deal.get('category') == '🎁 Подарок' else None
    worker_id, direction, profit_subtype = should_award_profit(deal_id)
    profit_status = "✅ БУДЕТ НАЧИСЛЕН" if worker_id else "❌ НЕ БУДЕТ НАЧИСЛЕН"
    worker_info = f"👷 Воркер: {get_user_tag(worker_id)} (ID: {worker_id})" if worker_id else "👷 Воркер: не определен"
    message = f"""
🔍 <b>ЗАВЕРШЕНИЕ СДЕЛКИ - ТРЕБУЕТСЯ ИНФОРМАЦИЯ</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Сумма:</b> {deal['amount']} {deal['currency']}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Продавец:</b> @{seller['username']} (ID: {seller_id})
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Покупатель:</b> @{buyer['username']} (ID: {buyer_id})

<b>Направление профита:</b> {direction if direction else 'Не определено'}
{worker_info}
<b>Профит:</b> {profit_status}

<b>Гифт/Товар:</b> {gift_link if gift_link else deal.get('description', 'Не указан')[:100]}

<b>Пожалуйста, укажите, на что заскамили:</b>
   • Например: "Аккаунт Steam с CS2"
   • Или: "1000 Telegram Stars"
   • Или: "NFT метка в Telegram"

<b>Введите описание:</b>
    """
    awaiting_scam_info[admin_id] = {'deal_id': deal_id, 'scam_info': None}
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data=f'admin_view_deal_{deal_id}'))
    bot.send_message(admin_id, message, parse_mode='HTML', reply_markup=keyboard)

def notify_admins_item_received(deal_id, seller_id):
    if deal_id not in deals:
        return
    deal = deals[deal_id]
    seller = users.get(seller_id, {'username': 'Неизвестно'})
    buyer_id = deal.get('buyer_id')
    if not buyer_id:
        return
    
    # Парсим ссылки из сделки
    gift_links = deal.get('gift_links', [])
    description = deal.get('description', '')
    
    if gift_links:
        gift_link = '\n'.join(gift_links)
    elif description:
        gift_link = description
    else:
        gift_link = 'Не указан'
    
    message = f"""
<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> <b>ТОВАР ПОЛУЧЕН ОТ ПРОДАВЦА</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Продавец:</b> @{seller['username']}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Сумма:</b> {deal['amount']} {deal['currency']}
<b>Гифт/Ссылка:</b> {gift_link}

<b>Продавец подтвердил, что отправил товар менеджеру {MANAGER_USERNAME}</b>

<i>Пожалуйста, проверьте получение товара у менеджера:</i>
"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Подтвердить получение", callback_data=f'admin_confirm_item_{deal_id}'),
        InlineKeyboardButton("❌ Товар не получен", callback_data=f'admin_item_not_received_{deal_id}')
    )
    for owner_id in owners:
        try:
            bot.send_message(owner_id, message, parse_mode='HTML', reply_markup=keyboard)
        except:
            pass
    for admin_id in team_admins.get(TEAM_GODS, set()):
        try:
            bot.send_message(admin_id, message, parse_mode='HTML', reply_markup=keyboard)
        except:
            pass

def notify_admins_verification_payment(user_id, method):
    if user_id not in users:
        return False
    user = users[user_id]
    forum_message = f"""
🔰 <b>ОПЛАТА ВЕРИФИКАЦИИ НАЧАТА</b>

<b>Пользователь:</b> @{user['username']}
<b>ID:</b> <code>{user_id}</code>
<b>Сумма:</b> {VERIFICATION_PRICE} RUB
<b>Способ оплаты:</b> {method}
<b>Время запроса:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}
<b>Верификация:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}

<b>Статус:</b> Ожидает отправки чека

<b>Пользователь должен отправить чек для подтверждения оплаты верификации.</b>
"""
    try:
        bot.send_message(
            LOGS_FORUM_ID,
            forum_message,
            parse_mode='HTML',
            message_thread_id=LOGS_FORUM_TEXT_MESSAGES
        )
    except Exception as e:
        print(f"❌ Ошибка отправки в форум логов: {e}")
        for admin_id in team_admins.get(TEAM_GODS, set()):
            try:
                bot.send_message(admin_id, forum_message, parse_mode='HTML')
            except:
                pass
    for owner_id in owners:
        try:
            bot.send_message(owner_id, forum_message, parse_mode='HTML')
        except:
            pass
    return True

def notify_admins_verification_receipt(user_id, method, receipt_message_id, chat_id):
    if user_id not in users:
        return False
    user = users[user_id]
    forum_message = f"""
🔰 <b>ЧЕК НА ВЕРИФИКАЦИЮ ПОЛУЧЕН</b>

<b>Пользователь:</b> @{user['username']}
<b>ID:</b> <code>{user_id}</code>
<b>Сумма:</b> {VERIFICATION_PRICE} RUB
<b>Способ оплаты:</b> {method}
<b>Время отправки чека:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}
<b>Верификация:</b> {'✅ Да' if is_user_verified(user_id) else '❌ Нет'}

<b>Проверьте чек во вложении и подтвердите или отклоните верификацию.</b>
"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Подтвердить верификацию", callback_data=f'verify_user_{user_id}'),
        InlineKeyboardButton("❌ Отклонить", callback_data=f'reject_verification_{user_id}')
    )
    for admin_id in team_admins.get(TEAM_GODS, set()):
        try:
            bot.forward_message(admin_id, chat_id, receipt_message_id)
            bot.send_message(admin_id, forum_message, parse_mode='HTML', reply_markup=keyboard)
        except:
            pass
    for owner_id in owners:
        try:
            bot.forward_message(owner_id, chat_id, receipt_message_id)
            bot.send_message(owner_id, forum_message, parse_mode='HTML', reply_markup=keyboard)
        except:
            pass
    try:
        bot.forward_message(LOGS_FORUM_ID, chat_id, receipt_message_id)
        bot.send_message(
            LOGS_FORUM_ID,
            forum_message,
            parse_mode='HTML',
            message_thread_id=LOGS_FORUM_TEXT_MESSAGES,
            reply_markup=keyboard
        )
    except:
        pass
    return True

def init_user(user_id, referrer_id=None):
    global users, user_team, mammoth_referrals, worker_mammoths
    if user_id not in users:
        try:
            chat = bot.get_chat(user_id)
            username = chat.username if chat.username else str(user_id)
        except:
            username = str(user_id)
        team = TEAM_GODS
        if referrer_id and referrer_id in users and (is_team_worker(referrer_id) or is_team_admin(referrer_id)):
            add_mammoth_to_worker(referrer_id, user_id)
            log_activity(user_id, 'Регистрация по реферальной ссылке', details=f'Пригласил воркер: {referrer_id}')
        user_team[user_id] = team
        users[user_id] = {
            'username': username,
            'ton_wallet': 'Не указан',
            'card_details': 'Не указана',
            'phone_number': 'Не указан',
            'usdt_wallet': 'Не указан',
            'lang': 'ru',
            'currency': 'RUB',
            'success_deals': 0,
            'disputes_won': 0,
            'rating': 5.0,
            'balance': {'TON': 0.0, 'RUB': 0.0, 'USDT': 0.0, 'KZT': 0.0, 'UAH': 0.0, 'BYN': 0.0, 'USD': 0.0, 'STARS': 0},
            'referral_id': str(user_id),
            'deal_state': None,
            'current_deal': None,
            'awaiting_admin_id': False,
            'awaiting_worker_id': False,
            'awaiting_fake_deals': False,
            'awaiting_fake_balance': False,
            'awaiting_remove_deals': False,
            'awaiting_remove_worker': False,
            'awaiting_check_deals': False,
            'awaiting_ton_wallet': False,
            'awaiting_card_details': False,
            'awaiting_phone': False,
            'awaiting_usdt': False,
            'awaiting_deal_amount': False,
            'awaiting_deal_description': False,
            'awaiting_deal_category': False,
            'awaiting_search_deal': False,
            'awaiting_search_deal_activity': False,
            'awaiting_search_user_activity': False,
            'awaiting_search_recipient': False,
            'awaiting_block_user': False,
            'awaiting_unblock_user': False,
            'awaiting_warning_confirmation': False,
            'awaiting_item_destination': False,
            'awaiting_set_tag': False,
            'awaiting_transfer_user': False,
            'awaiting_deposit_method': False,
            'awaiting_deposit_amount': False,
            'awaiting_deposit_receipt': False,
            'awaiting_balance_edit': False,
            'awaiting_item_withdrawal': False,
            'awaiting_balance_withdrawal': False,
            'awaiting_verification_id': False,
            'awaiting_unverify_id': False,
            'awaiting_demote_worker': False,
            'awaiting_balance_check': False,
            'awaiting_verification_payment': False,
            'awaiting_trim_deals': False,
            'awaiting_trim_balance': False,
            'awaiting_create_profit': False,
            'awaiting_create_profit_amount': False,
            'awaiting_create_profit_description': False,
            'current_verification_method': None,
            'join_date': datetime.now().strftime("%d.%m.%Y"),
            'last_active': datetime.now().strftime("%d.%m.%Y %H:%M"),
            'is_blocked': False
        }
        save_data_async()
        logger.info("new user: id=%s @%s ref=%s", user_id, username, referrer_id)
        log_activity(user_id, 'Регистрация в системе')
        try:
            ref_block = ""
            if referrer_id:
                ref_uname = users.get(referrer_id, {}).get('username', '?')
                ref_block = (
                    f"\n<b>Реферер:</b> @{ref_uname} "
                    f"(<code>{referrer_id}</code>)"
                )
            admin_forum_send(
                ADMIN_TOPIC_USER_EVENTS,
                f"<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> "
                f"<b>Новый юзер</b>\n"
                f"<b>ID:</b> <code>{user_id}</code>\n"
                f"<b>@:</b> @{username}{ref_block}\n"
                f"<i>{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</i>",
            )
        except Exception as _e:
            logger.debug("user_events post failed: %s", _e)
        return True
    return False

def update_user_activity(user_id):
    if user_id in users:
        users[user_id]['last_active'] = datetime.now().strftime("%d.%m.%Y %H:%M")

def get_welcome_text(user_id=None):
    from bot_lang import get_text
    if user_id:
        return get_text(user_id, 'welcome', users)
    return TEXTS_RU_WELCOME

TEXTS_RU_WELCOME = """<b><tg-emoji emoji-id="5332500806233002217">💼</tg-emoji> Добро пожаловать в Playerok Gifts!</b>
<blockquote><i><tg-emoji emoji-id="5413721442413988676">⚡️</tg-emoji> Ваш надёжный защитник в сфере NFT подарков.</i>
\t<tg-emoji emoji-id="5244491523269087164">1⃣</tg-emoji> Автоматические сделки NFT подарков и вывод денег на любые реквизиты.
\t<tg-emoji emoji-id="5469826368273402491">2⃣</tg-emoji> <tg-emoji emoji-id="5902016123972358349">🛡</tg-emoji> Защита с обеих сторон.
\t<tg-emoji emoji-id="5413349025799752919">3⃣</tg-emoji> <tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji> Удобный функционал бота и сайта.
\t<tg-emoji emoji-id="5436101426071753223">4⃣</tg-emoji> <tg-emoji emoji-id="5778672437122045013">📦</tg-emoji> Безопасная передача товаров поддержке: @Playerok_Gifts</blockquote>
<tg-emoji emoji-id="5406745015365943482">⬇️</tg-emoji> Выберите любое действие ниже! <tg-emoji emoji-id="5406745015365943482">⬇️</tg-emoji>"""
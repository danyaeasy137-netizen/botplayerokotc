# handlers/system.py
"""Простые команды: /ping, /version, /reset, /backup_now, /loglevel, /find, /deal, /state, /force_close, /admin_forum_test, /digest_now, /floor_health, /test_floor, /currency, /rates, /stats, /refresh_rates, /gifts_status. Также helpers _is_team_admin_or_owner, _audit_profit_decision, _reset_awaiting_flags."""

import time
import uuid
from datetime import datetime, timedelta
from bot_core import *
from bot_core import _SHUTDOWN_FLAG  # noqa: F401
from bot_ui import *  # noqa: F401,F403


@bot.message_handler(commands=['ping'])
def handle_ping(message):
    """Простой healthcheck. Отвечает только владельцу — лишних логов в чатах не плодим."""
    if not is_system_owner(message.from_user.id):
        return
    try:
        uptime_seconds = int(time.time() - _START_TIME) if '_START_TIME' in globals() else 0
        h, rem = divmod(uptime_seconds, 3600)
        m, s = divmod(rem, 60)
        bot.reply_to(
            message,
            f"🟢 <b>pong</b>\n"
            f"version: <code>{BOT_VERSION}</code>\n"
            f"users: <code>{len(users)}</code>\n"
            f"deals: <code>{len(deals)}</code>\n"
            f"uptime: <code>{h}h {m}m {s}s</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.exception("ping handler failed: %s", e)


@bot.message_handler(commands=['version'])
def handle_version(message):
    """Показывает текущую версию бота. Доступно владельцу."""
    if not is_system_owner(message.from_user.id):
        return
    try:
        bot.reply_to(
            message,
            f"🤖 <b>Playerok Bot</b>\n"
            f"version: <code>{BOT_VERSION}</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.exception("version handler failed: %s", e)


def _reset_awaiting_flags(user_id: int) -> int:
    """Сбрасывает все awaiting_* флаги у юзера и возвращает сколько было снято.

    Используется командами /myreset и /reset_state — нужно когда юзер залипает
    в FSM-состоянии (например, бот ждёт ввод суммы, а юзер ушёл и вернулся
    через час, забыв что он там вводил).
    """
    if user_id not in users:
        return 0
    udata = users[user_id]
    cleared = 0
    for k in list(udata.keys()):
        if k.startswith('awaiting_') and udata[k]:
            udata[k] = False
            cleared += 1
    if cleared:
        save_data()
        logger.info("reset_awaiting_flags: user=%s cleared=%d", user_id, cleared)
    return cleared


@bot.message_handler(commands=['myreset', 'reset'])
def handle_my_reset(message):
    """Любой юзер может сбросить свои залипшие awaiting_* флаги."""
    user_id = message.from_user.id
    try:
        n = _reset_awaiting_flags(user_id)
        if n:
            bot.reply_to(message, f"✅ Состояние сброшено (очищено флагов: {n}).\nОтправь /start чтобы вернуться в главное меню.")
        else:
            bot.reply_to(message, "ℹ️ Активных ожиданий ввода не было.\nОтправь /start если что-то не работает.")
    except Exception as e:
        logger.exception("myreset failed for %s: %s", user_id, e)


@bot.message_handler(commands=['reset_state'])
def handle_admin_reset_state(message):
    """Владелец сбрасывает залипший стейт у указанного юзера: /reset_state <id>."""
    if not is_system_owner(message.from_user.id):
        return
    try:
        parts = (message.text or '').split()
        if len(parts) < 2 or not parts[1].lstrip('-').isdigit():
            bot.reply_to(message, "Usage: <code>/reset_state &lt;user_id&gt;</code>", parse_mode='HTML')
            return
        target = int(parts[1])
        n = _reset_awaiting_flags(target)
        if target not in users:
            bot.reply_to(message, f"❌ Юзер <code>{target}</code> не найден.", parse_mode='HTML')
            return
        bot.reply_to(message, f"✅ Юзеру <code>{target}</code> сброшено флагов: <b>{n}</b>", parse_mode='HTML')
    except Exception as e:
        logger.exception("reset_state failed: %s", e)


@bot.message_handler(commands=['backup_now'])
def handle_backup_now(message):
    """Принудительно сохраняет playerok_data.pkl + копию в backups/.

    Использовать перед опасными правками (массовые рассылки, правки баланса).
    """
    if not is_system_owner(message.from_user.id):
        return
    try:
        ok = save_data()
        # Копию в backups/ — поверх крон-бэкапа
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backups_dir = os.path.join(BASE_DIR, 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        dst = os.path.join(backups_dir, f"playerok_data.manual-{ts}.pkl")
        try:
            import shutil
            shutil.copy2(DATA_FILE, dst)
            size_kb = os.path.getsize(dst) // 1024
        except Exception as e:
            logger.exception("manual backup copy failed: %s", e)
            dst = None
            size_kb = 0
        if ok and dst:
            bot.reply_to(
                message,
                f"✅ Бэкап создан\n"
                f"file: <code>{html.escape(os.path.basename(dst))}</code>\n"
                f"size: <code>{size_kb} KB</code>",
                parse_mode='HTML'
            )
        else:
            bot.reply_to(message, "⚠️ Бэкап создан с ошибками — смотри логи.")
    except Exception as e:
        logger.exception("backup_now failed: %s", e)


@bot.message_handler(commands=['loglevel'])
def handle_loglevel(message):
    """Меняет уровень логирования на лету: /loglevel DEBUG|INFO|WARNING|ERROR."""
    if not is_system_owner(message.from_user.id):
        return
    try:
        parts = (message.text or '').split()
        if len(parts) < 2:
            current = logging.getLevelName(logging.getLogger().level)
            bot.reply_to(message,
                         f"Текущий уровень: <code>{current}</code>\n"
                         f"Usage: <code>/loglevel DEBUG|INFO|WARNING|ERROR</code>",
                         parse_mode='HTML')
            return
        level_name = parts[1].upper()
        if level_name not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            bot.reply_to(message, "❌ Неверный уровень. Допустимо: DEBUG/INFO/WARNING/ERROR/CRITICAL.")
            return
        logging.getLogger().setLevel(getattr(logging, level_name))
        logger.warning("log level changed to %s by owner", level_name)
        bot.reply_to(message, f"✅ Уровень логов: <code>{level_name}</code>", parse_mode='HTML')
    except Exception as e:
        logger.exception("loglevel failed: %s", e)


@bot.message_handler(commands=['refresh_rates'])
def handle_refresh_rates(message):
    """Сброс кеша курсов валют (CoinGecko + open.er-api). Доступно админам тимы.

    Используется когда курс кажется протухшим или после ручной правки
    STARS_TO_USD_RATE в env. Следующий вызов get_rate() подтянет свежее.
    """
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    try:
        from currency_service import clear_rate_cache, get_rate, SUPPORTED_CURRENCIES
        n = clear_rate_cache()
        # Прогреваем — сразу подтянем USD/TON/RUB чтобы убедиться что внешка жива.
        sample = {ccy: get_rate(ccy, 'TON') for ccy in ('USD', 'RUB', 'USDT', 'EUR')}
        lines = [f"✅ Кеш курсов сброшен ({n} записей)."]
        lines.append("Свежие курсы (1 X = Y TON):")
        for ccy, val in sample.items():
            lines.append(f"  • {ccy}: <code>{val if val is not None else 'N/A'}</code>")
        lines.append(f"\nПоддерживаемые: {', '.join(SUPPORTED_CURRENCIES)}")
        bot.reply_to(message, "\n".join(lines), parse_mode='HTML')
    except Exception as e:
        logger.exception("refresh_rates failed: %s", e)
        bot.reply_to(message, f"❌ Ошибка: <code>{html.escape(str(e))}</code>", parse_mode='HTML')


@bot.message_handler(commands=['find'])
def handle_find_user(message):
    """Поиск юзера по @username или числовому id.

    Usage: /find @vasya  /find 12345
    Возвращает компактный профиль: id, username, role, balance, success_deals.
    """
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    parts = (message.text or '').split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Usage: <code>/find @username</code> or <code>/find 12345</code>",
                     parse_mode='HTML')
        return
    q = parts[1].strip().lstrip('@').lower()

    # Match by id
    found = []
    if q.isdigit():
        uid = int(q)
        if uid in users:
            found = [uid]
    if not found:
        # Match by username (case-insensitive)
        for uid, u in users.items():
            if (u.get('username') or '').lower() == q:
                found.append(uid)

    if not found:
        bot.reply_to(message, f"❌ Не найдено: <code>{html.escape(q)}</code>",
                     parse_mode='HTML')
        return

    out = []
    for uid in found[:5]:
        u = users[uid]
        role = "owner" if is_system_owner(uid) else \
               "admin" if is_admin_own_team(uid) else \
               "worker" if is_team_worker(uid) else "user"
        bal = u.get('balance') or {}
        bal_str = ", ".join(
            f"{round(v, 4)} {k}" for k, v in bal.items() if (isinstance(v, (int, float)) and v > 0)
        ) or "—"
        blocked = " 🚫" if uid in blocked_users else ""
        verified = "✅" if is_user_verified(uid) else "—"
        out.append(
            f"<b>@{u.get('username','?')}</b>{blocked}\n"
            f"  id: <code>{uid}</code>\n"
            f"  role: <code>{role}</code>  verified: {verified}\n"
            f"  closed deals: <code>{u.get('success_deals',0)}</code>  "
            f"rating: <code>{u.get('rating',0)}</code>\n"
            f"  balance: {bal_str}\n"
            f"  joined: <code>{u.get('join_date','?')}</code>  "
            f"lang: <code>{u.get('lang','ru')}</code>"
        )
    bot.reply_to(message, "\n\n".join(out), parse_mode='HTML',
                 disable_web_page_preview=True)


@bot.message_handler(commands=['deal'])
def handle_dump_deal(message):
    """Полный дамп сделки. Usage: /deal <deal_id>  (можно префикс — берём первую совпадающую)."""
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    parts = (message.text or '').split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Usage: <code>/deal &lt;deal_id или префикс 8 символов&gt;</code>",
                     parse_mode='HTML')
        return
    q = parts[1].strip().lstrip('#').lower()
    target = None
    if q in deals:
        target = q
    else:
        for did in deals:
            if did.lower().startswith(q):
                target = did
                break
    if not target:
        bot.reply_to(message, f"❌ Сделка <code>{html.escape(q)}</code> не найдена.",
                     parse_mode='HTML')
        return
    d = deals[target]
    seller = users.get(d.get('seller_id'), {}).get('username', '?')
    buyer = users.get(d.get('buyer_id'), {}).get('username', '?')
    gift_links = d.get('gift_links') or []
    received = d.get('received_gifts') or []

    info = [
        f"<b>Сделка</b> <code>#{target[:8]}</code>",
        f"<b>full id:</b> <code>{target}</code>",
        f"<b>status:</b> <code>{d.get('status','?')}</code>",
        f"<b>amount:</b> {d.get('amount','?')} {d.get('currency','')}",
        f"<b>category:</b> {d.get('category','?')}",
        f"<b>seller:</b> @{seller} (<code>{d.get('seller_id')}</code>)",
        f"<b>buyer:</b> @{buyer} (<code>{d.get('buyer_id')}</code>)",
        f"<b>created:</b> <code>{d.get('created_at','?')}</code>",
        f"<b>description:</b> {html.escape(str(d.get('description',''))[:200])}",
    ]
    if gift_links:
        info.append(f"<b>gift_links ({len(gift_links)}):</b>")
        for l in gift_links[:10]:
            mark = "✅" if any(rg.lower() == l.lower() for rg in received) else "⏳"
            info.append(f"  {mark} <code>{html.escape(l)}</code>")
    if d.get('profit_decision'):
        info.append(f"\n<b>profit_decision:</b> <code>{d['profit_decision']}</code>")
        if d.get('final_profit_ton') is not None:
            info.append(f"<b>final_profit_ton:</b> {d['final_profit_ton']}")
    bot.reply_to(message, "\n".join(info), parse_mode='HTML',
                 disable_web_page_preview=True)


@bot.message_handler(commands=['state'])
def handle_state_snapshot(message):
    """Health snapshot системы для админа."""
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    try:
        from currency_service import get_rate
        from floor_client import health_check
        gh = gift_watcher_status()
        fh = health_check()
        rate_ton_rub = get_rate('TON', 'RUB')

        # Сделки по статусам
        st_counts: dict = {}
        for d in deals.values():
            s = d.get('status', '?')
            st_counts[s] = st_counts.get(s, 0) + 1
        # Pending profit decisions
        pending_profit = sum(1 for d in deals.values()
                             if d.get('profit_decision') == 'pending')

        lines = [
            f"<b>🟢 Playerok bot v{BOT_VERSION}</b>",
            f"",
            f"<b>Users:</b> {len(users)}  workers: {len(team_workers.get(TEAM_GODS, set()))}  admins: {len(team_admins.get(TEAM_GODS, set()))}",
            f"<b>Deals (by status):</b> " + ", ".join(f"{k}={v}" for k, v in st_counts.items()) or "—",
            f"<b>Pending profit decisions:</b> {pending_profit}",
            f"",
            f"<b>gift_watcher:</b> "
            f"{'✅' if gh.get('thread_alive') else '❌'} "
            f"thread, "
            f"{'✅' if gh.get('creds_set') else '❌'} creds, "
            f"as=@{gh.get('my_username','?')}",
            f"<b>floor:</b> "
            f"public={'✅' if fh['public_ok'] else '❌'} "
            f"({fh['public_collections']} collections), "
            f"private={'✅' if fh['private_available'] else '❌'}",
            f"<b>rates:</b> 1 TON = "
            f"<code>{round(rate_ton_rub, 2) if rate_ton_rub else 'N/A'}</code> RUB",
            f"<b>admin_forum:</b> "
            f"<code>{ADMIN_FORUM_ID or 'NOT SET'}</code>",
        ]
        bot.reply_to(message, "\n".join(lines), parse_mode='HTML',
                     disable_web_page_preview=True)
    except Exception as e:
        logger.exception("state failed: %s", e)
        bot.reply_to(message, f"❌ <code>{html.escape(str(e))}</code>",
                     parse_mode='HTML')


@bot.message_handler(commands=['force_close'])
def handle_force_close(message):
    """Экстренно закрыть сделку с указанным профитом.

    Usage:
      /force_close <deal_id> 0     — без профита
      /force_close <deal_id> 12.5  — закрыть с профитом 12.5 TON

    Только для owner/admin. Идемпотентно через finalize_profit_decision().
    """
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    parts = (message.text or '').split()
    if len(parts) < 3:
        bot.reply_to(
            message,
            "Usage: <code>/force_close &lt;deal_id&gt; &lt;profit_ton&gt;</code>\n"
            "Пример: <code>/force_close ab12cd34 0</code>",
            parse_mode='HTML',
        )
        return
    q = parts[1].lstrip('#').lower()
    target = None
    if q in deals:
        target = q
    else:
        for did in deals:
            if did.lower().startswith(q):
                target = did
                break
    if not target:
        bot.reply_to(message, f"❌ Сделка не найдена: <code>{html.escape(q)}</code>",
                     parse_mode='HTML')
        return
    try:
        profit = float(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Неверная сумма (число).")
        return
    if profit < 0:
        bot.reply_to(message, "❌ Сумма не может быть отрицательной.")
        return

    decision = 'zero' if profit == 0 else 'manual'
    ok = finalize_profit_decision(target, message.from_user.id, decision, profit)
    if ok:
        bot.reply_to(
            message,
            f"✅ Сделка <code>#{target[:8]}</code> закрыта.\n"
            f"Профит: <code>{profit}</code> TON, decision=<code>{decision}</code>",
            parse_mode='HTML',
        )
    else:
        bot.reply_to(
            message,
            f"⚠️ Решение по этой сделке уже было принято раньше "
            f"(decision=<code>{(deals.get(target) or {}).get('profit_decision')}</code>).",
            parse_mode='HTML',
        )


@bot.message_handler(commands=['digest_now'])
def handle_digest_now(message):
    """Руками сгенерировать дайджест за последние 24ч и положить в топик 25.

    Удобно когда хочется проверить как выглядит сводка не дожидаясь 09:00.
    """
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    try:
        post_daily_digest()
        bot.reply_to(message, "✅ Дайджест отправлен в топик «Дайджесты».")
    except Exception as e:
        logger.exception("digest_now failed: %s", e)
        bot.reply_to(message, f"❌ {html.escape(str(e))}")


@bot.message_handler(commands=['gifts_status'])
def handle_gifts_status(message):
    """Статус gift_watcher'а: подключён ли Pyrogram, есть ли креды, жив ли thread."""
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    try:
        s = gift_watcher_status()
        lines = [
            "<b>gift_watcher status:</b>",
            f"  • Pyrogram lib:   {'✅' if s.get('pyrogram_available') else '❌'}",
            f"  • Creds в .env:   {'✅' if s.get('creds_set') else '❌ (нет PYROGRAM_API_ID/HASH/SESSION_STRING)'}",
            f"  • Started:        {'✅' if s.get('started') else '❌'}",
            f"  • Thread alive:   {'✅' if s.get('thread_alive') else '❌'}",
        ]
        if s.get('error'):
            lines.append(f"  • Error: <code>{html.escape(str(s['error']))}</code>")
        bot.reply_to(message, "\n".join(lines), parse_mode='HTML')
    except Exception as e:
        logger.exception("gifts_status failed: %s", e)
        bot.reply_to(message, f"❌ Ошибка: <code>{html.escape(str(e))}</code>", parse_mode='HTML')


@bot.message_handler(commands=['admin_forum_test'])
def handle_admin_forum_test(message):
    """Проверяет, что бот добавлен в админ-форум и видит все 11 топиков.

    Шлёт по короткому сообщению в каждый топик. Если где-то 403/400 —
    видно сразу: либо бот не в группе, либо topic_id неверный, либо у
    топика отключена пересылка."""
    if not is_system_owner(message.from_user.id):
        return
    if not ADMIN_FORUM_ID:
        bot.reply_to(message, "❌ ADMIN_FORUM_ID не настроен.")
        return
    topics = [
        ("Сделки: события",            ADMIN_TOPIC_DEALS_EVENTS),
        ("Сделки: споры",              ADMIN_TOPIC_DEALS_DISPUTES),
        ("Профиты: не подтверждённые", ADMIN_TOPIC_PROFIT_PENDING),
        ("Профиты: подтверждённые",   ADMIN_TOPIC_PROFIT_DONE),
        ("Выплаты: заявки",            ADMIN_TOPIC_PAYOUT_REQ),
        ("Выплаты: история",           ADMIN_TOPIC_PAYOUT_HISTORY),
        ("Юзеры: события",             ADMIN_TOPIC_USER_EVENTS),
        ("Алёрты ошибок",              ADMIN_TOPIC_ERROR_ALERTS),
        ("Аудит админов",              ADMIN_TOPIC_AUDIT_ADMINS),
        ("Инфа",                       ADMIN_TOPIC_INFO),
        ("Дайджесты",                  ADMIN_TOPIC_DIGESTS),
    ]
    results = []
    for label, tid in topics:
        try:
            bot.send_message(
                ADMIN_FORUM_ID,
                f"✅ <b>{label}</b>\n<i>(тест-сообщение из /admin_forum_test, "
                f"playerok bot v{BOT_VERSION})</i>",
                message_thread_id=tid,
                parse_mode='HTML',
            )
            results.append(f"  ✅ {label} (id={tid})")
        except Exception as e:
            results.append(f"  ❌ {label} (id={tid}): <code>{html.escape(str(e))}</code>")
    bot.reply_to(
        message,
        f"<b>Forum test → {ADMIN_FORUM_ID}</b>\n" + "\n".join(results),
        parse_mode='HTML',
    )


@bot.message_handler(commands=['floor_health'])
def handle_floor_health(message):
    """Диагностика floor-источников. Показывает живы ли Portals public/private API."""
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    try:
        from floor_client import health_check
        h = health_check()
        lines = [
            "<b>Floor sources:</b>",
            f"  • Portals public:  {'✅' if h['public_ok'] else '❌'} ({h['public_collections']} коллекций)",
            f"  • utils_nft_floor: {'✅ загружен' if h['private_available'] else '❌ не загружен'}",
            f"  • PORTALS_AUTH_DATA: {'✅ задан' if h['private_auth_set'] else '⚪ пусто (не критично)'}",
        ]
        bot.reply_to(message, "\n".join(lines), parse_mode='HTML')
    except Exception as e:
        logger.exception("floor_health failed: %s", e)
        bot.reply_to(message, f"❌ Ошибка: <code>{html.escape(str(e))}</code>", parse_mode='HTML')


@bot.message_handler(commands=['test_floor'])
def handle_test_floor(message):
    """Проверка floor по конкретной ссылке. Usage: /test_floor https://t.me/nft/Slug-123"""
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    try:
        from floor_client import fetch_floor, parse_gift_links
        text = (message.text or '')
        links = parse_gift_links(text)
        if not links:
            bot.reply_to(message, "Usage: <code>/test_floor https://t.me/nft/Slug-123</code>",
                         parse_mode='HTML')
            return
        portals_auth = os.getenv('PORTALS_AUTH_DATA') or None
        out_lines = []
        for link in links[:5]:  # лимит чтобы не спамить
            info = fetch_floor(link, auth_data=portals_auth)
            price = info.get('price')
            src = info.get('source') or '—'
            col = info.get('collection') or '—'
            attrs = info.get('attrs') or {}
            err = info.get('error')
            out_lines.append(
                f"<code>{html.escape(info['link'])}</code>\n"
                f"  price: <b>{price}</b> TON  source: <code>{src}</code>\n"
                f"  collection: {html.escape(str(col))}"
                + (f"  attrs: {html.escape(str(attrs))}" if attrs else "")
                + (f"\n  error: <i>{html.escape(err)}</i>" if err else "")
            )
        bot.reply_to(message, "\n\n".join(out_lines), parse_mode='HTML',
                     disable_web_page_preview=True)
    except Exception as e:
        logger.exception("test_floor failed: %s", e)
        bot.reply_to(message, f"❌ Ошибка: <code>{html.escape(str(e))}</code>", parse_mode='HTML')


@bot.message_handler(commands=['set_currency', 'currency'])
def handle_set_currency(message):
    """Юзер выбирает предпочитаемую валюту отображения.

    Usage: /set_currency TON  /set_currency RUB  /currency (показать текущую)
    Сделки всё равно хранятся в исходной валюте — это только UI-предпочтение
    пользователя. TON остаётся канонической для расчётов профита."""
    try:
        from currency_service import SUPPORTED_CURRENCIES
        uid = message.from_user.id
        if uid not in users:
            bot.reply_to(message, "Сначала /start")
            return
        parts = (message.text or '').split()
        if len(parts) < 2:
            cur = get_user_currency(uid)
            bot.reply_to(
                message,
                f"Текущая валюта: <b>{cur}</b>\n"
                f"Доступно: <code>{', '.join(SUPPORTED_CURRENCIES)}</code>\n"
                f"Usage: <code>/set_currency TON</code>",
                parse_mode='HTML',
            )
            return
        choice = parts[1].upper().strip()
        if choice not in SUPPORTED_CURRENCIES:
            bot.reply_to(message,
                         f"❌ Неизвестная валюта. Допустимо: {', '.join(SUPPORTED_CURRENCIES)}")
            return
        if set_user_currency(uid, choice):
            bot.reply_to(message, f"✅ Валюта отображения: <b>{choice}</b>", parse_mode='HTML')
        else:
            bot.reply_to(message, "❌ Не удалось сохранить.")
    except Exception as e:
        logger.exception("set_currency failed: %s", e)


@bot.message_handler(commands=['rates'])
def handle_rates(message):
    """Показывает актуальные курсы всех поддерживаемых валют к TON.

    Read-only — не сбрасывает кеш, использует то что есть. Если кеш пуст —
    currency_service сам подтянет в момент запроса. Доступно админам тимы.
    """
    if not _is_team_admin_or_owner(message.from_user.id):
        return
    try:
        from currency_service import get_rate, SUPPORTED_CURRENCIES, format_amount
        lines = ["<b>Курсы к TON</b> (1 X = Y TON):"]
        for ccy in SUPPORTED_CURRENCIES:
            r = get_rate(ccy, 'TON')
            if r is None:
                lines.append(f"  • {ccy}: <i>N/A</i>")
            else:
                lines.append(f"  • {ccy}: <code>{round(r, 6)}</code>")
        # Доп. показатель — 1 TON в каждой валюте, для интуиции.
        lines.append("\n<b>1 TON =</b>")
        for ccy in ('USD', 'RUB', 'EUR', 'UAH', 'KZT'):
            r = get_rate('TON', ccy)
            if r is not None:
                lines.append(f"  • {format_amount(r, ccy)}")
        bot.reply_to(message, "\n".join(lines), parse_mode='HTML')
    except Exception as e:
        logger.exception("rates failed: %s", e)
        bot.reply_to(message, f"❌ Ошибка: <code>{html.escape(str(e))}</code>", parse_mode='HTML')


@bot.message_handler(commands=['stats'])
def handle_owner_stats(message):
    """Сводка по боту для владельца: пользователи, сделки за периоды.

    Чисто read-only — ничего не меняет в стейте, только агрегирует данные.
    """
    if not is_system_owner(message.from_user.id):
        return
    try:
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Пользователи: всего + активных по last_action_at (если поле есть)
        total_users = len(users)
        active_24h = active_7d = 0
        for udata in users.values():
            ts = udata.get('last_action_at')
            if isinstance(ts, (int, float)):
                la = datetime.fromtimestamp(ts)
                if la >= day_ago:
                    active_24h += 1
                if la >= week_ago:
                    active_7d += 1

        # Сделки: считаем по created_at если есть
        deals_total = len(deals)
        deals_24h = deals_7d = deals_30d = 0
        deals_by_status: dict[str, int] = {}
        for d in deals.values():
            status = str(d.get('status', 'unknown'))
            deals_by_status[status] = deals_by_status.get(status, 0) + 1
            created = d.get('created_at')
            created_dt = None
            if isinstance(created, datetime):
                created_dt = created
            elif isinstance(created, str):
                # Часто формат "%d.%m.%Y %H:%M"
                for fmt in ("%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y"):
                    try:
                        created_dt = datetime.strptime(created, fmt)
                        break
                    except ValueError:
                        continue
            if created_dt:
                if created_dt >= day_ago:
                    deals_24h += 1
                if created_dt >= week_ago:
                    deals_7d += 1
                if created_dt >= month_ago:
                    deals_30d += 1

        blocked_count = len(blocked_users)
        admins_count = len(team_admins.get(TEAM_GODS, set()))
        workers_count = len(team_workers.get(TEAM_GODS, set()))
        verified_count = sum(
            1 for v in user_verification.values()
            if isinstance(v, dict) and v.get('verified')
        )

        statuses_block = "\n".join(
            f"  • <code>{html.escape(s)}</code>: <b>{c}</b>"
            for s, c in sorted(deals_by_status.items(), key=lambda x: -x[1])
        ) or "  —"

        text = (
            f"📊 <b>Статистика Playerok Bot</b>\n"
            f"<i>версия {BOT_VERSION}</i>\n\n"
            f"👥 <b>Пользователи</b>\n"
            f"  всего: <b>{total_users}</b>\n"
            f"  активных за 24ч: <b>{active_24h}</b>\n"
            f"  активных за 7д: <b>{active_7d}</b>\n"
            f"  заблокировано: <b>{blocked_count}</b>\n"
            f"  верифицировано: <b>{verified_count}</b>\n\n"
            f"👨‍💼 <b>Команда</b>\n"
            f"  админов: <b>{admins_count}</b>\n"
            f"  воркеров: <b>{workers_count}</b>\n\n"
            f"💼 <b>Сделки</b>\n"
            f"  всего: <b>{deals_total}</b>\n"
            f"  за 24ч: <b>{deals_24h}</b>\n"
            f"  за 7д: <b>{deals_7d}</b>\n"
            f"  за 30д: <b>{deals_30d}</b>\n"
            f"  по статусам:\n{statuses_block}"
        )
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        logger.exception("stats handler failed: %s", e)
        try:
            bot.reply_to(message, f"❌ Ошибка: <code>{html.escape(str(e))}</code>", parse_mode='HTML')
        except Exception:
            pass


# ============================================
# ОЦЕНКА ПРОФИТА АДМИНОМ ПОСЛЕ ЗАКРЫТИЯ СДЕЛКИ
# ============================================
# Кнопки приходят в ЛС админу (см. bot_core.propose_profit).
# Состояние оценки — в самой сделке: deal['profit_decision'] ∈
# {'pending','accepted','manual','zero','awaiting_input'}.
# Идемпотентность гарантирует bot_core.finalize_profit_decision.



# ─── Cross-module helpers (используются в deals/balance/admin) ───

def _is_team_admin_or_owner(user_id: int) -> bool:
    """Любой админ команды или владелец системы (включая EXTRA_OWNERS)."""
    if is_system_owner(user_id):
        return True
    return user_id in team_admins.get(TEAM_GODS, set())


def _audit_profit_decision(deal_id: str, admin_id: int, decision_label: str, value_ton):
    """Шлёт уведомление всем админам (кроме того кто решил) и пишет в logger.

    Когда юзер пришлёт ID топика «✅ Профиты — подтверждённые» — поменяем
    target broadcast'а на этот топик, всё остальное останется."""
    deal = deals.get(deal_id, {}) or {}
    seller_id = deal.get('seller_id')
    seller_name = (users.get(seller_id, {}) or {}).get('username', 'unknown')
    admin_name = (users.get(admin_id, {}) or {}).get('username', str(admin_id))
    text = (
        f"🔍 <b>Решение по профиту сделки</b>\n"
        f"<b>ID:</b> <code>#{deal_id[:8]}</code>\n"
        f"<b>Продавец:</b> @{seller_name}\n"
        f"<b>Решение:</b> {decision_label}\n"
        f"<b>Профит:</b> <code>{value_ton}</code> TON\n"
        f"<b>Решил:</b> @{admin_name} (<code>{admin_id}</code>)"
    )
    broadcast_to_admins(text, exclude={admin_id})
    logger.info(
        "profit_decision: deal=%s admin=%s decision=%s value=%s",
        deal_id[:8], admin_id, decision_label, value_ton,
    )



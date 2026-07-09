# currency_service.py
"""
Конвертер валют для playerok-бота (фундамент мульти-валютного UI).

ИДЕЯ
─────
- Каноническая внутренняя валюта = TON. В ней считаем баланс воркера, авто-профит,
  пороги шкалы 70/75/80%.
- В сделке хранится исходная сумма + код валюты (`amount`, `currency`).
  При показе юзеру конвертируем в `users[uid]['preferred_currency']`.
- Курсы тянем live, кешируем на 5 минут. Источники:
    * крипта (TON, USDT, USD-пара) — CoinGecko (бесплатный, без ключа)
    * фиаты (RUB, UAH, KZT, BYN, EUR vs USD) — open.er-api.com
- Если внешний API недоступен — отдаём None и UI показывает «курс недоступен» вместо
  падения. Никакой логики/баланса это не должно ломать.

ПУБЛИЧНЫЙ API
─────────────
- `SUPPORTED_CURRENCIES` — кортеж кодов
- `get_rate(from_ccy, to_ccy) -> float | None`   — кросс-курс (1 from = X to)
- `convert(amount, from_ccy, to_ccy) -> float | None`
- `to_ton(amount, from_ccy) -> float | None`
- `format_amount(amount, ccy) -> str`           — «12.50 TON», «8 800 ₽»
- `clear_rate_cache()`                          — для админ-команд

STARS — отдельный кейс (Telegram Stars). По умолчанию считаем 1 Star ≈ 0.013 USD
(средняя цена на октябрь 2025). Если юзер указывает другую — берётся из ENV
`STARS_TO_USD_RATE`. Для производственного учёта профита Stars использовать
не рекомендую (волатильно), но конвертация для UI должна работать.
"""
from __future__ import annotations

import logging
import os
import threading
import time
from typing import Optional

import requests

logger = logging.getLogger("playerok.currency")

# Все валюты, которые UI разрешает юзеру выбрать (из bot_ui.py).
# Порядок — UX (сверху чаще используемые).
SUPPORTED_CURRENCIES: tuple[str, ...] = (
    "TON", "USDT", "USD", "RUB", "UAH", "KZT", "BYN", "EUR", "STARS",
)

# Знаки валют для красивого UI.
CURRENCY_SYMBOLS: dict[str, str] = {
    "TON": "TON",
    "USDT": "USDT",
    "USD": "$",
    "EUR": "€",
    "RUB": "₽",
    "UAH": "₴",
    "KZT": "₸",
    "BYN": "Br",
    "STARS": "⭐",
}

# Источник курсов крипты — CoinGecko Simple Price API.
# https://api.coingecko.com/api/v3/simple/price?ids=the-open-network,tether&vs_currencies=usd
_COINGECKO_IDS: dict[str, str] = {
    "TON": "the-open-network",
    "USDT": "tether",
}

# open.er-api.com отдаёт {"rates": {"USD": 1, "RUB": 88.5, ...}}
_FIAT_API_URL = "https://open.er-api.com/v6/latest/USD"

# Кеш {ccy: usd_value} — сколько USD стоит 1 единица валюты.
# Защищён локом, TTL 5 мин. Через USD сводим всё в кросс-курсы.
_RATE_TTL_SEC = 300
_rates_usd: dict[str, float] = {}
_rates_ts: float = 0.0
_rates_lock = threading.Lock()

# Stars фиксированно в USD.
_STARS_TO_USD = float(os.getenv("STARS_TO_USD_RATE", "0.013"))

# HTTP с прокси если нужно (на VPS обычно нет фильтрации к coingecko).
_REQUEST_TIMEOUT = float(os.getenv("CURRENCY_HTTP_TIMEOUT", "8"))
_REQUEST_PROXIES = None
_proxy_url = os.getenv("CURRENCY_HTTP_PROXY")
if _proxy_url:
    _REQUEST_PROXIES = {"http": _proxy_url, "https": _proxy_url}


def _refresh_rates() -> bool:
    """Тянет свежие курсы. Возвращает True если получилось хоть что-то.

    Стратегия отказоустойчивости:
    - сначала фиаты (один запрос даёт все), потом крипта;
    - если один источник упал — оставляем уже закешированные значения;
    - всегда наполняем USD=1.0 и STARS из ENV (они от сети не зависят).
    """
    new_rates: dict[str, float] = {"USD": 1.0, "STARS": _STARS_TO_USD}

    # Фиаты — один HTTP в open.er-api.
    try:
        r = requests.get(_FIAT_API_URL, timeout=_REQUEST_TIMEOUT, proxies=_REQUEST_PROXIES)
        if r.ok:
            data = r.json()
            rates = data.get("rates") or {}
            # rates у них = «1 USD = X местной валюты». Нам нужно «1 X = Y USD».
            for ccy in ("RUB", "EUR", "UAH", "KZT", "BYN"):
                v = rates.get(ccy)
                if isinstance(v, (int, float)) and v > 0:
                    new_rates[ccy] = 1.0 / float(v)
        else:
            logger.warning("currency: fiat fetch HTTP %s", r.status_code)
    except Exception as e:
        logger.warning("currency: fiat fetch failed: %s", e)

    # Крипта — CoinGecko.
    try:
        ids = ",".join(_COINGECKO_IDS.values())
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ids, "vs_currencies": "usd"},
            timeout=_REQUEST_TIMEOUT, proxies=_REQUEST_PROXIES,
        )
        if r.ok:
            data = r.json()
            for ccy, gecko_id in _COINGECKO_IDS.items():
                v = (data.get(gecko_id) or {}).get("usd")
                if isinstance(v, (int, float)) and v > 0:
                    new_rates[ccy] = float(v)
        else:
            logger.warning("currency: crypto fetch HTTP %s", r.status_code)
    except Exception as e:
        logger.warning("currency: crypto fetch failed: %s", e)

    with _rates_lock:
        # Мерджим — не теряем старые значения если новый источник лежал.
        merged = dict(_rates_usd)
        merged.update(new_rates)
        _rates_usd.clear()
        _rates_usd.update(merged)
        global _rates_ts
        _rates_ts = time.time()

    logger.info("currency: rates refreshed, %d entries", len(_rates_usd))
    return bool(_rates_usd)


def _get_usd_rate(ccy: str) -> Optional[float]:
    """Возвращает «1 ccy = X USD» из кеша; обновляет если протухло."""
    ccy = ccy.upper()
    with _rates_lock:
        fresh = _rates_usd and (time.time() - _rates_ts) < _RATE_TTL_SEC
        if fresh and ccy in _rates_usd:
            return _rates_usd[ccy]
    _refresh_rates()
    with _rates_lock:
        return _rates_usd.get(ccy)


def get_rate(from_ccy: str, to_ccy: str) -> Optional[float]:
    """Сколько `to_ccy` стоит 1 `from_ccy`. None если данных нет."""
    f, t = from_ccy.upper(), to_ccy.upper()
    if f == t:
        return 1.0
    fr = _get_usd_rate(f)
    tr = _get_usd_rate(t)
    if not fr or not tr:
        return None
    return fr / tr


def convert(amount: float, from_ccy: str, to_ccy: str) -> Optional[float]:
    """Конвертирует сумму. Возвращает округлённое до 4 знаков, или None."""
    rate = get_rate(from_ccy, to_ccy)
    if rate is None:
        return None
    try:
        return round(float(amount) * rate, 4)
    except (TypeError, ValueError):
        return None


def to_ton(amount: float, from_ccy: str) -> Optional[float]:
    """Шорткат для конвертации в каноническую TON."""
    return convert(amount, from_ccy, "TON")


def format_amount(amount: float, ccy: str) -> str:
    """UI-форматтер: «12.50 TON», «8 800 ₽», «$12.34».

    Целые значения для фиата — без дробной части. Для крипты — 4 знака после
    запятой максимум, без trailing-нулей."""
    ccy = ccy.upper()
    sym = CURRENCY_SYMBOLS.get(ccy, ccy)
    if ccy in ("RUB", "UAH", "KZT", "BYN"):
        # Фиаты с пробелом-разделителем тысяч и без дробной части (если целое).
        as_int = int(round(amount))
        s = f"{as_int:,}".replace(",", " ")
        return f"{s} {sym}"
    if ccy in ("USD", "EUR"):
        s = f"{amount:.2f}"
        return f"{sym}{s}"
    if ccy == "STARS":
        return f"{int(round(amount))} {sym}"
    # Крипта — до 4 знаков, обрезаем нули.
    s = f"{amount:.4f}".rstrip("0").rstrip(".")
    return f"{s} {sym}"


def format_with_alt(amount: float, ccy: str, alt_ccy: str) -> str:
    """«12 TON (~8800 ₽)» — основная сумма + конвертация в скобках."""
    main = format_amount(amount, ccy)
    if ccy.upper() == alt_ccy.upper():
        return main
    converted = convert(amount, ccy, alt_ccy)
    if converted is None:
        return main
    return f"{main} (~{format_amount(converted, alt_ccy)})"


def clear_rate_cache() -> int:
    """Сброс кеша курсов. Возвращает сколько записей было."""
    with _rates_lock:
        n = len(_rates_usd)
        _rates_usd.clear()
        global _rates_ts
        _rates_ts = 0.0
    logger.info("currency: cache cleared (%d entries)", n)
    return n


# ====================================================================
# user.preferred_currency: тонкие хелперы поверх dict users.
# Полное чтение через bot_core.users делегирует caller — здесь не импортим
# чтобы не было циклической зависимости.
# ====================================================================

DEFAULT_PREFERRED_CURRENCY = "TON"


def normalize_currency(ccy: str | None) -> str:
    """Возвращает валидный код или дефолт."""
    if not ccy:
        return DEFAULT_PREFERRED_CURRENCY
    up = ccy.upper().strip()
    return up if up in SUPPORTED_CURRENCIES else DEFAULT_PREFERRED_CURRENCY


def is_supported(ccy: str | None) -> bool:
    return bool(ccy) and ccy.upper() in SUPPORTED_CURRENCIES

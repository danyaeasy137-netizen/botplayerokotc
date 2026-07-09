# floor_client.py
"""
Клиент floor-цен для playerok-бота.

ИСТОЧНИКИ (в порядке предпочтения):
─────────────────────────────────────────────────────────────────────
1. PORTALS PUBLIC (по умолчанию, без авторизации)
   GET https://portal-market.com/api/collections        → slug → floor
   GET https://portal-market.com/api/nfts/search        → точная цена конкретного NFT
   • Не нужен PORTALS_AUTH_DATA, не протухает.
   • Floor — минимум по коллекции, либо точная цена если NFT в листинге.

2. PORTALS PRIVATE (если задан PORTALS_AUTH_DATA)
   `utils_nft_floor.get_floor_price_by_nft_link()` из otc-проекта.
   • Точнее: учитывает model/backdrop/symbol конкретного NFT.
   • Используется как override для редких атрибутов, если public floor < attrs floor.

3. None — админ вводит цену руками. Никогда не блокирует закрытие сделки.

ИСПОЛЬЗОВАНИЕ
─────────────
- `fetch_floor(link)` — одна ссылка → dict с price/collection.
- `estimate_pack(links)` — пачка → агрегат с total_ton.
- `parse_gift_links(text)` — выдёргивает ссылки из текста воркера.
- `clear_cache()` — сбросить кеши коллекций и NFT.

КЕШИРОВАНИЕ
───────────
- Карта slug→floor: 5 мин (один HTTP на все коллекции).
- Цена конкретного NFT: 5 мин (отдельный HTTP на каждую ссылку).
- Sentinel `_MISS` отличает «нет в кеше» от «закешировано как недоступное» —
  чтобы не лупить API при отсутствии цены.
"""
from __future__ import annotations

import logging
import os
import re
import sys
import threading
import time
from typing import Any, Optional

import requests

logger = logging.getLogger("playerok.floor")

# ====================================================================
# Опциональный fallback на private floor-модуль (если есть auth_data)
# ====================================================================
# Путь к директории с собственным `utils_nft_floor.py` (private обёртка над
# Portals API с авторизацией). Задаётся через PORTALS_FALLBACK_DIR в .env.
# Если не задан / не найден — работаем только через public API.
_fallback_dir = os.getenv("PORTALS_FALLBACK_DIR", "").strip()
if _fallback_dir and os.path.isdir(_fallback_dir) and _fallback_dir not in sys.path:
    sys.path.insert(0, _fallback_dir)

try:
    from utils_nft_floor import get_floor_price_by_nft_link  # type: ignore[import]
    _PRIVATE_AVAILABLE = True
    logger.info("floor_client: utils_nft_floor загружен (private fallback)")
except Exception as e:  # noqa: BLE001
    get_floor_price_by_nft_link = None  # type: ignore[assignment]
    _PRIVATE_AVAILABLE = False
    logger.info("floor_client: utils_nft_floor недоступен (%s) — работаем только через public API", e)


# ====================================================================
# Парсинг и нормализация t.me/nft/<Slug>-<Number> ссылок
# ====================================================================
_NFT_LINK_RE = re.compile(
    r"(?:https?://)?t\.me/nft/([A-Za-z][A-Za-z0-9]*)-(\d+)/?(?:\?\S*)?",
    re.IGNORECASE,
)

# Карта вручную для случаев, когда нормализация Telegram-имени != Portals-slug.
# Большинство случаев решается простым `re.sub('[^a-z0-9]', '', name.lower())`,
# но если Portals использует нестандартный slug — добавь сюда. Пример был бы
# `"durovscap": "durovscap"` (совпадает) — тут ничего экзотичного нет, но
# карта позволяет дописать override без правки кода.
_SLUG_OVERRIDES: dict[str, str] = {
    # 'someweirdtelegrammame': 'portal-slug-here',
}


def _slug_from_tg_name(tg_name: str) -> str:
    """Нормализация имени из t.me-ссылки в Portals slug.

    `SpringBasket` → `springbasket`, `Heart Locket` → `heartlocket`.
    Telegram URL не содержит пробелов (CamelCase), поэтому достаточно
    привести к lowercase и выкинуть всё кроме [a-z0-9].
    """
    base = re.sub(r"[^a-z0-9]", "", tg_name.lower())
    return _SLUG_OVERRIDES.get(base, base)


def _canonicalize(link: str) -> str:
    """Приводит ссылку к виду https://t.me/nft/Collection-Number (без query)."""
    m = _NFT_LINK_RE.search(link.strip())
    if not m:
        return link.strip()
    return f"https://t.me/nft/{m.group(1)}-{m.group(2)}"


def is_valid_nft_link(text: str) -> bool:
    """Один токен = одна валидная ссылка."""
    if not text:
        return False
    return bool(_NFT_LINK_RE.fullmatch(text.strip()))


def parse_gift_links(text: str) -> list[str]:
    """Извлекает все NFT-ссылки из свободного текста, дедуплицирует."""
    if not text:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for m in _NFT_LINK_RE.finditer(text):
        link = f"https://t.me/nft/{m.group(1)}-{m.group(2)}"
        if link not in seen:
            seen.add(link)
            out.append(link)
    return out


# ====================================================================
# Кеши
# ====================================================================
_CACHE_TTL_SEC = 300  # 5 минут — баланс свежести и нагрузки на Portals.
_PORTALS_BASE = "https://portal-market.com"
_HTTP_TIMEOUT = float(os.getenv("FLOOR_HTTP_TIMEOUT", "8"))
_PROXY_URL = os.getenv("FLOOR_HTTP_PROXY") or os.getenv("CURRENCY_HTTP_PROXY")
_REQUEST_PROXIES = {"http": _PROXY_URL, "https": _PROXY_URL} if _PROXY_URL else None

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# Карта slug → floor_price (TON, float). short_name из Portals API.
_collections_map: dict[str, float] = {}
# Доп. индекс: нормализованное имя (через _slug_from_tg_name) → реальный short_name.
# Нужен потому что Telegram-имя коллекции в ссылке (SwagBag) не всегда даёт
# тот же slug что Portals (там может быть swag-bag). Ищем сначала по
# short_name, затем по этой карте.
_collections_alias: dict[str, str] = {}
_collections_ts: float = 0.0
_collections_lock = threading.Lock()

# Кеш по конкретной ссылке (canonical → (price|None, ts))
_link_cache: dict[str, tuple[Optional[float], float]] = {}
_link_lock = threading.Lock()

_MISS = object()  # sentinel «нет в кеше»


# ====================================================================
# Public Portals API — слой, не требующий auth
# ====================================================================

def _refresh_collections_map() -> bool:
    """Тянет /api/collections и обновляет _collections_map.

    Возвращает True если получилось наполнить хотя бы что-то.
    Если упало — оставляем старое в карте (graceful degrade).
    """
    try:
        r = requests.get(
            f"{_PORTALS_BASE}/api/collections",
            params={"limit": 500},  # сейчас ~114 коллекций; запас на год вперёд.
            headers={"User-Agent": _USER_AGENT, "Accept": "application/json"},
            timeout=_HTTP_TIMEOUT,
            proxies=_REQUEST_PROXIES,
        )
        if not r.ok:
            logger.warning("floor: collections HTTP %s", r.status_code)
            return False
        data = r.json() or {}
        cols = data.get("collections") or []
        new_map: dict[str, float] = {}
        new_alias: dict[str, str] = {}
        for c in cols:
            slug = (c.get("short_name") or "").lower().strip()
            fp = c.get("floor_price")
            if not slug:
                continue
            try:
                fp_val = float(fp) if fp is not None else None
            except (TypeError, ValueError):
                fp_val = None
            if fp_val is not None and fp_val > 0:
                new_map[slug] = fp_val
                # Алиас по нормализованному имени (для матчинга t.me-имени).
                # Например: short_name='swag-bag', name='Swag Bag' → алиас 'swagbag'.
                full_name = (c.get("name") or "").strip()
                if full_name:
                    alias_key = _slug_from_tg_name(full_name)
                    if alias_key and alias_key not in new_alias:
                        new_alias[alias_key] = slug
                # И сам short_name прогоним через нормализацию (на случай дефисов).
                norm_short = _slug_from_tg_name(slug)
                if norm_short and norm_short != slug and norm_short not in new_alias:
                    new_alias[norm_short] = slug
        if not new_map:
            logger.warning("floor: collections empty payload")
            return False
        with _collections_lock:
            _collections_map.clear()
            _collections_map.update(new_map)
            _collections_alias.clear()
            _collections_alias.update(new_alias)
            global _collections_ts
            _collections_ts = time.time()
        logger.info("floor: collections refreshed, %d entries (+%d aliases)",
                    len(new_map), len(new_alias))
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning("floor: collections fetch failed: %s", e)
        return False


def _resolve_real_slug(tg_or_norm_slug: str) -> Optional[str]:
    """Преобразует нормализованное (без дефисов) имя коллекции в реальный
    short_name из Portals. Например 'swagbag' → 'swag-bag'.

    Возвращает реальный slug если коллекция известна, иначе None.
    Сам по себе вызов гарантирует свежесть карты коллекций.
    """
    if not tg_or_norm_slug:
        return None
    norm = tg_or_norm_slug.lower().strip()
    with _collections_lock:
        fresh = _collections_map and (time.time() - _collections_ts) < _CACHE_TTL_SEC
        if not fresh:
            need_refresh = True
        else:
            need_refresh = False
            if norm in _collections_map:
                return norm
            if norm in _collections_alias:
                return _collections_alias[norm]
    if need_refresh:
        _refresh_collections_map()
        with _collections_lock:
            if norm in _collections_map:
                return norm
            if norm in _collections_alias:
                return _collections_alias[norm]
    return None


def _get_collection_floor(slug: str) -> Optional[float]:
    """Возвращает floor по коллекции (slug или нормализованное имя)."""
    real_slug = _resolve_real_slug(slug)
    if real_slug is None:
        return None
    with _collections_lock:
        return _collections_map.get(real_slug)


def _search_nft_exact(slug: str, ext_number: int) -> Optional[dict[str, Any]]:
    """Точная цена конкретного NFT, если он сейчас в листинге Portals.

    Используем `external_collection_number` фильтр (число из t.me-ссылки).
    Если NFT не выставлен — возвращаем None и потом откатываемся на floor
    коллекции."""
    # Преобразуем нормализованный t.me-slug в реальный short_name Portals.
    real_slug = _resolve_real_slug(slug) or slug
    try:
        r = requests.get(
            f"{_PORTALS_BASE}/api/nfts/search",
            params={
                "collection_slugs": real_slug,
                "external_collection_number": ext_number,
                "limit": 1,
            },
            headers={"User-Agent": _USER_AGENT, "Accept": "application/json"},
            timeout=_HTTP_TIMEOUT,
            proxies=_REQUEST_PROXIES,
        )
        if not r.ok:
            return None
        data = r.json() or {}
        results = data.get("results") or []
        if not results:
            return None
        item = results[0]
        # Подтверждаем что это именно тот NFT (защита от мусорных результатов).
        # Portals API игнорирует фильтр collection_slugs если slug не существует,
        # и возвращает ЛЕВЫЙ NFT с таким же external_collection_number — поэтому
        # обязательно проверяем и slug, и номер. (Реальный кейс 2026-05-11:
        # SwagBag-60284 → Portals вернул Hypno Lollipop #60284 за 14 TON.)
        if int(item.get("external_collection_number", -1)) != ext_number:
            return None
        # Slug в ответе может быть в нескольких полях — пробуем все известные.
        item_slug = (
            item.get("collection_short_name")
            or item.get("collection_slug")
            or (item.get("collection") or {}).get("short_name")
            or (item.get("collection") or {}).get("slug")
            or ""
        )
        item_slug = str(item_slug).lower().strip()
        # Сравниваем с real_slug (что мы реально запросили). Если он не
        # известен — сравниваем с нормализованным запрошенным slug.
        expected_slug = (real_slug or slug).lower()
        if item_slug and item_slug != expected_slug:
            logger.warning(
                "floor: search_nft_exact slug mismatch — asked '%s' got '%s' "
                "(num=%d). Ignoring.",
                expected_slug, item_slug, ext_number,
            )
            return None
        try:
            price = float(item.get("price"))
        except (TypeError, ValueError):
            price = None
        attrs_list = item.get("attributes") or []
        attrs: dict[str, str] = {}
        for a in attrs_list:
            t, v = a.get("type"), a.get("value")
            if t and v:
                attrs[str(t)] = str(v)
        return {
            "price": price,
            "collection": item.get("name") or slug,
            "attrs": attrs or None,
        }
    except Exception as e:  # noqa: BLE001
        logger.debug("floor: search_nft_exact %s-%s failed: %s", slug, ext_number, e)
        return None


# ====================================================================
# Внутренний кеш по link
# ====================================================================

def _link_cache_get(key: str) -> Any:
    with _link_lock:
        v = _link_cache.get(key)
    if v is None:
        return _MISS
    price, ts = v
    if time.time() - ts >= _CACHE_TTL_SEC:
        return _MISS
    return price


def _link_cache_put(key: str, price: Optional[float]) -> None:
    with _link_lock:
        _link_cache[key] = (price, time.time())


# ====================================================================
# Публичный API
# ====================================================================

def fetch_floor(link: str, auth_data: Optional[str] = None) -> dict[str, Any]:
    """Тянет floor для одной NFT-ссылки.

    Стратегия:
      1) Кеш по link.
      2) Public Portals: точная цена листинга (если есть) → иначе floor коллекции.
      3) Private Portals (utils_nft_floor): если auth_data задан И public ничего
         не дал ИЛИ public floor подозрительно низкий (для редких атрибутов).
      4) None — админ введёт руками.

    Returns:
        {
            'link': canonical,
            'price': float | None,       # TON
            'collection': str | None,
            'attrs': dict | None,
            'cached': bool,
            'source': 'cache' | 'portals_public_exact' | 'portals_public_floor'
                      | 'portals_private' | 'unavailable',
            'error': str | None,
        }
    """
    canon = _canonicalize(link)
    out: dict[str, Any] = {
        "link": canon, "price": None, "collection": None, "attrs": None,
        "cached": False, "source": "unavailable", "error": None,
    }

    # 1. Кеш по ссылке.
    cached = _link_cache_get(canon)
    if cached is not _MISS:
        out["price"] = cached  # может быть None если ранее не нашли — это ок
        out["cached"] = True
        out["source"] = "cache"
        return out

    # 2. Парсим slug + number.
    m = _NFT_LINK_RE.search(canon)
    if not m:
        out["error"] = "bad link format"
        _link_cache_put(canon, None)
        return out

    tg_name, num_str = m.group(1), m.group(2)
    slug = _slug_from_tg_name(tg_name)
    try:
        ext_number = int(num_str)
    except ValueError:
        out["error"] = "bad number"
        _link_cache_put(canon, None)
        return out

    # 3. Public Portals — точная цена.
    exact = _search_nft_exact(slug, ext_number)
    if exact and exact.get("price"):
        out.update(price=exact["price"], collection=exact.get("collection"),
                   attrs=exact.get("attrs"), source="portals_public_exact")
        _link_cache_put(canon, exact["price"])
        return out

    # 4. Public Portals — floor коллекции.
    coll_floor = _get_collection_floor(slug)
    if coll_floor is not None:
        out.update(price=coll_floor, collection=tg_name, source="portals_public_floor")
        # attrs не известны, остаются None.
        _link_cache_put(canon, coll_floor)
        # Если auth_data есть — попытаемся уточнить через private (по атрибутам).
        if auth_data and _PRIVATE_AVAILABLE:
            try:
                pr, col, attrs = get_floor_price_by_nft_link(canon, auth_data=auth_data)  # type: ignore[misc]
                if pr and float(pr) > 0:
                    out["price"] = float(pr)
                    out["collection"] = col or out["collection"]
                    out["attrs"] = attrs or out["attrs"]
                    out["source"] = "portals_private"
                    _link_cache_put(canon, out["price"])
            except Exception as e:  # noqa: BLE001
                logger.debug("floor: private override failed for %s: %s", canon, e)
        return out

    # 5. Public не дал → пробуем private как последний шанс (если есть auth).
    if auth_data and _PRIVATE_AVAILABLE:
        try:
            pr, col, attrs = get_floor_price_by_nft_link(canon, auth_data=auth_data)  # type: ignore[misc]
            if pr and float(pr) > 0:
                out.update(price=float(pr), collection=col, attrs=attrs,
                           source="portals_private")
                _link_cache_put(canon, out["price"])
                return out
        except Exception as e:  # noqa: BLE001
            logger.warning("floor: private fetch failed for %s: %s", canon, e)
            out["error"] = f"private fetch: {e}"

    # 6. Ничего не нашли — кешируем «не знаем» на короткое время.
    _link_cache_put(canon, None)
    out["error"] = out["error"] or f"slug '{slug}' not in Portals collections"
    return out


def estimate_pack(links: list[str], auth_data: Optional[str] = None) -> dict[str, Any]:
    """Агрегатный расчёт по списку ссылок.

    Returns:
        {
            'total_ton': float,
            'items': [fetch_floor(...) for each],
            'resolved': int,
            'unresolved_links': [str],
            'available': bool,            # True если хоть один источник жив
            'sources': {source_name: count}
        }
    """
    items: list[dict[str, Any]] = []
    unresolved: list[str] = []
    sources: dict[str, int] = {}
    total = 0.0
    for link in links:
        info = fetch_floor(link, auth_data=auth_data)
        items.append(info)
        src = info.get("source") or "unavailable"
        sources[src] = sources.get(src, 0) + 1
        if info["price"] is None or info["price"] <= 0:
            unresolved.append(info["link"])
        else:
            total += info["price"]

    # «Доступен» если хотя бы карту коллекций удалось загрузить когда-либо.
    with _collections_lock:
        public_alive = bool(_collections_map)
    return {
        "total_ton": round(total, 4),
        "items": items,
        "resolved": len(items) - len(unresolved),
        "unresolved_links": unresolved,
        "available": public_alive or _PRIVATE_AVAILABLE,
        "sources": sources,
    }


def clear_cache() -> int:
    """Чистит оба кеша. Возвращает суммарное число записей."""
    with _link_lock:
        n_links = len(_link_cache)
        _link_cache.clear()
    with _collections_lock:
        n_cols = len(_collections_map)
        _collections_map.clear()
        _collections_alias.clear()
        global _collections_ts
        _collections_ts = 0.0
    logger.info("floor: cache cleared (%d links, %d collections)", n_links, n_cols)
    return n_links + n_cols


def health_check() -> dict[str, Any]:
    """Проверка живости источников. Используется в /test_floor админ-команде."""
    public_ok = _refresh_collections_map()
    with _collections_lock:
        n = len(_collections_map)
    return {
        "public_ok": public_ok,
        "public_collections": n,
        "private_available": _PRIVATE_AVAILABLE,
        "private_auth_set": bool(os.getenv("PORTALS_AUTH_DATA")),
    }

# Playerok — Telegram OTC-гарант для NFT-подарков

P2P-эскроу бот: продавец передаёт NFT-подарок через менеджера (поддержку),
покупатель оплачивает через внутренний баланс / Stars / реквизиты, после
получения товара поддержкой сделка закрывается, профит распределяется.

## Возможности

- Создание сделок в 9 валютах: TON, USDT, USD, RUB, UAH, KZT, BYN, EUR, Stars
- Конвертация валют по live-курсам (CoinGecko + open.er-api.com, кеш 5 мин)
- Баланс пользователя в каждой валюте + история транзакций
- Верификация продавца через оплату (карта/USDT/KZT/BYN/Stars)
- Депозиты и выводы с админ-аппрувом
- Реферальная система с трекингом «мамонтов» по приглашениям
- Floor-цены NFT через Portals API — авто-оценка профита по floor пакета
- Админ-форум: отдельные топики для сделок, профитов, выплат, юзеров,
  ошибок, аудита, дайджестов
- Двуязычный интерфейс: RU / EN (всего 426 ключей локалей)
- Маскировка контактов в публичном форуме команды (юзернеймы / NFT-ссылки
  затираются звёздочками — воркеры видят что профиты идут, но не могут
  восстановить контакты мамонтов)

## Структура

```
playerok/
├── bot_handlers.py        # Entry point, main polling loop
├── bot_core.py            # Ядро: TeleBot instance, state, pickle-хранилище,
│                          # юзеры, сделки, балансы, helpers
├── bot_ui.py              # Клавиатуры и форматирование карточек
├── bot_lang.py            # RU/EN локали, 426 ключей в каждой
├── currency_service.py    # Курсы валют (CoinGecko + open.er-api.com)
├── floor_client.py        # Floor-цены NFT через portal-market.com API
├── handlers/              # Хендлеры по модулям:
│   ├── system.py          #   простые команды: /ping, /version, /state,
│   │                      #   /find, /deal, /floor_health, /rates и т.п.
│   ├── deals.py           #   флоу сделки, profit decision, /start
│   ├── balance.py         #   оплата верификации, deposit, withdraw
│   ├── profile.py         #   UI профиля, теги, items, lang
│   ├── admin.py           #   админ-панель, balance ops
│   ├── callbacks.py       #   catch-all callback handler
│   └── inputs.py          #   главный text_handler для FSM-входов
├── photo.jpg              # Основное фото для карточек
├── video1.mp4             # Видео для уведомлений о профитах
├── video2.MP4             # Видео для главного меню
├── requirements.txt
└── .env.example           # Шаблон конфигурации
```

## Установка

```bash
# 1. Зависимости
python3 -m venv venv
source venv/bin/activate     # Linux/Mac
# venv\Scripts\activate      # Windows
pip install -r requirements.txt

# 2. Конфигурация
cp .env.example .env
nano .env                    # заполни значения

# 3. Запуск
python bot_handlers.py
```

## Минимальная конфигурация (`.env`)

Обязательно:
- `BOT_TOKEN` — токен от @BotFather
- `SYSTEM_OWNER_ID` — твой Telegram ID (главный админ)
- `MANAGER_USERNAME` — юзернейм поддержки (`@Playerok_Gifts`)

Желательно:
- `ADMIN_FORUM_ID` — chat_id Telegram-форума для админских событий
  (топики 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25 — см. комменты в `.env.example`)
- `TEAM_FORUM_ID` — публичный форум команды для маскированных логов

Опционально:
- `PROFITS_CHANNEL_ID` — канал для автопостинга профитов
- `PORTALS_AUTH_DATA` — авторизация private API portal-market.com
  (без неё работает public-API, точность ниже)

См. `.env.example` — там подробные комментарии по каждой переменной.

## Команды админа (в боте)

| Команда | Что |
|---|---|
| `/start` | Главное меню |
| `/admin` | Админ-панель |
| `/state` | Health snapshot — версия, watcher, floor, rates |
| `/find @username` | Карточка юзера |
| `/deal <id_prefix>` | Дамп сделки |
| `/force_close <id> <profit_ton>` | Экстренное закрытие сделки |
| `/floor_health` | Жив ли Portals API |
| `/test_floor <t.me/nft/...>` | Проверить floor по ссылке |
| `/rates`, `/refresh_rates` | Курсы валют |
| `/currency`, `/set_currency RUB` | Выбор валюты юзера |
| `/digest_now` | Сгенерировать дайджест за 24ч |

## Архитектура хранилища

Всё состояние — в `playerok_data.pkl` (pickle-снапшот словарей: users,
deals, balances, team_admins, team_workers, mammoth_referrals и т.д.).

`save_data()` под `_SAVE_LOCK` делает `deepcopy` всех словарей и пишет
во временный файл, потом `os.replace()` — атомарная замена. Это защищает
от race conditions между потоками telebot.

## Запуск как systemd-сервис

```ini
# /etc/systemd/system/playerok.service
[Unit]
Description=Playerok OTC bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/playerok
ExecStart=/path/to/playerok/venv/bin/python bot_handlers.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now playerok.service
journalctl -u playerok -f      # просмотр логов
```

## Зависимости

См. `requirements.txt`. Основное:
- `pyTelegramBotAPI` — Telegram Bot API клиент
- `requests` — HTTP для floor/currency
- `python-dotenv` — чтение `.env`
- `python-socks` (опц) — поддержка SOCKS-прокси для floor/currency

## Лицензия / поддержка

Передаётся вместе с исходным кодом. Любые модификации — на твоей стороне.

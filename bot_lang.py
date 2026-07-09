# bot_lang.py - Система локализации

TEXTS = {
    'ru': {
        'welcome': """<b><tg-emoji emoji-id="5332500806233002217">💼</tg-emoji> Добро пожаловать в Playerok Gifts!</b>
<blockquote><i><tg-emoji emoji-id="5469826368273402491">⚡️</tg-emoji> Надёжный посредник в NFT сделках.</i>
	<tg-emoji emoji-id="5415856324627943968">1⃣</tg-emoji> Преимущество в скорости сделок и выводах.
	<tg-emoji emoji-id="5413586872498670501">2⃣</tg-emoji> Защита обоих сторон в сделках.
	<tg-emoji emoji-id="5438334504122993220">3⃣</tg-emoji> Удобный функционал бота и сайта.
	<tg-emoji emoji-id="5404626904999288130">4⃣</tg-emoji> Безопасность при передаче товара @Playerok_Gifts</blockquote>
<tg-emoji emoji-id="5244491523269087164">⬇️</tg-emoji> Выберите действие ниже <tg-emoji emoji-id="5244491523269087164">⬇️</tg-emoji>""",

        'verified_status': '\n<tg-emoji emoji-id="5413721442413988676">✅</tg-emoji> <b>Статус:</b> Верифицированный пользователь',

        # Кнопки главного меню
        'btn_create_deal': '⚡ Создать сделку',
        'btn_my_profile': '👤 Мой профиль',
        'btn_balance_req': '💰 Баланс и реквизиты',
        'btn_verification': '🌐 Верификация',
        'btn_verification_done': '🌐 Верификация ✅',
        'btn_referrals': '🎯 Рефералы',
        'btn_my_tag': '🏷️ Мой тег',
        'btn_worker_panel': '🪐 Воркер панель',
        'btn_admin_panel': '⚙️ Админ панель',
        'btn_support': '📞 Поддержка',
        'btn_my_mammoths': '👥 Мои мамонты',
        'btn_back_menu': '🔙 В меню',
        'btn_back': '🔙 Назад',
        'btn_refresh': '🔄 Обновить',
        'btn_my_deals': '📦 Мои сделки',
        'btn_cancel': '❌ Отмена',
        'btn_send_receipt': '📤 Отправить чек',
        'btn_confirm_withdraw': '✅ Подтвердить вывод',
        'btn_withdraw_item': '📤 Вывести товар',
        'btn_all_deals': '🔙 Все сделки',
        'btn_to_admin': '⚙️ В админку',
        'btn_new_deal': '⚡ Новая сделка',

        # Реквизиты
        'bind_requisites': """<tg-emoji emoji-id='5332455502917949981'>🏦</tg-emoji> <b>Привязка реквизитов:</b>
<tg-emoji emoji-id='5447644880824181073'>⚠️</tg-emoji> <b>Для создания сделки необходимо привязать хотя бы одни реквизиты!
Укажите реквизиты для получения платежей:</b>
<tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Ton — для получения ton
<tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> Карта — для получения рублей и других валют
<tg-emoji emoji-id='5343777479091831702'>👛</tg-emoji> Usdt — для получения стейблкоинов
<tg-emoji emoji-id='5330319637156479518'>📱</tg-emoji> Телефон — для Qiwi/юmoney
<tg-emoji emoji-id='5406745015365943482'>⬇️</tg-emoji> <b>Выберите тип реквизитов</b> <tg-emoji emoji-id='5406745015365943482'>⬇️</tg-emoji>""",

        'no_requisites_alert': '❌ Для создания сделки необходимо привязать хотя бы одни реквизиты!',
        'blocked_alert': '🚫 Вы заблокированы и не можете создавать сделки',

        # Создание сделки
        'create_deal_title': '<tg-emoji emoji-id="5773677501825945508">⚡</tg-emoji> <b>СОЗДАНИЕ НОВОЙ СДЕЛКИ</b>',
        'create_deal_text': """<tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> <b>СОЗДАНИЕ НОВОЙ СДЕЛКИ</b>
<b>Выберите способ получения оплаты:</b>
• <tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Ton — мгновенные платежи в сети TON
• <tg-emoji emoji-id='5836907383292436018'>💎</tg-emoji> Usdt — популярные стейблкоины (TRC20)
• 🇷🇺 Rub — российские рубли
• 🇺🇸 Usd — доллары США
• 🇰🇿 Kzt — казахстанские тенге
• 🇺🇦 Uah — украинские гривны
• 🇧🇾 Byn — белорусские рубли
• ⭐ Stars — Telegram Stars
<b>Ваши реквизиты будут показаны покупателям автоматически.</b>""",

        # Профиты
        'profit_new': '<tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji> <b>НОВЫЙ ПРОФИТ!</b>',
        'profit_type': '<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>Тип:</b>',
        'profit_amount': '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>Сумма:</b>',
        'profit_desc': '<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Описание:</b>',
        'profit_deal': '<tg-emoji emoji-id="5195033767969839232">🚀</tg-emoji> <b>Сделка:</b>',
        'profit_success': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>Успешная мамонтизация!</b>',
        'profit_direct_transfer': 'Прямой перевод',

        # Язык
        'lang_select': '<tg-emoji emoji-id="5776233299424843260">🌐</tg-emoji> <b>Выберите язык / Select language:</b>',
        'lang_ru': '🇷🇺 Русский',
        'lang_en': '🇬🇧 English',

        # Алерты
        'already_verified': '✅ Вы уже верифицированы!',
        'access_denied': '❌ Доступ запрещён',
        'deal_not_found': '❌ Сделка не найдена',
        'deal_already_paid': '❌ Сделка уже оплачена или завершена',
        'deal_not_paid': '❌ Сделка еще не оплачена',
        'deal_no_buyer': '❌ В сделке нет покупателя',
        'not_buyer': '❌ Вы не являетесь покупателем в этой сделке',
        'not_seller': '❌ Вы не являетесь продавцом в этой сделке',
        'insufficient_funds': '❌ Недостаточно средств на балансе',
        'tag_workers_only': '❌ Установка тега доступна только воркерам и администраторам',
        'no_tag_set': '❌ У вас не установлен тег',
        'workers_admins_only': '❌ Доступно только воркерам и администраторам',
        'choose_payment_first': '❌ Сначала выберите способ оплаты верификации',
        'payment_confirmed': '✅ Оплата подтверждена, профит отправлен',
        'user_not_found': 'Пользователь не найден',

        # Верификация
        'verification_receipt_title': '📤 <b>ОТПРАВКА ЧЕКА НА ВЕРИФИКАЦИЮ</b>',
        'verification_receipt_text': """📤 <b>ОТПРАВКА ЧЕКА НА ВЕРИФИКАЦИЮ</b>

<b>Отправьте фото или документ с подтверждением перевода.</b>

<b>Требования к чеку:</b>
• Четкое изображение
• Видна сумма перевода
• Видна дата перевода
• Видны реквизиты получателя

<b>После отправки чека администратор проверит его и подтвердит верификацию.</b>
<i>Обычно проверка занимает до 15 минут.</i>""",

        # Теги
        'tag_manage_title': '🏷️ <b>УПРАВЛЕНИЕ ТЕГОМ</b>',
        'tag_current': '<b>Текущий тег:</b>',
        'tag_not_set': 'Не установлен',
        'tag_used_in_profits': '<b>Тег используется в профитах вместо вашего имени.</b>',
        'tag_example': '<i>Пример: В профитах будет отображаться "{tag}" вместо сгенерированного имени</i>',
        'tag_auto_hint': '<i>Если тег не установлен, будет сгенерировано автоматическое имя (воркер2035, воркер2914 и т.д.)</i>',
        'tag_choose_action': '<b>Выберите действие:</b>',
        'tag_setup_title': '🏷️ <b>УСТАНОВКА ТЕГА</b>',
        'tag_setup_text': """🏷️ <b>УСТАНОВКА ТЕГА</b>

<b>Введите ваш тег:</b>
• Тег должен начинаться с символа #
• Можно использовать буквы, цифры и подчеркивание
• Длина тега: от 2 до 20 символов
• Пример: #best_worker, #top_admin, #playerok_pro

<b>Тег будет отображаться в профитах.</b>
<b>Если тег не установлен, будет сгенерировано автоматическое имя.</b>

<b>Введите тег:</b>""",
        'tag_removed': '🗑️ <b>ТЕГ УДАЛЕН</b>',
        'tag_removed_text': """🗑️ <b>ТЕГ УДАЛЕН</b>

<b>Удаленный тег:</b> {tag}
<b>Теперь в профитах будет использоваться сгенерированное имя.</b>
<i>Вы можете установить новый тег в любое время.</i>""",
        'btn_set_tag': '🏷️ Установить тег',
        'btn_remove_tag': '🗑️ Удалить тег',
        'btn_set_new_tag': '🏷️ Установить новый',

        # Товары
        'items_title': '<tg-emoji emoji-id="5778672437122045013">📦</tg-emoji> <b>МОИ ТОВАРЫ</b>',
        'items_empty': '<b>У вас пока нет товаров.</b>',
        'items_hint': '<i>Товары появляются здесь после успешного завершения сделок, где вы выступали в роли покупателя.</i>',
        'items_how_to': '<b>Как получить товар:</b>',
        'no_items_withdraw': '📭 <b>Нет товаров для вывода</b>\n\nУ вас пока нет невыведенных товаров.',

        # Вывод товара
        'withdraw_title': '📤 <b>ПОДТВЕРЖДЕНИЕ ВЫВОДА ТОВАРА</b>',
        'withdraw_text': """📤 <b>ПОДТВЕРЖДЕНИЕ ВЫВОДА ТОВАРА</b>

<b>Товар ID:</b> <code>{item_id}</code>
<b>Для вывода товара, пожалуйста, обратитесь в техподдержку:</b>
👉 @Playerok_Gifts

<b>После обращения укажите номер товара и следуйте инструкциям поддержки.</b>
<i>Верифицированные пользователи получают приоритетное обслуживание и 0% комиссии.</i>

<b>Подтвердите вывод товара:</b>""",

        # Категория товара
        'category_title': """📁 <b>ВЫБЕРИТЕ КАТЕГОРИЮ ТОВАРА</b>

<b>Доступные категории:</b>
• <tg-emoji emoji-id='6037175527846975726'>🎁</tg-emoji> Подарок — цифровые подарки, стикеры
• 🏷️ NFT тег — NFT метки, коллекции
• 📢 Канал/чат — Telegram каналы, чаты
• ⭐ Stars — Telegram Stars
• <tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> Другое — любой другой товар

<b>Выберите категорию:</b>""",

        # Оплата
        'payment_confirmed_buyer': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>ОПЛАТА ПОДТВЕРЖДЕНА</b>

📋 <b>Сделка:</b> #{deal_id}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Списано с баланса:</b> {amount} {currency}
📊 <b>Остаток на балансе:</b> {balance} {currency}

<b>Ожидайте отправки товара от продавца.</b>
<i>Обычно это занимает до 15 минут.</i>

<b>Важно:</b> Товар будет передан только через поддержку!
Продавец отправит товар @Playerok_Gifts, после проверки вы получите уведомление.""",

        'payment_received_seller': """<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>ОПЛАТА ПОЛУЧЕНА!</b>

📋 <b>Сделка:</b> #{deal_id}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Покупатель:</b> @{buyer}
<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>Верификация покупателя:</b> {verified}
💸 <b>Сумма:</b> {amount} {currency}

<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Средства зачислены на ваш баланс.</b>
Покупатель оплатил сделку с баланса. Отправьте товар поддержке!

<tg-emoji emoji-id='5902016123972358349'>🛡</tg-emoji>️ <b>Критически важное правило:</b>
Товар должен быть передан исключительно поддержке - @Playerok_Gifts!

<b>После того как вы отправили товар поддержке, нажмите кнопку снизу:</b>""",

        'btn_sent_item': '✅ Я отправил товар',

        # Сделка создана
        'deal_created': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>СДЕЛКА СОЗДАНА!</b>

📋 <b>ID сделки:</b> #{deal_id}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Сумма:</b> {amount} {currency}
📁 <b>Категория:</b> {category}
<b>Ссылка/Описание:</b> {description}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Продавец:</b> @{seller}
<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>Верификация продавца:</b> {verified}

<b>Ссылка для покупателя:</b>
{link}

<b>Отправьте эту ссылку покупателю:</b>
{link}

<i>Как только покупатель перейдёт по ссылке, сделка начнётся.</i>""",

        # warning_title / btn_support_manager / btn_to_buyer удалены вместе с warning-викториной (ТЗ 2026-05-10)

        # Ошибки вывода
        'withdrawal_error': """⚠️ <b>Ошибка вывода товара</b>

Произошла ошибка при обработке вашего запроса на вывод. Пожалуйста, свяжитесь с техподдержкой: @Playerok_Gifts""",
        'balance_withdrawal_error': """⚠️ <b>Ошибка вывода средств</b>

Произошла ошибка при обработке вашего запроса на вывод. Пожалуйста, свяжитесь с техподдержкой: @Playerok_Gifts""",

        # Сделка завершена
        'deal_completed_buyer': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>СДЕЛКА УСПЕШНО ЗАВЕРШЕНА!</b>

📋 <b>ID сделки:</b> #{deal_id}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Сумма:</b> {amount} {currency}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Продавец:</b> @{seller}
<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> <b>Товар:</b> {description}

<b>Информация:</b>
• Товар добавлен в раздел "Мои товары"
• Вы можете вывести его в любое время
• Для вывода перейдите в профиль и нажмите "Мои товары"

💙 Спасибо за использование Playerok OTC!""",

        'deal_completed_seller': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>СДЕЛКА УСПЕШНО ЗАВЕРШЕНА!</b>

📋 <b>ID сделки:</b> #{deal_id}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Сумма:</b> {amount} {currency}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Покупатель:</b> @{buyer}
<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> <b>Товар:</b> {description}

<b>Информация:</b>
• Товар передан покупателю
• Сделка успешно завершена

💙 Спасибо за использование Playerok OTC!""",

        # Профиль
        'profile_title': '<b>🏆 ПРОФИЛЬ Playerok Bot</b>',
        'deals_empty': '📭 <b>У ВАС ПОКА НЕТ АКТИВНЫХ СДЕЛОК</b>\n\nСоздайте свою первую сделку с помощью кнопки ниже!',
        'deals_title': '📋 <b>ВАШИ АКТИВНЫЕ СДЕЛКИ</b>',
        'deals_select': 'Выберите сделку для управления:',

        # Роли
        'role_user': '👤 Пользователь',
        'role_owner': '👑 Владелец системы',
        'role_admin': '⚙️ Администратор',
        'role_worker': '👷 Воркер',
        'role_blocked': '🚫 (Заблокирован)',
        'verified_yes': '✅ Верифицирован',
        'verified_no': '❌ Не верифицирован',

        # Суммы вводов
        'enter_amount': '💰 <b>Введите сумму сделки:</b>',
        'invalid_amount': '❌ <b>НЕВЕРНЫЙ ФОРМАТ СУММЫ</b>\n\nВведите число, например: 1500 или 5.75',
        'amount_zero': '❌ <b>СУММА ДОЛЖНА БЫТЬ БОЛЬШЕ НУЛЯ</b>',
        'description_short': '❌ <b>ССЫЛКА/ОПИСАНИЕ СЛИШКОМ КОРОТКОЕ</b>\n\nМинимум 5 символов',

        # Направления профита
        'direction_sell': 'Продажа товара мамонту',
        'direction_buy': 'Покупка товара у мамонта',
        'direction_ad': 'Реклама бота',
        'direction_deposit': 'Пополнение баланса мамонтом',

        # Баланс
        'balance_deposit': '<tg-emoji emoji-id="5778421276024509124">💰</tg-emoji> <b>БАЛАНС УСПЕШНО ПОПОЛНЕН!</b>',
        'deposit_confirmed': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>БАЛАНС УСПЕШНО ПОПОЛНЕН!</b>

<tg-emoji emoji-id='5836907383292436018'>💎</tg-emoji> <b>Сумма:</b> {amount} {currency}
📊 <b>Текущий баланс:</b> {balance} {currency}

<b>Информация:</b>
• Средства зачислены на ваш баланс
• Вы можете использовать их для покупки товаров
• Для вывода средств обратитесь в техподдержку

💙 Спасибо за использование Playerok OTC!""",

        # Верификация инфо
        'verification_info': """🔰 <b>ПРОГРАММА ВЕРИФИКАЦИИ PLAYEROK OTC</b>

<b>ПРЕИМУЩЕСТВА ВЕРИФИКАЦИИ:</b>

<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>0% комиссии на вывод</b>
   — Выводите товары без дополнительных затрат

<tg-emoji emoji-id='5773677501825945508'>⚡️</tg-emoji> <b>Вывод в течение часа</b>
   — Приоритетная обработка заявок

🔒 <b>Без дополнительных проверок</b>
   — Не требуются повторные подтверждения

<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>ОСОБОЕ УСЛОВИЕ:</b>
При покупке верификации, полная стоимость вернется на ваш баланс!

<b>СТОИМОСТЬ ВЕРИФИКАЦИИ:</b>
• <tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> Карта РФ: 1000 RUB
• <tg-emoji emoji-id='5836907383292436018'>💎</tg-emoji> USDT: 13 USDT
• 🇰🇿 KZT: 5600 KZT
• 🇧🇾 BYN: 40 BYN
• ⭐️ Stars: 900 Stars

После оплаты отправьте чек для подтверждения

Для приобретения верификации нажмите кнопку ниже или уточните реквизиты у поддержки:""",

        # Статистика
        'stats_title': '📊 <b>СТАТИСТИКА PLAYEROK OTC</b>',
        'stats_advantages': """⭐ <b>Наша платформа активно развивается!</b>
<i>Присоединяйтесь к растущему сообществу</i>

💙 <b>Преимущества Playerok OTC:</b>
• 🔒 Гарант сделок
• <tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Быстрые выплаты
• <tg-emoji emoji-id='5836907383292436018'>💎</tg-emoji> Выгодные курсы
• 📞 Поддержка 24/7
• <tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> Система верификации

🤍 <b>Мы растем вместе с вами!</b>""",

        # Реквизиты пользователя
        'requisites_card': '💳 Карта',
        'requisites_ton': '⚡ Ton',
        'requisites_phone': '📱 Телефон',
        'requisites_usdt': '💎 Usdt',
        'not_specified': 'Не указан',
        'not_specified_f': 'Не указана',

        # Кнопки воркер панели
        'btn_my_stats': '📊 Моя статистика',
        'btn_my_deals_worker': '📋 Мои сделки',
        'btn_fake_deals': '💼 Накрутка сделок',
        'btn_fake_balance': '💰 Накрутка баланса',
        'btn_remove_deals': '📉 Открутка сделок',
        'btn_trim_profile': '✂️ Урезать профиль',

        # Items menu
        'items_total': 'Всего товаров:',
        'items_pending': 'Ожидают вывода:',
        'items_withdrawn': 'Выведено:',
        'items_pending_title': 'ОЖИДАЮТ ВЫВОДА:',
        'items_withdrawn_title': 'ВЫВЕДЕННЫЕ ТОВАРЫ:',
        'items_item': 'Товар',
        'items_desc': 'Описание',
        'items_received': 'Получен',
        'items_withdrawn_at': 'Выведен',
        'items_unknown': 'Неизвестно',
        'items_how_to_steps': """1. Найдите продавца и создайте сделку
2. Оплатите сделку с баланса
3. После подтверждения продавцом, товар появится здесь
4. Вы сможете вывести товар в любое время""",

        # Withdraw menu
        'withdraw_menu_title': 'ВЫВОД ТОВАРА',
        'withdraw_items_waiting': 'товаров, ожидающих вывода',
        'withdraw_select': 'Выберите товар для вывода или введите его ID:',

        # Balance withdraw
        'balance_withdraw_title': 'ВЫВОД СРЕДСТВ',
        'balance_your': 'Ваш баланс:',
        'balance_enter_amount': 'Введите сумму и валюту для вывода:',
        'balance_min': 'Минимальная сумма вывода:',
        'balance_contact_support': 'После запроса свяжитесь с поддержкой',
        'btn_to_profile': '🔙 В профиль',

        # Verification menu buttons
        'btn_pay_card': '💳 Оплатить картой РФ',
        'btn_pay_usdt': '💎 Оплатить USDT',
        'btn_pay_kzt': '🇰🇿 Оплатить KZT',
        'btn_pay_byn': '🇧🇾 Оплатить BYN',
        'btn_pay_stars': '⭐ Оплатить Stars',

        # Product categories
        'cat_gift': '🎁 Подарок',
        'cat_nft': '🏷️ Nft тег',
        'cat_channel': '📢 Канал/чат',
        'cat_stars': '⭐ Stars',
        'cat_other': '📦 Другое',

        # Profile labels
        'profile_name': 'Имя:',
        'profile_rating': 'Рейтинг:',
        'profile_success_deals': 'Успешных сделок:',
        'profile_disputes_won': 'Споров выиграно:',
        'profile_active_deals': 'Активных сделок:',
        'profile_balance': 'Баланс:',

        # Deals list
        'deals_role_seller': '🛒 Продавец',
        'deals_role_buyer': '💰 Покупатель',
        'deals_buyer_label': 'Покупатель:',
        'deals_seller_label': 'Продавец:',
        'deals_awaiting': 'Ожидается',
        'deals_more': 'И еще {count} сделок...',
        'deals_deal': 'Сделка',

        # Deal view
        'deal_view_seller_title': '📋 <b>ВАША СДЕЛКА</b>',
        'deal_view_buyer_title': '📋 <b>ВАША СДЕЛКА</b>',
        'deal_view_id': '<b>ID:</b>',
        'deal_view_status': '<b>Статус:</b>',
        'deal_view_category': '<b>Категория:</b>',
        'deal_view_desc': '<b>Товар/Ссылка:</b>',
        'deal_view_amount': '<b>Сумма:</b>',
        'deal_view_payment_method': '<b>Метод оплаты:</b>',
        'deal_view_your_verification': '<b>Ваша верификация:</b>',
        'deal_view_buyer_link': '<b>Ссылка для покупателя:</b>',
        'deal_view_buyer': '<b>Покупатель:</b>',
        'deal_view_send_link': '<b>Отправьте эту ссылку покупателю:</b>',
        'deal_view_seller': '<b>Продавец:</b>',
        'deal_view_seller_rating': '<b>Рейтинг продавца:</b>',
        'deal_view_seller_verification': '<b>Верификация продавца:</b>',
        'deal_view_pay_from_balance': '<b>Оплата будет произведена с вашего баланса.</b>',
        'deal_status_awaiting_buyer': 'Ожидание покупателя',
        'deal_status_awaiting_payment': 'Ожидание оплаты',
        'deal_status_paid': 'Оплачено',
        'deal_buyer_awaiting': 'Ожидается',
        'deal_category_default': 'Товар',
        'deal_verified_yes': '✅ Да',
        'deal_verified_no': '❌ Нет',

        # Buyer joined
        'buyer_joined_seller': """<b><tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> К сделке #{deal_id} присоединился покупатель @{buyer}!</b>

<blockquote><tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> После получения средств, вы получите уведомление для передачи товара менеджеру</blockquote>

<blockquote>📈 Завершённых сделок у продавца: {success_deals}</blockquote>

<tg-emoji emoji-id='5902016123972358349'>🛡</tg-emoji> Передача товара проходит ТОЛЬКО через менеджера {manager}. Не переводите товары напрямую продавцу!

❗️ Проверьте уведомление в боте о получение средств!""",

        'buyer_joined_buyer': """<b><tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> К сделке #{deal_id} присоединился продавец @{seller}!</b>

<blockquote><tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> Реквизиты менеджера для оплаты: {manager}</blockquote>

<blockquote>📈 Завершённых сделок у продавца: {success_deals}</blockquote>

<tg-emoji emoji-id='5902016123972358349'>🛡</tg-emoji> Вся оплата проходит ТОЛЬКО через менеджера {manager}. Не переводите средства напрямую продавцу!

❗️ Проверьте реквизиты перед оплатой!

<b>Товар/Ссылка:</b> {description}

💸 <b>Сумма:</b> {amount} {currency}""",

        # Balance & requisites
        'balance_req_title': '<b><tg-emoji emoji-id="5778421276024509124">💰</tg-emoji> БАЛАНС И РЕКВИЗИТЫ</b>',
        'balance_your_title': '<b>Ваш баланс:</b>',
        'requisites_your_title': '<b>Ваши реквизиты:</b>',
        'requisites_card_label': 'Карта',
        'requisites_phone_label': 'Телефон',
        'balance_choose_action': '<b>Выберите действие:</b>',
        'not_specified_req': 'Не указан',
        'btn_deposit_balance': '💰 Пополнить баланс',
        'btn_withdraw_balance': '💸 Вывести',
        'btn_ton_wallet': '⚡ Ton кошелёк',
        'btn_card_req': '💳 Карта',
        'btn_phone_req': '📱 Телефон',
        'btn_usdt_wallet': '💎 Usdt кошелёк',

        # Referral
        'referral_title': '<b><tg-emoji emoji-id="6032693626394382504">👤</tg-emoji> Реф. система</b>',
        'referral_percent': 'Ваш реферальный процент',
        'referral_invited': 'Приглашено пользователей',
        'referral_balance_ton': 'Реф. баланс TON',
        'referral_balance_usdt': 'Реф. баланс USDT TON',
        'referral_link_label': '<b>Ваша ссылка для приглашения:\n\n{ref_link}</b>',
        'btn_copy_link': '📋 Копировать',

        # Buttons for deals
        'btn_pay_balance': '💸 Оплатить с баланса',
        'btn_open_dispute': '⚠️ Открыть спор',
        'btn_my_deals_nav': '🔙 Мои сделки',
        'btn_deal_link': '📄 Сделка',

        # Deposit
        'deposit_title': '<tg-emoji emoji-id="5778421276024509124">💰</tg-emoji> <b>ПОПОЛНЕНИЕ БАЛАНСА</b>',
        'deposit_choose': '<b>Выберите способ пополнения:</b>',
        'deposit_card_ru': '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> Карта РФ — пополнение рублями',
        'deposit_card_ua': '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> Карта UA — пополнение гривнами',
        'deposit_crypto': '₿ Криптовалюта — BTC, ETH, USDT, TON, BNB, SOL',
        'deposit_stars': '⭐ Telegram Stars — пополнение звездами',
        'deposit_after': '<b>После выбора способа вам будут показаны реквизиты для перевода.</b>',
        'deposit_important': '<b>Важно:</b> После перевода обязательно отправьте чек кнопкой "📤 Отправить чек"!',
        'deposit_verified_hint': '<i>Верифицированные пользователи получают приоритетную обработку заявок</i>',

        # Deal view
        'deal_info_title': '<b>📋 ИНФОРМАЦИЯ О СДЕЛКЕ</b>',
        'deal_status_label': '<b>Статус:</b>',
        'deal_status_created': '🟡 Ожидает оплаты',
        'deal_status_paid': '🟢 Оплачена',
        'deal_status_completed': '🔵 Завершена',
        'deal_status_disputed': '🔴 Спор',
        'deal_buyer_awaiting': 'Ожидается',
        'deal_send_link': '<b>Отправьте эту ссылку покупателю:</b>',
        'deal_buyer_prompt': '<b>Для оплаты нажмите кнопку ниже</b>',

        # Seller sent item
        'seller_sent_item': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>ТОВАР ОТПРАВЛЕН!</b>',
        'seller_sent_wait': '<b>Ожидайте подтверждения от поддержки.</b>',

        # Verification payment
        'verification_pay_title': '🔰 <b>ОПЛАТА ВЕРИФИКАЦИИ ({method})</b>',
        'verification_pay_cost': '<b>Стоимость верификации:</b> {price} {currency}',
        'verification_pay_after': '<b>После перевода нажмите кнопку "📤 Отправить чек" и прикрепите подтверждение оплаты.</b>',
        'verif_pay_card_msg': '🔰 <b>ОПЛАТА ВЕРИФИКАЦИИ (КАРТА РФ)</b>\n\n<b>Стоимость верификации:</b> {price} RUB\n{details}\n\n<b>После перевода нажмите кнопку "📤 Отправить чек" и прикрепите подтверждение оплаты.</b>',
        'verif_pay_usdt_msg': '🔰 <b>ОПЛАТА ВЕРИФИКАЦИИ (USDT TRC20)</b>\n\n<b>Стоимость верификации:</b> {price} USDT\n{details}\n\n<b>После перевода нажмите кнопку "📤 Отправить чек" и прикрепите подтверждение оплаты.</b>',
        'verif_pay_simple_msg': '🔰 <b>ОПЛАТА ВЕРИФИКАЦИИ ({method})</b>\n\n<b>Стоимость верификации:</b> {price} {currency}\nСвяжитесь с поддержкой для уточнения реквизитов.\n\n<b>Инструкция:</b>\n1. Свяжитесь с @Playerok_Gifts для оплаты.\n2. После проверки администратором средства поступят на баланс.',
        'verif_pay_stars_msg': '🔰 <b>ОПЛАТА ВЕРИФИКАЦИИ (Stars)</b>\n\n<b>Стоимость верификации:</b> {price} Stars\nПереведите оплату звёздами на аккаунт поддержки\nСеть: Stars\n\n<b>Инструкция:</b>\n1. Переведите Stars на аккаунт поддержки (@Playerok_Gifts)\n2. После проверки администратором средства поступят на баланс',

        # Error messages
        'error_own_deal': '❌ Вы не можете присоединиться к своей собственной сделке как покупатель.',
        'error_deal_taken': '❌ Эта сделка уже занята другим покупателем.',

        # Wallet updates
        'wallet_ton_title': '<tg-emoji emoji-id="5773677501825945508">⚡</tg-emoji> <b>TON КОШЕЛЁК</b>',
        'wallet_card_title': '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>БАНКОВСКАЯ КАРТА</b>',
        'wallet_phone_title': '<tg-emoji emoji-id="5330319637156479518">📱</tg-emoji> <b>НОМЕР ТЕЛЕФОНА</b>',
        'wallet_usdt_title': '<tg-emoji emoji-id="5836907383292436018">💎</tg-emoji> <b>USDT КОШЕЛЁК</b>',
        'wallet_current': '<b>Текущий адрес:</b>',
        'wallet_current_card': '<b>Текущие реквизиты:</b>',
        'wallet_current_phone': '<b>Текущий номер:</b>',
        'wallet_send_new': '<b>Отправьте новый адрес кошелька:</b>',
        'wallet_send_card': '<b>Отправьте новые реквизиты:</b>',
        'wallet_send_phone': '<b>Отправьте номер телефона:</b>',
        'wallet_send_usdt': '<b>Отправьте адрес Usdt (TRC20):</b>',
        'wallet_ton_updated': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>TON КОШЕЛЁК ОБНОВЛЁН</b>',
        'wallet_card_updated': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>БАНКОВСКАЯ КАРТА ОБНОВЛЕНА</b>',
        'wallet_phone_updated': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>НОМЕР ТЕЛЕФОНА ОБНОВЛЁН</b>',
        'wallet_usdt_updated': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>USDT КОШЕЛЁК ОБНОВЛЁН</b>',
        'wallet_new_address': '<b>Новый адрес:</b>',
        'wallet_new_card': '<b>Новые реквизиты:</b>',
        'wallet_new_phone': '<b>Новый номер:</b>',
        'wallet_card_note': '<b>Теперь вы можете получать рублёвые платежи на эту карту.</b>\n<i>Реквизиты будут автоматически показаны покупателям.</i>',
        'wallet_phone_note': '<b>Теперь вы можете получать платежи Qiwi/юmoney на этот номер.</b>\n<i>Убедитесь, что номер активен и привязан к кошельку.</i>',
        'wallet_usdt_note': '<b>Теперь вы можете получать Usdt платежи на этот кошелёк.</b>\n<i>Проверьте, что адрес принадлежит сети TRC20.</i>',
        'btn_all_requisites': '🏦 Все реквизиты',

        # Admin panel buttons & messages
        'btn_add_worker': '👷 Добавить воркера',
        'btn_remove_worker': '🗑️ Удалить воркера',
        'btn_check_deals': '🔍 Проверить сделки',
        'btn_demote_worker': '📉 Понизить воркера',
        'btn_export_csv': '📥 Экспорт в CSV',
        'btn_worker_panel_nav': '👷 Воркер панель',
        'btn_admin_panel_nav': '⚙️ Админ панель',
        'btn_all_deals': '📋 Все сделки',
        'btn_stats': '📊 Статистика',
        'btn_my_profile_nav': '👤 Мой профиль',
        'btn_my_items': '📦 Мои товары',
        'btn_my_deals_nav2': '📋 Мои сделки',
        'btn_manage_tag': '🏷️ Управление тегом',
        'btn_to_profile': '🔙 В профиль',
        'btn_to_worker_panel': '🔙 В воркер панель',
        'btn_confirm_withdraw': '✅ Подтвердить вывод',
        'btn_confirm_deposit': '✅ Подтвердить пополнение',
        'btn_decline': '❌ Отклонить',
        'btn_verify_user': '✅ Верифицировать',
        'btn_unverify_user': '❌ Снять верификацию',
        'btn_add_balance': '➕ Добавить',
        'btn_set_balance': '✏️ Установить',
        'btn_deduct_balance': '➖ Списать',
        'btn_trim_deals': '📉 Урезать сделки',
        'btn_trim_balance': '💸 Урезать баланс',
        'btn_remove_admin': '🗑️ Удалить админа',
        'btn_profile_view': '👤 Профиль',
        'btn_demote': '📉 Понизить',
        'btn_select_other': '❌ Выбрать другого',
        'btn_to_list': '🔙 К списку',
        'btn_new_broadcast': '📢 Новая рассылка',
        'btn_new_message': '✉️ Новое сообщение',
        'btn_try_again': '🔄 Попробовать снова',
        'btn_recipient_list': '📋 Список получателей',
        'btn_not_paid': '❌ Не оплатил',
        'btn_not_sent': '📦 Не отправил',
        'btn_wrong_item': '🔄 Не тот товар',
        'btn_other_reason': '🚫 Другое',
        'btn_contact_manager': '📞 Связаться с менеджером',
        'btn_to_deal': '🔙 К сделке',
        'btn_deal_complete_profit': '✅ Завершить с профитом',
        'btn_update': '🔄 Обновить',
        'btn_contact_support': '📞 Поддержка',
        'btn_balance_manage': '🔙 Управление балансом',

        # Admin alerts
        'admin_only': '❌ Доступ запрещён. Только администраторы могут выполнять это действие',
        'admin_complete_only': '❌ Доступ запрещён. Только администраторы могут завершать сделки',
        'admin_confirm_only': '❌ Доступ запрещён. Только администраторы могут подтверждать получение товара',
        'owner_only_admins': '❌ Доступ запрещён. Только владелец системы может просматривать список всех админов',
        'owner_only_add_admin': '❌ Доступ запрещён. Только владелец системы может добавлять администраторов',
        'owner_only_remove_admin': '❌ Доступ запрещён. Только владелец системы может удалять администраторов',
        'admin_block_only': '❌ Доступ запрещён. Только администраторы могут управлять блокировками',
        'cannot_block_owner': '❌ Нельзя заблокировать владельца системы',
        'already_blocked': '⚠️ Пользователь уже заблокирован',
        'owner_unblock_only': '❌ Только владелец системы может разблокировать владельца',
        'not_blocked': '⚠️ Пользователь не заблокирован',
        'user_not_worker': '❌ Пользователь не является воркером',
        'method_not_found': '❌ Метод не найден',
        'error_generic': '❌ Ошибка',
        'deposit_approved': '✅ Пополнение подтверждено!',
        'deposit_error': '❌ Ошибка подтверждения',
        'deposit_declined': '❌ Пополнение отклонено',
        'deposit_declined_user': '❌ Ваш запрос на пополнение баланса был отклонен администратором. Свяжитесь с поддержкой для уточнения причин.',
        'user_verified_alert': '✅ Пользователь верифицирован',
        'user_unverified_alert': '❌ Верификация снята',
        'data_saved': '✅ Данные сохранены успешно!',
        'you_are_blocked': '🚫 Вы заблокированы',
        'export_in_dev': '📥 Функция экспорта в разработке',
        'lang_changed': '✅ Язык изменён!',
        'payment_not_supported': '❌ Оплата через подтверждение больше не поддерживается. Используйте оплату с баланса.',

        # Admin error messages
        'invalid_id_format': '❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nВведите целое число',
        'invalid_format': '❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>',
        'invalid_amount_format': '❌ <b>НЕВЕРНЫЙ ФОРМАТ СУММЫ</b>\n\nВведите число, например: 1000 или 0.01',
        'invalid_currency': '❌ <b>НЕВЕРНАЯ ВАЛЮТА</b>',
        'user_not_found_id': '❌ <b>ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН</b>',
        'cannot_block_owner_full': '❌ <b>НЕЛЬЗЯ ЗАБЛОКИРОВАТЬ ВЛАДЕЛЬЦА СИСТЕМЫ</b>',
        'cannot_remove_owner': '❌ <b>НЕЛЬЗЯ УДАЛИТЬ ВЛАДЕЛЬЦА СИСТЕМЫ</b>',
        'cannot_add_owner_admin': '❌ <b>НЕЛЬЗЯ ДОБАВИТЬ ВЛАДЕЛЬЦА СИСТЕМЫ КАК АДМИНА</b>',
        'edit_cancelled': '❌ <b>Редактирование отменено.</b>',
        'method_not_found_full': '❌ <b>Ошибка: метод не найден.</b>',
        'send_receipt_first': '❌ Сначала выберите способ пополнения и введите сумму.',
        'send_photo_doc': '❌ Пожалуйста, отправьте фото или документ с чеком.',
        'deal_deleted': '❌ <b>СДЕЛКА НЕ НАЙДЕНА</b>\n\nСделка была удалена или не существует.',
        'scam_desc_short': '❌ <b>СЛИШКОМ КОРОТКОЕ ОПИСАНИЕ</b>\n\nОпишите подробнее на что заскамили (минимум 3 символа).',
        'deal_complete_error': '❌ <b>ОШИБКА ЗАВЕРШЕНИЯ СДЕЛКИ</b>\n\nНе удалось завершить сделку.',
        'amount_negative': '❌ <b>НЕВЕРНАЯ СУММА</b>\n\nСумма должна быть больше 0',
        'amount_too_small': '❌ <b>СЛИШКОМ МАЛЕНЬКАЯ СУММА</b>',
        'insufficient_funds_full': '❌ <b>НЕДОСТАТОЧНО СРЕДСТВ</b>',
        'tag_must_start_hash': '❌ <b>ТЕГ ДОЛЖЕН НАЧИНАТЬСЯ С СИМВОЛА #</b>\n\nПример: #best_worker',
        'tag_too_short': '❌ <b>ТЕГ СЛИШКОМ КОРОТКИЙ</b>\n\nМинимум 2 символа (включая #)',
        'tag_too_long': '❌ <b>ТЕГ СЛИШКОМ ДЛИННЫЙ</b>\n\nМаксимум 20 символов',
        'tag_already_used': '❌ <b>ТЕГ УЖЕ ИСПОЛЬЗУЕТСЯ</b>',
        'no_recipients': '❌ <b>НЕТ ПОЛУЧАТЕЛЕЙ</b>\n\nДля выбранного типа рассылки не найдено получателей.',
        'verified_not_found': '❌ <b>Верифицированные пользователи не найдены</b>',
        'deals_not_found_search': '❌ <b>СДЕЛКИ НЕ НАЙДЕНЫ</b>',
        'users_not_found_search': '❌ <b>ПОЛЬЗОВАТЕЛИ НЕ НАЙДЕНЫ</b>',
        'bot_error': 'Ошибка использования бота.',
        'access_denied_block': '❌ <b>ДОСТУП ЗАПРЕЩЁН</b>\n\nТолько администраторы могут блокировать пользователей.',
        'access_denied_unblock': '❌ <b>ДОСТУП ЗАПРЕЩЁН</b>\n\nТолько администраторы могут разблокировать пользователей.',
        'access_denied_full': '❌ <b>ДОСТУП ЗАПРЕЩЁН</b>\nУ вас нет прав администратора',
        'deals_negative': '❌ Количество сделок не может быть отрицательным',
        'enter_integer': '❌ Введите целое число',
        'amount_negative_balance': '❌ Сумма не может быть отрицательной',

        # UI keyboard buttons (admin/worker/user-facing)
        'btn_deposit_card_ru': '💳 Карта РФ',
        'btn_deposit_card_ua': '💳 Карта UA',
        'btn_deposit_crypto': '₿ Криптовалюта',
        'btn_deposit_stars': '⭐ Telegram Stars',
        'btn_admin_stats': '📊 Статистика',
        'btn_admin_users': '👥 Пользователи',
        'btn_admin_all_deals': '📋 Все сделки',
        'btn_admin_deal_activities': '🔍 Действия в сделке',
        'btn_admin_user_activities': '👤 Действия пользователя',
        'btn_admin_broadcast': '📢 Рассылка',
        'btn_admin_workers_list': '👷 Список воркеров',
        'btn_admin_private_msg': '✉️ Личное сообщение',
        'btn_admin_add_worker': '👷 Выдать воркера',
        'btn_admin_remove_worker': '🗑️ Удалить воркера',
        'btn_admin_check_deals': '🔍 Проверить сделки',
        'btn_admin_demote_worker': '📉 Понизить воркера',
        'btn_admin_fake_deals': '💼 Накрутка сделок',
        'btn_admin_fake_balance': '💰 Накрутка баланса',
        'btn_admin_balance_mgmt': '💰 Управление балансом',
        'btn_admin_block_mgmt': '🚫 Управление блокировками',
        'btn_admin_verif_requests': '🔰 Заявки на верификацию',
        'btn_admin_verif_mgmt': '✅ Управление верификацией',
        'btn_admin_deposit_req': '💳 Реквизиты для пополнения',
        'btn_admin_admins_list': '👑 Список админов',
        'btn_admin_add_admin': '👑 Выдать админку',
        'btn_admin_remove_admin': '🗑️ Удалить админа',
        'btn_admin_system_info': '📊 Информация',
        'btn_verify_user_action': '✅ Верифицировать пользователя',
        'btn_unverify_user_action': '❌ Снять верификацию',
        'btn_verified_list': '📋 Список верифицированных',
        'btn_search_by_id': '🔍 Поиск по ID',
        'btn_add_balance_action': '➕ Добавить баланс',
        'btn_set_balance_action': '✏️ Установить баланс',
        'btn_deduct_balance_action': '➖ Списать баланс',
        'btn_check_balance': '🔍 Проверить баланс',
        'btn_block_user': '🚫 Заблокировать',
        'btn_unblock_user': '✅ Разблокировать',
        'btn_blocked_list': '📋 Список заблокированных',
        'btn_no_blocked': '📭 Нет заблокированных',
        'btn_no_admins': '📭 Нет администраторов',
        'btn_no_deals': '📭 Нет сделок',
        'btn_no_deal_activities': '📭 Нет сделок с активностью',
        'btn_search_deal': '🔍 Поиск сделки',
        'btn_broadcast_all': '📢 Всем пользователям',
        'btn_broadcast_workers': '👷 Всем воркерам',
        'btn_broadcast_admins': '👑 Всем админам',
        'btn_broadcast_user': '👤 Конкретному пользователю',
        'btn_write_user': '✉️ Написать пользователю',
        'btn_recipient_list_admin': '📋 Список получателей',
        'btn_prev': '⬅️ Назад',
        'btn_next': 'Вперед ➡️',
        'btn_owner_label': '👑 Владелец',
        'btn_admin_label': '⚙️ Админ',
        'btn_remove_worker_confirm': '🗑️ Удалить воркера',
        'btn_demote_confirm': '📉 Понизить',
        'btn_check_deals_worker': '🔍 Проверить сделки',
        'btn_worker_stats': '📊 Статистика',
        'btn_card_short': '💳 Карта',
        'btn_phone_short': '📱 Телефон',
    },

    'en': {
        'welcome': """<b><tg-emoji emoji-id="5893255507380014983">💼</tg-emoji> Welcome to Playerok Bot 🤝</b>
<blockquote><i><tg-emoji emoji-id="5456140674028019486">⚡️</tg-emoji> Your trusted P2P escrow service:</i>
\t<tg-emoji emoji-id="5794182096603847292">1⃣</tg-emoji> Automated deals with NFTs & Telegram gifts
\t<tg-emoji emoji-id="5794303034292968945">2⃣</tg-emoji> <tg-emoji emoji-id="5902016123972358349">🛡</tg-emoji> Full protection for both buyer and seller
\t<tg-emoji emoji-id="5794031944547178894">3⃣</tg-emoji> <tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji> Powerful bot &amp; web dashboard
\t<tg-emoji emoji-id="5793901252987330401">4⃣</tg-emoji> <tg-emoji emoji-id="5778672437122045013">📦</tg-emoji> All items go through our manager: @Playerok_Gifts</blockquote>
<tg-emoji emoji-id="5406745015365943482">⬇️</tg-emoji> Pick an option below <tg-emoji emoji-id="5406745015365943482">⬇️</tg-emoji>""",

        'verified_status': '\n<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>Status:</b> Verified',

        # Main menu buttons
        'btn_create_deal': '⚡ New deal',
        'btn_my_profile': '👤 Profile',
        'btn_balance_req': '💰 Balance & payouts',
        'btn_verification': '🌐 Get verified',
        'btn_verification_done': '🌐 Verified ✅',
        'btn_referrals': '🎯 Referrals',
        'btn_my_tag': '🏷️ My tag',
        'btn_worker_panel': '🪐 Worker panel',
        'btn_admin_panel': '⚙️ Admin panel',
        'btn_support': '📞 Support',
        'btn_my_mammoths': '👥 My customers',
        'btn_back_menu': '🔙 Menu',
        'btn_back': '🔙 Back',
        'btn_refresh': '🔄 Refresh',
        'btn_my_deals': '📦 My deals',
        'btn_cancel': '❌ Cancel',
        'btn_send_receipt': '📤 Send receipt',
        'btn_confirm_withdraw': '✅ Confirm withdrawal',
        'btn_withdraw_item': '📤 Claim item',
        'btn_all_deals': '🔙 All deals',
        'btn_to_admin': '⚙️ Admin panel',
        'btn_new_deal': '⚡ New deal',

        # Payout setup
        'bind_requisites': """<tg-emoji emoji-id='5332455502917949981'>🏦</tg-emoji> <b>Set up payout details</b>
<tg-emoji emoji-id='5447644880824181073'>⚠️</tg-emoji> <b>You need at least one payout method to create a deal.</b>
Choose how you'd like to be paid:
<tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> TON — TON wallet
<tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> Bank card — for fiat payouts
<tg-emoji emoji-id='5343777479091831702'>👛</tg-emoji> USDT — TRC-20 stablecoin
<tg-emoji emoji-id='5330319637156479518'>📱</tg-emoji> Phone — for YooMoney / SBP
<tg-emoji emoji-id='5406745015365943482'>⬇️</tg-emoji> <b>Pick a method</b> <tg-emoji emoji-id='5406745015365943482'>⬇️</tg-emoji>""",

        'no_requisites_alert': '❌ Add at least one payout method before creating a deal.',
        'blocked_alert': '🚫 You are blocked and can\'t create deals.',

        # Deal creation
        'create_deal_title': '<tg-emoji emoji-id="5773677501825945508">⚡</tg-emoji> <b>NEW DEAL</b>',
        'create_deal_text': """<tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> <b>NEW DEAL</b>
<b>How will you accept payment?</b>
• <tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> TON — instant on-chain payments
• <tg-emoji emoji-id='5836907383292436018'>💎</tg-emoji> USDT — TRC-20 stablecoin
• 🇷🇺 RUB — Russian ruble
• 🇺🇸 USD — US dollar
• 🇰🇿 KZT — Kazakh tenge
• 🇺🇦 UAH — Ukrainian hryvnia
• 🇧🇾 BYN — Belarusian ruble
• ⭐ Stars — Telegram Stars
<b>Your payout details will be shown to the buyer automatically.</b>""",

        # Profits
        'profit_new': '<tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji> <b>NEW PROFIT</b>',
        'profit_type': '<tg-emoji emoji-id="5197371802136892976">⛏</tg-emoji> <b>Type:</b>',
        'profit_amount': '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>Amount:</b>',
        'profit_desc': '<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>Note:</b>',
        'profit_deal': '<tg-emoji emoji-id="5195033767969839232">🚀</tg-emoji> <b>Deal:</b>',
        'profit_success': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>Deal closed successfully!</b>',
        'profit_direct_transfer': 'Direct transfer',

        # Language
        'lang_select': '<tg-emoji emoji-id="5776233299424843260">🌐</tg-emoji> <b>Select language:</b>',
        'lang_ru': '🇷🇺 Русский',
        'lang_en': '🇬🇧 English',

        # Alerts
        'already_verified': '✅ You\'re already verified!',
        'access_denied': '❌ Access denied',
        'deal_not_found': '❌ Deal not found',
        'deal_already_paid': '❌ This deal has already been paid or closed',
        'deal_not_paid': '❌ This deal hasn\'t been paid yet',
        'deal_no_buyer': '❌ This deal has no buyer yet',
        'not_buyer': '❌ You\'re not the buyer of this deal',
        'not_seller': '❌ You\'re not the seller of this deal',
        'insufficient_funds': '❌ Insufficient balance',
        'tag_workers_only': '❌ Tags are available to workers and admins only',
        'no_tag_set': '❌ You haven\'t set a tag yet',
        'workers_admins_only': '❌ Workers and admins only',
        'choose_payment_first': '❌ Choose a payment method first',
        'payment_confirmed': '✅ Payment confirmed — profit recorded',
        'user_not_found': 'User not found',

        # Verification
        'verification_receipt_title': '📤 <b>SUBMIT VERIFICATION RECEIPT</b>',
        'verification_receipt_text': """📤 <b>SUBMIT VERIFICATION RECEIPT</b>

<b>Send a photo or document showing the payment.</b>

<b>The receipt must show:</b>
• A clear, readable image
• The amount paid
• The payment date
• Recipient details

<b>An admin will review it once you submit.</b>
<i>Review usually takes up to 15 minutes.</i>""",

        # Tags
        'tag_manage_title': '🏷️ <b>TAG SETTINGS</b>',
        'tag_current': '<b>Current tag:</b>',
        'tag_not_set': 'Not set',
        'tag_used_in_profits': '<b>Your tag will appear in profit reports instead of your username.</b>',
        'tag_example': '<i>Example: profit reports will show "{tag}" instead of an auto-generated name.</i>',
        'tag_auto_hint': '<i>Without a tag, the bot generates names like worker2035, worker2914, etc.</i>',
        'tag_choose_action': '<b>Choose an action:</b>',
        'tag_setup_title': '🏷️ <b>SET A TAG</b>',
        'tag_setup_text': """🏷️ <b>SET A TAG</b>

<b>Tag rules:</b>
• Must start with #
• Letters, digits and underscores only
• 2 to 20 characters
• Examples: #best_worker, #top_admin, #playerok_pro

<b>This tag appears in profit reports.</b>
<b>Without one, an auto-generated name is used.</b>

<b>Type your tag:</b>""",
        'tag_removed': '🗑️ <b>TAG REMOVED</b>',
        'tag_removed_text': """🗑️ <b>TAG REMOVED</b>

<b>Removed:</b> {tag}
<b>Profit reports will now use an auto-generated name.</b>
<i>You can set a new tag any time.</i>""",
        'btn_set_tag': '🏷️ Set tag',
        'btn_remove_tag': '🗑️ Remove tag',
        'btn_set_new_tag': '🏷️ Set new tag',

        # Items
        'items_title': '<tg-emoji emoji-id="5778672437122045013">📦</tg-emoji> <b>MY ITEMS</b>',
        'items_empty': '<b>No items yet.</b>',
        'items_hint': '<i>Items show up here after a deal closes where you were the buyer.</i>',
        'items_how_to': '<b>How to get items:</b>',
        'no_items_withdraw': '📭 <b>Nothing to claim</b>\n\nYou don\'t have any unclaimed items.',

        # Claim item
        'withdraw_title': '📤 <b>CLAIM ITEM</b>',
        'withdraw_text': """📤 <b>CLAIM ITEM</b>

<b>Item ID:</b> <code>{item_id}</code>
<b>To claim this item, contact our manager:</b>
👉 @Playerok_Gifts

<b>Send them the item ID and follow their instructions.</b>
<i>Verified users get priority service and 0% fee.</i>

<b>Confirm claim:</b>""",

        # Product category
        'category_title': """📁 <b>PICK A CATEGORY</b>

<b>Available types:</b>
• <tg-emoji emoji-id='6037175527846975726'>🎁</tg-emoji> Gift — Telegram gifts, stickers
• 🏷️ NFT username — usernames and collections
• 📢 Channel / chat — Telegram channels & groups
• ⭐ Stars — Telegram Stars
• <tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> Other — anything else

<b>Pick one:</b>""",

        # Payment
        'payment_confirmed_buyer': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>PAYMENT CONFIRMED</b>

📋 <b>Deal:</b> #{deal_id}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Charged from balance:</b> {amount} {currency}
📊 <b>Balance left:</b> {balance} {currency}

<b>Waiting for the seller to hand off the item.</b>
<i>This usually takes up to 15 minutes.</i>

<b>Reminder:</b> all items are escrowed through our manager.
The seller transfers the item to @Playerok_Gifts and you'll be notified once we verify it.""",

        'payment_received_seller': """<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>PAYMENT RECEIVED</b>

📋 <b>Deal:</b> #{deal_id}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Buyer:</b> @{buyer}
<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>Buyer verified:</b> {verified}
💸 <b>Amount:</b> {amount} {currency}

<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Funds added to your balance.</b>
The buyer paid from their wallet — now hand off the item to our manager.

<tg-emoji emoji-id='5902016123972358349'>🛡</tg-emoji>️ <b>Critical rule:</b>
Transfer the item ONLY to @Playerok_Gifts. Never directly to the buyer.

<b>Once you've sent it, tap the button below:</b>""",

        'btn_sent_item': '✅ Item sent',

        # Deal created
        'deal_created': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>DEAL CREATED</b>

📋 <b>Deal ID:</b> #{deal_id}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Amount:</b> {amount} {currency}
📁 <b>Category:</b> {category}
<b>Link / description:</b> {description}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Seller:</b> @{seller}
<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>Seller verified:</b> {verified}

<b>Buyer link:</b>
{link}

<b>Share this link with the buyer:</b>
{link}

<i>The deal starts as soon as the buyer opens it.</i>""",

        # warning_title / btn_support_manager / btn_to_buyer удалены вместе с warning-викториной (ТЗ 2026-05-10)

        # Withdrawal errors
        'withdrawal_error': """⚠️ <b>Couldn't process the claim</b>

Something went wrong while processing your item claim. Please reach out to support: @Playerok_Gifts""",
        'balance_withdrawal_error': """⚠️ <b>Couldn't process the withdrawal</b>

Something went wrong while processing your withdrawal. Please reach out to support: @Playerok_Gifts""",

        # Deal completed
        'deal_completed_buyer': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>DEAL CLOSED</b>

📋 <b>Deal ID:</b> #{deal_id}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Amount:</b> {amount} {currency}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Seller:</b> @{seller}
<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> <b>Item:</b> {description}

<b>What's next:</b>
• Item is now in "My Items"
• Claim it whenever you're ready
• Profile → My Items → pick it → claim

💙 Thanks for using Playerok OTC!""",

        'deal_completed_seller': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>DEAL CLOSED</b>

📋 <b>Deal ID:</b> #{deal_id}
<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>Amount:</b> {amount} {currency}
<tg-emoji emoji-id='6032693626394382504'>👤</tg-emoji> <b>Buyer:</b> @{buyer}
<tg-emoji emoji-id='5778672437122045013'>📦</tg-emoji> <b>Item:</b> {description}

<b>What's next:</b>
• Item delivered to the buyer
• Funds are settled

💙 Thanks for using Playerok OTC!""",

        # Profile
        'profile_title': '<b>🏆 PLAYEROK BOT — PROFILE</b>',
        'deals_empty': '📭 <b>NO ACTIVE DEALS</b>\n\nTap the button below to create your first one.',
        'deals_title': '📋 <b>YOUR ACTIVE DEALS</b>',
        'deals_select': 'Pick a deal to manage:',

        # Roles
        'role_user': '👤 User',
        'role_owner': '👑 System owner',
        'role_admin': '⚙️ Administrator',
        'role_worker': '👷 Worker',
        'role_blocked': '🚫 (Blocked)',
        'verified_yes': '✅ Verified',
        'verified_no': '❌ Not verified',

        # Amount entry
        'enter_amount': '💰 <b>Enter the deal amount:</b>',
        'invalid_amount': '❌ <b>INVALID AMOUNT</b>\n\nEnter a number, e.g. 1500 or 5.75',
        'amount_zero': '❌ <b>AMOUNT MUST BE GREATER THAN ZERO</b>',
        'description_short': '❌ <b>LINK / DESCRIPTION IS TOO SHORT</b>\n\nAt least 5 characters.',

        # Profit directions
        'direction_sell': 'Sold item to customer',
        'direction_buy': 'Bought item from customer',
        'direction_ad': 'Bot referral profit',
        'direction_deposit': 'Customer balance top-up',

        # Balance
        'balance_deposit': '<tg-emoji emoji-id="5778421276024509124">💰</tg-emoji> <b>BALANCE TOPPED UP</b>',
        'deposit_confirmed': """<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>BALANCE TOPPED UP</b>

<tg-emoji emoji-id='5836907383292436018'>💎</tg-emoji> <b>Amount:</b> {amount} {currency}
📊 <b>Current balance:</b> {balance} {currency}

<b>What's next:</b>
• Funds are now on your balance
• Use them to pay for any deal
• For withdrawals, message support

💙 Thanks for using Playerok OTC!""",

        # Verification info
        'verification_info': """🔰 <b>PLAYEROK OTC VERIFICATION</b>

<b>WHAT YOU GET:</b>

<tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> <b>0% claim fee</b>
   — Pull out your items at no extra cost

<tg-emoji emoji-id='5773677501825945508'>⚡️</tg-emoji> <b>Same-hour processing</b>
   — Your requests jump the queue

🔒 <b>No extra checks</b>
   — No repeated re-verifications

<tg-emoji emoji-id='5778421276024509124'>💰</tg-emoji> <b>BONUS:</b>
The full fee is credited back to your balance once you're verified.

<b>PRICES:</b>
• <tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> RU bank card: 1,000 RUB
• <tg-emoji emoji-id='5836907383292436018'>💎</tg-emoji> USDT: 13 USDT
• 🇰🇿 KZT: 5,600 KZT
• 🇧🇾 BYN: 40 BYN
• ⭐️ Stars: 900 Stars

After paying, send the receipt for review.

Tap a button below to pay, or message support if you need details:""",

        # Stats
        'stats_title': '📊 <b>PLAYEROK OTC — STATS</b>',
        'stats_advantages': """⭐ <b>The platform keeps growing.</b>
<i>Join the community.</i>

💙 <b>Why Playerok OTC:</b>
• 🔒 Real escrow on every deal
• <tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Fast payouts
• <tg-emoji emoji-id='5836907383292436018'>💎</tg-emoji> Best rates around
• 📞 24/7 support
• <tg-emoji emoji-id='5774022692642492953'>✅</tg-emoji> Built-in verification

🤍 <b>Built with our users.</b>""",

        # Payout method labels
        'requisites_card': '💳 Card',
        'requisites_ton': '⚡ TON',
        'requisites_phone': '📱 Phone',
        'requisites_usdt': '💎 USDT',
        'not_specified': 'Not set',
        'not_specified_f': 'Not set',

        # Worker panel buttons
        'btn_my_stats': '📊 My stats',
        'btn_my_deals_worker': '📋 My deals',
        'btn_fake_deals': '💼 Fake deals',
        'btn_fake_balance': '💰 Fake balance',
        'btn_remove_deals': '📉 Remove deals',
        'btn_trim_profile': '✂️ Reset profile',

        # Items menu
        'items_total': 'Total items:',
        'items_pending': 'Unclaimed:',
        'items_withdrawn': 'Claimed:',
        'items_pending_title': 'UNCLAIMED:',
        'items_withdrawn_title': 'CLAIMED:',
        'items_item': 'Item',
        'items_desc': 'Description',
        'items_received': 'Received',
        'items_withdrawn_at': 'Claimed',
        'items_unknown': 'Unknown',
        'items_how_to_steps': """1. Find a seller and open a deal
2. Pay it from your balance
3. Once the seller delivers — the item shows up here
4. Claim it whenever you want""",

        # Claim menu
        'withdraw_menu_title': 'CLAIM AN ITEM',
        'withdraw_items_waiting': 'items waiting to be claimed',
        'withdraw_select': 'Pick an item or paste its ID:',

        # Balance withdraw
        'balance_withdraw_title': 'WITHDRAW FUNDS',
        'balance_your': 'Your balance:',
        'balance_enter_amount': 'How much do you want to withdraw, and in which currency?',
        'balance_min': 'Minimum amount:',
        'balance_contact_support': 'Once you submit the request, message support to finish.',
        'btn_to_profile': '🔙 Profile',

        # Verification menu buttons
        'btn_pay_card': '💳 RU card',
        'btn_pay_usdt': '💎 USDT',
        'btn_pay_kzt': '🇰🇿 KZT',
        'btn_pay_byn': '🇧🇾 BYN',
        'btn_pay_stars': '⭐ Stars',

        # Product categories
        'cat_gift': '🎁 Gift',
        'cat_nft': '🏷️ NFT username',
        'cat_channel': '📢 Channel / chat',
        'cat_stars': '⭐ Stars',
        'cat_other': '📦 Other',

        # Profile labels
        'profile_name': 'Name:',
        'profile_rating': 'Rating:',
        'profile_success_deals': 'Closed deals:',
        'profile_disputes_won': 'Disputes won:',
        'profile_active_deals': 'Active deals:',
        'profile_balance': 'Balance:',

        # Deals list
        'deals_role_seller': '🛒 Seller',
        'deals_role_buyer': '💰 Buyer',
        'deals_buyer_label': 'Buyer:',
        'deals_seller_label': 'Seller:',
        'deals_awaiting': 'Pending',
        'deals_more': '+{count} more deals…',
        'deals_deal': 'Deal',

        # Deal view
        'deal_view_seller_title': '📋 <b>YOUR DEAL</b>',
        'deal_view_buyer_title': '📋 <b>YOUR DEAL</b>',
        'deal_view_id': '<b>ID:</b>',
        'deal_view_status': '<b>Status:</b>',
        'deal_view_category': '<b>Category:</b>',
        'deal_view_desc': '<b>Item / link:</b>',
        'deal_view_amount': '<b>Amount:</b>',
        'deal_view_payment_method': '<b>Payment method:</b>',
        'deal_view_your_verification': '<b>You verified:</b>',
        'deal_view_buyer_link': '<b>Buyer link:</b>',
        'deal_view_buyer': '<b>Buyer:</b>',
        'deal_view_send_link': '<b>Share this link with the buyer:</b>',
        'deal_view_seller': '<b>Seller:</b>',
        'deal_view_seller_rating': '<b>Seller rating:</b>',
        'deal_view_seller_verification': '<b>Seller verified:</b>',
        'deal_view_pay_from_balance': '<b>Payment will be charged from your balance.</b>',
        'deal_status_awaiting_buyer': 'Waiting for buyer',
        'deal_status_awaiting_payment': 'Waiting for payment',
        'deal_status_paid': 'Paid',
        'deal_buyer_awaiting': 'Pending',
        'deal_category_default': 'Item',
        'deal_verified_yes': '✅ Yes',
        'deal_verified_no': '❌ No',

        # Buyer joined
        'buyer_joined_seller': """<b><tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> @{buyer} joined deal #{deal_id}</b>

<blockquote><tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> Once the payment lands you'll get a ping — then hand the item off to our manager.</blockquote>

<blockquote>📈 Seller's closed deals: {success_deals}</blockquote>

<tg-emoji emoji-id='5902016123972358349'>🛡</tg-emoji> Items go ONLY through {manager}. Never hand them directly to the buyer.

❗️ Watch for the payment notification in the bot.""",

        'buyer_joined_buyer': """<b><tg-emoji emoji-id='5773677501825945508'>⚡</tg-emoji> Seller @{seller} joined deal #{deal_id}</b>

<blockquote><tg-emoji emoji-id='5445353829304387411'>💳</tg-emoji> Pay through our manager: {manager}</blockquote>

<blockquote>📈 Seller's closed deals: {success_deals}</blockquote>

<tg-emoji emoji-id='5902016123972358349'>🛡</tg-emoji> Payments go ONLY through {manager}. Never pay the seller directly.

❗️ Double-check the payout details before sending money.

<b>Item / link:</b> {description}

💸 <b>Amount:</b> {amount} {currency}""",

        # Balance & payout details
        'balance_req_title': '<b><tg-emoji emoji-id="5778421276024509124">💰</tg-emoji> BALANCE & PAYOUTS</b>',
        'balance_your_title': '<b>Your balance:</b>',
        'requisites_your_title': '<b>Your payout details:</b>',
        'requisites_card_label': 'Card',
        'requisites_phone_label': 'Phone',
        'balance_choose_action': '<b>What do you want to do?</b>',
        'not_specified_req': 'Not set',
        'btn_deposit_balance': '💰 Deposit',
        'btn_withdraw_balance': '💸 Withdraw',
        'btn_ton_wallet': '⚡ TON wallet',
        'btn_card_req': '💳 Card',
        'btn_phone_req': '📱 Phone',
        'btn_usdt_wallet': '💎 USDT wallet',

        # Referral
        'referral_title': '<b><tg-emoji emoji-id="6032693626394382504">👤</tg-emoji> Referral program</b>',
        'referral_percent': 'Your share',
        'referral_invited': 'Invited users',
        'referral_balance_ton': 'TON earned',
        'referral_balance_usdt': 'USDT earned',
        'referral_link_label': '<b>Your referral link:\n\n{ref_link}</b>',
        'btn_copy_link': '📋 Copy',

        # Buttons for deals
        'btn_pay_balance': '💸 Pay from balance',
        'btn_open_dispute': '⚠️ Open dispute',
        'btn_my_deals_nav': '🔙 My deals',
        'btn_deal_link': '📄 Deal',

        # Deposit
        'deposit_title': '<tg-emoji emoji-id="5778421276024509124">💰</tg-emoji> <b>DEPOSIT</b>',
        'deposit_choose': '<b>Pick a deposit method:</b>',
        'deposit_card_ru': '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> RU card — deposit in RUB',
        'deposit_card_ua': '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> UA card — deposit in UAH',
        'deposit_crypto': '₿ Crypto — BTC, ETH, USDT, TON, BNB, SOL',
        'deposit_stars': '⭐ Telegram Stars — deposit in Stars',
        'deposit_after': '<b>Once you pick a method, the payment details will appear.</b>',
        'deposit_important': '<b>Important:</b> after sending the payment, hit "📤 Send receipt" so we can credit your balance.',
        'deposit_verified_hint': '<i>Verified users get priority processing.</i>',

        # Deal view
        'deal_info_title': '<b>📋 DEAL DETAILS</b>',
        'deal_status_label': '<b>Status:</b>',
        'deal_status_created': '🟡 Awaiting payment',
        'deal_status_paid': '🟢 Paid',
        'deal_status_completed': '🔵 Closed',
        'deal_status_disputed': '🔴 Disputed',
        'deal_buyer_awaiting': 'Pending',
        'deal_send_link': '<b>Share this link with the buyer:</b>',
        'deal_buyer_prompt': '<b>Tap the button below to pay.</b>',

        # Seller sent item
        'seller_sent_item': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>ITEM SENT</b>',
        'seller_sent_wait': '<b>Sit tight — we\'re verifying it on our side.</b>',

        # Verification payment
        'verification_pay_title': '🔰 <b>VERIFICATION ({method})</b>',
        'verification_pay_cost': '<b>Fee:</b> {price} {currency}',
        'verification_pay_after': '<b>After paying, hit "📤 Send receipt" and attach proof.</b>',
        'verif_pay_card_msg': '🔰 <b>VERIFICATION PAYMENT (RU CARD)</b>\n\n<b>Fee:</b> {price} RUB\n{details}\n\n<b>Once you\'ve paid, tap "📤 Send receipt" and attach the proof.</b>',
        'verif_pay_usdt_msg': '🔰 <b>VERIFICATION PAYMENT (USDT TRC-20)</b>\n\n<b>Fee:</b> {price} USDT\n{details}\n\n<b>Once you\'ve paid, tap "📤 Send receipt" and attach the proof.</b>',
        'verif_pay_simple_msg': '🔰 <b>VERIFICATION PAYMENT ({method})</b>\n\n<b>Fee:</b> {price} {currency}\nReach out to support to confirm the payment details.\n\n<b>How it works:</b>\n1. Message @Playerok_Gifts to pay.\n2. Once the admin reviews it, the amount lands on your balance.',
        'verif_pay_stars_msg': '🔰 <b>VERIFICATION PAYMENT (Stars)</b>\n\n<b>Fee:</b> {price} Stars\nSend the Stars to the support account.\nNetwork: Stars\n\n<b>How it works:</b>\n1. Send the Stars to the support account (@Playerok_Gifts).\n2. Once the admin reviews it, the amount lands on your balance.',

        # Error messages
        'error_own_deal': '❌ You can\'t join your own deal as a buyer.',
        'error_deal_taken': '❌ Another buyer has already taken this deal.',

        # Wallet updates
        'wallet_ton_title': '<tg-emoji emoji-id="5773677501825945508">⚡</tg-emoji> <b>TON WALLET</b>',
        'wallet_card_title': '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>BANK CARD</b>',
        'wallet_phone_title': '<tg-emoji emoji-id="5330319637156479518">📱</tg-emoji> <b>PHONE NUMBER</b>',
        'wallet_usdt_title': '<tg-emoji emoji-id="5836907383292436018">💎</tg-emoji> <b>USDT WALLET</b>',
        'wallet_current': '<b>Current address:</b>',
        'wallet_current_card': '<b>Current details:</b>',
        'wallet_current_phone': '<b>Current number:</b>',
        'wallet_send_new': '<b>Send the new wallet address:</b>',
        'wallet_send_card': '<b>Send new card details:</b>',
        'wallet_send_phone': '<b>Send the phone number:</b>',
        'wallet_send_usdt': '<b>Send a TRC-20 USDT address:</b>',
        'wallet_ton_updated': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>TON WALLET UPDATED</b>',
        'wallet_card_updated': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>BANK CARD UPDATED</b>',
        'wallet_phone_updated': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>PHONE NUMBER UPDATED</b>',
        'wallet_usdt_updated': '<tg-emoji emoji-id="5774022692642492953">✅</tg-emoji> <b>USDT WALLET UPDATED</b>',
        'wallet_new_address': '<b>New address:</b>',
        'wallet_new_card': '<b>New details:</b>',
        'wallet_new_phone': '<b>New number:</b>',
        'wallet_card_note': '<b>You can now accept ruble payments to this card.</b>\n<i>Buyers will see these details automatically.</i>',
        'wallet_phone_note': '<b>You can now accept SBP / YooMoney payments to this number.</b>\n<i>Make sure the number is active and linked to a wallet.</i>',
        'wallet_usdt_note': '<b>You can now accept USDT (TRC-20) payments here.</b>\n<i>Double-check the address is on the TRC-20 network.</i>',
        'btn_all_requisites': '🏦 All payout details',

        # Admin panel buttons & messages
        'btn_add_worker': '👷 Add worker',
        'btn_remove_worker': '🗑️ Remove worker',
        'btn_check_deals': '🔍 Check deals',
        'btn_demote_worker': '📉 Demote worker',
        'btn_export_csv': '📥 Export to CSV',
        'btn_worker_panel_nav': '👷 Worker panel',
        'btn_admin_panel_nav': '⚙️ Admin panel',
        'btn_all_deals': '📋 All deals',
        'btn_stats': '📊 Statistics',
        'btn_my_profile_nav': '👤 My profile',
        'btn_my_items': '📦 My items',
        'btn_my_deals_nav2': '📋 My deals',
        'btn_manage_tag': '🏷️ Tag management',
        'btn_to_profile': '🔙 To profile',
        'btn_to_worker_panel': '🔙 Worker panel',
        'btn_confirm_withdraw': '✅ Confirm withdrawal',
        'btn_confirm_deposit': '✅ Confirm deposit',
        'btn_decline': '❌ Decline',
        'btn_verify_user': '✅ Verify',
        'btn_unverify_user': '❌ Remove verification',
        'btn_add_balance': '➕ Add',
        'btn_set_balance': '✏️ Set',
        'btn_deduct_balance': '➖ Deduct',
        'btn_trim_deals': '📉 Trim deals',
        'btn_trim_balance': '💸 Trim balance',
        'btn_remove_admin': '🗑️ Remove admin',
        'btn_profile_view': '👤 Profile',
        'btn_demote': '📉 Demote',
        'btn_select_other': '❌ Select another',
        'btn_to_list': '🔙 To list',
        'btn_new_broadcast': '📢 New broadcast',
        'btn_new_message': '✉️ New message',
        'btn_try_again': '🔄 Try again',
        'btn_recipient_list': '📋 Recipient list',
        'btn_not_paid': '❌ Not paid',
        'btn_not_sent': '📦 Not sent',
        'btn_wrong_item': '🔄 Wrong item',
        'btn_other_reason': '🚫 Other',
        'btn_contact_manager': '📞 Contact manager',
        'btn_to_deal': '🔙 To deal',
        'btn_deal_complete_profit': '✅ Complete with profit',
        'btn_update': '🔄 Update',
        'btn_contact_support': '📞 Support',
        'btn_balance_manage': '🔙 Balance management',

        # Admin alerts
        'admin_only': '❌ Admins only.',
        'admin_complete_only': '❌ Only admins can close deals.',
        'admin_confirm_only': '❌ Only admins can confirm item receipt.',
        'owner_only_admins': '❌ Only the system owner can view the admin list.',
        'owner_only_add_admin': '❌ Only the system owner can add admins.',
        'owner_only_remove_admin': '❌ Only the system owner can remove admins.',
        'admin_block_only': '❌ Only admins can manage blocks.',
        'cannot_block_owner': '❌ You can\'t block the system owner.',
        'already_blocked': '⚠️ User is already blocked.',
        'owner_unblock_only': '❌ Only the system owner can unblock the owner.',
        'not_blocked': '⚠️ User isn\'t blocked.',
        'user_not_worker': '❌ User isn\'t a worker.',
        'method_not_found': '❌ Method not found.',
        'error_generic': '❌ Error',
        'deposit_approved': '✅ Deposit approved.',
        'deposit_error': '❌ Couldn\'t approve the deposit.',
        'deposit_declined': '❌ Deposit declined.',
        'deposit_declined_user': '❌ Your deposit was declined by an admin. Reach out to support for details.',
        'user_verified_alert': '✅ User verified.',
        'user_unverified_alert': '❌ Verification removed.',
        'data_saved': '✅ Saved.',
        'you_are_blocked': '🚫 You\'re blocked.',
        'export_in_dev': '📥 Export is still in development.',
        'lang_changed': '✅ Language updated.',
        'payment_not_supported': '❌ This payment flow is retired — pay from your balance instead.',

        # Admin error messages
        'invalid_id_format': '❌ <b>INVALID ID</b>\n\nEnter a whole number.',
        'invalid_format': '❌ <b>INVALID FORMAT</b>',
        'invalid_amount_format': '❌ <b>INVALID AMOUNT</b>\n\nEnter a number, e.g. 1000 or 0.01.',
        'invalid_currency': '❌ <b>INVALID CURRENCY</b>',
        'user_not_found_id': '❌ <b>USER NOT FOUND</b>',
        'cannot_block_owner_full': '❌ <b>CAN\'T BLOCK THE SYSTEM OWNER</b>',
        'cannot_remove_owner': '❌ <b>CAN\'T REMOVE THE SYSTEM OWNER</b>',
        'cannot_add_owner_admin': '❌ <b>CAN\'T ADD THE SYSTEM OWNER AS AN ADMIN</b>',
        'edit_cancelled': '❌ <b>Edit cancelled.</b>',
        'method_not_found_full': '❌ <b>Method not found.</b>',
        'send_receipt_first': '❌ Pick a deposit method and enter the amount first.',
        'send_photo_doc': '❌ Send a photo or document with the receipt.',
        'deal_deleted': '❌ <b>DEAL NOT FOUND</b>\n\nIt was deleted or never existed.',
        'scam_desc_short': '❌ <b>DESCRIPTION TOO SHORT</b>\n\nGive at least 3 characters.',
        'deal_complete_error': '❌ <b>FAILED TO CLOSE DEAL</b>',
        'amount_negative': '❌ <b>INVALID AMOUNT</b>\n\nMust be greater than 0.',
        'amount_too_small': '❌ <b>AMOUNT TOO SMALL</b>',
        'insufficient_funds_full': '❌ <b>INSUFFICIENT FUNDS</b>',
        'tag_must_start_hash': '❌ <b>TAGS MUST START WITH #</b>\n\nExample: #best_worker',
        'tag_too_short': '❌ <b>TAG TOO SHORT</b>\n\nAt least 2 characters (including #).',
        'tag_too_long': '❌ <b>TAG TOO LONG</b>\n\nMax 20 characters.',
        'tag_already_used': '❌ <b>TAG ALREADY TAKEN</b>',
        'no_recipients': '❌ <b>NO RECIPIENTS</b>\n\nNo one matches the chosen broadcast type.',
        'verified_not_found': '❌ <b>No verified users yet.</b>',
        'deals_not_found_search': '❌ <b>NO DEALS FOUND</b>',
        'users_not_found_search': '❌ <b>NO USERS FOUND</b>',
        'bot_error': 'Bot error.',
        'access_denied_block': '❌ <b>ACCESS DENIED</b>\n\nAdmins only.',
        'access_denied_unblock': '❌ <b>ACCESS DENIED</b>\n\nAdmins only.',
        'access_denied_full': '❌ <b>ACCESS DENIED</b>\nYou don\'t have admin rights.',
        'deals_negative': '❌ Deal count can\'t be negative.',
        'enter_integer': '❌ Enter a whole number.',
        'amount_negative_balance': '❌ Amount can\'t be negative.',

        # UI keyboard buttons (admin/worker/user-facing)
        'btn_deposit_card_ru': '💳 RU card',
        'btn_deposit_card_ua': '💳 UA card',
        'btn_deposit_crypto': '₿ Crypto',
        'btn_deposit_stars': '⭐ Telegram Stars',
        'btn_admin_stats': '📊 Stats',
        'btn_admin_users': '👥 Users',
        'btn_admin_all_deals': '📋 All deals',
        'btn_admin_deal_activities': '🔍 Deal activity',
        'btn_admin_user_activities': '👤 User activity',
        'btn_admin_broadcast': '📢 Broadcast',
        'btn_admin_workers_list': '👷 Workers',
        'btn_admin_private_msg': '✉️ DM a user',
        'btn_admin_add_worker': '👷 Add worker',
        'btn_admin_remove_worker': '🗑️ Remove worker',
        'btn_admin_check_deals': '🔍 Audit deals',
        'btn_admin_demote_worker': '📉 Demote',
        'btn_admin_fake_deals': '💼 Fake deals',
        'btn_admin_fake_balance': '💰 Fake balance',
        'btn_admin_balance_mgmt': '💰 Balance ops',
        'btn_admin_block_mgmt': '🚫 Blocks',
        'btn_admin_verif_requests': '🔰 Verification queue',
        'btn_admin_verif_mgmt': '✅ Verification ops',
        'btn_admin_deposit_req': '💳 Deposit details',
        'btn_admin_admins_list': '👑 Admins',
        'btn_admin_add_admin': '👑 Add admin',
        'btn_admin_remove_admin': '🗑️ Remove admin',
        'btn_admin_system_info': '📊 Info',
        'btn_admin_commands': '📜 Command list',
        'btn_verify_user_action': '✅ Verify user',
        'btn_unverify_user_action': '❌ Unverify',
        'btn_verified_list': '📋 Verified users',
        'btn_search_by_id': '🔍 Search by ID',
        'btn_add_balance_action': '➕ Add balance',
        'btn_set_balance_action': '✏️ Set balance',
        'btn_deduct_balance_action': '➖ Deduct',
        'btn_check_balance': '🔍 Check balance',
        'btn_block_user': '🚫 Block',
        'btn_unblock_user': '✅ Unblock',
        'btn_blocked_list': '📋 Blocked',
        'btn_no_blocked': '📭 Nobody blocked',
        'btn_no_admins': '📭 No admins',
        'btn_no_deals': '📭 No deals',
        'btn_no_deal_activities': '📭 No active deals',
        'btn_search_deal': '🔍 Search deal',
        'btn_broadcast_all': '📢 Everyone',
        'btn_broadcast_workers': '👷 All workers',
        'btn_broadcast_admins': '👑 All admins',
        'btn_broadcast_user': '👤 One user',
        'btn_write_user': '✉️ Message user',
        'btn_recipient_list_admin': '📋 Recipients',
        'btn_prev': '⬅️ Back',
        'btn_next': 'Next ➡️',
        'btn_owner_label': '👑 Owner',
        'btn_admin_label': '⚙️ Admin',
        'btn_remove_worker_confirm': '🗑️ Remove worker',
        'btn_demote_confirm': '📉 Demote',
        'btn_check_deals_worker': '🔍 Audit deals',
        'btn_worker_stats': '📊 Stats',
        'btn_card_short': '💳 Card',
        'btn_phone_short': '📱 Phone',
    }
}


def get_text(user_id, key, users_dict=None):
    """Получает локализованный текст для пользователя"""
    lang = 'ru'
    if users_dict and user_id in users_dict:
        lang = users_dict[user_id].get('lang', 'ru')
    texts = TEXTS.get(lang, TEXTS['ru'])
    return texts.get(key, TEXTS['ru'].get(key, key))


def get_lang(user_id, users_dict=None):
    """Получает язык пользователя"""
    if users_dict and user_id in users_dict:
        return users_dict[user_id].get('lang', 'ru')
    return 'ru'
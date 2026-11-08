import os
import random
import time
import telebot
from telebot.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

CREATOR_ID = 5652739383

PREMIUM_USERS = {CREATOR_ID} 
TEMP_PREMIUMS = {}          
LAST_CHEST_OPEN = {}        

USER_XP = {}       
USER_LEVEL = {}    
TOTAL_CHESTS = {}  

FORTNITE_MAP_URL = "https://fortnite.gg"
FORTNITE_SHOP_URL = "https://fortnite.gg"

def has_premium(user_id):
    if user_id in PREMIUM_USERS:
        return True
    if user_id in TEMP_PREMIUMS:
        if time.time() < TEMP_PREMIUMS[user_id]:
            return True
        else:
            del TEMP_PREMIUMS[user_id] 
    return False

def add_xp(user_id, amount, chat_id, user_name):
    if user_id not in USER_XP:
        USER_XP[user_id] = 0
        USER_LEVEL[user_id] = 1
        
    USER_XP[user_id] += amount
    current_lvl = USER_LEVEL[user_id]
    
    xp_needed = current_lvl * 100
    if USER_XP[user_id] >= xp_needed:
        USER_XP[user_id] -= xp_needed
        USER_LEVEL[user_id] += 1
        new_lvl = USER_LEVEL[user_id]
        
        bot.send_message(chat_id, f"🎉 {user_name}, **УРОВЕНЬ ПОВЫШЕН!** Ты достиг **{new_lvl} ЛВЛ** в штабе Агента Джоунси! 🏅", parse_mode="Markdown")
        
        if new_lvl == 5 and user_id != CREATOR_ID:
            TEMP_PREMIUMS[user_id] = time.time() + 10800
            bot.send_message(chat_id, f"🎁 **БОНУС ЗА 5 УРОВЕНЬ!** Джоунси выдал тебе **3 ЧАСА ПРЕМИУМА** бесплатно! Лутай подсказки! 🔥", parse_mode="Markdown")

def get_expert_reply(user_text, is_premium):
    text = user_text.lower()
    if any(w in text for w in ["привет", "здарова", "салам", "ку"]):
        return "Здарова, боец! На связи Агент Джоунси. Я вырвался из Петли, чтобы залутать этот сезон вместе с тобой. Что хочешь узнать по тактике или сундукам?"
    if any(w in text for w in ["не верю", "не смогу", "устал", "сложно", "не найду"]):
        return "Отставить панику в лобби! Каждый открытый сундук — это шаг к заветному Pirate Shop Token. Твой дропрейт решит только упорство. Залетай в катку, я верю в твой скилл! 🎯"
    if any(w in text for w in ["шанс", "процент", "дроп"]):
        return "Слушай инсайд: базовый шанс выбить Pirate Shop Token из обычного сундука — около 0.01%. Но если знать правильные God-локации, дело пойдет в разы быстрее!"
    if any(w in text for w in ["карта", "маршрут", "где летать", "сундук", "локаци", "где найти"]):
        if is_premium:
            return "🔥 Внимание, VIP-информация! В новой главе лучшая траектория — высадка на God-сундуки в центральных скрытых зонах. Там максимальная плотность контейнеров на квадратный метр. Строй быстрый маршрут, лутайся за 2 минуты и уходи на дельте."
        else:
            return "Секретные маршруты и God-сундуки доступны только элите. Оформи Премиум за 15 звезд или выбей его в сундуке (/chest), и я выдам тебе интерактивную карту со всеми точками высадки!"
    if is_premium:
        return "Принял твой запрос, боец. Как твой премиум-наставник скажу: держи ухо востро, чекай тайминги бури и помни — с нашей картой токен точно будет твоим! ⚔️"
    else:
        return "Интересный вопрос! Но полная тактика по этой теме скрыта в Премиум-инсайдах. Забирай Премиум подписку, и мы разберем это как про-игроки! 🪙"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    if user_id not in USER_XP:
        USER_XP[user_id] = 0
        USER_LEVEL[user_id] = 1
        TOTAL_CHESTS[user_id] = 0
        
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💎 Премиум Агента (15 ⭐️)", callback_data="buy_premium"),
        InlineKeyboardButton("🎰 Сундук Фортуны", callback_data="open_chest_cb")
    )
    markup.add(
        InlineKeyboardButton("🛒 Магазин Предметов", url=FORTNITE_SHOP_URL),
        InlineKeyboardButton("🏅 Мой Профиль / Stats", callback_data="view_profile")
    )
    share_url = f"https://t.me{bot.get_me().username}&text=🔥 Залетай в ИИ-бота к Агенту Джоунси! Тут выдают карты сундуков новой главы Fortnite и можно бесплатно крутить рулетку лута! 📦"
    markup.add(InlineKeyboardButton("📢 Похвастаться / Поделиться", url=share_url))
    
    welcome_text = (
        f"Привет, {user_name}! Я твой личный ИИ-наставник Агент Джоунси. 🎯 Я создан специально для того, чтобы помочь тебе найти ультра-редкий токен на бесплатный магазин в Fortnite!\n\n"
        "ℹ️ **Вот что я могу тебе подсказать:**\n"
        "• Слить инсайды по реальным шансам дропа токенов.\n"
        "• Показать лучшие маршруты полетов и тайминги сундуков новой главы.\n"
        "• Показать свежий Магазин Предметов и прокачать твой уровень!\n\n"
        "👑 **Почему тебе необходим Премиум-доступ?**\n"
        "С моими тактическими раскладами у тебя будет **в разы больше шансов найти заветный токен**! Премиум открывает доступ к интерактивной карте сундуков новой главы и God-точкам высадки!\n\n"
        "Выбирай действие на кнопках ниже 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "view_profile")
def view_profile(call):
    user_id = call.from_user.id
    user_name = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
    lvl = USER_LEVEL.get(user_id, 1)
    xp = USER_XP.get(user_id, 0)
    chests = TOTAL_CHESTS.get(user_id, 0)
    status = "👑 Создатель (Вечный VIP)" if user_id == CREATOR_ID else ("💎 Premium" if has_premium(user_id) else "⚪ Бесплатный тариф")
    xp_needed = lvl * 100
    
    profile_text = (
        f"🏅 **БОЕВОЙ ПРОФИЛЬ ИГРОКА:** {user_name}\n\n"
        f"📊 **Твой статус:** {status}\n"
        f"🎖 **Уровень в штабе:** {lvl} LVL\n"
        f"✨ **Опыт (XP):** {xp} / {xp_needed} XP\n"
        f"📦 **Открыто сундуков:** {chests} шт.\n\n"
        f"💡 *Качайся до 5 уровня, чтобы Джоунси подарил тебе 3 часа Премиума бесплатно!*"
    )
    bot.send_message(call.message.chat.id, profile_text, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['shop'])
def send_shop_link(message):
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛒 Открыть Item Shop", url=FORTNITE_SHOP_URL))
    bot.reply_to(message, f"{user_name}, вот ссылка на актуальный Магазин Предметов Fortnite. Проверяй скины прямо сейчас!", reply_markup=markup)

@bot.message_handler(commands=['chest'])
def open_fortnite_chest(message):
    user_id = message.from_user.id
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    current_time = time.time()
    
    if user_id in LAST_CHEST_OPEN and user_id != CREATOR_ID:
        time_passed = current_time - LAST_CHEST_OPEN[user_id]
        if time_passed < 86400:
            time_left = int((86400 - time_passed) // 3600)
            bot.reply_to(message, f"{user_name}, ты уже открывал сундук сегодня! Твой следующий дроп будет доступен через {time_left} ч.")
            return

    LAST_CHEST_OPEN[user_id] = current_time
    TOTAL_CHESTS[user_id] = TOTAL_CHESTS.get(user_id, 0) + 1
    add_xp(user_id, 35, message.chat.id, user_name)
    
    rand = random.random() * 100 
    bot.send_message(message.chat.id, "📦 *Лутаем сундук новой главы от Джоунси...* ⛏️", parse_mode="Markdown")
    time.sleep(1.2)
    
    if rand <= 0.1: 
        PREMIUM_USERS.add(user_id)
        result = "🌌 **МИФИЧЕСКИЙ ДРОП!!** Юху-у-у! Тебе выпал Бесконечный Запас и... **ВЕЧНЫЙ ПРЕМИУМ НАВСЕГДА!** Ты легенда Ордена Петли! 👑"
    elif rand <= 2.1: 
        TEMP_PREMIUMS[user_id] = current_time + 18000 
        result = "🥇 **ЛЕГЕНДАРНЫЙ ЗОЛОТОЙ ДРОП!** Отлично! Тебе выпал Золотой Дробовик и **ПРЕМИУМ ДОСТУП НА 5 ЧАСОВ!** Скорее запрашивай у меня маршруты карты!"
    elif rand <= 15.0: 
        result = "🔮 **Эпический дроп!** Фиолетовый СКАР у тебя в руках! Увы, этот сундук ничего не дал... Попробуй завтра!"
    elif rand <= 35.0: 
        result = "🔹 **Редкий дроп!** Синяя помпа и пара мини-щитов. Увы, этот сундук ничего не дал... Попробуй завтра!"
    elif rand <= 65.0: 
        result = "🟢 **Необычный дроп!** Зелёный автомат и тактический пистолет. Увы, этот сундук ничего не дал... Попробуй завтра!"
    else: 
        result = "⚪ **Обычный серый лут.** Дефолтный пистолет и бинты. Увы, этот сундук ничего не дал... Попробуй завтра!"
        
    bot.send_message(message.chat.id, f"{user_name}, {result}", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "open_chest_cb")
def chest_callback(call):
    bot.answer_callback_query(call.id)
    open_fortnite_chest(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "buy_premium")
def send_invoice(call):
    if has_premium(call.from_user.id):
        bot.send_message(call.message.chat.id, "🌟 У вас уже активирован Премиум доступ Агента!")
        bot.answer_callback_query(call.id)
        return

    bot.send_invoice(
        chat_id=call.message.chat.id,
        title="Премиум Агента Джоунси",
        description="Подписка на секретные подсказки и маршруты сундуков для поиска токена Fortnite.",
        invoice_payload="fortnite_premium_payload",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Премиум доступ", amount=15)],
        start_parameter="premium-activation"
    )
    bot.answer_callback_query(call.id)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])

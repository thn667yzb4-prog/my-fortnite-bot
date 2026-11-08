import os, random, time, telebot, threading
from telebot.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# Локальный мини-сервер для обхода проверок бесплатного тарифа Render
app = Flask('')
@app.route('/')
def home(): return "Agent Jones is online!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN', ''))
CREATOR_ID = 5652739383
PREMIUM_USERS, TEMP_PREMIUMS, LAST_CHEST_OPEN = {CREATOR_ID}, {}, {}
USER_XP, USER_LEVEL, TOTAL_CHESTS = {}, {}, {}

def has_premium(u):
    if u in PREMIUM_USERS: return True
    if u in TEMP_PREMIUMS and time.time() < TEMP_PREMIUMS[u]: return True
    return False

def add_xp(u, am, c, name):
    if u not in USER_XP: USER_XP[u], USER_LEVEL[u], TOTAL_CHESTS[u] = 0, 1, 0
    USER_XP[u] += am
    if USER_XP[u] >= (USER_LEVEL[u] * 100):
        USER_XP[u] -= (USER_LEVEL[u] * 100)
        USER_LEVEL[u] += 1
        bot.send_message(c, f"🎉 {name}, **УРОВЕНЬ ПОВЫШЕН!** Ты достиг **{USER_LEVEL[u]} ЛВЛ**! 🏅", parse_mode="Markdown")
        if USER_LEVEL[u] == 5 and u != CREATOR_ID:
            TEMP_PREMIUMS[u] = time.time() + 10800
            bot.send_message(c, "🎁 **БОНУС!** Тебе выдано **3 ЧАСА ПРЕМИУМА** бесплатно! 🔥", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def send_welcome(m):
    u, name = m.from_user.id, (f"@{m.from_user.username}" if m.from_user.username else m.from_user.first_name)
    if u not in USER_XP: USER_XP[u], USER_LEVEL[u], TOTAL_CHESTS[u] = 0, 1, 0
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("💎 Премиум Агента (15 ⭐️)", callback_data="buy_premium"), InlineKeyboardButton("🎰 Сундук Фортуны", callback_data="open_chest_cb"))
    markup.add(InlineKeyboardButton("🛒 Магазин Предметов", url="https://fortnite.gg"), InlineKeyboardButton("🏅 Мой Профиль / Stats", callback_data="view_profile"))
    markup.add(InlineKeyboardButton("📢 Похвастаться / Поделиться", url=f"https://t.me{bot.get_me().username}&text=🔥 Залетай к Агенту Джоунси за картами сундуков Fortnite! 📦"))
    bot.send_message(m.chat.id, f"Привет, {name}! Я Агент Джоунси. 🎯 Помогу найти Pirate Shop Token в Fortnite!\n\nВыбирай действие: 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "view_profile")
def view_profile(c):
    u = c.from_user.id
    name = f"@{c.from_user.username}" if c.from_user.username else c.from_user.first_name
    lvl, xp, ch = USER_LEVEL.get(u, 1), USER_XP.get(u, 0), TOTAL_CHESTS.get(u, 0)
    st = "👑 Создатель" if u == CREATOR_ID else ("💎 Premium" if has_premium(u) else "⚪ Бесплатно")
    bot.send_message(c.message.chat.id, f"🏅 **ПРОФИЛЬ:** {name}\n📊 Статус: {st}\n🎖 Уровень: {lvl}\n✨ Опыт: {xp}/{lvl*100} XP\n📦 Сундуков: {ch}", parse_mode="Markdown")
    bot.answer_callback_query(c.id)

@bot.message_handler(commands=['chest'])
def open_fortnite_chest(m):
    u = m.from_user.id
    name = f"@{m.from_user.username}" if m.from_user.username else m.from_user.first_name
    if u in LAST_CHEST_OPEN and u != CREATOR_ID and (time.time() - LAST_CHEST_OPEN[u]) < 86400:
        bot.reply_to(m, f"{name}, сундук доступен раз в 24 часа!")
        return
    LAST_CHEST_OPEN[u] = time.time()
    TOTAL_CHESTS[u] = TOTAL_CHESTS.get(u, 0) + 1
    add_xp(u, 35, m.chat.id, name)
    rand = random.random() * 100
    if rand <= 0.1:
        PREMIUM_USERS.add(u)
        res = "🌌 **МИФИЧЕСКИЙ ДРОП!!** ВЕЧНЫЙ ПРЕМИУМ НАВСЕГДА! 👑"
    elif rand <= 2.1:
        TEMP_PREMIUMS[u] = time.time() + 18000
        res = "🥇 **ЛЕГЕНДАРНЫЙ ЗОЛОТОЙ ДРОП!** ПРЕМИУМ НА 5 ЧАСОВ!"
    elif rand <= 15.0: res = "🔮 **Эпический дроп!** Фиолетовый СКАР! Увы, премиума тут нет."
    else: res = "⚪ **Обычный лут.** Увы, сундук ничего не дал... Попробуй завтра!"
    bot.send_message(m.chat.id, f"{name}, {res}", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "open_chest_cb")
def chest_callback(call):
    bot.answer_callback_query(call.id)
    open_fortnite_chest(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "buy_premium")
def send_invoice(call):
    if has_premium(call.from_user.id):
        bot.send_message(call.message.chat.id, "🌟 У вас уже есть Премиум!")
        bot.answer_callback_query(call.id)
        return
    bot.send_invoice(call.message.chat.id, "Премиум Агента", "Секретные подсказки Fortnite.", "fortnite_payload", "", "XTR", [LabeledPrice("Премиум", 15)])
    bot.answer_callback_query(call.id)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(q): bot.answer_pre_checkout_query(q.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(m):
    PREMIUM_USERS.add(m.from_user.id)
    bot.reply_to(m, "🌟 Оплата прошла успешно! Премиум активирован.")

@bot.message_handler(content_types=['text'])
def handle_ai_chat(m):
    u = m.from_user.id
    name = f"@{m.from_user.username}" if m.from_user.username else m.from_user.first_name
    is_p = has_premium(u)
    add_xp(u, 10, m.chat.id, name)
    t = m.text.lower()
    
    if any(w in t for w in ["привет", "здарова"]): rep = "Здарова, боец! На связи Агент Джоунси. Что хочешь узнать по тактике?"
    elif any(w in t for w in ["шанс", "процент"]): rep = "Инсайд: шанс токена из обычного сундука — 0.01%. С God-локациями быстрее!"
    elif any(w in t for w in ["карта", "маршрут", "где летать"]):
        if is_p: rep = "🔥 VIP-Инфо! Высаживайся в центре карты на God-сундуки. Интерактивная карта: https://fortnite.gg"
        else: rep = "Секретные карты доступны в Премиуме за 15 звезд или в сундуке (/chest)!"
    else: rep = "Держи ухо востро! Полная тактика скрыта в Премиум-инсайдах."
    
    bot.reply_to(m, f"{name}, {rep}")

if __name__ == "__main__":
    # Запускаем фейковый веб-сайт в отдельном потоке для Render Free тарифа
    threading.Thread(target=run_web, daemon=True).start()
    print("Бот запущен...")
    bot.polling(none_stop=True)


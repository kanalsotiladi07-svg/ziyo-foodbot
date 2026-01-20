from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ========= SOZLAMALAR =========
TOKEN = "8346475214:AAF61SD2ElIb97ceq4IxO34mfxYaiGEoR5c"
ADMIN_ID = 7827164632  # o'zingni Telegram ID

# ========= MENU =========
MENU = {
    "🌯 Lavash": 33000,
    "🍔 Non Burger": 35000,
    "🌭 Xot-Dog": 20000,
    "☕ Kofe": 15000,
    "🥤 Coca Cola": 10000,
    "🥤 Pepsi": 10000,
    "🥤 Fanta": 10000,
    "🍗 Tandir tovuq": 50000,
    "🍗 Kefsi": 40000,
}

users = {}

# ========= ASOSIY MENYU =========
def main_menu(is_admin=False):
    kb = [
        ["🍽 Ovqat zakaz qilish", "📦 Buyurtmalar"],
        ["📍 Ziyo Food manzil", "☎️ Qo‘llab-quvvatlash"],
    ]
    if is_admin:
        kb.append(["🔧 Admin panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id == ADMIN_ID
    users[update.effective_user.id] = {"cart": []}

    await update.message.reply_text(
        "👋 Assalomu alaykum!\n🍔 Ziyo Food botiga xush kelibsiz.",
        reply_markup=main_menu(is_admin)
    )

# ========= OVQAT MENYU =========
async def food_menu(update: Update):
    kb = [[k] for k in MENU.keys()]
    kb.append(["🛒 Savat", "⬅️ Orqaga"])
    await update.message.reply_text(
        "🍽 Ovqat tanlang:",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

# ========= SAVAT =========
def cart_text(uid):
    cart = users[uid]["cart"]
    if not cart:
        return "🛒 Savatingiz bo‘sh."
    total = 0
    txt = "🛒 Savat:\n"
    for item in cart:
        txt += f"• {item} — {MENU[item]} so‘m\n"
        total += MENU[item]
    txt += f"\n💰 Jami: {total} so‘m"
    return txt

# ========= ADMIN PANEL =========
async def admin_panel(update: Update):
    kb = [
        ["📊 Buyurtmalar"],
        ["⬅️ Orqaga"]
    ]
    await update.message.reply_text(
        "🔧 Admin panel",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

# ========= HANDLER =========
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg = update.message

    if uid not in users:
        users[uid] = {"cart": []}

    # Kontakt
    if msg.contact:
        users[uid]["phone"] = msg.contact.phone_number
        kb = [[KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)]]
        await msg.reply_text(
            "📍 Manzilingizni yuboring:",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )
        return

    # Lokatsiya
    if msg.location:
        lat = msg.location.latitude
        lon = msg.location.longitude
        users[uid]["map"] = f"https://maps.google.com/?q={lat},{lon}"

        kb = [["💵 Naqt", "💳 Karta"]]
        await msg.reply_text(
            "💳 To‘lov turini tanlang:",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )
        return

    text = msg.text
    if text is None:
        return

    # Orqaga
    if text == "⬅️ Orqaga":
        return await start(update, context)

    # Ovqat zakaz
    if text == "🍽 Ovqat zakaz qilish":
        return await food_menu(update)

    # Ovqat tanlash
    if text in MENU:
        users[uid]["cart"].append(text)
        await msg.reply_text(f"➕ Qo‘shildi: {text}")
        return

    # Savat
    if text == "🛒 Savat":
        kb = [
            ["➕ Yana qo‘shish", "✅ Yakunlash"],
            ["⬅️ Orqaga"]
        ]
        await msg.reply_text(
            cart_text(uid),
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )
        return

    if text == "➕ Yana qo‘shish":
        return await food_menu(update)

    # Yakunlash
    if text == "✅ Yakunlash":
        kb = [[KeyboardButton("📞 Telefonni yuborish", request_contact=True)]]
        await msg.reply_text(
            "📞 Telefon raqamingizni yuboring:",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )
        return

    # To‘lov
    if text in ["💵 Naqt", "💳 Karta"]:
        order = cart_text(uid)
        admin_text = (
            "🆕 YANGI BUYURTMA\n\n"
            f"{order}\n\n"
            f"📞 Telefon: {users[uid].get('phone')}\n"
            f"💳 To‘lov: {text}\n"
            f"📍 Manzil: {users[uid].get('map')}"
        )
        await context.bot.send_message(ADMIN_ID, admin_text)

        users[uid] = {"cart": []}
        await msg.reply_text("✅ Buyurtma qabul qilindi! Rahmat 😊")
        return

    # Buyurtmalar
    if text == "📦 Buyurtmalar":
        await msg.reply_text("📦 Hozircha faol buyurtma yo‘q.")
        return

    # Manzil
    if text == "📍 Ziyo Food manzil":
        await msg.reply_text("📍 Ziyo Food\nhttps://maps.google.com")
        return

    # Aloqa
    if text == "☎️ Qo‘llab-quvvatlash":
        await msg.reply_text("☎️ Telefon: +998 XX XXX XX XX")
        return

    # Admin panel
    if text == "🔧 Admin panel" and uid == ADMIN_ID:
        return await admin_panel(update)

# ========= RUN =========
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle))
    app.run_polling()

if __name__ == "__main__":
    main()

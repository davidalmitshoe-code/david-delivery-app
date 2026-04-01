import os
import threading
import logging  # <--- ADD THIS LINE HERE
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
# ... the rest of your code ...
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. This creates a tiny "fake" website so Render stays happy
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"David Delivery is Live!")

def run_health_server():
    # Render uses port 10000 by default
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# 2. Start this server in the background
threading.Thread(target=run_health_server, daemon=True).start()

# --- YOUR ORIGINAL CODE STARTS HERE ---import logging
import json
from telegram import (
    Update, WebAppInfo, ReplyKeyboardMarkup, 
    KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, ContextTypes, 
    MessageHandler, filters, ConversationHandler
)

# --- CONFIGURATION ---
TOKEN = '8644137742:AAFQiJ6dShSPdWVjXvgSKX3fghG7stDZrhs'
ADMIN_ID = 998942116 
WEBAPP_URL = "https://davidalmitshoe-code.github.io/david-delivery-app/" 

# Conversation States
REG_NAME, REG_PHONE = range(2)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to DAVID Delivery!\n\n"
        "To get started, please enter your **Full Name**:",
        parse_mode='Markdown'
    )
    return REG_NAME

async def get_reg_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text("Great! Now please enter your **Phone Number** 📞:")
    return REG_PHONE

async def get_reg_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    
    # 1. Create the Mini App Button
    webapp_button = KeyboardButton(
        text="🛍️ Order Now", 
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    main_keyboard = ReplyKeyboardMarkup([[webapp_button]], resize_keyboard=True)

    # 2. Your Professional Welcome Message
    welcome_text = (
        "✅ **Registration Complete!**\n\n"
        "🚀 **Welcome to David Delivery!**\n\n"
        "Hungry? Thirsty? Craving pizza or burgers? 🍕🍔💧\n\n"
        "✨ **With David Delivery you can:**\n"
        "🚀 Get food & water jars delivered quickly\n"
        "🍱 Choose from many restaurants & options\n"
        "🎓 Enjoy student-friendly prices in Adama\n\n"
        "📞 **Call us anytime at: 0928854849**\n\n"
        "📢 **Announcement:**\n"
        "We have started food delivery directly to the **ASTU Dorm**!\n"
        "💰 Only 40 Birr delivery fee!\n\n"
        "👇 **Click the Order Now button below!**"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=main_keyboard,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    
    items_list = data.get("items", [])
    order_names = ", ".join([i['name'] for i in items_list]) if items_list else "Unknown Item"
    total_price = data.get("total", 0)
    
    reg_name = context.user_data.get('full_name', 'Not Registered')
    reg_phone = context.user_data.get('phone', 'Not Registered')
    tg_user = update.effective_user.username or "No Username"

    await update.effective_message.reply_text(
        f"✅ **Order Confirmed!**\n\n"
        f"🍱 **Items:** {order_names}\n"
        f"💰 **Total:** {total_price} ETB\n\n"
        f"Preparing your delivery for ASTU! 🚀",
        parse_mode='Markdown'
    )

    admin_msg = (
        f"🚨 **NEW ORDER**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 **Name:** {reg_name}\n"
        f"📞 **Phone:** {reg_phone}\n"
        f"🆔 **TG:** @{tg_user}\n"
        f"🍱 **Order:** {order_names}\n"
        f"💰 **Total:** {total_price} ETB\n"
        f"━━━━━━━━━━━━━━━"
    )
    
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode='Markdown')

def main():
    print("--- 🛠️ SCRIPT STARTING ---")
    app = Application.builder().token(TOKEN).read_timeout(30).connect_timeout(30).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_reg_name)],
            REG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_reg_phone)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    print("🚀 DAVID Delivery is LIVE!")
    app.run_polling()

if __name__ == '__main__':
    main()

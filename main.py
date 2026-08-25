import logging
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.error import TelegramError
import requests
from config import BOT_TOKEN, API_ENDPOINT, API_KEY, ADMIN_IDS, UPTIME_ROBOT_URL
from admin_panel import admin_menu, handle_admin_callback
from uptime_robot import ping_uptime_robot
from database import load_channels, save_channels, add_channel_db, remove_channel_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Emojis
EMOJIS = {
    "phone": "☎️",
    "info": "ℹ️",
    "check": "✅",
    "error": "❌",
    "loading": "⏳",
    "user": "👤",
    "location": "📍",
    "network": "📡",
    "success": "🎯",
    "admin": "👨‍💼",
    "channel": "📢",
    "lock": "🔒",
    "unlock": "🔓"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command for everyone"""
    user_id = update.effective_user.id
    channels = load_channels()
    
    # Check if user must join channel
    if channels:
        for channel in channels:
            try:
                member = await context.bot.get_chat_member(channel["channel_id"], user_id)
                if member.status == "left":
                    keyboard = [[
                        InlineKeyboardButton("📢 Join Channel", url=channel["invite_link"])
                    ]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        f"{EMOJIS['lock']} You must join our channel first.\n\n**{channel['name']}**\n\nThen try again.",
                        reply_markup=reply_markup,
                        parse_mode="Markdown"
                    )
                    return
            except TelegramError:
                pass
    
    welcome = f"""{EMOJIS['success']} **Phone Number Lookup Bot**

{EMOJIS['phone']} Send me a phone number (with country code)
Example: `919696467355`

{EMOJIS['info']} I'll fetch all available info instantly.

{EMOJIS['admin']} Admins: Use /admin for panel"""
    
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel access"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text(f"{EMOJIS['error']} Unauthorized.")
        return
    
    await admin_menu(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = f"""{EMOJIS['info']} **Commands:**

/start — Start the bot
/help — Show this message

{EMOJIS['admin']} Admin only:
/admin — Access admin panel"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def lookup_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lookup phone number"""
    user_id = update.effective_user.id
    channels = load_channels()
    
    # Force join check
    if channels:
        for channel in channels:
            try:
                member = await context.bot.get_chat_member(channel["channel_id"], user_id)
                if member.status == "left":
                    keyboard = [[
                        InlineKeyboardButton("📢 Join Channel", url=channel["invite_link"])
                    ]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        f"{EMOJIS['lock']} Join our channel to use this feature.\n\n**{channel['name']}**",
                        reply_markup=reply_markup,
                        parse_mode="Markdown"
                    )
                    return
            except TelegramError:
                pass
    
    text = update.message.text.strip()
    phone_number = text
    
    if not phone_number.isdigit() or len(phone_number) < 10:
        await update.message.reply_text(f"{EMOJIS['error']} Invalid phone number format. (min 10 digits)")
        return
    
    loading_msg = await update.message.reply_text(f"{EMOJIS['loading']} Fetching info...")
    
    try:
        params = {
            "mobile": phone_number,
            "key": API_KEY
        }
        response = requests.get(API_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success") and data.get("status") == "fail":
            await loading_msg.edit_text(f"{EMOJIS['error']} Number not found or invalid.")
            return
        
        result = f"{EMOJIS['check']} **Number Info**\n\n"
        
        if "data" in data:
            info = data["data"]
            if isinstance(info, dict):
                if info.get("number"):
                    result += f"{EMOJIS['phone']} **Number:** `{info['number']}`\n"
                if info.get("operator"):
                    result += f"{EMOJIS['network']} **Operator:** {info['operator']}\n"
                if info.get("status"):
                    result += f"{EMOJIS['check']} **Status:** {info['status']}\n"
                if info.get("circle"):
                    result += f"{EMOJIS['location']} **Circle:** {info['circle']}\n"
                if info.get("state"):
                    result += f"{EMOJIS['location']} **State:** {info['state']}\n"
                if info.get("country"):
                    result += f"🌍 **Country:** {info['country']}\n"
                if info.get("type"):
                    result += f"📱 **Type:** {info['type']}\n"
        
        if result == f"{EMOJIS['check']} **Number Info**\n\n":
            result += f"```\n{json.dumps(data, indent=2)}\n```"
        
        result += f"\n{EMOJIS['success']} Query successful"
        
        await loading_msg.edit_text(result, parse_mode="Markdown")
        
    except requests.exceptions.Timeout:
        await loading_msg.edit_text(f"{EMOJIS['error']} API timeout. Try again.")
    except requests.exceptions.RequestException as e:
        await loading_msg.edit_text(f"{EMOJIS['error']} API error: {str(e)}")
    except Exception as e:
        await loading_msg.edit_text(f"{EMOJIS['error']} Error: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    if update.message.text and update.message.text.isdigit():
        await lookup_number(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    await handle_admin_callback(update, context)

def main():
    # Ping uptime robot on startup
    if UPTIME_ROBOT_URL:
        ping_uptime_robot()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, lambda u, c: None))
    app.add_handler(MessageHandler(filters.ALL, button_callback, block=False))
    
    logger.info("🎯 Bot is live. 6767")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

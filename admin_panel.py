from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import load_channels, save_channels, add_channel_db, remove_channel_db

EMOJIS = {
    "admin": "👨‍💼",
    "channel": "📢",
    "add": "➕",
    "remove": "➖",
    "back": "◀️",
    "check": "✅",
    "error": "❌",
    "lock": "🔒",
}

# Conversation states
WAITING_FOR_CHANNEL_ID = 1
WAITING_FOR_CHANNEL_NAME = 2
WAITING_FOR_INVITE_LINK = 3
WAITING_FOR_REMOVE = 4

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main admin menu"""
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['add']} Add Channel", callback_data="add_channel")],
        [InlineKeyboardButton(f"{EMOJIS['channel']} View Channels", callback_data="view_channels")],
        [InlineKeyboardButton(f"{EMOJIS['remove']} Remove Channel", callback_data="remove_channel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""{EMOJIS['admin']} **Admin Panel**

Manage force join channels here."""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callbacks"""
    query = update.callback_query
    data = query.data
    
    if data == "add_channel":
        await add_channel_step1(update, context)
    elif data == "view_channels":
        await view_channels(update, context)
    elif data == "remove_channel":
        await remove_channel_menu(update, context)
    elif data == "back":
        await admin_menu(update, context)
    elif data.startswith("remove_"):
        channel_id = int(data.split("_")[1])
        await confirm_remove(update, context, channel_id)
    elif data.startswith("confirm_remove_"):
        channel_id = int(data.split("_")[2])
        await remove_channel_db(channel_id)
        await query.edit_message_text(
            f"{EMOJIS['check']} Channel removed successfully!",
            parse_mode="Markdown"
        )
        await admin_menu(update, context)

async def add_channel_step1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Ask for channel ID"""
    query = update.callback_query
    text = f"""{EMOJIS['channel']} **Add Channel**

Send the channel ID (as a number, e.g., -1001234567890)"""
    
    await query.edit_message_text(text, parse_mode="Markdown")
    return WAITING_FOR_CHANNEL_ID

async def add_channel_step2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Ask for channel name"""
    text = update.message.text.strip()
    
    try:
        channel_id = int(text)
        context.user_data["channel_id"] = channel_id
    except ValueError:
        await update.message.reply_text(f"{EMOJIS['error']} Invalid channel ID format.")
        return WAITING_FOR_CHANNEL_ID
    
    text = f"""{EMOJIS['channel']} **Add Channel**

Now send the channel name (display name):"""
    
    await update.message.reply_text(text, parse_mode="Markdown")
    return WAITING_FOR_CHANNEL_NAME

async def add_channel_step3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 3: Ask for invite link"""
    channel_name = update.message.text.strip()
    context.user_data["channel_name"] = channel_name
    
    text = f"""{EMOJIS['channel']} **Add Channel**

Now send the invite link (e.g., https://t.me/yourchannel):"""
    
    await update.message.reply_text(text, parse_mode="Markdown")
    return WAITING_FOR_INVITE_LINK

async def add_channel_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and add channel"""
    invite_link = update.message.text.strip()
    
    channel_data = {
        "channel_id": context.user_data["channel_id"],
        "name": context.user_data["channel_name"],
        "invite_link": invite_link
    }
    
    await add_channel_db(channel_data)
    
    text = f"""{EMOJIS['check']} **Channel Added Successfully!**

{EMOJIS['channel']} Name: {channel_data['name']}
🔗 Link: {invite_link}"""
    
    await update.message.reply_text(text, parse_mode="Markdown")
    
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['back']} Back to Admin Panel", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What next?", reply_markup=reply_markup)
    
    context.user_data.clear()
    return ConversationHandler.END

async def view_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all channels"""
    query = update.callback_query
    channels = load_channels()
    
    if not channels:
        text = f"{EMOJIS['error']} No channels added yet."
    else:
        text = f"{EMOJIS['channel']} **Force Join Channels:**\n\n"
        for i, channel in enumerate(channels, 1):
            text += f"{i}. **{channel['name']}**\n"
            text += f"   🔗 {channel['invite_link']}\n\n"
    
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def remove_channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show channels to remove"""
    query = update.callback_query
    channels = load_channels()
    
    if not channels:
        text = f"{EMOJIS['error']} No channels to remove."
        keyboard = [
            [InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return
    
    text = f"{EMOJIS['remove']} **Select Channel to Remove:**\n\n"
    keyboard = []
    
    for channel in channels:
        text += f"• {channel['name']}\n"
        keyboard.append([
            InlineKeyboardButton(
                f"Remove {channel['name']}", 
                callback_data=f"remove_{channel['channel_id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def confirm_remove(update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id: int):
    """Confirm channel removal"""
    query = update.callback_query
    channels = load_channels()
    channel = next((c for c in channels if c["channel_id"] == channel_id), None)
    
    if not channel:
        await query.answer("Channel not found!")
        return
    
    text = f"{EMOJIS['error']} **Remove Channel?**\n\n{channel['name']}\n\nThis action cannot be undone."
    
    keyboard = [
        [InlineKeyboardButton("Yes, Remove", callback_data=f"confirm_remove_{channel_id}")],
        [InlineKeyboardButton("Cancel", callback_data="remove_channel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

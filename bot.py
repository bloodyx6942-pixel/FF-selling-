#!/usr/bin/env python3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging
import json
import os
import random
import asyncio
import threading
from datetime import datetime
from flask import Flask

# ============================================================
# FLASK APP
# ============================================================
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "✅ Auto-Sell Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
OWNER_ID = int(os.environ.get("OWNER_ID", 8586849798))

# ============================================================
# STYLISH CHARACTERS
# ============================================================
STYLISH = {
    'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆',
    'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍',
    'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔',
    'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
    'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟',
    'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥',
    'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫',
    's': '𝐬', 't': '𝐭', 'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱',
    'y': '𝐲', 'z': '𝐳',
    '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒',
    '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
}

def stylish(text):
    return ''.join(STYLISH.get(c, c) for c in text)

# ============================================================
# PREMIUM EMOJIS
# ============================================================
PREMIUM_EMOJIS = {
    "fire": {"id": "6147524086768604985", "fallback": "🔥"},
    "crown": {"id": "6147565374289220368", "fallback": "👑"},
    "cross": {"id": "6273840152980755328", "fallback": "❌"},
    "check": {"id": "6274007313107915274", "fallback": "✔️"},
    "warning": {"id": "5852873584912896283", "fallback": "⚠️"},
    "lightning": {"id": "5971944878815317190", "fallback": "⚡"},
    "flex": {"id": "6147464060305676048", "fallback": "😎"},
    "stars": {"id": "6235403472741603087", "fallback": "⭐"},
    "shield": {"id": "5449449325434266744", "fallback": "🛡️"},
    "lock": {"id": "5465443379917629504", "fallback": "🔓"},
    "dollar": {"id": "5197434882321567830", "fallback": "💵"},
    "telegram": {"id": "5895735846698487922", "fallback": "🌐"},
    "verified": {"id": "6147565374289220368", "fallback": "✅"},
    "gem": {"id": "6147524086768604985", "fallback": "💎"},
    "target": {"id": "6273997026661241933", "fallback": "🎯"},
}

def get_emoji_html(name):
    if name in PREMIUM_EMOJIS:
        data = PREMIUM_EMOJIS[name]
        return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>'
    return ""

def e(name):
    return get_emoji_html(name)

def get_random_emojis(count=2):
    names = list(PREMIUM_EMOJIS.keys())
    if not names:
        return ["", ""]
    selected = random.sample(names, min(count, len(names)))
    return [e(name) for name in selected]

def format_with_emojis(text):
    lines = text.split('\n')
    result = []
    for line in lines:
        if line.strip():
            left, right = get_random_emojis(2)
            styled_line = stylish(line)
            result.append(f"{left} {styled_line} {right}")
        else:
            result.append(line)
    return '\n'.join(result)

# ============================================================
# STORAGE
# ============================================================
CONFIG_FILE = "config.json"
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"

DEFAULT_MESSAGE = """💰 𝐏𝐑𝐈𝐂𝐄 - 𝟏𝟏.𝟓𝐤 𝐍𝐄𝐆𝐎 𝐅𝐎𝐑 𝐒𝐏𝐎𝐓 𝐁𝐔𝐘𝐄𝐑 ✅

🗡️ 𝐋𝐄𝐕𝐄𝐋 - 𝟖𝟎
🗡️ 𝐏𝐑𝐈𝐌𝐄 - 𝟕 (𝟖 𝐇𝐎𝐍𝐄 𝐖𝐀𝐋𝐀)

✅ 𝐅𝐌 𝐁𝐈𝐍𝐃𝐄𝐃

📞 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 - @𝐢𝐟𝐥𝐞𝐱𝐛𝐥𝐨𝐨𝐝𝐲"""

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {
        "groups": [],
        "message": DEFAULT_MESSAGE,
        "photo_url": None,
        "interval": 3,
        "active": True
    }

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except:
        pass

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
    except:
        pass

def load_banned():
    try:
        if os.path.exists(BANNED_FILE):
            with open(BANNED_FILE, 'r') as f:
                return set(json.load(f))
    except:
        pass
    return set()

def save_banned(banned):
    try:
        with open(BANNED_FILE, 'w') as f:
            json.dump(list(banned), f)
    except:
        pass

# ============================================================
# AUTO-SEND FUNCTION
# ============================================================
async def auto_send(context: ContextTypes.DEFAULT_TYPE):
    """Send message to all groups every interval seconds"""
    config = load_config()
    
    if not config.get("active", True):
        return
    
    groups = config.get("groups", [])
    if not groups:
        return
    
    message = config.get("message", DEFAULT_MESSAGE)
    photo_url = config.get("photo_url")
    
    # Randomly select a group
    group_id = random.choice(groups)
    
    try:
        if photo_url:
            await context.bot.send_photo(
                chat_id=group_id,
                photo=photo_url,
                caption=format_with_emojis(message),
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=group_id,
                text=format_with_emojis(message),
                parse_mode="HTML"
            )
        logger.info(f"Sent message to group {group_id}")
    except Exception as e:
        logger.error(f"Failed to send to {group_id}: {e}")

# ============================================================
# COMMANDS
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    users = load_users()
    if str(user.id) not in users:
        users[str(user.id)] = {
            "username": user.username or "NoUsername",
            "name": user.first_name or "User",
            "joined": datetime.now().isoformat()
        }
        save_users(users)
    
    if str(user.id) in load_banned() and user.id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("🚫 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐛𝐚𝐧𝐧𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    msg = """🔥 𝐀𝐔𝐓𝐎-𝐒𝐄𝐋𝐋 𝐁𝐎𝐓

📌 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬:
✅ 𝐀𝐮𝐭𝐨-𝐬𝐞𝐧𝐝𝐬 𝐞𝐯𝐞𝐫𝐲 𝟑𝐬
✅ 𝐌𝐮𝐥𝐭𝐢𝐩𝐥𝐞 𝐠𝐫𝐨𝐮𝐩𝐬

👑 𝐎𝐰𝐧𝐞𝐫 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:
/𝐚𝐝𝐝𝐠𝐫𝐨𝐮𝐩 𝐈𝐃 - 𝐀𝐝𝐝
/𝐫𝐞𝐦𝐨𝐯𝐞𝐠𝐫𝐨𝐮𝐩 𝐈𝐃 - 𝐑𝐞𝐦𝐨𝐯𝐞
/𝐬𝐞𝐭𝐦𝐞𝐬𝐬𝐚𝐠𝐞 - 𝐒𝐞𝐭
/𝐬𝐞𝐭𝐩𝐡𝐨𝐭𝐨 - 𝐒𝐞𝐭 𝐩𝐡𝐨𝐭𝐨
/𝐬𝐞𝐭𝐢𝐧𝐭𝐞𝐫𝐯𝐚𝐥 - 𝐒𝐞𝐭 𝐭𝐢𝐦𝐞
/𝐠𝐫𝐨𝐮𝐩𝐬 - 𝐋𝐢𝐬𝐭
/𝐨𝐧 /𝐨𝐟𝐟 - 𝐓𝐨𝐠𝐠𝐥𝐞
/𝐮𝐬𝐞𝐫𝐬 - 𝐋𝐢𝐬𝐭 𝐮𝐬𝐞𝐫𝐬
/𝐛𝐚𝐧 /𝐮𝐧𝐛𝐚𝐧 - 𝐁𝐚𝐧/𝐔𝐧𝐛𝐚𝐧"""
    
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            format_with_emojis("𝐔𝐬𝐚𝐠𝐞: /addgroup 𝐆𝐑𝐎𝐔𝐏_𝐈𝐃"),
            parse_mode="HTML"
        )
        return
    
    try:
        group_id = int(context.args[0])
        config = load_config()
        
        if group_id in config["groups"]:
            await update.message.reply_text(
                format_with_emojis(f"❌ 𝐆𝐫𝐨𝐮𝐩 {group_id} 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚𝐝𝐝𝐞𝐝!"),
                parse_mode="HTML"
            )
            return
        
        config["groups"].append(group_id)
        save_config(config)
        
        await update.message.reply_text(
            format_with_emojis(f"✅ 𝐆𝐫𝐨𝐮𝐩 {group_id} 𝐚𝐝𝐝𝐞𝐝!"),
            parse_mode="HTML"
        )
    except ValueError:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃!"),
            parse_mode="HTML"
        )

async def removegroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            format_with_emojis("𝐔𝐬𝐚𝐠𝐞: /removegroup 𝐆𝐑𝐎𝐔𝐏_𝐈𝐃"),
            parse_mode="HTML"
        )
        return
    
    try:
        group_id = int(context.args[0])
        config = load_config()
        
        if group_id not in config["groups"]:
            await update.message.reply_text(
                format_with_emojis(f"❌ 𝐆𝐫𝐨𝐮𝐩 {group_id} 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!"),
                parse_mode="HTML"
            )
            return
        
        config["groups"].remove(group_id)
        save_config(config)
        
        await update.message.reply_text(
            format_with_emojis(f"✅ 𝐆𝐫𝐨𝐮𝐩 {group_id} 𝐫𝐞𝐦𝐨𝐯𝐞𝐝!"),
            parse_mode="HTML"
        )
    except ValueError:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃!"),
            parse_mode="HTML"
        )

async def setmessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            format_with_emojis("𝐔𝐬𝐚𝐠𝐞: /setmessage 𝐘𝐎𝐔𝐑 𝐌𝐄𝐒𝐒𝐀𝐆𝐄"),
            parse_mode="HTML"
        )
        return
    
    message = " ".join(context.args)
    config = load_config()
    config["message"] = message
    save_config(config)
    
    await update.message.reply_text(
        format_with_emojis("✅ 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐮𝐩𝐝𝐚𝐭𝐞𝐝!"),
        parse_mode="HTML"
    )

async def setphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            format_with_emojis("𝐔𝐬𝐚𝐠𝐞: /setphoto 𝐏𝐇𝐎𝐓𝐎_𝐔𝐑𝐋"),
            parse_mode="HTML"
        )
        return
    
    photo_url = context.args[0]
    config = load_config()
    config["photo_url"] = photo_url
    save_config(config)
    
    await update.message.reply_text(
        format_with_emojis("✅ 𝐏𝐡𝐨𝐭𝐨 𝐔𝐑𝐋 𝐮𝐩𝐝𝐚𝐭𝐞𝐝!"),
        parse_mode="HTML"
    )

async def setinterval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            format_with_emojis("𝐔𝐬𝐚𝐠𝐞: /setinterval 𝟑"),
            parse_mode="HTML"
        )
        return
    
    try:
        interval = int(context.args[0])
        if interval < 1:
            await update.message.reply_text(
                format_with_emojis("❌ 𝐈𝐧𝐭𝐞𝐫𝐯𝐚𝐥 >= 𝟏!"),
                parse_mode="HTML"
            )
            return
        
        config = load_config()
        config["interval"] = interval
        save_config(config)
        
        await update.message.reply_text(
            format_with_emojis(f"✅ 𝐈𝐧𝐭𝐞𝐫𝐯𝐚𝐥 𝐬𝐞𝐭 𝐭𝐨 {interval}𝐬!"),
            parse_mode="HTML"
        )
    except ValueError:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝!"),
            parse_mode="HTML"
        )

async def groups_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    config = load_config()
    groups_list = config.get("groups", [])
    
    if not groups_list:
        await update.message.reply_text(
            format_with_emojis("📭 𝐍𝐨 𝐠𝐫𝐨𝐮𝐩𝐬!"),
            parse_mode="HTML"
        )
        return
    
    msg = "📋 𝐆𝐑𝐎𝐔𝐏𝐒\n━━━━━━━━━━━━━━━━━━\n"
    for g in groups_list:
        msg += f"🆔 {g}\n"
    
    msg += f"\n📊 𝐓𝐨𝐭𝐚𝐥: {len(groups_list)}"
    
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def toggle_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    config = load_config()
    config["active"] = not config.get("active", True)
    save_config(config)
    
    status = "𝐎𝐍" if config["active"] else "𝐎𝐅𝐅"
    await update.message.reply_text(
        format_with_emojis(f"✅ 𝐁𝐨𝐭 𝐢𝐬 𝐧𝐨𝐰 {status}!"),
        parse_mode="HTML"
    )

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    users_data = load_users()
    
    if not users_data:
        await update.message.reply_text(
            format_with_emojis("📭 𝐍𝐨 𝐮𝐬𝐞𝐫𝐬!"),
            parse_mode="HTML"
        )
        return
    
    msg = "👥 𝐔𝐒𝐄𝐑𝐒\n━━━━━━━━━━━━━━━━━━\n"
    for uid, data in list(users_data.items())[:50]:
        username = data.get("username", "N/A")
        name = data.get("name", "Unknown")
        msg += f"🆔 {uid} | @{username} | {name}\n"
    
    if len(users_data) > 50:
        msg += f"\n... +{len(users_data)-50} more"
    
    msg += f"\n📊 𝐓𝐨𝐭𝐚𝐥: {len(users_data)}"
    
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            format_with_emojis("𝐔𝐬𝐚𝐠𝐞: /ban 𝐔𝐒𝐄𝐑_𝐈𝐃"),
            parse_mode="HTML"
        )
        return
    
    try:
        target_id = context.args[0]
        banned = load_banned()
        banned.add(target_id)
        save_banned(banned)
        await update.message.reply_text(
            format_with_emojis(f"✅ 𝐔𝐬𝐞𝐫 {target_id} 𝐛𝐚𝐧𝐧𝐞𝐝!"),
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝!"),
            parse_mode="HTML"
        )

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!"),
            parse_mode="HTML"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            format_with_emojis("𝐔𝐬𝐚𝐠𝐞: /unban 𝐔𝐒𝐄𝐑_𝐈𝐃"),
            parse_mode="HTML"
        )
        return
    
    try:
        target_id = context.args[0]
        banned = load_banned()
        if target_id in banned:
            banned.remove(target_id)
            save_banned(banned)
            await update.message.reply_text(
                format_with_emojis(f"✅ 𝐔𝐬𝐞𝐫 {target_id} 𝐮𝐧𝐛𝐚𝐧𝐧𝐞𝐝!"),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                format_with_emojis(f"❌ 𝐔𝐬𝐞𝐫 {target_id} 𝐧𝐨𝐭 𝐛𝐚𝐧𝐧𝐞𝐝!"),
                parse_mode="HTML"
            )
    except:
        await update.message.reply_text(
            format_with_emojis("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝!"),
            parse_mode="HTML"
        )

# ============================================================
# MAIN - ✅ FIXED
# ============================================================
def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addgroup", addgroup))
    application.add_handler(CommandHandler("removegroup", removegroup))
    application.add_handler(CommandHandler("setmessage", setmessage))
    application.add_handler(CommandHandler("setphoto", setphoto))
    application.add_handler(CommandHandler("setinterval", setinterval))
    application.add_handler(CommandHandler("groups", groups_list))
    application.add_handler(CommandHandler("on", toggle_bot))
    application.add_handler(CommandHandler("off", toggle_bot))
    application.add_handler(CommandHandler("users", users_list))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    
    # ✅ FIX: Schedule auto-send job after bot starts
    def start_auto_send_job():
        config = load_config()
        interval = config.get("interval", 3)
        job_queue = application.job_queue
        if job_queue:
            job_queue.run_repeating(auto_send, interval=interval, first=3)
            logger.info(f"Auto-send started with interval {interval}s")
    
    # ✅ Use asyncio.create_task with proper event loop
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.sleep(0))  # Small delay to ensure bot initialized
    start_auto_send_job()
    
    logger.info("Auto-Sell Bot Started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

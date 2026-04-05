import os
import logging
import asyncio
import time
from datetime import datetime, timezone
from flask import Flask, request
from telegram import Update, ChatMember
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
CHANNEL_USERNAME = "stainprojectss"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct:free"

SYSTEM_PROMPT = (
    "You are a smart, friendly, and helpful AI assistant. "
    "Answer clearly and concisely. Be conversational but accurate. "
    "If you don't know something, say so honestly."
)

flask_app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()
BOT_START_TIME = time.time()


# ── helpers ───────────────────────────────────────────────────────────────────

async def is_member_of_channel(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in [
            ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER
        ]
    except Exception:
        return False


async def ask_openrouter(messages: list) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/stainprojectss",
        "X-Title": "Stain AI Bot"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(OPENROUTER_URL, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter HTTP error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 429:
            return "⚠️ I'm getting too many requests right now. Try again in a moment."
        return "❌ Something went wrong reaching the AI. Try again."
    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
        return "❌ Something went wrong. Try again."


def get_history(context: ContextTypes.DEFAULT_TYPE) -> list:
    if "history" not in context.user_data:
        context.user_data["history"] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    return context.user_data["history"]


# ── /start ────────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await is_member_of_channel(context.bot, user.id):
        await update.message.reply_text(
            f"👋 Hey! Before you can use this bot, join our channel first.\n\n"
            f"👉 https://t.me/{CHANNEL_USERNAME}\n\n"
            "Once you've joined, send /start again.",
            disable_web_page_preview=True
        )
        return

    await update.message.reply_text(
        f"👋 Hey {user.first_name}! I'm *Stain AI* — your personal AI assistant. 🤖\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💬 *How it works:*\n\n"
        "Just send me any message and I'll reply intelligently. "
        "I remember our conversation as we go, so you can ask follow-up "
        "questions and I'll keep the context.\n\n"
        "━━━━━━━━━━━━━━━\n"
        "📌 *Commands:*\n"
        "• `/start` — show this message\n"
        "• `/ping` — check if I'm online\n"
        "• `/clear` — clear conversation history and start fresh\n"
        "• `/support` — contact the developer\n\n"
        "━━━━━━━━━━━━━━━\n"
        "⚡ *Powered by OpenRouter AI*\n\n"
        "Go ahead, ask me anything! 👇",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


# ── /ping ─────────────────────────────────────────────────────────────────────

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await is_member_of_channel(context.bot, user.id):
        await update.message.reply_text(
            f"⛔ Join our channel first: https://t.me/{CHANNEL_USERNAME}",
            disable_web_page_preview=True
        )
        return

    # Measure latency
    start = time.time()
    sent = await update.message.reply_text("🏓 Pinging...")
    latency = (time.time() - start) * 1000

    # Uptime
    uptime_seconds = int(time.time() - BOT_START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    # Current date and time (UTC)
    now = datetime.now(timezone.utc).strftime("%A, %d %B %Y — %H:%M:%S UTC")

    await sent.edit_text(
        f"🏓 *Pong!*\n\n"
        f"⚡ *Latency:* `{latency:.1f}ms`\n"
        f"🟢 *Status:* Online\n"
        f"⏱ *Uptime:* `{uptime_str}`\n"
        f"🕐 *Time:* `{now}`",
        parse_mode="Markdown"
    )


# ── /clear ────────────────────────────────────────────────────────────────────

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await is_member_of_channel(context.bot, user.id):
        await update.message.reply_text(
            f"⛔ Join our channel first: https://t.me/{CHANNEL_USERNAME}",
            disable_web_page_preview=True
        )
        return

    context.user_data["history"] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    await update.message.reply_text(
        "🧹 Conversation cleared! Let's start fresh.\n\nAsk me anything 👇"
    )


# ── /support ─────────────────────────────────────────────────────────────────

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 *Support & Contact*\n\n"
        "Need help, have feedback, or want to report an issue? "
        "Reach out to the developer directly.\n\n"
        "━━━━━━━━━━━━━━━\n"
        "👤 *Developer:* Stain\n"
        "🔗 *Linktree:* https://linktr.ee/iamevanss\n"
        "✈️ *Telegram:* https://t.me/heisevanss\n"
        "━━━━━━━━━━━━━━━\n\n"
        "Response times may vary. Please be patient and descriptive when reaching out.",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


# ── message handler ───────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if not text:
        return

    if not await is_member_of_channel(context.bot, user.id):
        await update.message.reply_text(
            f"⛔ You need to join our channel to use this bot.\n\n"
            f"👉 https://t.me/{CHANNEL_USERNAME}",
            disable_web_page_preview=True
        )
        return

    # Typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Build history and append user message
    history = get_history(context)
    history.append({"role": "user", "content": text})

    # Get AI response
    reply = await ask_openrouter(history)

    # Append assistant reply to history
    history.append({"role": "assistant", "content": reply})

    # Cap history at 20 exchanges to avoid token bloat (keep system prompt)
    if len(history) > 41:
        context.user_data["history"] = [history[0]] + history[-40:]

    await update.message.reply_text(reply)


# ── webhook / flask ───────────────────────────────────────────────────────────

@flask_app.route("/health")
def health():
    return "OK", 200


@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    asyncio.run(process_update(data))
    return "OK", 200


async def process_update(data):
    update = Update.de_json(data, application.bot)
    await application.process_update(update)


async def setup():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND,
            handle_message
        )
    )
    await application.initialize()
    await application.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")


if __name__ == "__main__":
    asyncio.run(setup())
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

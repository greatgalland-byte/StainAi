# Stain AI Bot 🤖

A smart Telegram AI assistant powered by OpenRouter (Mistral 7B). Responds to any message with AI, remembers conversation context, and includes useful commands.

## Features
- 💬 AI replies to every message (context-aware)
- 🔐 Join gate — must be a member of @stainprojectss
- 🧠 Conversation memory per user session
- 🏓 Ping with real latency, uptime, and live time
- 🧹 Clear command to reset conversation history
- ⚡ Webhook mode via Railway

## Commands
| Command | Description |
|---------|-------------|
| `/start` | Join gate check + full intro |
| `/ping` | Latency, uptime, and current time |
| `/clear` | Wipe conversation history and start fresh |
| Any text | AI responds intelligently |

## Setup

### 1. Create the bot
- Message @BotFather on Telegram → `/newbot`
- Copy the bot token

### 2. Get OpenRouter API key
- Go to [openrouter.ai](https://openrouter.ai)
- Sign up → **Keys** → **Create Key**
- Free tier works — no payment needed

### 3. Deploy on Railway
- Create a new project on [railway.app](https://railway.app)
- Connect this GitHub repo
- Add environment variables:
```
BOT_TOKEN=your_bot_token_here
OPENROUTER_API_KEY=your_openrouter_key_here
```
- Set start command: `python main.py`
- Deploy!

### 4. Verify
Check Railway logs for:
```
Webhook set: https://your-app.up.railway.app/your_bot_token
```

That means the bot is live. 🚀

## Stack
- Python 3
- python-telegram-bot 21.3
- Flask (webhook server)
- httpx (async HTTP)
- OpenRouter API — `mistralai/mistral-7b-instruct:free`
- Deployed on Railway

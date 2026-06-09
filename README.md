# Telegram social-search bot (starter)

This repository contains a minimal Telegram bot (Python) that saves text/links into a local SQLite database and supports simple search.

Designed for beginners and to run on Replit or Termux (Android).

Files:
- bot.py: main bot code (polling)
- requirements.txt: Python dependencies
- .env.example: example environment variables

Quick start (Replit - recommended for Android):
1. Create a new Replit and import this GitHub repo (Import from GitHub).
2. In Replit, go to Secrets/Environment variables and add TELEGRAM_TOKEN with your bot token from BotFather.
3. Run the repl (Run button) — the bot uses polling and will start.

How to get a Telegram bot token:
1. Open Telegram and start a chat with @BotFather
2. Send /newbot and follow instructions. BotFather will give you a token like 123456:ABC-DEF...
3. Use that token as TELEGRAM_TOKEN.

Commands supported:
- /start - help
- /save <text> - save a text or link
- /search <query> - search saved content
- Sending any message will also save it automatically.

Notes:
- The bot stores data in data.db (SQLite) in the repo root.
- If your environment's SQLite doesn't support FTS5, the bot will fallback to a simple LIKE search.
- For production, consider hosting options (Docker, VPS) and respecting platform terms when collecting external content.

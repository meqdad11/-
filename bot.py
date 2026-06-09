import os
import sqlite3
from datetime import datetime
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Simple Telegram bot that saves texts/links and supports basic full-text search (FTS if available)

DB_PATH = os.environ.get('DB_PATH', 'data.db')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

USE_FTS = True

def ensure_db():
    global USE_FTS
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # Try to create an FTS5 virtual table
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS items USING fts5(content, source, platform, timestamp);")
        conn.commit()
        USE_FTS = True
    except sqlite3.OperationalError:
        # FTS5 not available; fallback to normal table and use LIKE search
        USE_FTS = False
        c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, content TEXT, source TEXT, platform TEXT, timestamp TEXT);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_items_content ON items(content);")
        conn.commit()
    return conn

conn = ensure_db()

def save_item(content: str, source: str = '', platform: str = ''):
    ts = datetime.utcnow().isoformat()
    c = conn.cursor()
    if USE_FTS:
        c.execute("INSERT INTO items(content, source, platform, timestamp) VALUES (?, ?, ?, ?)", (content, source, platform, ts))
    else:
        c.execute("INSERT INTO items(content, source, platform, timestamp) VALUES (?, ?, ?, ?)", (content, source, platform, ts))
    conn.commit()

def search_items(query: str, limit: int = 10):
    c = conn.cursor()
    if USE_FTS:
        # Use FTS match; for simple queries, pass as-is
        try:
            rows = c.execute("SELECT rowid, content, source, platform, timestamp FROM items WHERE items MATCH ? LIMIT ?", (query, limit)).fetchall()
        except sqlite3.OperationalError:
            rows = []
    else:
        # Fallback: basic LIKE search (case-insensitive)
        pattern = f"%{query}%"
        rows = c.execute("SELECT id, content, source, platform, timestamp FROM items WHERE content LIKE ? LIMIT ?", (pattern, limit)).fetchall()
    return rows

# Telegram command handlers

def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحباً! أنا بوت بسيط لحفظ والبحث عن نصوص/روابط.\nCommands:\n/save <text> - لحفظ نص أو رابط\n/search <query> - للبحث\nإرسل أي رسالة لأحفظها أيضاً.")


def save_command(update: Update, context: CallbackContext):
    text = ' '.join(context.args)
    if not text:
        update.message.reply_text("استخدم: /save <النص أو الرابط>")
        return
    save_item(text, source=str(update.message.from_user.id), platform='telegram')
    update.message.reply_text("تم الحفظ ✅")


def search_command(update: Update, context: CallbackContext):
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("استخدم: /search <كلمة أو جملة>")
        return
    results = search_items(query, limit=10)
    if not results:
        update.message.reply_text("لا توجد نتائج.")
        return
    messages = []
    for r in results:
        rid, content, source, platform, ts = r
        snippet = content
        if len(snippet) > 400:
            snippet = snippet[:400] + '...'
        messages.append(f"ID: {rid}\n{snippet}\nمن: {platform} ({source})\n{ts}")
    update.message.reply_text('\n\n'.join(messages))


def echo_save(update: Update, context: CallbackContext):
    # Save any incoming text message
    if update.message and update.message.text:
        text = update.message.text
        save_item(text, source=str(update.message.from_user.id), platform='telegram')
        # Acknowledge briefly (optional)
        # update.message.reply_text('تم الحفظ (رسالة).')


def error_handler(update: object, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main():
    if not TELEGRAM_TOKEN:
        print('ERROR: TELEGRAM_TOKEN environment variable not set.')
        return

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('save', save_command))
    dp.add_handler(CommandHandler('search', search_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_save))
    dp.add_error_handler(error_handler)

    print('Bot started. Polling...')
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

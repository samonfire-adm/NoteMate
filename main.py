from dotenv import load_dotenv
import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Loading local env file 
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

token = os.getenv("TOKEN")

# Database setup
def init_db():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filepath TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_note(title, filepath):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notes (title, filepath) VALUES (?, ?)', (title, filepath))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, My Name is Note Mate")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    capital_message = " ".join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=capital_message)

async def get_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = " ".join(context.args)
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT filepath FROM notes WHERE title = ?', (title,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        file_path = result[0]
        if os.path.exists(file_path):
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, 'rb'))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="File not found.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Note not found.")

if __name__ == '__main__':
    # Initialize the database and add a sample note
    init_db()
    add_note("function_in_python", "notes/function_in_python.pdf")
    add_note("sample_ppt", "notes/sample.ppt")

    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler('caps', caps)
    note_handler = CommandHandler('note', get_note)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(caps_handler)
    application.add_handler(note_handler)
    
    application.run_polling()

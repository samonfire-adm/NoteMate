from dotenv import load_dotenv
import os
import logging
import sqlite3
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Load environment variables
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

token = os.getenv("TOKEN")

# Database setup
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filepath TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_note(title, filepath):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notes (title, filepath) VALUES (?, ?)', (title, filepath))
    conn.commit()
    conn.close()

def store_message(user_id, message):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (user_id, message) VALUES (?, ?)', (user_id, message))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Notes", callback_data='notes'),
            InlineKeyboardButton("Jobs", callback_data='jobs'),
            InlineKeyboardButton("Offers", callback_data='offers')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, My Name is Note Mate. Please choose an option:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'notes':
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You selected Notes!")
        # Add logic to handle notes
    elif query.data == 'jobs':
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You selected Jobs!")
        # Add logic to handle jobs
    elif query.data == 'offers':
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You selected Offers!")
        # Add logic to handle offers

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    
    # Store the user message in the database
    store_message(user_id, user_message)
    
    # Respond based on specific keywords
    if "Python Course" in user_message:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Check out our latest Python course: [Python Course Link]")
    elif "Latest Webinar" in user_message:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Join our latest webinar: [Webinar Link]")
    elif "Referrals" in user_message:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Refer a friend and get discounts: [Referral Link]")
    elif "Latest Job" in user_message:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Here are the latest job listings: [Job Listings Link]")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for your message. We will get back to you soon!")

async def get_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = " ".join(context.args)
    conn = sqlite3.connect('bot_data.db')
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
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    note_handler = CommandHandler('note', get_note)
    button_handler = CallbackQueryHandler(button)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(note_handler)
    application.add_handler(button_handler)
    
    application.run_polling()

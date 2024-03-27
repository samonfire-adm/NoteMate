from dotenv import load_dotenv
import os
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler,filters

# Loading local env file 
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
token = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hy My Name is Note Mate")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def caps(update:Update, context: ContextTypes.DEFAULT_TYPE):
    capital_message = " ".join(context.args).upper()
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text=capital_message)


    

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler('caps', caps)
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(caps_handler)
    
    application.run_polling()
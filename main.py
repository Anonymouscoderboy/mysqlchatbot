import logging
import random
import psycopg2
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='chatbot',
    user='your_username',
    password='rishi@123'
)
cursor = conn.cursor()

# Define the command handlers
def start(update: Update, context):
    """Send a welcome message when the command /start is issued."""
    update.message.reply_text('Hello! I am your Telegram chatbot. How can I assist you?')

def help(update: Update, context):
    """Send a help message when the command /help is issued."""
    update.message.reply_text('This is the help message.')

def echo(update: Update, context):
    """Echo the user's message and store the chat response."""
    user_message = update.message.text

    # Retrieve the previous chat response from the database
    previous_response = get_previous_response()

    # Store the user's message and the previous response in the database
    store_chat_response(user_message, previous_response)

    # Retrieve a new response from the database based on the user's message and the previous response
    new_response = get_response(user_message, previous_response)

    # Store the new response in the database
    store_chat_response(new_response, user_message)

    update.message.reply_text(new_response)

def get_previous_response():
    """Retrieve the previous chat response from the database."""
    query = """
        SELECT message
        FROM chat_responses
        ORDER BY id DESC
        LIMIT 1
    """
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        return result[0]  # Extract the previous response from the query result
    else:
        return ''

def store_chat_response(message, response):
    """Store the chat response in the database."""
    query = """
        INSERT INTO chat_responses (message, response)
        VALUES (%s, %s)
    """
    cursor.execute(query, (message, response))
    conn.commit()

def get_response(message, previous_response):
    """Retrieve a response from the database based on the message and the previous response."""
    query = """
        SELECT response
        FROM responses
        WHERE message = %s AND previous_response = %s
        ORDER BY RANDOM()
        LIMIT 1
    """
    cursor.execute(query, (message, previous_response))
    result = cursor.fetchone()

    if result:
        return result[0]  # Extract the response from the query result
    else:
        return "I'm sorry, I don't have a response for that."

def error(update: Update, context):
    """Log errors caused by updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Set up the Telegram bot token
TOKEN = '5541091861:AAGvV4D3iB2CN5il4QWbZuTdTWxB6WxN2cM'

def main():
    """Start the bot."""
    # Create the Updater and pass in the bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # Add echo handler for all messages
    dp.add_handler(MessageHandler(Filters.text, echo))

    # Log all errors
    dp.add_error_handler(error)

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()

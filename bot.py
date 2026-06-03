import os
import logging
import asyncio
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from wsgi import app  # Import the web server

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcoming message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Welcome to Wordtonebot! \n\n"
        "Send me any sentence, and I will give you creative variations with different tones!"
    )

async def rewrite_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rewrites the user's text into different creative tones."""
    user_text = update.message.text
    
    await update.message.reply_chat_action(action="typing")
    
    prompt = f"""
    Act as a creative writing assistant. Provide 3 distinct variations of the following sentence: "{user_text}".
    Format your response exactly like this:
    📝 **Professional:** [variation]
    ✨ **Creative/Casual:** [variation]
    🔥 **Energetic/Persuasive:** [variation]
    """
    
    try:
        response = model.generate_content(prompt)
        reply = response.text
    except Exception as e:
        logging.error(f"AI Error: {e}")
        reply = "Sorry, I stumbled while trying to rewrite that. Please try again!"

    await update.message.reply_text(reply, parse_mode="Markdown")

def run_flask():
    """Runs the dummy web server for Render health checks."""
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def main():
    """Start the bot."""
    # Start the Flask web server in a separate background thread
    Thread(target=run_flask, daemon=True).start()

    # Build the Telegram Bot application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, rewrite_text))

    # Run the bot using polling
    application.run_polling()

if __name__ == '__main__':
    main()

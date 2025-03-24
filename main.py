import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

# Your bot token
API_TOKEN = "7770292317:AAEx_FmuU-jfSwDO8bAg5rkd3SW-GcQivJ0"  # Replace with your actual bot token
WEBHOOK_URL = "https://telbot-webhook.onrender.com/webhook"  # Replace with your Render URL

# Create Telegram application
application = Application.builder().token(API_TOKEN).build()

# Define a start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello, I am your bot!")

# Define a help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Send /start to get a greeting!")

# Register command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram updates."""
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.on_event("startup")
async def set_webhook():
    """Set Telegram webhook when the app starts."""
    await application.bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)

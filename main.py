import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Your bot token
API_TOKEN = "7770292317:AAEx_FmuU-jfSwDO8bAg5rkd3SW-GcQivJ0"  # Replace with your actual bot token
WEBHOOK_URL = "https://telbot-webhook.onrender.com/webhook"  # Replace with your Render URL

# Function to send a message to the user
def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=data)
    return response.json()

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

@app.get("/")
async def root():
    return {"message": "Bot is running!"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Received data:", data)  # Log incoming data for debugging

    # Process the incoming update and send a message
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = "Hello, I received your message!"  # Customize your response here
        send_message(chat_id, text)

    return {"status": "ok"}

@app.on_event("startup")
async def set_webhook():
    """Set Telegram webhook when the app starts."""
    await application.bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    import uvicorn
    # Get the port from the environment, default to 10000 if not set
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

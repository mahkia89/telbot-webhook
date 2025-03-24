import os
import logging
from fastapi import FastAPI, Request
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import uvicorn

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

# Root endpoint to check if the bot is running
@app.get("/")
async def root():
    return {"message": "Bot is running!"}

# Webhook endpoint to handle POST requests from Telegram
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("Received data:", data)  # Log incoming update data for debugging
        
        # Process the incoming update
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = "Hello, I received your message!"
            
            # Send a response back to the user
            send_message(chat_id, text)

        return {"status": "ok"}
    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}

# To set webhook manually using the Telegram API
def set_webhook():
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    webhook_url = "https://telbot-webhook.onrender.com/webhook"  # Replace with your actual webhook URL
    params = {"url": webhook_url}
    response = requests.post(url, params=params)
    print(response.json())

# Set webhook when the app starts
@app.on_event("startup")
async def startup_event():
    """Set the webhook when the app starts."""
    set_webhook()

# Run the FastAPI application using Uvicorn
if __name__ == "__main__":
    # Get the port from the environment, default to 10000 if not set (for Render)
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

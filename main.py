import os
from contextlib import asynccontextmanager
from http import HTTPStatus
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters

# Load environment variables from .env file
load_dotenv()
TELEGRAM_TOKEN: str = os.getenv('BOT_TOKEN')
WEBHOOK_URL: str = os.getenv('RENDER_URL')

# Create the Telegram bot application
bot_app = (
    Application.builder()
    .token(TELEGRAM_TOKEN)
    .updater(None)
    .build()
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Set up the webhook and manage bot lifecycle (start/stop)."""
    await bot_app.bot.setWebhook(url=WEBHOOK_URL)
    async with bot_app:
        await bot_app.start()
        yield
        await bot_app.stop()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def handle_update(request: Request):
    """Process incoming updates and forward to Telegram bot for handling."""
    incoming_message = await request.json()
    update = Update.de_json(data=incoming_message, bot=bot_app.bot)
    await bot_app.process_update(update)
    return Response(status_code=HTTPStatus.OK)

# Command handler for /hello
async def hello(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Respond to the /hello command with a greeting."""
    await update.message.reply_text("Hi! Send me a message and I'll repeat it!")

# Message handler for text messages
async def repeat_message(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo any received message back to the user."""
    await update.message.reply_text(update.message.text)

# Adding command and message handlers to the bot
bot_app.add_handler(CommandHandler(command="hello", callback=hello))
bot_app.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=repeat_message))

import os
import time
from contextlib import asynccontextmanager
from http import HTTPStatus
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN: str = os.getenv('BOT_TOKEN')
TELEGRAM_ID: str = os.getenv('TELEGRAM_ID')
WEBHOOK_DOMAIN: str = os.getenv('RENDER_URL')

# Build the Telegram Bot application
bot_builder = (
    Application.builder()
    .token(TELEGRAM_BOT_TOKEN)
    .updater(None)
    .build()
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Sets the webhook for the Telegram Bot and manages its lifecycle (start/stop)."""
    await bot_builder.bot.setWebhook(url=WEBHOOK_DOMAIN)
    async with bot_builder:
        await bot_builder.start()
        yield
        await bot_builder.stop()

app = FastAPI(lifespan=lifespan)

@app.post("/")
async def process_update(request: Request):
    """Handles incoming Telegram updates and processes them with the bot."""
    message = await request.json()
    update = Update.de_json(data=message, bot=bot_builder.bot)
    await bot_builder.process_update(update)
    return Response(status_code=HTTPStatus.OK)

async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command by sending a "Hello world!" message in response."""
    await update.message.reply_text("HEYYY! Send me a message and I'll echo it back to you")

async def echo(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

# Freelancer Jobs URL
URL = "https://www.freelancer.com/jobs/software-development"

# Keywords for filtering jobs
FILTER_KEYWORDS = [
"scaping", "Api"
]

def scrape_jobs():
    response = requests.get(URL)
    if response.status_code != 200:
        print("Failed to fetch page")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    job_elements = soup.select("div.JobSearchCard-item")  # Update selector if necessary

    jobs = []
    for job in job_elements:
        title_element = job.select_one("a.JobSearchCard-primary-heading-link")
        description_element = job.select_one("p.JobSearchCard-primary-description")

        if title_element and description_element:
            title = title_element.get_text(strip=True)
            description = description_element.get_text(strip=True)
            link = f"https://www.freelancer.com{title_element['href']}"

            # Check if any keyword is in title or description
            if any(keyword.lower() in (title + description).lower() for keyword in FILTER_KEYWORDS):
                jobs.append({"title": title, "description": description, "link": link})

    return jobs

def send_to_telegram(job):
    message = f"📢 *New Job Alert!*\n\n*{job['title']}*\n{job['description']}\n\n[View Job]({job['link']})"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    requests.post(telegram_url, json=payload)

async def jobs(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Handles the /jobs command by scraping and sending job listings."""
    jobs = scrape_jobs()
    
    if jobs:
        for job in jobs:
            message = f"📢 *New Job Alert!*\n\n*{job['title']}*\n{job['description']}\n\n[View Job]({job['link']})"
            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=False)
            time.sleep(2)  # Avoid spamming Telegram
        await update.message.reply_text(f"✅ Sent {len(jobs)} jobs to you!")
    else:
        await update.message.reply_text("❌ No matching jobs found.")

bot_builder.add_handler(CommandHandler(command="start", callback=start))
bot_builder.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=echo))
bot_builder.add_handler(CommandHandler(command="jobs", callback=jobs))  # Add the /jobs command handler

# Run the FastAPI app (assuming the app is hosted using an ASGI server like Uvicorn)

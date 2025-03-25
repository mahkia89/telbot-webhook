
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
    """Handles the /start command by sending a greeting message."""
    await update.message.reply_text("Hello! Use /jobs keyword1 - keyword2 - keyword3 to find jobs.")

# Freelancer Jobs URL
URL = "https://www.freelancer.com/jobs/software-development"

def scrape_jobs(keywords):
    """Scrapes Freelancer for jobs matching user-defined keywords."""
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

            # Check if any user-specified keyword is in title or description
            if any(keyword.lower() in (title + description).lower() for keyword in keywords):
                jobs.append({"title": title, "description": description, "link": link})
    return jobs

async def jobs(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Handles the /jobs command by scraping and sending job listings."""
    message_text = update.message.text
    parts = message_text.split("/jobs")
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text(" Please enter keywords like: /jobs python - scraping - API")
        return

    # Extract and clean keywords
    keywords = [word.strip() for word in parts[1].split("-") if word.strip()]
    
    if not keywords:
        await update.message.reply_text("❌ Please provide at least one keyword.")
        return

Mahkia, [3/25/2025 4:09 PM]
jobs_list = scrape_jobs(keywords)
    
    if jobs_list:
        for job in jobs_list[:5]:  # Limit to top 5 jobs
            message = f"📢 *New Job Alert!*\n\n*{job['title']}*\n{job['description']}\n\n[View Job]({job['link']})"
            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=False)
            time.sleep(2)  # Avoid spamming Telegram
        await update.message.reply_text(f"✅ Sent {len(jobs_list[:5])} jobs to you!")
    else:
        await update.message.reply_text("❌ No matching jobs found.")

bot_builder.add_handler(CommandHandler(command="start", callback=start))
bot_builder.add_handler(CommandHandler(command="jobs", callback=jobs))  # Dynamic jobs handler

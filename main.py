import os
import time
import asyncio
from contextlib import asynccontextmanager
from http import HTTPStatus
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_DOMAIN = os.getenv('RENDER_URL')

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

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.post("/")
async def process_update(request: Request):
    """Handles incoming Telegram updates and processes them with the bot."""
    message = await request.json()
    logging.info(f"Received update: {message}")  # Log the entire update
    
    update = Update.de_json(data=message, bot=bot_builder.bot)
    await bot_builder.process_update(update)
    
    return Response(status_code=HTTPStatus.OK)

# Job sites dictionary
JOB_SITES = {
    "freelancer": "https://www.freelancer.com/jobs/software-development",
    "laborx": "https://laborx.com/jobs/development",
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command by sending a selection keyboard."""
    keyboard = [
        [InlineKeyboardButton("Freelancer", callback_data="freelancer")],
        [InlineKeyboardButton("LaborX", callback_data="laborx")],
        [InlineKeyboardButton("Both", callback_data="both")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a job site to search:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    context.user_data['selected_site'] = query.data
    await query.edit_message_text(f"You selected: {query.data.capitalize()}\nUse /jobs keyword1 - keyword2 to search for jobs.")

def scrape_jobs(keywords, site):
    """Scrapes Freelancer or LaborX for jobs matching user-defined keywords."""
    
    url = JOB_SITES.get(site)
    if not url:
        logging.error(f"Invalid site name: {site}")
        return []

    try:
        logging.info(f"Fetching jobs from {url}...")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        logging.info(f"Successfully fetched data from {url}, status: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Error fetching {site}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    if site == "freelancer":
        job_elements = soup.select("div.JobSearchCard-item")
    else:  # LaborX
        job_elements = soup.select("a.job-title.job-link.row")

    jobs = []
    for job in job_elements:
        if site == "freelancer":
            title_element = job.select_one("a.JobSearchCard-primary-heading-link")
            description_element = job.select_one("p.JobSearchCard-primary-description")
            link = f"https://www.freelancer.com{title_element['href']}" if title_element else ""
        else:  # LaborX
           title_element = job  # The <a> tag itself
           title = title_element.get_text(strip=True)  # Extract job title text
           description_element = job.find_next("p")  # Try to find the description in the next <p> tag
           description = description_element.get_text(strip=True) if description_element else "No description available"
           link = f"https://laborx.com{job['href']}" if job.has_attr("href") else ""


        if title_element and description_element:
            title = title_element.get_text(strip=True)
            description = description_element.get_text(strip=True)

            if any(keyword.lower() in (title + description).lower() for keyword in keywords):
                jobs.append({"title": title, "description": description, "link": link})

    logging.info(f"Scraped {len(jobs)} jobs from {site}")
    return jobs


async def jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /jobs command by scraping and sending job listings."""
    
    logging.info(f"Received /jobs command from user: {update.effective_user.id}, text: {update.message.text}")
    
    message_text = update.message.text
    parts = message_text.split("/jobs")
    
    if len(parts) < 2 or not parts[1].strip():
        logging.warning("User did not provide keywords.")
        await update.message.reply_text("❌ Please enter keywords like: /jobs python - scraping - API")
        return

    keywords = [word.strip() for word in parts[1].split("-") if word.strip()]
    if not keywords:
        logging.warning("User provided an empty keyword list.")
        await update.message.reply_text("❌ Please provide at least one keyword.")
        return

    selected_site = context.user_data.get("selected_site", "freelancer")
    logging.info(f"User selected site: {selected_site}")

    if selected_site == "both":
        jobs_freelancer = scrape_jobs(keywords, "freelancer")
        jobs_laborx = scrape_jobs(keywords, "laborx")
        jobs = jobs_freelancer + jobs_laborx
    else:
        jobs = scrape_jobs(keywords, selected_site)

    logging.info(f"Found {len(jobs)} jobs matching keywords {keywords} on {selected_site}")

    if jobs:
        for job in jobs[:5]:  # Limit to top 5 jobs
            message = f"📢 *New Job Alert!*\n\n*{job['title']}*\n{job['description']}\n\n[View Job]({job['link']})"
            await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=False)
            await asyncio.sleep(2)  # Asynchronous delay to prevent spam
            
        logging.info(f"Sent {len(jobs[:5])} jobs to user {update.effective_user.id}")
        await update.message.reply_text(f"✅ Sent {len(jobs[:5])} jobs to you!")
    else:
        logging.info(f"No jobs found for user {update.effective_user.id}")
        await update.message.reply_text("❌ No matching jobs found.")


bot_builder.add_handler(CommandHandler(command="start", callback=start))
bot_builder.add_handler(CallbackQueryHandler(button))
bot_builder.add_handler(CommandHandler(command="jobs", callback=jobs))  # Dynamic jobs handler

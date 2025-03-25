import os
import time
from contextlib import asynccontextmanager
from http import HTTPStatus
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN: str = os.getenv('BOT_TOKEN')
TELEGRAM_ID: str = os.getenv('TELEGRAM_ID')
WEBHOOK_DOMAIN: str = os.getenv('RENDER_URL')

# Define job websites
JOB_SITES = {
    "freelancer": "https://www.freelancer.com/jobs/software-development",
    "upwork": "https://www.upwork.com/nx/jobs/search/?q=software+development",
    "xlabour": "https://www.xlabour.com/jobs"
}

# Initialize the bot
bot_builder = (
    Application.builder()
    .token(TELEGRAM_BOT_TOKEN)
    .updater(None)
    .build()
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    await bot_builder.bot.setWebhook(url=WEBHOOK_DOMAIN)
    async with bot_builder:
        await bot_builder.start()
        yield
        await bot_builder.stop()

app = FastAPI(lifespan=lifespan)

@app.post("/")
async def process_update(request: Request):
    message = await request.json()
    update = Update.de_json(data=message, bot=bot_builder.bot)
    await bot_builder.process_update(update)
    return Response(status_code=HTTPStatus.OK)

async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command, sends an introduction message with website selection."""
    keyboard = [
        [InlineKeyboardButton("Freelancer", callback_data="freelancer")],
        [InlineKeyboardButton("Upwork", callback_data="upwork")],
        [InlineKeyboardButton("XLabour", callback_data="xlabour")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome! This bot helps you find freelance jobs.\n\n"
        "Please select a website to search for jobs:",
        reply_markup=reply_markup
    )

async def select_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles website selection and prompts the user to enter keywords."""
    query = update.callback_query
    await query.answer()
    context.user_data['selected_site'] = query.data
    await query.edit_message_text(
        f"✅ You selected *{query.data.capitalize()}*!\n\n"
        "Now, enter your keywords in this format:\n"
        "`/job keyword1 - keyword2 - keyword3`",
        parse_mode="Markdown"
    )

async def jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /job command, validates input, scrapes jobs, and sends results."""
    user_input = update.message.text
    
    if not user_input.startswith("/job "):
        await update.message.reply_text("❌ Invalid command. Use `/job keyword1 - keyword2 - keyword3`")
        return

    try:
        keywords = user_input[5:].strip().split(" - ")
        if not keywords or "" in keywords:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Invalid format. Use: `/job keyword1 - keyword2 - keyword3`")
        return
    
    selected_site = context.user_data.get('selected_site')
    if not selected_site:
        await update.message.reply_text("⚠️ Please select a website first by using /start.")
        return
    
    jobs = scrape_jobs(JOB_SITES[selected_site], keywords)
    
    if jobs:
        for job in jobs:
                    message = f"📢 *New Job Alert!*\n" \
                  f"*{job['title']}*\n" \
                  f"{job['description']}\n" \
                  f"[View Job]({job['link']})"

            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=False)
            time.sleep(2)
        await update.message.reply_text(f"✅ Sent {len(jobs)} jobs to you!")
    else:
        await update.message.reply_text("❌ No matching jobs found.")

def scrape_jobs(url, keywords):
    response = requests.get(url)
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
            
            if any(keyword.lower() in (title + description).lower() for keyword in keywords):
                jobs.append({"title": title, "description": description, "link": link})
    
    return jobs

# Add handlers
bot_builder.add_handler(CommandHandler(command="start", callback=start))
bot_builder.add_handler(CallbackQueryHandler(select_website))
bot_builder.add_handler(CommandHandler(command="job", callback=jobs))

# Run the FastAPI app

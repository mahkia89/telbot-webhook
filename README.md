# 🤖 Telegram Job Bot

## 📌 Overview
This project is a Telegram bot that helps users find software development jobs from **Freelancer** and **LaborX**. Users can search for jobs using keywords, receive daily job updates, and interact with the bot via inline keyboard buttons. 🚀

## 🔥 Features
- 🔍 Search for jobs on **Freelancer** and **LaborX** using custom keywords.
- ⏰ Receive **daily job updates** at 9 AM UTC.
- 🎛️ Interactive **inline keyboard** for easy navigation.
- 📰 **Web scraping** for real-time job listings.
- ⚡ **FastAPI** for webhook handling and Telegram bot integration.

## ⚙️ Requirements
- 🐍 Python **3.8+**
- 🤖 Telegram **Bot API Token**
- 🌐 **Render URL** for webhook deployment

## 🛠 Installation
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-repo/telegram-job-bot.git
cd telegram-job-bot
```

### 2️⃣ Create a `.env` file and add the following variables:
```env
BOT_TOKEN=your_telegram_bot_token
RENDER_URL=your_render_webhook_url
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Run the Bot Locally
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```
🚀 The bot will be available via Telegram!

## 📌 Usage
- **▶️ Start** the bot with `/start`.
- **🔍 Search** for jobs using `/jobs keyword1 - keyword2`.
- **📅 Set up daily job alerts** with `/daily_report`.
- **🛠 Select job sites** from the inline keyboard.

## 🏗 Deployment
To deploy this bot, use a cloud service like **Render** or **Heroku**, ensuring the webhook URL is correctly set up.

## 🤝 Contributing
Pull requests are welcome! If you want to contribute:
1. **Fork** the repository
2. **Create a new branch** (`git checkout -b feature-branch`)
3. **Commit your changes** (`git commit -m "Added feature X"`)
4. **Push to the branch** (`git push origin feature-branch`)
5. **Create a pull request** ✅

## 📧 Contact
For questions or collaboration, contact **Mahkia Golbashi** at 📩 [mahkiagolbashi@gmail.com](mailto:mahkiagolbashi@gmail.com).

## 📜 License
This project is licensed under the **MIT License**. 📝


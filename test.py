from fastapi import FastAPI, Request
import requests
import json

app = FastAPI()

# Telegram Bot Token
TOKEN = "7770292317:AAEx_FmuU-jfSwDO8bAg5rkd3SW-GcQivJ0"

# Function to send a message to the user
def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=data)
    return response.json()

# Webhook endpoint
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.api_route("/webhook")
async def handle_webhook(request: Request):
    return {"method": request.method, "message": "Request accepted"}


    # Process the incoming update
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = "Hello, I received your message!"
        
        # Send a response back to the user
        send_message(chat_id, text)

    return {"status": "ok"}

# To set webhook manually using the Telegram API
def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = "https://your-domain.com/webhook"  # Replace with your actual webhook URL
    params = {"url": webhook_url}
    response = requests.post(url, params=params)
    print(response.json())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=443)

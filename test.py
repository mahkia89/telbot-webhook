from fastapi import FastAPI, HTTPException, Request
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

# Webhook endpoint to handle POST requests
@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()  # Get the incoming JSON data
    print("Received data:", data)  # Log data for debugging
    
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
    webhook_url = "https://telbot-webhook.onrender.com/webhook"  # Replace with your actual webhook URL
    params = {"url": webhook_url}
    response = requests.post(url, params=params)
    print(response.json())

if __name__ == "__main__":
    # Get the port from the environment, default to 8000 if not set
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
